#!/usr/bin/env python3

"""Module to manage action related to Docker.

Docker must be installed and available on the cluster machine in order to pull
docker images.
"""

from attr import dataclass
import logging
import re

from pydantic import BaseModel
from lolapy.algorithm.algorithm import AlgorithmRecipe

from lolapy.tools import settings
from lolapy.tools import errors as tools_errors
from lolapy.tools import shell_command


class DockerImage(BaseModel):
    """Hold information on docker image.

    Attributes:
        name: Name of the Docker image. Contains the tag version. Must match the name used in the scenario
        url: Url where to download the docker image. Contains the tag version. Must match the url of the harbor version
    """

    name: str | None
    url: str

    def sanitize(self):
        """Call the docker image sanitizer SanitizeDockerUrl.

        Edit the url attribute.
        """

        self.url = SanitizeDockerUrl(url=self.url).sanitize()


class GetImageList:
    """Extract list of [DockerImage][lolapy.tools.docker.DockerImage] from a json file (scenario or algorithm json)."""

    @staticmethod
    def from_algo_recipe(algorithm_recipe: AlgorithmRecipe) -> list[DockerImage]:
        """Extract the docker image from algorithm recipe

        Generate a list because PullDockerImages uses it

        Args:
            algorithm_recipe: Recipe of the algorithm
        Returns:
            List of [DockerImage][lolapy.tools.docker.DockerImage]
        """
        docker_image = DockerImage(
            url=SanitizeDockerUrl(algorithm_recipe.harbor_url).sanitize(),
            name=None,  # No name in algo_recipe.json
        )
        return [docker_image]


@dataclass
class PullDockerImages:
    """Download Docker images on the cluster.

    This object required a SSH connection to the cluster. It uses [SSHToCluster][lolapy.tools.ssh_cluster.SSHToCluster]
    to connect to the cluster and run `docker` commands.

    Attributes:
        docker_images: The list of docker images to pull
    """

    docker_images: list[DockerImage]

    def pull(self):
        """Entrypoint of the object.

        Connect to the docker harbor instance if necessary and pull docker images
        NOTE:
            If Settings.harbor_pull_images is set to False, don't pull docker images
        """
        if settings.get().harbor_pull_images:
            self._login()
            self._pull_images()
        else:
            logging.warning("HARBOR_PULL_IMAGES is set to False. No image will be downloaded")

    def _login(self):
        """Run docker login on the cluster machine.

        Use docker login to connect to the interne harbor instance.
        """

        app_parameters = settings.get()
        cluster_name = app_parameters.cluster_host
        docker_host = app_parameters.harbor_host
        docker_user = app_parameters.harbor_user
        docker_password = app_parameters.harbor_password

        login_command = f"docker login {docker_host}"

        # If user and password are not set, consider image are public
        # (used on mayflower)
        if not docker_user and not docker_password:
            logging.info("Skip login to harbor instance because HARBOR_USER and/or HARBOR_PASSWORD are not set")
            return

        logging.info(f"Trying to connect to harbor instance '{docker_host}'")
        cmd_result = shell_command.ShellCommand.from_env(
            command=login_command,
            environment={
                "DOCKER_USER": docker_user,
                "DOCKER_PASSWORD": docker_password,
            },
        ).run()

        if cmd_result.stderr and not "login succeeded" in str(cmd_result.stdout).lower():
            raise tools_errors.DockerLoginError(cmd=login_command, stderr=str(cmd_result.stderr))
        logging.info(f"Connection successful to '{docker_host}'")

    def _pull_images(self):
        """Pull docker images after login.

        Note:
            use self._login() method before to connect to the harbor instance
        """
        for image in self.docker_images:
            pull_command = f"docker pull {image.url}"
            logging.info(f"Start to pull docker image with {pull_command}")
            cmd_result = shell_command.ShellCommand.from_env(command=pull_command).run()
            if cmd_result.stderr:
                raise tools_errors.DockerPullError(pull_command=pull_command, stderr=cmd_result.stderr)
            else:
                logging.info(f"Images pulled")
            # Tag image if image.name is not None
            if image.name:
                retag_command = f"docker tag {image.url} {image.name}"
                logging.info(f"Try to tag docker image with {retag_command}")
                cmd_result = shell_command.ShellCommand.from_env(command=retag_command).run()
                if cmd_result.stderr:
                    logging.warning(f"stderr when {retag_command}, stderr: {cmd_result.stderr}")


@dataclass
class SanitizeDockerUrl:
    """Class to sanitize docker image url.

    Attributes:
        url: Url to sanitize. Can starts with http(s) or not.

    Examples:
        >>> SanitizeDockerUrl()

    TODO:
        - Refactor this. Use a matched list to allow targetting different forges.
          For exemple, don't target only harbor.loria.fr or lola.lhs.loria.fr:4443
    """

    url: str

    def sanitize(self) -> str:
        """Adapt the url to the harbor instance used on the server.

        Use a special regex to extract path of the image. Replace the url by the one store in
        the env variable HARBOR_HOST.

          https://lola.lhs.loria.fr:4443/dir/image:tag     # yes
          https://lola.lhs.loria.fr/dir/image:tag          # yes
          https://lola.lhs.loria.fr:4443                   # no
          https://lola.lhs.loria.com:4443/dir/image:tag    # no
          https://www.lola.lhs.loria.fr:4443/dir/image:tag # no
          lola.lhs.loria.fr:4443/dir/image:tag             # yes
          lola.lhs.loria.fr/dir/image:tag                  # yes
          lola.lhs.loria.fr                                # no
          /dir/image:tag                               # no

        For working regex, image name returned is `/dir/image:tag`

        :param url: str: URL to sanitize
        :raise scenario_errors.WrongDockerImageUrl: If the pattern of docker image url is wrong
        :return: str: url with good host
        """
        docker_image_regex = re.compile(r"lola.lhs.loria.fr(:4443){0,1}([\/_a-zA-Z0-9:.-]*)")

        if matches := docker_image_regex.findall(self.url):
            # findall return a [(':4443', '/dir/image:tag')] in case of success
            # extract image name in matches[0][1]
            if matches[0][1]:
                image_path = matches[0][1]
            else:
                raise tools_errors.WrongDockerImageUrl(self.url, str(docker_image_regex))
        else:
            raise tools_errors.WrongDockerImageUrl(self.url, str(docker_image_regex))

        harbor_host = settings.get().harbor_host

        return f"{harbor_host}{image_path}"
