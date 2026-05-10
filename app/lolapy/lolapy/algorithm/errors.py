#!/usr/bin/env python3

"""Module to store errors related to algorithms"""

from pathlib import Path
from typing import List
import re

import pydantic
import jinja2

from lolapy.errors import LolapyGlobalError, extract_missing_fields


class AlgorithmErrors(LolapyGlobalError):
    """Main error for algorithm"""

    pass


class InstallationDirNotEmpty(AlgorithmErrors):
    """If Installation directory exist and not empty"""

    def __init__(self, directory: Path):
        self.directory = directory
        self.message = f"Can't clone repository, '{self.directory}' exists and is not empty"
        self.public_message = LolapyGlobalError.standard_public_message


class InstallationMissingRequiredFile(AlgorithmErrors):
    """If there is a missing file in the list of required files for a scenario."""

    def __init__(self, filename: str, algorithm: str):
        self.message = f"Installation of algorithm '{algorithm}' abord due to missing file: '{filename}'"
        ## hide path of the scenario in public_message
        self.public_message = f"Installation of algorithm abord due to missing file: '{filename}'"


class AlgorithmNotExist(AlgorithmErrors):
    """If the algorithm does not exist"""

    def __init__(self, directory: Path):
        self.message = f"Path '{directory}' does not exist"
        self.public_message = f"Algorithm {directory.stem} does not exist"


class AlgorithmRecipeMissingField(AlgorithmErrors):
    """If there is a missing field in the algorithm parameter
    TODO:"""

    def __init__(self, algorithm_data: dict, error: pydantic.ValidationError):
        if "name" in algorithm_data:
            algorithm_name = algorithm_data["name"]
        else:
            algorithm_name = "Missing 'name' field"
        self.message = f"Algo recipe '{algorithm_name}' is not well formated: {str(error)}"
        self.public_message = f"Algo recipe '{algorithm_name}' is not well formated: {str(error)}"


class AlgorithmParameterMissingField(AlgorithmErrors):
    """If there is a missing field in the algorithm parameter
    TODO:"""

    def __init__(self, algorithm_data: dict, error: pydantic.ValidationError):
        # In case the only missing field is name, we cannot search for the algorithm_name
        if "name" in algorithm_data:
            algorithm_name = algorithm_data["name"]
        else:
            algorithm_name = "Missing 'name' field"
        self.message = f"Parameter '{algorithm_name}' is not well formated: {str(error)}"
        self.public_message = f"Parameter '{algorithm_name}' is not well formated: {str(error)}"


class AlgorithmParameterFieldWrongFormat(AlgorithmErrors):
    """If the format of a field in algorithm parameter is wrong."""

    def __init__(self, field: str, value: str, additionnal_msg: str | None = None):
        additionnal_msg = f": {additionnal_msg}" if additionnal_msg else ""
        self.message = f"Field '{field}': '{value}' in parameter is wrong: {additionnal_msg}"
        self.public_message = self.message


class AlgorithmCommandTemplateExpansion(AlgorithmErrors):
    """If there is a problem when the expansion of the command template"""

    def __init__(self, validation_error: jinja2.exceptions.UndefinedError, command: str):
        missing_fields = extract_missing_fields(validation_error)
        self.message = f"Missing variable when expanding command : '{command}'. Missing variable in parameters: {', '.join(missing_fields)}"
        self.public_message = self.message


class AlgorithmNextflowTemplateExpansion(AlgorithmErrors):
    """If there is a problem when the expansion of the command template"""

    def __init__(self, validation_error: jinja2.exceptions.UndefinedError, nf_template: str):
        missing_fields = extract_missing_fields(validation_error)
        self.message = f"Missing variable(s) when expanding nextflow template '{nf_template}': Missing variable(s) in parameters: {', '.join(missing_fields)}"
        self.public_message = self.message


class ResultsErrors(LolapyGlobalError):
    """Main error when dealing with results from a run of a nextflow run."""

    pass

class NoWorkingDirectory(ResultsErrors):
    """Error when Result working directory is not available"""

    def __init__(self, working_directory: Path):
        self.message = f"Missing working directory '{working_directory}' that should contains results"
        self.public_message = "Internal server error"

class NoArchiveResults(ResultsErrors):
    """Error when the archive result is missing"""

    def __init__(self, archive_file: Path):
        self.message = f"'{archive_file}' archive file does not exist."
        self.public_message = "Internal server error"
