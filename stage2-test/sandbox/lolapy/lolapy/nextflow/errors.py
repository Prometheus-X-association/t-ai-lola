#!/usr/bin/env python3

"""List of all nextflow related errors."""

from pathlib import Path

from lolapy.errors import LolapyGlobalError


class NextflowEnvironmentError(LolapyGlobalError):
    """Main Error related to the nextflow installation"""

    pass

class NextflowWorkDirExists(NextflowEnvironmentError):
    def __init__(self, work_dir: Path, identifier: str):
        self.message = f"Unique identifier '{identifier}' for nextflow run must be unique. But {work_dir} already exists!"
        self.public_message = f"Unique identifier '{identifier}' for nextflow run must be unique. But directory aleady exists"

class NextflowExecutableError(NextflowEnvironmentError):
    def __init__(self, executable_path: Path, stderr: str):
        self.message = f"Error when testing the following nextflow binary: '{executable_path}'. Stderr: {stderr}"
        self.public_message = LolapyGlobalError.standard_public_message

class NextflowEnvironmentFileError(NextflowEnvironmentError):
    def __init__(self, message: str):
        self.message = message
        self.public_message = LolapyGlobalError.standard_public_message
