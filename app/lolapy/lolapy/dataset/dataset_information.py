#!/usr/bin/env python3

"""Fetch information on Dataset."""

from typing import TypedDict
from pathlib import Path

from lolapy.tools.frontend_api import FrontendRequest
from lolapy.tools import settings
from lolapy.dataset import errors as dataset_error
# from lolapy.dataset import mysql_connect
import shutil

class DatasetFileInfo(TypedDict):
    """Information on a data file in the dataset archive"""

    name: str | None
    size_bytes: int | None

class DatasetInfo(TypedDict):
    """Information returned to the frontend about a dataset"""

    size_mb: int | None
    files: list[DatasetFileInfo] | None

class DatasetInformation:
    """Object use to fetch information on a database based on its name."""

    def __init__(self, dataset_hash: str):
        """Constructor of DatasetInformation.

        Fetch data on a specific dataset.
        :dataset_hash: str: Hash unique of the dataset
        """
        self.dataset_hash = dataset_hash
        
    def get_dataset_dir(self) -> Path:
        """Return the path where the dataset files are stored"""
        dataset_dir = settings.get().lolapy_dataset_path / self.dataset_hash
        if not dataset_dir.exists():
            raise dataset_error.DatasetDoesNotExist(self.dataset_hash)
        return dataset_dir
        

    def get_size(self) -> int:
        """Return the complete size of the database for the dataset.

        Returns:
            int: Size of the database in MegaBytes
        """
        dataset_dir = self._get_dataset_dir()

        total_size_bytes = 0
        for f in dataset_dir.rglob("*"):
            if f.is_file():
                total_size_bytes += f.stat().st_size

        size_mb = round(total_size_bytes / (1024 * 1024))
        return int(size_mb)

    def get_dataset_info(self, user_hash: str) -> DatasetInfo:
        """Return basic information about a dataset.

        Used by the frontend to print a summary.

        returns:
        - size_mb: int: Size of the dataset in MegaBytes
        - files: list[DataFileInfo]: List of files in the dataset archive with

        :param user_hash: str: Hash unique of the user. Used when checking permission
        :raise error.DatasetPermissionDenied: If the user have no permission on the dataset
        """

        # Check if the user have permissions on the database
        # If frontend api return a 200, data are good, otherwise it will return 400
        has_permission = FrontendRequest.dataset_permission(
            user_hash, self.dataset_hash
        )
        if not has_permission:
            raise dataset_error.DatasetPermissionDenied(
                dataset=self.dataset_hash, user=user_hash
            )

        dataset_dir = self._get_dataset_dir()
        if not dataset_dir.exists():
            raise dataset_error.DatasetDoesNotExist(self.dataset_hash)
        size_mb = self.get_size()

        files: list[DatasetFileInfo] = []
        for f in dataset_dir.rglob("*"):
            if f.is_file():
                relative_name = f.relative_to(dataset_dir).as_posix()
                files.append(
                    DatasetFileInfo(
                        name=relative_name,
                        size_bytes=f.stat().st_size,
                    )
                )

        return DatasetInfo(size_mb=size_mb, files=files)


class DatasetRemove:
    def __init__(self, dataset_hash: str):
        self.dataset_hash = dataset_hash

    def remove(self, user_hash: str):
        # Check if the user have permissions on the database
        # If frontend api return a 200, data are good, otherwise it will return 400
        has_permission = FrontendRequest.dataset_permission(
            user_hash, self.dataset_hash
        )
        if not has_permission:
            raise dataset_error.DatasetPermissionDenied(
                dataset=self.dataset_hash, user=user_hash
            )

        dataset_dir = settings.get().lolapy_dataset_path / self.dataset_hash
        if not dataset_dir.exists():
            raise dataset_error.DatasetDoesNotExist(self.dataset_hash)

        shutil.rmtree(dataset_dir)
