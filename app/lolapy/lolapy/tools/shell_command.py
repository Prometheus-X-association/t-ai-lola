#!/usr/bin/env python3

"""Module used to run Shell Command on localhost or Cluster (via SSH)

Used when it's necessary to download docker images, get some files or stuff on the cluster.

Keep in mind that SSH connection required an SSH key and authorization to connect properly on the server.
Ensure that `ssh user@my_machine` works properly before using SSH connection

If the command can be run on dynamic machine (localhost or distant machine), then use ShellCommand.from_env().
The method will read settings ([settings.Settings]) and decide where to run the command (based on CLUSTER_IS_BACKEND and
CLUSTER_SERVER variables). If the target is exclusively localhost or distant, use ShellCommand.new() method.

Note:
    If the SSH connection is correctly setup and paramiko raise an error about authentication
        then check that your ssh server is able to read your ssh key (for example, rsa-1024 cannot
        be used anymore)

Examples:
    # Run command on the cluster
    >>> cmd_result = ShellCommand.new(command="ls -alh", on_localhost=True).run()
    >>> print(cmd_result.stdout.split("\n"))
    ['total 96K',
     'drwxr-xr-x. 1 pnoel pnoel  402 30 août  11:33 .',
     'drwxr-xr-x. 1 pnoel pnoel  590  2 août  16:04 ..',
     '-rw-r--r--. 1 pnoel pnoel  52K 30 août  11:33 .coverage',
     'drwxrwxr-x. 1 pnoel pnoel 4,5K 17 août  14:17 cov_html',
     ...
      'drwxrwxr-x. 1 pnoel pnoel  130 30 août  11:04 tests',
    ]
"""

import logging
import socket
import subprocess
import os
from attr import dataclass
from pathlib import Path

import paramiko
from paramiko.client import SSHClient

from lolapy import tools
from lolapy.tools import errors

@dataclass
class CommandResult:
    """Store the results of the command.

    If it's an ssh connection, then exit_code is None.
    Store the whole stdout/stderr, even with multi-lines.
    """
    exit_code: int | None
    stdout: str
    stderr: str


class ShellCommand:
    """Object to run shell commands on server or localhost.

    A SSH key and authorization must be configured before using this method on other server.
    Don't use the constructor directly, use new() method instead to build a proper command.
    Attributes:
        server: str: url or ip adress of the server to connect on. Can be None if on_localhost is set to True
        command: str: Shell command to run.
        background: bool: If yes, capture the stdout and stderr to print them later. If no, print during
            execution the stdout/stderr. There is no separation. Use in the lola sandbox. In the library or the server,
            use True to avoid missing stdout and stderr. Default: True
        environment: dict: Environment to use with the command.
        ssh_client: paramiko.client.SSHClient: Created in new() method. Set to None if the command must be run
            on localhost.
        on_localhost: bool: If set to True, run the command on the local machine. If False,
            run with SSH on the
        work_dir: Path: Change the working directory of the command. If None, execute normally.
    """

    def __init__(
        self,
        server: str | None,
        command: str,
        background: bool,
        environment: dict,
        ssh_client: SSHClient | None,
        on_localhost: bool,
        work_dir: Path | None,
    ):
        self.server: str | None = server
        self.command: str = command
        self.background: bool = background
        self.environment: dict = environment
        self.ssh_client: SSHClient | None = ssh_client
        self.on_localhost: bool = on_localhost
        self.work_dir: Path | None = work_dir

    @classmethod
    def new(
        cls,
        command: str,
        server: str | None = None,
        background: bool = True,
        environment: dict | None = None,
        on_localhost: bool = False,
        work_dir: Path | None = None
    ):
        """Create an instance of ShellCommand object

        Use this method only if the command must be run on the same machine every
        times (or change `server` and `on_localhost` parameters). Else, use ShellCommand.from_env().

        Args:
            command: The command to run.
            server: IP adress or name of the server to connect with SSH.
                Can be set to None if on_localhost is True
            background: bool: If yes, capture the stdout and stderr to print them later. If no, print during
                execution the stdout/stderr. There is no separation. Use in the lola sandbox. Default: True
            environment: Dictionnary with env variables to use
            on_localhost: Boolean. If set to True, run the command on localhost without ssh connection
                If False, `server` must be set to something.
            work_dir: Path: Change the working directory of the command. If None, execute normally.
        Raises:
            NotImplementedError: if both `server` and `on_localhost` are False/None
        Returns:
            ShellCommand: a instance of ShellCommand
        """

        if not environment:
            environment = os.environ.copy()
        # If both target are None, raise an NotImplemented
        if not server and not on_localhost:
            raise NotImplementedError("server and on_localhost cannot be both None")
        # Initialize a ssh connection if localhost is set to None
        ssh_client: SSHClient | None = None
        if not on_localhost and server:
            ssh_client = cls._init_connection(server)

        return cls(
            server=server,
            command=command,
            background=background,
            environment=environment,
            ssh_client=ssh_client,
            on_localhost=on_localhost,
            work_dir=work_dir,
        )

    @classmethod
    def from_env(cls, command: str, background: bool = True, environment: dict | None = None):
        """Generate a ShellCommand object from the environment.

        If you don't know if the command should be run on localhost or distant server,
        use from_env() instead of new()
        The method read Settings to create a ShellCommand.
        """
        # Load settings module here to avoid polluting the whole ssh_command module with
        # settings and required a env_file to be load
        from lolapy.tools import settings

        cluster_type = settings.get().cluster_type
        if cluster_type == "local":
            return ShellCommand.new(
                command=command,
                on_localhost=True,
                background=background,
                environment=environment,
            )

        return ShellCommand.new(
            command=command,
            on_localhost=False,
            server=settings.get().cluster_host,
            background=background,
            environment=environment,
        )


    def run(self) -> CommandResult:
        """Run the command on the correct machine.

        Returns:
            CommandResult: stdout, stderr and status code of the command
        """
        if self.on_localhost:
            return self._cmd_localhost()
        else:
            return self._cmd_ssh()

    def _cmd_localhost(self) -> CommandResult:
        """Run command on the localmachine.

        Returns:
            CommandResult: stdout, stderr and exit_code of the command
        """
        if self.work_dir:
            work_dir = self.work_dir
        else:
            work_dir = Path(".").absolute()
        processes = subprocess.run(self.command.split(), capture_output=self.background, text=True, cwd=work_dir, env=self.environment)
        return CommandResult(exit_code=processes.returncode, stderr=processes.stderr, stdout=processes.stdout)

    def _cmd_ssh(self) -> CommandResult:
        """Run command on ssh server.

        Returns:
            CommandResult: stdout and stderr of the command. exit_code is None because
                it cannot be catch with paramiko
        """
        if self.work_dir:
            command = f"cd {self.work_dir}; {self.command}"
        else:
            command = self.command
        try:
            _, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(command, environment=self.environment)
            # Read and decode immediatly because it will be removed after closing session
            stdout = ssh_stdout.read().decode("utf-8")
            stderr = ssh_stderr.read().decode("utf-8")
            return CommandResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=None
            )
        except Exception as e:
            raise e
        finally:
            if self.ssh_client:
                self.ssh_client.close()

    @staticmethod
    def _init_connection(server: str) -> SSHClient:
        """Private method to init SSH connection.

        Args:
            server: str: Initiate ssh connection on this server
        Raises:
            SSHConnectionsError: When encouter an error with ssh connection on the server.
        Returns:
            SSHClient: The paramiko.SSHClient object used for SSh connection
        """
        try:
            print(server)
            ssh = paramiko.SSHClient()
            print("initializing")
            logging.getLogger("paramiko").setLevel(logging.DEBUG)  # Limit paramiko logs
            print("log")
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("aaa")
            ssh.load_system_host_keys()
            print(server)
            ssh.connect(server)
        except (
            socket.gaierror,
            socket.timeout,
            socket.herror,
            paramiko.AuthenticationException,
        ) as e:
            raise errors.SSHConnectionError(str(e), tools.object_fullname(e), server)
        return ssh
