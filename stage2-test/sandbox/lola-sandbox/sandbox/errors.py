##!/usr/bin/env python3

from __future__ import annotations
import abc
from pathlib import Path
from attr import dataclass

import requests

from sandbox import lrs
from sandbox import run

@dataclass
class SandboxErrors(abc.ABC, Exception):
    """Parent class for all errors in the sandbox app.

    Inherit from ABC to force the definition of 'message' attribute"""
    message: str

    def __str__(self) -> str:
        return self.message

    def post_msg(self, post_message: str) -> Self:
        """Edit self.message to add a post message."""
        self.message = f"{self.message} {post_message}"
        return self

    def pre_msg(self, pre_message: str) -> Self:
        """Edit self.message to add a pre message"""
        self.message = f"{pre_message} {self.message}"
        return self

class ParseJsonError(SandboxErrors):
    def __init__(self, json_path: Path, error_msg: str):
        self.message = f"Error when decoding json file '{str(json_path)}' : {error_msg}"

class RequirementsError(SandboxErrors):
    """Error raised when requirements are not satisfied"""
    def __init__(self, message: str) -> None:
        self.message = message

class MissingFile(SandboxErrors):
    def __init__(self, filename: Path) -> None:
        self.message = f"Missing file '{str(filename)}'"

class MissingDir(SandboxErrors):
    def __init__(self, dirname: Path) -> None:
        self.message = f"Directory '{str(dirname)}' does not exist"

class LRSNotAvailable(SandboxErrors):
    def __init__(self, my_lrs: lrs.LRSUrl, request_error: requests.exceptions.ConnectionError | None = None, response: requests.Response | None = None):
        if request_error:
            self.message = f"Error in the request to the LRS at adress '{my_lrs.complete_request}' : {str(request_error)}"
        elif response:
            self.message = f"Error in the connexion to the LRS at adress '{my_lrs.complete_request}' : status code of the response : {str(response.status_code)}"
        else:
            self.message = f"Cannot connect to the LRS at adress '{my_lrs.complete_request}'"
        self.message += "\nStart the LRS server"


class NextflowExecutableNotFound(SandboxErrors):
    def __init__(self):
        nf_exec_name = run.GlobalSandboxRun.nextflow_exec_name
        nf_exec_env_var = run.GlobalSandboxRun.nextflow_path_env_variable
        self.message = f"""Unable to find the executable '{nf_exec_name}' for nextflow.
Add it in the PATH or use the env variable with :
`export {nf_exec_env_var}=path_to_my_nextflow_executable`"""
