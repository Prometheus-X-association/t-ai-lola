#!/usr/bin/env python3

"""Module to manage Git Repository"""

from dataclasses import dataclass
import logging
import os
from pathlib import Path

from lolapy.tools import settings
from lolapy.tools import errors as tools_errors
from lolapy.tools import shell_command


@dataclass
class GitRepo:
    """Object that manage git repository and clone them.

    Attributes:
        git_repo: url of the git repository
        destination: Path of the directory when to clone the repository
        git_tag: git tag to clone
    """

    git_repo: str
    destination: Path
    git_tag: str

    def _check_destination(self) -> None:
        """Check if the destination can be created and if not, it's not empty.

        Raises:
            GitCloneDestionnationError: If there is an error when creating dir or dir is not empty.
        """
        # if dir does not exist, create it
        if not self.destination.exists():
            try:
                self.destination.mkdir()
            except Exception as e:
                raise tools_errors.GitCloneDestionnationError(
                    self, f"Error when creating directory: {e}"
                )
            logging.info(f"Create {self.destination} to clone repository")
        else:
            # Compute the number of files in the existing directory
            number_of_files = len([ii for ii in self.destination.glob("*")])
            if number_of_files >= 1:
                raise tools_errors.GitCloneDestionnationError(
                    self, "Destination directory is not empty"
                )

    def clone(self):
        """Clone the git repository.

        Creates 'destination' if the path does not exist.
        Raises:
            GitCloneError: if there is an error with the clone
        """

        # Create output directory or check if it's empty
        self._check_destination()

        # If the variable is in the env file, get it. Else, it's False
        http_proxy: str | None = settings.get().http_proxy
        # 'env' parameter used in subprocess.run can add new env variable. But it replace all current
        # env variable set. So we save them with os.environ and add http_proxy into it
        # TODO: Move this to its own class
        if http_proxy:
            my_env = (
                os.environ.copy()
            )  # Make a copy of the environnement. DON'T USE os.environ directly because it edits the global environment directly
            my_env["http_proxy"] = http_proxy
            my_env["https_proxy"] = http_proxy
        else:
            my_env = os.environ.copy()

        command = f"git clone --depth 1 --single-branch --branch {self.git_tag} {self.git_repo} {self.destination}"
        cmd_result = shell_command.ShellCommand.new(
            command=command,
            environment=my_env,
            on_localhost=True,
        ).run()

        if cmd_result.exit_code != 0:
            raise tools_errors.GitCloneError(self, cmd_result.stderr)

        logging.info(
            f"Cloned Scenario '{self.git_repo}' with tag '{self.git_tag}' into '{self.destination}'"
        )
