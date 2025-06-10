#!/usr/bin/env python3

import json
import logging
from pathlib import Path

from attr import dataclass

from lolapy.errors import LolapyGlobalError
from lolapy.scenario import scenario
from lolapy.scenario import errors as scenario_errors
from lolapy.nextflow import errors as nextflow_errors
from lolapy.tools import settings, shell_command

@dataclass
class NextflowCheckEnv():
    """Generate environment to run a Nextflow run

    Attributes:
        run_id: str: Name to give to the nextflow run. The name should be unique.
            Usually, the run_id is the run_hash given by the frontend
    """
    nextflow_executable: Path
    nextflow_work_dir: Path
    run_work_dir: Path
    config_file_docker: Path
    nextflow_log_listener: str
    run_id: str
    on_local: bool

    @classmethod
    def from_env(cls, run_workdir: Path, run_id: str) -> "NextflowCheckEnv":
        """Build a NextflowCheckEnv from the settings environment.

        Verification not runned with this method. Use check()
        Args:
            run_id: str: Unique identifier of the nextflow run that should be defined by the frontend.
                Used as a working directory.
        """
        app_settings = settings.get()

        nextflow_workdir = app_settings.nextflow_workdir

        return cls(
            nextflow_executable=app_settings.nextflow_executable,
            nextflow_work_dir=nextflow_workdir,
            run_work_dir=run_workdir,
            nextflow_log_listener=app_settings.nextflow_log_listener_host,
            config_file_docker=run_workdir / "backend_docker.config",
            run_id=run_id,
            on_local=app_settings.cluster_is_backend
        )

    def check(self):
        """Test the environment for nextflow before the run."""
        self.check_nextflow_executable()
        self.gen_docker_conf_file()

    def check_nextflow_executable(self):
        """Test the nextflow executable provided by the env variable.

        Test if it exists and if it's runnable.
        Raises:
            NextflowExecutableError: If there is an error with the nextflow executable
        """
        if not self.nextflow_executable.exists():
            raise nextflow_errors.NextflowExecutableError(
                executable_path=self.nextflow_executable, stderr="File not found"
            )
        try:
            command_return = shell_command.ShellCommand.new(command=str(self.nextflow_executable), on_localhost=True).run()
        except PermissionError as e:
            raise nextflow_errors.NextflowExecutableError(
                executable_path=self.nextflow_executable,
                stderr=f"Permission Denied on nextflow executable: {e}"
            )
        if command_return.exit_code != 0:
            raise nextflow_errors.NextflowExecutableError(
                executable_path=self.nextflow_executable,
                stderr=command_return.stderr,
            )

    def gen_docker_conf_file(self):
        """Generate Docker configuration file for nextflow.

        This file enable option to force nextflow behavior. It force the use of slurm and the usage of Docker.
        The method check the md5sum of the config file on the machine to update it if needed.
        """
        import hashlib

        # Change the process executor based on on_local.
        # See https://www.nextflow.io/docs/latest/executor.html#local
        if self.on_local:
            process_executor = "local"
        else:
            process_executor = "slurm"

        docker_config = f"""process.executor = '{process_executor}'
trace {{
    enabled = true
    file = 'workflow_trace.tsv'
    fields='task_id,hash,native_id,process,tag,name,status,exit,module,container,cpus,time,disk,memory,attempt,submit,start,complete,duration,realtime,queue,%cpu,%mem,rss,vmem,peak_rss,peak_vmem,rchar,wchar,syscr,syscw,read_bytes,write_bytes,vol_ctxt,inv_ctxt,env,workdir,script,scratch,error_action'
}}
docker {{
       enabled = true
       runOptions = "--network=host --user \\$(id -u):\\$(id -g)"
}}"""  # To know why using the --user option instead of fixOwnership = true, see https://gitlab.inria.fr/lola/back-end/lolapy/-/issues/111
        docker_config = docker_config.encode()
        try:
            hash_file = hashlib.md5(
                open(self.config_file_docker, "rb").read()
            ).hexdigest()
        except FileNotFoundError:
            # If file not found, use an empty md5 so regenerate the file
            logging.info(f"File {self.config_file_docker} not found. Will be generated")
            hash_file = ""
        hash_string = hashlib.md5(docker_config).hexdigest()

        # Generate the file if md5sum are not the same
        if hash_file != hash_string:
            logging.info(f"Generate {self.config_file_docker} because wrong md5sum")
            with open(self.config_file_docker, "wb") as conf_file:
                conf_file.write(docker_config)


class RunNextflow():
    """Class to manage nextflow run <scenario> with correct parameters.

    It does not check if run_name already exists or scenario exists. Throw an error if not
    """

    def __init__(self, nextflow_env: NextflowCheckEnv, scenario: scenario.Scenario, parameters: dict | None = None, background: bool = True):
        """Nextflow object.

        Args:
            scenario_tag: str: Tag unique of the scenario
            parameters: dict: Dictionnary of all parameters to give to nextflow during the run
        """
        self.scenario = scenario
        self.parameters = parameters or {}
        self.nextflow_env = nextflow_env
        self.background = background

        # File where to store parameters used to the run
        self.parameter_file = self.nextflow_env.run_work_dir / f"{self.nextflow_env.run_id}_parameters.json"

    def run(self):
        """Run a nextflow job.

        Raises:
            scenario_errors.ScenarioError: If there is an error when starting the run
        """
        # Generate parameter file
        self.generate_parameter_file()

        command_line_parameters = [
            str(self.nextflow_env.nextflow_executable),
        ]
        # If the command run in background, use -bg option after `nextflow run`
        if self.background:
            command_line_parameters.append("-bg")
        # Add global parameters for the command line
        command_line_parameters.extend([
            "-c",  # Use the next config file
            str(
                self.nextflow_env.config_file_docker
            ),  # force the usage of docker. Must be executed before run option
            "run",
            str(self.scenario.scenario_path),  # run command of nextflow and name of the workflow
            "-offline",  # Does not check for online scenario. Win time to the execution
            "-name",  # Give a name to the run
            self.nextflow_env.run_id,  # Name of the run
            "-work-dir",  # Set the working dir
            str(
                self.nextflow_env.run_work_dir
            ),  # Change the working directory to avoid saving temporary files at random places
            "-with-trace",  # have to enable -with-trace to trace ressource usages
            "-params-file",  # Json file containing parameters of the scenario
            str(self.parameter_file),  # use file which contains all parameters
        ])
        if self.background:
            # Option to send logs to a http server
            command_line_parameters.append(
                f"-with-weblog {self.nextflow_env.nextflow_log_listener}"
            )

        # Use the parameter cwd to force nextflow to use the correct working-directory.
        # The parameter -work-dir given to nextflow change just where to store temporary results
        cmd_result = shell_command.ShellCommand.new(
            command=" ".join(command_line_parameters),
            on_localhost=True,
            background=self.background,
            work_dir=self.nextflow_env.run_work_dir).run()

        # If the command return a stderr, try to parse it to raise errors
        if cmd_result.stderr:
            # If __get_error find the correct error, raise it.
            # If not (and return None), raise a ScenarioRunError
            if error := self.__get_error_stderr(stderr=cmd_result.stderr):
                raise error
            raise scenario_errors.ScenarioRunError(
                stdout=cmd_result.stdout, stderr=cmd_result.stderr
            )
        # Parse stdout to catch missing errors. Sometimes, error can be in stdout instead of stderr
        # issue on nextflow : https://github.com/nextflow-io/nextflow/issues/2916
        if error := self.__get_error_stdout(stdout=cmd_result.stdout):
            raise error

    def generate_parameter_file(self):
        """Generate the parameter file containing all parameters of the run.

        Generate the file in the json format. For example:
        {
           "maximum": 5,
           "mae": "accept/mae",
           "knnflag": true,
        }
        """
        ## Parse all value to "sanitize" boolean values.
        ## TODO: Remove this this when https://gitlab.inria.fr/lola/frontend/-/issues/52 will be solved
        for key, value in self.parameters.items():
            # use str() to convert parameter (like 'port' as an int) into string
            if (str(value).lower() == "true"):
                # this avoid 'AttributeError: 'int' object has no attribute 'lower'
                self.parameters[key] = True
            if str(value).lower() == "false":
                self.parameters[key] = False

        # write json file
        with open(self.parameter_file, "w") as param_file:
            param_file.write(json.dumps(self.parameters))

    def __get_error_stderr(self, stderr: str) -> LolapyGlobalError | None:
        """Parse stderr after a `nextflow run` to raise correct error.

        Raises:
            NextflowErrors: in case of missing scenario
        Return:
            LolapyGlobalError | None: An error if the message was found. None if the error cannot be
                identify
        """
        if not stderr:
            return None
        if "sure exists a GitHub repository at this address" in stderr:
            return scenario_errors.ScenarioNotExist(self.scenario.scenario_path)
        if "Remote resource not found" in stderr:
            return scenario_errors.ScenarioNotExist(self.scenario.scenario_path)

    def __get_error_stdout(self, stdout: str) -> LolapyGlobalError | None:
        """Parse stdout after a `nextflow run` to search for errors.

        Sometimes nextflow store error messages in stdout instead of stderr, so the stdout
        must be parse to check errors.
        It's an error in nextflow (issue: https://github.com/nextflow-io/nextflow/issues/2916)

        Raises:
            NextflowErrors: in case of missing file in scenario
        Return:
            LolapyGlobalError | None: An error if the message was found. None if there is no error
                to identify
        """
        if not stdout:
            return None
        if "No such file" in stdout:
            # Concatenate all line containing 'No such file' in case of multiple missing files
            error_message = "\n".join(
                [line for line in stdout.split("\n") if "No such file" in line]
            )
            return scenario_errors.ScenarioRunError(stdout=error_message)
