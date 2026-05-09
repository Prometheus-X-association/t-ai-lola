#!/usr/bin/env python3

"""List of all scenario related errors.

LolapyGlobalError
│
├── ScenarioErrors
│   ├── ScenarioRunError
│   ├── ScenarioTemplateNoExist
│   └── ScenarioNotExist
│
├── ScenarioInstallationError
│   ├── InstallationDirNotEmpty
│   ├── InstallationErrorOnClone
│   ├── InstallationMissingRequiredFile
│   └── InstallationWrongFormattedJSON
│
└── ResultsErrors
    ├── NoWorkingDirectory
    └── NoArchiveResults



"""
from pathlib import Path

import pydantic
from lolapy.errors import LolapyGlobalError, extract_missing_fields


class ScenarioErrors(LolapyGlobalError):
    """Main error for scenario"""

    pass


class ScenarioRunError(ScenarioErrors):
    """Error when running nextflow workflow and got stderr."""

    def __init__(self, stdout: str | None = None, stderr: str | None = None):
        """Constructor of ScenarioRunError error.

        Concatenate in the output error message the stdout and stderr as parameters if they
        are not None
        """
        message = "Error starting a scenario."
        if stdout:
            message += f" stdout: {stdout}"
        if stderr:
            message += f" stderr: {stderr}"
        self.message = message
        self.public_message = message


class ScenarioTemplateNotExist(ScenarioErrors):
    """Error when template file does not exist"""

    def __init__(self, template_file: Path, scenario: Path):
        self.message = f"Error in scenario '{scenario.absolute()}': template file '{template_file.absolute()}' does not exist"
        # Hide full path in the message for public
        self.public_message = f"Error in scenario '{scenario}': template file '{template_file}' does not exist"


class ScenarioNotExist(ScenarioErrors):
    """If path of the scenario does not exist"""

    def __init__(self, directory: Path):
        self.message = f"Path '{directory.absolute()}' does not exist"
        self.public_message = f"Scenario {directory.stem} does not exist"


class ScenarioMissingFile(ScenarioErrors):
    """If there is a missing file in the scenario"""

    def __init__(self, scenario_name: str, file_path: Path, file_type: str):
        """

        :param scenario_name: str: Name of the scenario
        :param file_path: Path: Path of the missing file
        :param file_type: str: Type of missing file. For exemple 'config file' or 'template file'
        """
        self.message = f"File '{file_path.absolute()}' of type {file_type} is missing in scenario '{scenario_name}'"
        self.public_message = f"File '{file_path.name}' of type {file_type} is missing in scenario '{scenario_name}'"

class ScenarioRecipeMissingField(ScenarioErrors):
    """If there is a missing field in the scenario recipe (params.json)

        The error generate a correct error message depending of missing fields in the params.json
    """

    def __init__(self, scenario_data: dict, error: pydantic.error_wrappers.ValidationError):
        # In case the only missing field is name, we cannot search for the algorithm_name
        if "name" in scenario_data:
            scenario_name = scenario_data["name"]
            sanitized_error_message: str = f"Missing fields:{extract_missing_fields(error)}"
        else:
            scenario_name = "**Unknow scenario** because the 'name' field missing"
            sanitized_error_message: str = str(error)
        self.message = f"Recipe for algorithm '{scenario_name}' is not well formated: {sanitized_error_message}"
        self.public_message = f"Recipe for algorithm '{scenario_name}' is not well formated: {sanitized_error_message}"

class ScenarioParameterMissingField(ScenarioErrors):
    """If there is a missing field in the scenario parameter"""

    def __init__(self, scenario_data: dict, error: pydantic.error_wrappers.ValidationError):
        # In case the only missing field is name, we cannot search for the scenario_name
        if "name" in scenario_data:
            scenario_name = scenario_data["name"]
            sanitized_error_message: str = f"Missing fields:{extract_missing_fields(error)}"
        else:
            scenario_name = "**Unknow scenario** because the 'name' field missing"
            sanitized_error_message: str = str(error)
        self.message = f"Parameter '{scenario_name}' is not well formated: {sanitized_error_message}"
        self.public_message = f"Parameter '{scenario_name}' is not well formated: {sanitized_error_message}"


class ScenarioParameterFieldWrongFormat(ScenarioErrors):
    """If the format of a field in scenario parameter is wrong."""

    def __init__(self, field: str, value: str, additionnal_msg: str | None = None):
        additionnal_msg = f": {additionnal_msg}" if additionnal_msg else ""
        self.message = f"Field '{field}': '{value}' in parameter is wrong: {additionnal_msg}"
        self.public_message = self.message

class ScenarioInstallationErrors(LolapyGlobalError):
    """Main error for InstallationScenario"""

    pass


class InstallationDirNotEmpty(ScenarioInstallationErrors):
    """If Installation directory exist and not empty"""

    def __init__(self, directory: Path):
        self.directory = directory
        self.message = (
            f"Can't clone repository, '{self.directory}' exists and is not empty"
        )
        self.public_message = LolapyGlobalError.standard_public_message
