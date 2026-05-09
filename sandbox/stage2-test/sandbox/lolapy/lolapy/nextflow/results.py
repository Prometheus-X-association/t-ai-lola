#!/usr/bin/env python3

"""Module to manage results produced by nextflow

To prepare or get results, the object need the path of the working directory used by
the process. This workDir is stored in nextflow logs send to the frontend.
Usually, path are like '/home/lolauser/nf-workdir/b5/e62aababea38416fe27e21af985ee8'
"""

import logging
from pathlib import Path
import zipfile

from lolapy.tools import frontend_api
from lolapy.tools import settings
from lolapy.algorithm import errors as algorithm_errors

ARCHIVE_STATIC_NAME = "results_{}.zip"


class PrepareResults:
    def __init__(self, run_hash: str, working_directories: list[Path] | None):
        """Constructor of ScenarioResults.

        :param run_hash: str: hash of the run provided by the frontend
        :param working_directories: list[Path]: List of all working directory to compress.
        """
        # Generate the Path of the output archive lile '/home/lolauser/nf-workdir/results_dfgdjfsdf.zip'
        self.output_archive: Path = (
            settings.get().nextflow_workdir / ARCHIVE_STATIC_NAME.format(run_hash)
        )

        self.files: list[Path] | None = None  # defined in list_files

        self.working_directories: list[Path] | None = working_directories
        if self.working_directories:
            self.__remove_duplicate_dir()
            # Check if all directories in working_directories exists. Raise an error if not
            self.__exists_dir()

    def __remove_duplicate_dir(self):
        """Remove all duplicate directories.

        The method edit self.working_directories in place to remove duplicate.
        The frontend send all workdir in the logs. As each logs are in at most 3 copies, the same workdir
        can be present multiple times in the list. The filter of duplicate is made by the backend to allow
        compress data of failed process
        """
        if not self.working_directories:
            raise TypeError("self.working_directory is None and should be set")
        self.working_directories = list(set(self.working_directories))

    def __exists_dir(self):
        """Check if all directory exist.

        :raise: scenario_errors.NoWorkingDirectory: If the directory does not exist
        """
        if not self.working_directories:
            raise TypeError("self.working_directory is None and should be set")
        for dir in self.working_directories:
            if not dir.exists():
                raise algorithm_errors.NoWorkingDirectory(dir)

    def list_files(self, hidden: bool = True) -> list[Path]:
        """Defines value of self.files, list of all files present in the working directories

        By default, include hidden files. Exclude file named 'results.zip' to avoid recursive compression
        :param hidden: bool: If True, include hidden files. (default: True)
        :return: List[Path]: Return the Path of all files in all directories
        """
        if not self.working_directories:
            raise TypeError("self.working_directory is None and should be set")
        glob_pattern = "[!.]*"  # Exclude hidden files that start with .
        if hidden:
            glob_pattern = "*"
        all_files = []
        for dir in self.working_directories:
            all_files.extend(
                [
                    file
                    for file in dir.glob(glob_pattern)
                    if file.name != ARCHIVE_STATIC_NAME
                ]
            )
        return all_files

    def filter(self, list_filenames: list[str]):
        """Filter self.files to remove file that are not in list_filenames.

        Args:
            list_filenames: List of filename to search and to look
        """
        if not self.files:
            self.files = self.list_files()

        remains_files = []
        for my_file in self.files:
            if my_file.name in list_filenames:
                remains_files.append(my_file)

        self.files = remains_files

    def compress(self):
        """Compress all files in the working directry"""
        if not self.working_directories:
            raise TypeError("self.working_directory is None and should be set")

        if not self.files:
            self.files = self.list_files()

        with zipfile.ZipFile(self.output_archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in self.files:
                # Strip the workdir to the filename to avoid keeping full hierarchie.
                # For exemple a file named /home/lolauser/nf-workdir/f8/8dv3/my_file.csv become f8/8dv3/my_file.csv
                filename_in_archive = str(f).replace(
                    str(settings.get().nextflow_workdir), ""
                )
                zf.write(f, filename_in_archive)

    def prepare_send_archive(self) -> Path:
        """Prepare send file in the return of a Flask call.

        Check if file is available, raise an error if not.
        Raises:
            algorithm_errors.NoArchiveResults(): if the archive is not available
        Returns:
            Path: Path of the result archive
        TODO: Maybe check permission on file
        """
        if not self.output_archive.exists():
            raise algorithm_errors.NoArchiveResults(self.output_archive)
        return self.output_archive
