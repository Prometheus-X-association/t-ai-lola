#!/usr/bin/env python3

from __future__ import annotations
import argparse
from urllib.parse import urlparse

import requests

from sandbox import errors

class LRSUrl:
    """Deserialize the URL of the LRS.

    Used to validate the url of the LRS. Parse the port number and
    validate that the scheme (http(s)) is set.

    Attributes:
        url: URL of the LRS with scheme. For example 'http://localhost'.
            To connect to the LRS, requests packages needs a scheme (http(s))
        port: int: Port if the LRS
        complete_request: The concatenation of the url and the port.
    """
    def __init__(self, url: str, port: int):
        self.url = url
        self.port = port
        self.complete_request = f"{self.url}:{self.port}"

    @classmethod
    def validate_url(cls, arg_url: str) -> "LRSUrl":
        """Generate and validate LRSUrl from argument that comes from argparse argument.

        Raises:
            argparse.ArgumentTypeError: if the url does not contains scheme
        Return:
            LRSUrl: A LRSUrl structure
        """
        complete_url = urlparse(arg_url)
        if not complete_url.port:
            port = 80
        else:
            port = complete_url.port
        if not "http" in complete_url.scheme:
            raise argparse.ArgumentTypeError("Error in option '--lrs-host': Missing scheme in url (add 'http://' or 'https://')")
        return cls(url=f"{complete_url.scheme}://{complete_url.hostname}", port=port)

    def ping(self):
        """Try to connect to the LRS.

        Raises:
            sandbox.LRSNotAvailable: if the connexion is not possible
        """
        try:
            response = requests.get(self.complete_request)
        except requests.exceptions.ConnectionError as e:
            raise errors.LRSNotAvailable(my_lrs=self, request_error=e)
        if response.status_code != 200:
            raise errors.LRSNotAvailable(my_lrs=self, response=response)
        return True
