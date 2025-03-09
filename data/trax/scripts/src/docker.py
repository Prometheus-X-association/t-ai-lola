#!/usr/bin/env python3

import os
import logging

from src import error, warning
from src import utils


class Docker:
    """
    Object for holding parameters for Docker containers
    """

    def __init__(
        self,
        image: str = "",
        name: str = None,
        volumes: dict = {},
        ports: dict = {},
        env_variables: dict = {},
        command: str = "",
    ):
        """
        Constructor for Docker object

        :param image: Name of the Docker image
        :type image: str
        :param name: Name of the docker container
        :type name: str
        :param volumes: Dictionnary containing informations on volumes to mount
        :type volumes: dict
        :param ports: Port(s) to bind on the local machine (127.0.0.1)
        :type ports: int
        :param env_variables: Dict containing environments variables to bind in the container
        where keys are variables and values are values of variables
        :type env_variables: dict
        :param command: Command to execute when running the container
        :type command: str
        :return: A Docker object
        :rtype: Docker
        :"""
        self.image = image
        if not name:
            self.name = self.__set_random_name()
        self.volumes = volumes
        self.command = command
        self.ports = ports
        self.env_variables = env_variables

    def add_volume(self, src, dest):
        src = os.path.abspath(src)
        if not os.path.exists(src):
            error("'{}' path does not exist. Cannot bind to container")
        if src in self.volumes:
            warning(f"'{src}' path already set for this Docker object. The new path is '{src:dest}'")
        self.volumes[src] = dest

    def add_env(self, key, value):
        if key in self.env_variables:
            warning(
                "Env variable already set with previsous values '{}:{}'.".format(key, self.env_variables[key])
            )
            warning("New values are '{}:{}'".format(key, value))
        self.env_variables[key] = value

    def __set_random_name(self):
        """
        Set a random `name` for the docker container
        """
        import random
        import string

        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(10))
        self.name = result_str

    def __gen_txt_ports(self):
        """
        Generate the line text for ports
        """
        txt = ""
        for port in self.ports:
            txt = f"{txt} -p 127.0.0.1:{port}:{self.ports[port]}"
        return txt

    def __gen_txt_env_variables(self):
        """
        Generate the line text for env variables
        """
        txt = ""
        for env in self.env_variables:
            txt = f"{txt} -e {env}={self.env_variables[env]}"
        return txt

    def __gen_txt_volumes(self):
        """
        Generate the line text for volumes
        """
        txt = ""
        for volume in self.volumes:
            txt = f"{txt} -v {volume}:{self.volumes[volume]}"
        return txt

    def __check_image(self):
        """
        Check if the Docker image exists
        Stop the program in case of errors
        Use the command 'docker image my_image:tag'
        """
        cmd = f"docker images {self.image}"
        stdout, stderr = utils.bash_cmd(cmd)
        if len(stdout.split("\n")) == 1:
            error(f"The image '{self.image}' is not available. Build it before.")

    def __check_ports(self):
        """
        Check all if wanted ports are available on host
        Stop the program in case of errors
        """
        not_availables = []
        for port in self.ports:
            if not utils.is_port_available(port):
                utils.not_available.append(port)

        if not_availables:
            error("The following ports are not available for binding: '{}'".format(", ".join(not_availables)))

    def __check_volumes(self):
        """
        Check if all volumes exists on local host before binding
        Stop the program in case of errors
        """
        for volume in self.volumes:
            src = os.path.abspath(volume)
            if not os.path.exists(src):
                error("'{src}' path does not exist. Cannot bind to container")

    def check_status(self):
        """
        Check if a container is running by searching container name
        Return True if container exists and is running. Raise error otherwise
        """
        if not self.name:
            warning("Container should have a name different than ''")

        command = f"docker inspect -f '{{.State.Running}}' {self.name}"
        stdout, stderr = utils.bash_cmd(command)
        if "true" in stdout:
            return True
        if "Error: No such object:" in stderr:
            error(f"Container {self.name} is not running ")
            return False
        else:
            error(f"{stderr}")
            return False

    def exec_docker(self):
        """
        Execute a command on a running container
        """
        # Check all parameters
        self.__check_ports()
        self.__check_image()
        self.__check_volumes()
        self.check_status()

        txt_volumes = self.__gen_txt_volumes()
        txt_ports = self.__gen_txt_ports()

        command = f"docker exec {txt_volumes} {txt_ports} {self.name} {self.command}"
        stdout, stderr = utils.bash_cmd(command)
        utils.print_bash(stdout, logging.info)
        utils.print_bash(stderr, logging.warning)

    def run_docker(self):
        """
        Run a command with Docker run
        """
        # Check all parameters
        self.__check_ports()
        self.__check_image()
        self.__check_volumes()

        txt_volumes = self.__gen_txt_volumes()
        txt_ports = self.__gen_txt_ports()

        command = (
            f"docker run -d {txt_volumes} {txt_ports} --name {self.name} {self.image} {self.command}"
        )
        stdout, stderr = utils.bash_cmd(command)
        utils.print_bash(stdout, logging.info)
        utils.print_bash(stderr, logging.warning)

    def stop(self):
        """
        Stop a container and remove it
        """
        # Stop the container
        self.check_status()
        command = f"docker stop {self.namename}"
        stdout, stderr = utils.bash_cmd(command)
        utils.print_bash(stdout, logging.info)
        utils.print_bash(stderr, logging.warning)

        # remove the container
        command = f"docker rm {self.name}"
        stdout, stderr = utils.bash_cmd(command)
        utils.print_bash(stdout, logging.info)
        utils.print_bash(stderr, logging.warning)


class Compose(Docker):
    def __init__(
            self,
            image: str = "",
            name: str = None,
            volumes: dict = {},
            ports: dict = {},
            env_variables: dict = {},
            command: str = "",
            compose_files: [str] = [],
    ):

        # Constructor of Docker object
        Docker.__init__(self, image, volumes, ports, env_variables, command)
        self.compose_files = [os.path.abspath(ii) for ii in compose_files]

    def __check_compose_files(self):
        """
        Check if all docker-compose file exists
        """
        not_availables = []
        for compose in self.compose_files:
            if not os.path.isfile(compose):
                not_availables.append(compose)
        if not_availables:
            error("The following Compose file(s) does not exist: '{}'".format("', '".join(not_availables)))

    def __gen_txt_compose_files(self):
        """
        Generate the line text for compose files
        """
        txt = ""
        for compose in self.compose_files:
            txt = f"{txt} -f {compose}"
        return txt

    def run_compose(self):
        """
        Run a command with Docker run
        """
        # Check all parameters
        self._Docker__check_ports()
        self._Docker__check_image()
        self._Docker__check_volumes()
        self.__check_compose_files()

        txt_volumes = self._Docker__gen_txt_volumes()
        txt_ports = self._Docker__gen_txt_ports()
        txt_env_variables = self._Docker__gen_txt_env_variables()
        txt_compose = self.__gen_txt_compose_files()

        command = f"docker-compose {txt_compose} run -d {txt_volumes} {txt_ports} {txt_env_variables} --name {self.name} {self.image} {self.command}"
        stdout, stderr = utils.bash_cmd(command)
        utils.print_bash(stdout, logging.info)
        utils.print_bash(stderr, logging.warning)
