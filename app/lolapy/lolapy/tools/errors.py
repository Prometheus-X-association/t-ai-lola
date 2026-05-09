#!/usr/bin/env python3

r"""
Module containing errors for Lolapy API and errors linked to lolapi module

All errors implemented in Lolapy must inherit from LolapyError

LolapyGlobalError
│
├── ToolsErrors
│   ├── SettingsErrors
│   │   └── SettingsMissingParameters
│   ├── SSHError
│   │   └── SSHConnectionError
│   ├── ApilogErrors
│   │   ├── ApilogUnknownStatusCode
│   │   ├── GitCloneError
│   │   └── GitCloneDestionnationError
│   └── CheckInstallationError
│       └── TraxImageNotFound
├── DockerErrors
│   ├── DockerLoginError
│   ├── DockerCMDError
│   ├── WrongDockerImageUrl
│   └── DockerPullError
"""

from pathlib import Path

import pydantic
from lolapy.tools import settings
from lolapy.algorithm.errors import extract_missing_fields
from lolapy.errors import LolapyGlobalError
from lolapy.tools import git


class ToolsErrors(LolapyGlobalError):
    """Global error for the Tool module.

    All errors must of the tool module should inherit from this one.
    """

    pass


class SettingsErrors(ToolsErrors):
    """Main error for Settings errors."""

    pass


class SettingsMissingParameters(ToolsErrors):
    """If there is a problem when the expansion of the command template"""

    def __init__(
        self, validation_error: pydantic.error_wrappers.ValidationError, env_file: str
    ):
        missing_fields = extract_missing_fields(validation_error)
        self.message = f"Missing variable(s) when reading '{env_file}': Missing variable(s): {', '.join(missing_fields)}"
        self.public_message = self.message

class SSHError(LolapyGlobalError):
    """Main error for SSHToCluster"""

    pass


class SSHConnectionError(SSHError):
    """Error when connection occurs to cluster"""

    def __init__(self, error: str, error_type: str, server: str):
        self.message = f"Error when connecting to '{server}': {error_type}:{error}"
        self.public_message = LolapyGlobalError.standard_public_message


class ApilogErrors(ToolsErrors):
    """Main error for Apilog errors."""

    pass


class ApilogUnknownStatusCode(ApilogErrors):
    """Error when there is an Unknown status code get from apilog."""

    def __init__(self, status_code: int):
        """ApilogUnknownStatusCode.

        Args:
            status_code: The unknown HTTP status code
        """
        self.message = f"Unknown HTTP status code '{status_code}' got from frontend Api"
        self.public_message = LolapyGlobalError.standard_public_message


class GitCloneError(ApilogErrors):
    """Error when cloning git repository."""

    def __init__(self, clone_object: git.GitRepo, stderr: str):
        """InstallationErrorOnClone.

        Public_message is the same as message without the path of the target directory.
        It avoid leaking the structure of the backend
        Args:
            clone_object: Object that contains data about the repo to clone
            stderr: Message returned by the `git clone` command
        """
        self.message = f"Can't clone {clone_object.git_repo} with tag {clone_object.git_tag} \
        into {clone_object.destination} : stderr = {stderr}"
        self.public_message = self.message.replace(
            str(clone_object.destination), "**hidden_path**"
        )


class GitCloneDestionnationError(ApilogErrors):
    """Error when there is error with destination directory of git clone."""

    def __init__(self, clone_object: git.GitRepo, stderr: str):
        """GitCloneDestionnationError.

        Public_message is the same as message without the path of the target directory.
        It avoid leaking the structure of the backend
        Args:
            clone_object: Object that contains data about the repo to clone
            stderr: Message returned by the `git clone` command
        """
        self.message = f"Can't clone {clone_object.git_repo} with tag {clone_object.git_tag} \
        into {clone_object.destination} : stderr = {stderr}"
        self.public_message = LolapyGlobalError.standard_public_message

class CheckInstallationError(ToolsErrors):
    """Error with starting of lolapy"""

    pass

class DockerErrors(LolapyGlobalError):
    """Error with docker commands."""

    pass


class DockerLoginError(DockerErrors):
    """Error when using docker login"""

    def __init__(self, cmd: str, stderr: str):
        """DockerLoginError.

        Args:
            cmd: docker login command runned
            stderr: stderr returned by the `cmd`
        """
        self.message = f"Error when docker login with '{cmd}'. stderr: {stderr}"
        self.public_message = LolapyGlobalError.standard_public_message


class DockerPullError(DockerErrors):
    """Error when using docker pull."""

    def __init__(self, pull_command: str, stderr: str):
        """DockerPullError.

        Args:
            pull_command: docker pull command runned
            stderr: stderr returned by the `cmd`
        """
        self.message = (
            f"Error when pulling docker image with '{pull_command}'. stderr: {stderr}"
        )
        self.public_message = self.message


class DockerCMDError(DockerErrors):
    """Got error with docker but unkown errir"""

    def __init__(self, cmd: str, stderr: str):
        """DockerCMDError.

        Args:
            cmd: docker command runned
            stderr: stderr returned by the `cmd`
        """
        self.message = f"Docker error with command: '{cmd}'. Stderr: '{stderr}'"
        self.public_message = LolapyGlobalError.standard_public_message


class WrongDockerImageUrl(DockerErrors):
    """If error in the regex of the docker image url"""

    def __init__(self, docker_url: str, regex: str):
        """WrongDockerImageUrl.

        Args:
            docker_url: url of the docker image
            regex: Regex expression that should match
        """
        self.message = f"Error docker image URL '{docker_url}' does not match '{regex}' regular expression"
        self.public_message = self.message
