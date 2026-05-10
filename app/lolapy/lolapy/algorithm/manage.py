#!/usr/bin/env python3

import logging
from pathlib import Path
import shutil


from lolapy.tools import git
from lolapy.tools import docker
from lolapy.tools import frontend_api
from lolapy.algorithm import errors
from lolapy.algorithm.algorithm import Algorithm
from lolapy.tools import settings

"""Module to manage installation/removal of algorithm.

Algorithms are stored in the NEXTFLOW_ALGORITHM_DIR (env variable) in their own directory corresponding
in their hash identifier. The frontend manage hash unique for algorithm. This hash is the name of the directory of the algorithm
"""


class InstallAlgorithm:
    """Class to fetch online the algorithm and to manage dependencies.

    Attributes:
        repository_url: url of the git repository for the algorithm
        git_version: name of the git branch to clone
        algo_hash: Hash unique of the algorithm
        algo_path: Full Path where the algorithm will be store after installation
    """

    def __init__(self, repository_url: str, git_version: str, algo_hash: str):
        self.repository_url = repository_url
        self.git_version = git_version
        self.algo_hash = algo_hash

        settings_app = settings.get()
        self.algo_path = settings_app.nextflow_algorithm_dir / self.algo_hash

    def install(self):
        """Install the created algorithm"""
        # Create destination directory
        self._manage_algo_path()
        # Clone algorithm repository
        git.GitRepo(
            git_repo=self.repository_url,
            git_tag=self.git_version,
            destination=self.algo_path,
        ).clone()
        # Validate the algorithm
        new_algo: Algorithm = Algorithm.from_hash(self.algo_hash)
        # Download docker dependencies
        docker_image_url = docker.SanitizeDockerUrl(
            new_algo.get_recipe().harbor_url
        ).sanitize()
        #docker.PullDockerImages(
        #    [docker.DockerImage(name="", url=docker_image_url)]
        #).pull()
        # everything is Done. Log complete to the frontend
        frontend_api.FrontendRequest.get(
            url=f"/api/algorithm/{self.algo_hash}/complete"
        )

    def _manage_algo_path(self):
        """Check if the destination path is available."""
        if self.algo_path.is_dir():  # handle if dir exists too
            if len(list(self.algo_path.glob("*"))):  # If directory is not empty
                raise errors.InstallationDirNotEmpty(self.algo_path)
        else:
            # Use parents=True to create the full dir tree if it does not exist
            # exist_ok raise an error if dir already exists -> avoid collision between algorithms
            self.algo_path.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Create '{self.algo_path}' to clone scenario")

    @staticmethod
    def remove(algo_hash: str):
        """Remove an installed algorithm

        :param tag_hash: str: Hash unique of the algo.
        """
        my_algorithm = Algorithm.from_hash(algo_hash=algo_hash, check_exists=True)
        algo_path = my_algorithm.algo_path
        shutil.rmtree(algo_path)
        frontend_api.FrontendRequest.log(f"{algo_hash} algorithm removed")
