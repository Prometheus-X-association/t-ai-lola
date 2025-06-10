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
import ijson
import jsonschema
from lolapy.dataset.dataset_information import DatasetInformation

import lolapy.dataset.errors as dataset_error
from lolapy.slurm.errors import SbatchImportDataset
from lolapy.tools.frontend_api import FrontendRequest
from lolapy.slurm import slurm_job
from lolapy.slurm import sbatch
from lolapy.tools import settings
from lolapy.dataset import mysql_connect


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
        self.job_name_trax_instance: str = f"trax_instance_{self.job_name}"
        self.job_name_populate_trax: str = f"populate_trax_{self.job_name}"

        # set in install_from_archive
        self.user_hash: str | None = None
        self.dataset_hash: str | None = None

        # ExtractArchive instance. Defined in install_from_archive()
        # Keep track of all object initialized in install_from_archive()
        self.extraction_obj: ExtractArchive | None = None
        # Path where to store splitted files
        self.splitted_dir: Path = (
            settings_app.nextflow_workdir / f"splitted_json_{self.import_id}"
        )
        # Keep track of splitted object
        self.split_obj: SplitxAPI | None = None  # Defined in install_from_archive()
        # Trax objects Defined in install_from_archive()
        self.trax_job: slurm_job.SlurmTrax | None = None
        self.populate_trax_job: slurm_job.SlurmJob | None = None
        self.dataset_size: int | None = None

    def install_from_archive(self):
        logging.debug(f"Start import database with import ID: {self.import_id}")
        details_message = f"Dataset temporary ID={self.import_id}"

        # Check if the encrypted dataset contains xapi data by reading the first byte
        # See cryptncompress library for more information
        # Do nothing if it's not xapi
        dataset_file_type = InstallDataset.get_dataset_filetype(self.archive_full_path)
        if dataset_file_type != "xapi":
            logging.info(
                f"The file {self.archive_full_path.name} is {dataset_file_type}. Do nothing"
            )
            FrontendRequest.log(
                log_type="ImportDataset",
                message="API got dataset but its not xapi.",
                details=f"{details_message}. The lolapy got a dataset to integrate but the dataset is '{dataset_file_type}' type",
            )
            return
        # Send start to frontend logs
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

        bordereau_path, xapi_path = self.check_extracted_files(
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

        self.split_obj = SplitxAPI(xapi_path=xapi_path, splitted_dir=self.splitted_dir)
        self.split_obj.split_json()

        # Create database if not already exists
        if self.dataset_hash not in mysql_connect.TraxDB.list_trax_db():
            mysql_connect.TraxDB.create_trax_db(self.dataset_hash)

        # Start trax instance on cluster
        self.trax_job = slurm_job.SlurmTrax(
            run_id=self.job_name_trax_instance,
            database_name=self.dataset_hash,
            sbatch_type=sbatch.SbatchScript.START_INIT_TRAX,
        )
        self.trax_job.start()
        logging.info(
            f"Run ID: {self.import_id}. Reserve the Trax instance for dataset {self.dataset_hash}"
        )
        self.wait_trax_ready(self.trax_job)
        logging.info(f"Import ID: {self.import_id}. Trax is ready to use")

        trax_docker_port = self.trax_job.get_docker_port()

        slurm_populate_trax = slurm_job.SlurmJob(
            run_id=self.job_name,
            trax_port=trax_docker_port,
            sbatch_type=sbatch.SbatchScript.POPULATE_TRAX,
            json_directory=self.splitted_dir,
        )
        logging.info(
            f"Run ID: {self.import_id}. Reserve the job to populate trax with xapi files"
        )
        slurm_populate_trax.start()
        # Wait until slurm job to populate Trax is pending by scheduler
        while slurm_populate_trax.is_pending():
            logging.info(
                f"Run ID: {self.import_id}. Slurm Job to populate Trax is pending by slurm"
            )
            time.sleep(60)
        # Wait until slurm job to populate Trax is done
        while slurm_populate_trax.is_done() == False:
            logging.info(
                f"Run ID: {self.import_id}. Slurm Job to populate Trax is running by slurm"
            )
            ## Get completion and send it to the frontend
            if completion := UploadProgress.get_progress(self.populate_trax_job):
                FrontendRequest.get(
                    f"/api/dataset/{self.dataset_hash}/progress/{completion}"
                )
            ## Check if data are in
            time.sleep(30)
        if not slurm_populate_trax.is_success():
            raise SbatchImportDataset(slurm_populate_trax.job_name)
        self.size = DatasetInformation(self.dataset_hash).get_size()

    def wait_trax_ready(self, trax_service: slurm_job.SlurmTrax) -> None:
        """Lock function to wait until trax is ready.

        This function lock the execution until it's return None
        Trax is runned by a sbatch script and have to wait in the slurm queue.
        Args:
            trax_service: Slurm instance where to find information on Trax
        """
        if trax_service.is_pending():
            logging.info(
                f"Import ID: {self.import_id}. Trax import server is pending by slurm"
            )
        while trax_service.is_pending():
            time.sleep(60)
        logging.info(f"Run ID: {self.import_id}. Start Slurm Job to populate Trax")

        # Sometimes the trax_obj.stdout_slurm is not instantly created by slurm. It raises an error if not
        # So loop 100 times until the file is created. Use for loop to avoid using a infinite loop
        for _ in range(100):
            try:
                # After the start of trax, it needs to initiate database with trax stuff. It can take time
                # Loop on the stdout until trax is full ready with the message "Trax for populating is running"
                # "Trax for populating is running" is generated by the sbatch script used to start trax container
                # (see /home/pnoel/Documents/lola/lolapy/lolapy/slurm/sbatch.py)
                while (
                    not b"Trax for populating is running"
                    in trax_service.stdout_slurm.read_bytes()
                ):
                    logging.info(
                        f"Import ID: {self.import_id}. Waiting for trax to be ready"
                    )
                    time.sleep(30)
            except FileNotFoundError:
                logging.debug(
                    f"Import ID: {self.import_id}. slurm stdout file '{str(trax_service.stdout_slurm)}' is missing. Re-try reading it"
                )
                time.sleep(1)
                continue
            break

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
            xapi_path = file_1
        else:
            bordereau_path = file_1
            xapi_path = file_2

        return bordereau_path, xapi_path

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
            The filetype of the dataset. "file" or "xapi"
        """
        with open(path_encrypted_data, "rb") as input_file:
            bin_file_type = input_file.read(1)  # Get firt byte
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


class SplitxAPI:
    """Split large JSON xAPI file into multiple files.

    Use the ijson to get a consistent usage of memory.
    Split the large JSON into chunk of 20 000 statements
    """

    statements_chunk = 20_000

    def __init__(self, xapi_path: Path, splitted_dir: Path | None = None):
        """Constructor for SplitJson object.

        :param json_path: Path: Path of the input json (xapi) file to split
        :param splitted_dir: Path: Path to the directory where to store splitted files.
        The dir must exist. If no set, a temporary directory is created with tempfile.mkdtemp(). (Default: None)
        """
        self.xapi_path = xapi_path
        self.splitted_dir = splitted_dir or Path(tempfile.mkdtemp())
        self.number_splitted_files = 0
        self.total_statements = 0

    def split_json(self):
        """Method to split large xAPI into smaller ones."""
        if not self.splitted_dir.exists():
            self.mkdir(self.splitted_dir)

        index_file = 1  # Start to 1. So the first file is {filename}_1

        json_file = open(self.xapi_path)
        statements = ijson.items(json_file, "item")
        statements_generator = (statement for statement in statements)

        # Temporary list to store json data. This list is purged when size >= statements_chunk
        json_statements_tmp = []
        try:
            for statement in statements_generator:
                json_statements_tmp.append(statement)
                self.total_statements += 1
                if len(json_statements_tmp) >= SplitxAPI.statements_chunk:
                    self.write_json(index_file, json_statements_tmp)
                    self.number_splitted_files += 1
                    index_file += 1
                    json_statements_tmp = []
            # Write last statements in file
            self.write_json(index_file, json_statements_tmp)
        except ijson.IncompleteJSONError:
            raise
        logging.info(
            f"Splitted '{self.xapi_path}' into {index_file} files in {self.splitted_dir}. Total statements = {self.total_statements}"
        )

    def write_json(self, index_file: int, json_data: list):
        """Write smaller json file."""
        file_path = self.splitted_dir / f"{index_file}.json"
        file_path.write_text(json.dumps(json_data))

    def remove_files(self):
        """Delete the directory with splitted json files."""
        shutil.rmtree(self.splitted_dir)
        logging.debug(f"Remove '{self.splitted_dir}' directory with splitted Json")

    def mkdir(self, path: Path):
        """Create directory to store splited"""
        if not path.exists():
            logging.debug(f"Create '{path}' directory")
            path.mkdir()


class UploadProgress:
    """Class to check progression of the uploading dataset."""

    @staticmethod
    def get_progress(slurm_job: slurm_job.SlurmJob | None) -> float | None:
        """Read slurm stdout file to parse the completion status.

        If the slurm file does not yet exist, return None.
        return None if there is no pattern in the file.
        if the pattern is found, return the completion as a float
        Args:
            slurm_job: If `SlurmJob`, the method analyze the `stdout` to compute the
                completion. If None, there is nothing to parse and return None
        Returns:
            None: if there is no progress data or if there is an error when parsing
                values
            Float: % of the completion with 1 decimal
        """
        if not slurm_job:
            return None
        # if stdout for slurm does not exist
        if not slurm_job.stdout_slurm.exists:
            return None

        regex = re.compile("DONE file ([0-9]+)/([0-9]+)")
        stdout_slurm: Path = slurm_job.stdout_slurm
        try:
            with open(stdout_slurm) as slurm_file:
                text = slurm_file.read().split()
            all_matches = []
            for line in text:
                if line.startswith("DONE file"):
                    matches = re.search(regex, line)
                    if matches:
                        all_matches.append((matches.group(1), matches.group(2)))
        except Exception as e:
            logging.warning(traceback.format_exc())
            logging.warning(
                f"Error when parsing slurm stdout to find upload progression: file'{stdout_slurm}': {e}"
            )
            return None
        if all_matches:
            # Return maximum value in % rounded with 2 digits
            return max([current / total for current, total in all_matches])
