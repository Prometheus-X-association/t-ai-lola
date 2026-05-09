#!/usr/bin/env python3

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from lolapy.errors import LolapyGlobalError

if TYPE_CHECKING:
    from lolapy.dataset import mysql_connect


class CreateDatasetError(LolapyGlobalError):
    """Main error for dataset module"""

    pass


class DatasetPermissionDenied(CreateDatasetError):
    """Error when user has no permission on dataset."""

    def __init__(self, user: str, dataset: str):
        """Constructor for DatasetPermissionDenied.

        It send log to the frontend when the error is raised

        :param user: str: Hash unique of the User who tried to access dataset
        :param dataset: str: Hash unique of the dataset
        """
        self.message = f"'{user}' has no permission to access '{dataset}' dataset. Permission denied"
        self.public_message = "Permission Denied"


class DatasetDoesNotExist(CreateDatasetError):
    """Error"""

    def __init__(self, hash_dataset: str):
        self.message = f"Dataset {hash_dataset} does not exist"
        self.public_message = self.message


class DatasetFileNumberError(CreateDatasetError):
    """Error when file in archive is superior to 2."""

    def __init__(self, file_number: int):
        max_file = 2
        self.message = f"Wrong file number in Dataset's Archive. There is '{file_number}'. Only {max_file} allowed."
        self.public_message = self.message


class DatasetDecryptError(CreateDatasetError):
    """Error when decrypting/decompressing archive."""

    def __init__(self, archive: Path, stderr: str):
        self.message = f"Error when decrypting/decompressing archive file: '{archive}' with cryptncompress lib. Error='{stderr}'"
        self.public_message = (
            "Error when trying to decrypt/uncompress archive file. Wrong format"
        )


class BordereauFormatError(CreateDatasetError):
    """Error if bordereau is wrong format."""

    def __init__(self, msg: str):
        """Constructor for the DatasetFormatError."""
        self.message = f"Error with bordereau file: {msg}"
        self.public_message = self.message


class MySQLError(Exception):
    """Main error for MySQL errors."""

    pass


class MySQLConnectionError(MySQLError):
    """Error when connecting to MySQL database"""

    def __init__(self, mysql: mysql_connect.MySQL, error: str):
        """Construct MySQLConnectionError.

        :param mysql: MySQL: MySQL object himself to get information on connection information
        :param error: str: Message of the error
        """
        self.message = f"Unable to connect to SQL Server with user/password. host:'{mysql.host}', port:'{mysql.port}', error:'{error}'"
        if mysql.database:
            self.message += f", database:'{mysql.database}'"
        self.public_message = LolapyGlobalError.standard_public_message


class MySQLCommandError(MySQLError):
    """Error in MySQL commands"""

    def __init__(self, command: str):
        """Construct MySQLCommandError.

        :param command: str: Command which fail on the SQL server
        """
        self.message = f"Error when running command to SQL server: command='{command}'"
        self.public_message = LolapyGlobalError.standard_public_message
