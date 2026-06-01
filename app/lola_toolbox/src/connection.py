#!/usr/bin/env python3

from pathlib import Path
import time
import json

import paramiko
import requests


class sftp:
    def __init__(self, host="171.33.77.155", user="aziz", password="password", port=2222):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.sftp_handler = None

    def init_connection(self):
        t = paramiko.Transport((self.host, self.port))
        t.connect(username=self.user, password=self.password)
        self.sftp_handler = paramiko.SFTPClient.from_transport(t)

    def put(self, datafile: Path, callback: callable = None):
        filename = datafile.name
        self.sftp_handler.put(datafile, 'upload/'+filename, callback=callback)


class Releases:
    """
    Class to work with releases on gitlab.loria.fr
    """
    ACCESS_TOKEN = "N9vnrHqsQcU7PtcNEAjN"

    @staticmethod
    def get_latest_version():
        """
        Main function to check new releases
        Return the version number of the last version in format X.Y.Z
        """
        json_data = Releases.get_releases()
        lst_releases = [v["tag_name"] for v in json_data]
        lst_releases_sorted = Releases.sort_version(lst_releases)
        return lst_releases_sorted[0]

    @staticmethod
    def get_releases():
        """
        Use the gitlab API to get all releases on the repository

        :return: The json if the request works. Return None otherwise
        :rtype: dict or None
        """
        retry = 0
        while retry != 5:
            # Get all releases on the lola_toolbox repository
            try:
                req = requests.get("https://gitlab.inria.fr/api/v4/projects/27921/releases", headers={"PRIVATE-TOKEN": Releases.ACCESS_TOKEN})
            except requests.exceptions.ConnectionError:
                return None
            if req.status_code == 200:
                return json.loads(req.content)
            retry += 1
            time.sleep(1)
        return None

    @staticmethod
    def sort_version(lst_releases):
        ## Generate sanitized version number
        sanitized_lst_releases = []
        for r in lst_releases:
            try:
                r = int(r.replace(".", ""))
                sanitized_lst_releases.append(r)
            except ValueError:
                ## ValueError means the tag version is wrong (maybe in the format vX.Y.Z )
                ## Add 0 to the list to keep length of the initial list
                sanitized_lst_releases.append(0)
                pass
        assert len(sanitized_lst_releases) >= 1
        _, sorted_releases = zip(*sorted(zip(sanitized_lst_releases, lst_releases), reverse=True))
        return sorted_releases
