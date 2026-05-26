#!/usr/bin/env python3

"""
Module to contact the frontal API

Used for debug/logs information like Lolapy logs or Nextflow logs
Can be used to search information on the frontend such user permissions on dataset
"""

from __future__ import annotations
from enum import Enum
import json
import logging
from pathlib import Path
from typing import Callable

import requests

from lolapy.tools import settings
from lolapy.tools import errors


class MimeType(Enum):
    """Enumerate for mime type variant"""

    ZIP = "application/zip"


class PostFile:
    """Store information to send files in Flask way.

    Attributes:
        filetype: enumerate of the [MimeType][lolapy.tools.frontend_api.MimeType]
        filepath: Path of the file to send
        filename: Name of the file in SEND request. It's to avoid long path. Default to None.
            If None, it get the filename of the `filepath` parameter.
    """

    def __init__(self, filetype: MimeType, filepath: Path, filename: str | None = None):
        self.filetype = filetype
        self.filepath = filepath
        self.filename = filename or self.filepath.name

    def format_file(self) -> dict:
        """Format the file to the correct format requested by Request.post.

        For exemple {'file': ('test_hello.py', open('test_hello.py', 'rb'), 'application/zip')}
        Returns:
            dict:
        """
        return {"file": (self.filename, open(self.filepath, "rb"), self.filetype.value)}


class _FrontendApi:
    """
    Class to communicate with the frontend API
    Most of the time, you don't want to use this class. Use FrontendRequest instead !
    """

    def __init__(self, adress: str, port: int, fake_request: bool = False):
        """Constructor for _FrontendApi.

        Don't use it directly. Use FrontedRequest instead.

        Args:
            adress: url of the server. For exemple http://0.0.0.0 or http://localhost. Should
                start with `http(s)://` but this constructor will add it if missing.
            port: port of the server
            fake_request: If set to True, no request will be send to the frontend. Every request
                `will return` 200
        """
        if not adress.startswith("http"):
            self.adress = f"http://{adress}"
        else:
            self.adress = adress
        self.port = int(port)
        self.fake_request = fake_request

    @classmethod
    def init_from_env(cls) -> Self:
        """Create a FrontendApi instance from environment."""
        app_settings = settings.get()

        return cls(
            adress=app_settings.frontend_api_ip,
            port=app_settings.frontend_api_port,
            fake_request=app_settings.frontend_api_fake,
        )

    def _request(
        self,
        request_fct: Callable,
        url: str,
        data: str | None = None,
        files: PostFile | None = None,
    ) -> int:
        """Execute the correct request to the url.

        Send data if necessary.
        Args:
            fct: Callable function. Actually supported: [requests.get] and [requests.post]
                Request to execute.
            url: URL to target. For example: `/api/user/{user-id}`(not http://localhost/api/lolapi/log)
            data: Data to send. If Json data, it must be formatted before. Default to `None`
            file: Postfile to send. Default to `None`
        Returns:
            int: Status code of the request
        Raises:
            NotImplementedError: If the method get a requests not implemented. For example `request_fct=requests.put`
        """

        # If FRONTEND_API_FAKE is set to True, return 200 in any cases
        if self.fake_request:
            logging.warning(
                f"FRONTEND_API_FAKE is set to True. Request '{request_fct}' to '{url}' return 200 everytimes"
            )
            return 200

        if not url.startswith("/"):
            url = f"/{url}"

        final_url = f"{self.adress}:{self.port}{url}"
        # if data is empty, don't send it. Use GET instead of POST
        match request_fct:
            case requests.get:
                log_request = "GET"
                result: requests.Response = request_fct(final_url)
            case requests.post:
                log_request = "POST"
                result: requests.Response = request_fct(final_url, data, files)
            case _:
                log_request = f"UNKNOW REQUEST: {request_fct}"
                raise NotImplementedError(f"Unimplement request type {request_fct}")

        log_message = f"Send '{log_request}' with data '{result.request.body}' to '{final_url}'. Got response: '{result.content.decode('UTF-8')}'"

        # log status code
        if result.status_code >= 200 and result.status_code <= 299:
            logging.debug(log_message)
        elif result.status_code >= 400:
            logging.error(log_message)
        else:
            logging.warning(log_message)

        return result.status_code


class FrontendRequest:
    """
    Class abstraction to use FrontendApi requests like get, post, etc ...
    """

    @staticmethod
    def get(url: str) -> int:
        """Send GET request to the given url.

        Args:
            url: The url to target. For example `/api/user/{user-id}`
                Be careful, this method don't do expansion
        Returns:
            int: The status code of the request
        """
        frontend_apilog = _FrontendApi.init_from_env()
        status_code = frontend_apilog._request(
            request_fct=requests.get, url=url, data=None
        )
        return status_code

    @staticmethod
    def post(url: str, data: dict | None = None, files: PostFile | None = None) -> int:
        """Send POST request to the given url with or without data.

        Args:
            url: The url to target. For example `/api/check-database`
                Be careful, this method don't do expansion
            data: dict: Dictionnary of data to send. The method will serialize data to JSON. Default to None.
            files: PostFile to send.
        Returns:
            int: The status code of the request of the POST Request
        """
        frontend_apilog = _FrontendApi.init_from_env()
        status_code = frontend_apilog._request(
            request_fct=requests.post, url=url, data=json.dumps(data), files=files
        )
        return status_code

    @staticmethod
    def log(log_type: str, message: str | None = None, details: str | None = None):
        """Send post message to the frontend API to the adress /api/lolapi/log.

        The sended request is in the form
        {
          type: "<log_type>",
          message: "<message>",
          details: "<details>",
        }
        Args:
            log_type: Type of log. Nothing formalized. See TODO
            message: Log message to send.
            details: More information on the error
        TODO:
            - Formalize `log_type`
            - Restructure logs for the Frontend
        Returns:
            int: the status code of the post request
        """

        frontend_apilog = _FrontendApi.init_from_env()
        status_code = frontend_apilog._request(
            request_fct=requests.post,
            url="/api/lolapi/log",
            data={
                "type": log_type,
                "message": message,
                "details": details,
            },
        )
        return status_code

    @staticmethod
    def _permission(url: str, data: dict) -> bool:
        """Private method to send request on the frontend for permission access.

        Use FrontendRequest.dataset_permission() or FrontendRequest.scenario_permission() instead
        Args:
            url: URL to target
            data: dict. Data to send (will be serialiazed)
        Raises:
            ApilogUnknownStatusCode: if the error code is not 200 or 400
        Returns:
            bool: Depending of the status code of the request. Return False for 400 error
                True otherwise.
        """

        status_code = FrontendRequest.post(url=url, data=data)

        # Status code == 400 means the user has no permission
        # 200, User has permission
        if status_code == 400:
            return False
        elif status_code != 200:
            raise errors.ApilogUnknownStatusCode(status_code)
        return True

    @staticmethod
    def dataset_permission(user_hash: str, dataset_hash: str) -> bool:
        """Check if user can have access to the dataset.

        Args:
            user_hash: Hash unique of the user (should starts with `U`)
            dataset_hash: Hash unique of the dataset. (should starts with `D`)
        Returns:
            bool: True if the user has acces. False otherwise.
        """
        url: str = "/api/dataset/check"
        json_data: dict = {
            "user": user_hash,
            "dataset": dataset_hash,
        }
        return FrontendRequest._permission(url, json_data)

    @staticmethod
    def scenario_permission(user_hash: str, scenario_hash: str) -> bool:
        """Check if the user has access on the scenario.


        Args:
            user_hash: Hash unique of the user (should starts with `U`)
            scenario_hash: Hash unique of the scenario. (should starts with `S`)
        Returns:
            bool: True if the user has acces. False otherwise.
        """
        url: str = "/api/scenario/check"
        json_data: dict = {
            "user": user_hash,
            "scenario": scenario_hash,
        }
        return FrontendRequest._permission(url, json_data)
