#!/usr/bin/env python3

"""
Module used to import dataset into a trax instance
"""

from pathlib import Path
import json
import logging
import re
import traceback
import uuid
import tempfile
from typing import Tuple
import time
import shutil

from cryptncompress import crypto, compress, errors as crypt_errors
import jsonschema
from lolapy.dataset.dataset_information import DatasetInformation

import lolapy.dataset.errors as dataset_error
# from lolapy.slurm.errors import SbatchImportDataset
from lolapy.tools.frontend_api import FrontendRequest
# from lolapy.slurm import slurm_job
# from lolapy.slurm import sbatch
from lolapy.tools import settings
# from lolapy.dataset import mysql_connect


class InstallDataset:
    """
    Object holding informations on a dataset

    Attributes:
        env: Environment that contains parameters of the whole Application
        archive_full_path: Full path of the archive to install. Based on the relative Path given in the constructor
            and the global Path where the Dataset is store
        import_id: Random uuid generated to identify the import session. This identifier is send to the frontend
            to identify the duration and number of time a dataset is uploaded
        job_name: Interior name to identify the installation step. Used in logs and with slurm jobs
        job_name_trax_instance: Name of the slurm job that run the Trax instance
        job_name_populate_trax: Name of the slurm job used to send splitted xAPI files to Trax instance
        user_hash: Hash unique of the user. Used for permission access on the dataset
        dataset_hash: Hash unique of the dataset.
        extraction_obj (ExtractArchive | None): ExtractArchive when created used to extract the whole encrypted archive
        splitted_dir: Path where will be stored encrypted files
        split_obj: SplitxAPI Object used to Split the xAPI file
        trax_job: SlurmTrax instance. This is the slurm job used to start the trax instance
        populate_trax_job: SlurmJob instance. This is the slurm job used to populate the Trax instance
        dataset_size: Size of the dataset at the end of the importation in Megabytes
    """

    def __init__(self, archive: Path):
        """Create an InstallDataset object.

        Args:
            archive: The archive containing dataset file and bordereau
        """
        settings_app = settings.get()
        self.archive_full_path: Path = settings_app.lolapy_dataset_path / archive
        self.import_id: str = str(uuid.uuid4())  # Identifier of the import
        # used in the frontend to compute import time
        self.job_name: str = f"importid_{self.import_id}"
        
        # set in install_from_archive
        self.user_hash: str | None = None
        self.dataset_hash: str | None = None

        # ExtractArchive instance. Defined in install_from_archive()
        # Keep track of all object initialized in install_from_archive()
        self.extraction_obj: ExtractArchive | None = None
        self.dataset_size: int | None = None
        

    def install_from_archive(self):
        logging.debug(f"Start import database with import ID: {self.import_id}")
        details_message = f"Dataset temporary ID={self.import_id}"

        # Check if the encrypted dataset contains xapi data by reading the first byte
        # See cryptncompress library for more information
        # Do nothing if it's not xapi
        # dataset_file_type = InstallDataset.get_dataset_filetype(self.archive_full_path)
        FrontendRequest.log(
            log_type="ImportDataset",
            message="API start to import a dataset",
            details=details_message,
        )

        try:
            self.extraction_obj = ExtractArchive(self.archive_full_path)
            self.extraction_obj.decrypt_archive()
            self.extraction_obj.extract_archive()
        except crypt_errors.CryptErrors as e:
            FrontendRequest.log(
                log_type="Error",
                message=str(e),
                details=f"Dataset temporary ID={self.import_id}",
            )
            raise dataset_error.DatasetDecryptError(
                archive=self.archive_full_path, stderr=str(e)
            )

        try:
            bordereau_path, data_path = self.check_extracted_files(
                self.extraction_obj.extract_dir
            )
        
            dataset_hash, user_hash = InstallDataset.read_bordereau(bordereau_path)
            self.dataset_hash = dataset_hash
            self.user_hash = user_hash
            logging.debug(
                f"Importing dataset {self.dataset_hash} for user {self.user_hash} for import ID {self.import_id}"
            )

            ## Send dataset hash to the frontend LOGS
            FrontendRequest.log(
                log_type="ImportDataset",
                message=f"Import dataset {self.dataset_hash}",
                details="Dataset temporary ID={tmp_id_dataset}",
            )

            # Check permission
            has_permission = FrontendRequest.dataset_permission(
                self.user_hash, self.dataset_hash
            )
            if not has_permission:
                raise dataset_error.DatasetPermissionDenied(
                    dataset=self.dataset_hash, user=self.user_hash
                )
            # Send start to the frontend to indicate the beginning of the upload
            FrontendRequest.get(f"/api/dataset/{self.dataset_hash}/start/{self.import_id}")

            settings_app = settings.get()
            dataset_dir = settings_app.lolapy_dataset_path / self.dataset_hash
            if not dataset_dir.exists():
                logging.info(f"Create dataset directory '{dataset_dir}'")
                dataset_dir.mkdir(parents=True, exist_ok=True)
                
            target_path = dataset_dir / data_path.name
            logging.info(f"Move dataset file '{data_path}' to '{target_path}'")
            
            # for progress bar in LOLA frontend
            UploadProgress.copy_with_progress(src=data_path, dst=target_path, 
                            dataset_hash=self.dataset_hash, import_id=self.import_id, 
                            start_progress=0.0,end_progress=1.0)
            
            # compute size of the dataset via DatasetInformation to keep logic in one place
            #self.dataset_size = DatasetInformation(self.dataset_hash).get_size()
            #logging.info(f"Dataset {self.dataset_hash} imported on filesystem, total size ~ {self.dataset_size} MB")

        finally:
            if self.extraction_obj:
                self.extraction_obj.remove_files()
       

    def check_extracted_files(self, extracted_dir: Path) -> Tuple[Path, Path]:
        """Check files in the extracted folder and return Path for bordereau and xapi.

        Args:
            extracted_dir: Path of the extracted directory containing xapi and bordereau file.
        Raises:
            dataset_error.DatasetFileNumberError: If there are more than 2 files in the extracted_dir.
        Returns:
            Tuple[Path, Path]: Return Path of bordereau file and Path of xapi file
        """
        # The directory should have 2 files, a bordereau and the dataset
        # These files are processed during the creation of the dataset
        all_files = list(extracted_dir.glob("*"))
        if len(all_files) > 2:
            raise dataset_error.DatasetFileNumberError(len(all_files))
        file_1, file_2 = all_files
        file_1, file_2 = Path(file_1), Path(file_2)
        # Consider bordereau is the smaller file
        # check the smaller file to avoid explosion memory
        if file_1.stat().st_size > file_2.stat().st_size:
            bordereau_path = file_2
            dataset_path = file_1
        else:
            bordereau_path = file_1
            dataset_path = file_2

        return bordereau_path, dataset_path

    @staticmethod
    def read_bordereau(bordereau_path: Path) -> Tuple[str, str]:
        """Try to read the bordereau file.

        Return as a tuple the dataset name and the user_hash
        If the bordereau file is in the wrong format, raise a BordereauFormatError
        Args:
            bordereau_path: Path: Path of the bordereau file
        Returns:
            Tuple[dataset_hash, hash_name]: A tuple of 2 strings, where dataset_hash is
                the dataset_hash and hash_name is the hash_name
        """
        # Describe what kind of json you expect.
        bordereau_schema = {
            "type": "object",
            "properties": {
                "dataset": {
                    "description": "The unique identifier for a dataset",
                    "type": "string",
                },
                "user": {
                    "description": "The unique identifier for a user",
                },
            },
            "required": ["dataset", "user"],
        }
        try:
            json_data = json.load(open(bordereau_path))
            jsonschema.validate(instance=json_data, schema=bordereau_schema)
        except jsonschema.ValidationError as err:
            # the file is not the bordereau file
            raise dataset_error.BordereauFormatError(str(err))
        except json.decoder.JSONDecodeError as err:
            raise dataset_error.BordereauFormatError(str(err))

        return json_data["dataset"], json_data["user"]

    @staticmethod
    def get_dataset_filetype(path_encrypted_data: Path) -> str:
        """Determine the type of archive.

        From an encrypted file, determine if the file is an xapi file and should
        be incorporate in trax. According to the documentation of cryptncompress package,
        the first byte represent the type of the file

        Args:
            path_encrypted_data: Path to the encrypted data file
        Returns:
            The filetype of the dataset. "file"
        """
        with open(path_encrypted_data, "rb") as input_file:
            bin_file_type = input_file.read(1)  # Get first byte
            return crypto.FileType.bin_to_str(bin_file_type)


class ExtractArchive:
    """Manage extraction and decryption of the archive"""

    def __init__(self, path_encrypted_file: Path):
        self.encrypted_file = path_encrypted_file
        self.decrypt_dir = Path(tempfile.mktemp())
        self.decrypted_output_file = self.decrypt_dir / "decrypted_file.zip"
        self.extract_dir = Path(tempfile.mktemp())

    def decrypt_archive(self):
        self.mkdir(self.decrypt_dir)
        app_settings = settings.get()
        decrypt_obj = crypto.Decrypt(app_settings.lolapy_dataset_decrypt_key)
        decrypt_obj.decrypt_file(
            input_file=self.encrypted_file, output_file=self.decrypted_output_file
        )

    def extract_archive(self):
        self.mkdir(self.extract_dir)
        extract_obj = compress.Extract(
            archive=str(self.decrypted_output_file),
            output_dir=str(self.extract_dir),
            files_in_archive=2,
        )
        extract_obj.extract()

    def mkdir(self, path: Path):
        if not path.exists():
            logging.debug(f"Create '{path}' directory")
            path.mkdir()

    def remove_files(self):
        """Delete all directories and files inside."""
        if self.decrypt_dir.exists():
            shutil.rmtree(self.decrypt_dir)
            logging.debug(f"Remove '{self.decrypt_dir}' directory with decrypt file")
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
            logging.debug(
                f"Remove '{self.extract_dir}' directory with extracted file(s)"
            )

class UploadProgress:
    """Class to check progression of the uploading dataset."""

    @staticmethod
    def copy_with_progress(
        src: Path,
        dst: Path,
        dataset_hash: str,
        import_id: str,
        start_progress: float = 0.0,
        end_progress: float = 1.0,
        chunk_size: int = 1024 * 1024,
    ):
        """Copy file from src to dst and send progress updates to frontend."""

        total_size = src.stat().st_size
        copied = 0

        if total_size == 0:
            FrontendRequest.get(f"/api/dataset/{dataset_hash}/progress/{end_progress}")
            dst.write_bytes(b"")
            return

        last_reported = -1.0

        with src.open("rb") as fsrc, dst.open("wb") as fdst:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break

                fdst.write(chunk)
                copied += len(chunk)

                fraction = copied / total_size
                progress = start_progress + (end_progress - start_progress) * fraction

                # clamp progress
                progress = max(0.0, min(progress, 1.0))

                # send update every 1%
                if progress - last_reported >= 0.01 or progress == 1.0:
                    FrontendRequest.get(
                        f"/api/dataset/{dataset_hash}/progress/{progress}"
                    )
                    last_reported = progress

        # FrontendRequest.get(f"/api/dataset/{dataset_hash}/complete/{import_id}")
