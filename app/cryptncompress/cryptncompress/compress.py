#!/usr/bin/env python3

"""
``compress`` module
=================

Module used to compress/decompress files in the lola project

"""

from pathlib import Path
import zipfile


class Extract:
    """
    Create a Extract object to hold information on compressed file, where to store output, etc ...
    """

    def __init__(self, archive: str, output_dir: str, files_in_archive: int = None):
        """
        Create a Extract object which hold information on how to extract a file
        A verification step is used to check is the archive is a zip file

        :param archive: path of the archive file
        :type archive: str
        :param output_dir: path of the directory when to extract files
        :type output_dir: str
        :param files_in_archive: If set, check the number of file in the archive
        Raise an error if there are more or less files. Default = None
        :type files_in_archive: int
        :return: an extract object
        :rtype: Extract
        """

        self.archive = Extract.__check_archive(archive, files_in_archive)
        self.output_dir = Path(output_dir)
        if not self.output_dir.is_dir():
            raise FileNotFoundError(f"{self.output_dir} does not exists.")

    @staticmethod
    def __check_archive(archive: str, file_number: int = None) -> Path:
        """
        Check if the archive is a zipfile and contains the good number of files

        :param archive: path of the archive
        :type archive: str
        :param file_number: number of file in the archive
        :type file_number: int
        :raise ExtractError: if the number of file is different or
        if the archive does not exist
        :return: The path of the archive
        :rtype: zipfile.ZipFile
        """
        archive = Path(archive)
        if not archive.is_file():
            raise IOError(f"'{archive}' file does not exist")

        if not zipfile.is_zipfile(archive):
            raise IOError(f"'{archive}' file is not a zipfile")

        zip_archive = zipfile.ZipFile(archive)
        if file_number:
            if len(zip_archive.namelist()) != file_number:
                raise IOError(
                    f"'{archive}' archive have more or less than {file_number} file(s)"
                )

        return archive

    def extract(self):
        """
        Extract files
        """
        with zipfile.ZipFile(self.archive, "r") as zipObj:
            zipObj.extractall(self.output_dir)


class Compress:
    """
    Create a Compress object to hold information on how to compress file, where to store output, etc ...
    """

    def __init__(self, output_archive: str):
        """
        Create a Compress object which hold information on how to compress files
        A verification step is used to check is the files exists

        :param output_archive: path of the output archive file
        :type output_archive: str
        :return: a Compress object
        :rtype: Compress
        """

        self.output_archive = Path(output_archive)

    @staticmethod
    def __check_file(f: str) -> Path:
        """
        Check if the exist and is readable

        :param f: path of the file to check
        :type f: str
        :return: A Path object of the file
        :rtype: pathlib.Path
        """
        my_file = Path(f)
        if not my_file.is_file():
            raise IOError(f"'{my_file}' file does not exist")

        return my_file

    def compress(self, files: list):
        """
        Compress a list of files

        :param files: a list of files
        :type files: list
        """
        sanitized_list_files = [self.__check_file(f) for f in files]

        zf = zipfile.ZipFile(self.output_archive, 'w', zipfile.ZIP_DEFLATED)
        for f in sanitized_list_files:
            zf.write(f, f.name)
