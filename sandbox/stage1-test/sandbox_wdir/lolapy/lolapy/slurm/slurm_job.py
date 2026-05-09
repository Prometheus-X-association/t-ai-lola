#!/usr/bin/env python3

import json
import logging
from pathlib import Path
import time
from lolapy.scenario.errors import ScenarioRunError

from lolapy.tools import settings, shell_command
from lolapy.slurm import job_info
from lolapy.slurm import errors as slurm_errors


class SlurmJob:
    """
    Manage Slurm Job

    The object must have a unique identifier to avoid conflicts between runs and containers.
    """

    def __init__(self, run_id: str, **kwargs):
        """Instantiate a SlurmJob object.

        Don't forget optionnal arguments if you want to generate sbatch script and/or Trax containers

        :param run_id: str: Unique identifier used to tag the run and identify jobs

        Optionnal arguments
        :param database: str: Name of the database to use for the job. [Default: None]
        :param sbatch_type: sbatch.SbatchScript: Type of sbatch to use for the Slurm Job. The sbatch will be created on
        :param trax_port: int: Port of the running Trax container on the cluster
        start if it is not set to None. [Default: None]
        :param json_directory: Path: Path to the directory splitted json (xapi) files
        """
        self.run_id = run_id
        self.job_name = f"slurm_job_{run_id}"

        # Optionnal arguments
        self.sbatch_type = kwargs.get("sbatch_type")
        self.database = kwargs.get("database_name")
        self.trax_port = kwargs.get("trax_port")
        self.json_directory = kwargs.get("json_directory")

        # Variables from environment
        app_settings = settings.get()
        self.working_dir = app_settings.nextflow_workdir
        self.cluster_host = app_settings.cluster_host

        # Path for output files
        self.slurm_batch_script = self.working_dir / Path(self.job_name + ".sbatch")
        self.stdout_slurm = self.working_dir / Path(self.job_name + ".stdout")
        self.stderr_slurm = self.working_dir / Path(self.job_name + ".stderr")

    def start(self):
        """Start the slurm job.

        Be carefull, the sbatch file must exist
        """
        # Create sbatch script
        if self.sbatch_type:
            self.__gen_sbatch()
        # Check if sbatch file exists
        if not self.slurm_batch_script.exists:
            raise IOError(f"{self.slurm_batch_script} does not exist")

        # Execute command to run sbatch
        cmd_result = shell_command.ShellCommand.new(
            command=f"sbatch {self.slurm_batch_script}",
            on_localhost=True
        ).run()
        # If there is an error, stop the reservation by cancelling the job
        if cmd_result.exit_code != 0:
            self.stop()
            raise ScenarioRunError(stdout=cmd_result.stdout, stderr=cmd_result.stderr)
        logging.info(f"Job sumbitted", extra={"request_id": self.job_name})

    def stop(self):
        """Stop a slurm Job by cancelling the job"""
        # -f option in scancel is to send the signal to all process of the job
        # This signal can be trapped by the sbatch script and kill the container/children processes
        cmd_result = shell_command.ShellCommand.new(
            command=f"scancel -f --name {self.job_name}",
            on_localhost=True
        ).run()
        if cmd_result.exit_code != 0:
            logging.error(
                f"while stopping slurm job on {self.cluster_host}. Error: {cmd_result.stderr}",
                extra={"request_id": self.job_name},
            )
            return cmd_result.stderr
        logging.info(f"Job stopped", extra={"request_id": self.job_name})

    def is_pending(self) -> bool:
        """Check if the job is pending by slurm controller.

        :return: bool: True is the job is pending. False otherwise.
        """
        if (
            job_info.SlurmJobInfo.get_job_status(self.job_name)
            == job_info.SacctJobStatus.PENDING
        ):
            return True
        return False

    def is_done(self) -> bool:
        """Check if the job is completed and canceled.

        :return: bool: True if the job is completed, failed or canceled. False if running or pending.
        """
        from lolapy.slurm.job_info import SacctJobStatus

        status = job_info.SlurmJobInfo.get_job_status(self.job_name)
        match status:
            case SacctJobStatus.CANCELLED | SacctJobStatus.COMPLETED | SacctJobStatus.FAILED:
                return True
        return False

    def is_success(self) -> bool:
        """Check if the job is failed.

        :return: bool: True if the job is on error.
        """
        from lolapy.slurm.job_info import SacctJobStatus

        status = job_info.SlurmJobInfo.get_job_status(self.job_name)
        match status:
            case SacctJobStatus.COMPLETED:
                return True
        return False

    def __gen_sbatch(self):
        """Generate all variables to create sbatch scripts"""
        app_settings = settings.get()
        # List of required variables for SbatchScript
        variables = {
            "job_name": self.job_name,
            "stdout_slurm": self.stdout_slurm,
            "stderr_slurm": self.stderr_slurm,
            "json_directory": self.json_directory,
            "db_host": app_settings.sql_host_ip,
            "database_name": self.database,
            "db_user": app_settings.sql_root_user,
            "db_password": app_settings.sql_root_password,
            "trax_port": self.trax_port,
        }
        # Filter None values
        # This avoid passing None value to sbatch methods and complete sbatch script with empty value.
        # If value is not set and required by a methods, the program raise an error
        variables = {key: value for key, value in variables.items() if value}
        txt_script = self.sbatch_type.get_script(**variables)
        self.slurm_batch_script.write_text(txt_script)


class SlurmTrax(SlurmJob):
    def is_trax_running(self, trax_port: int) -> bool:
        """Check if the Trax instance is running on the cluster.

        :param trax_port: int: Port of the trax container to check
        :return: bool: Return True if running, False otherwise.
        """
        command = f"curl -Ss 0.0.0.0:{trax_port}"
        cmd_result = shell_command.ShellCommand.from_env(command=command).run()
        if cmd_result.stderr:  # If stderr is not empty: problem !
            logging.info(f"Trax container not runnning: {cmd_result.stderr}")
            return False
        return True

    def get_docker_port(self) -> int:
        """Extract the Port attributed to the Docker container.

        This method use SSH connection to run docker inspect command on the cluster. Sometimes, docker run can
        takes times to start. So run the commande 5 times before fail.
        :return: int: The port of the running Docker Trax
        """
        command = f"docker inspect {self.job_name}"
        stdout, stderr = ("", "")  # Avoid "possibly unbound stdout, stderr"
        retry = 0
        while retry < 5:
            cmd_result = shell_command.ShellCommand.from_env(command=command).run()
            stderr, stdout = cmd_result.stderr, cmd_result.stdout
            if stderr:
                logging.info(
                    f"Try to inspect container {self.job_name}. Attempting:{retry}. Stderr: {stderr}"
                )
                time.sleep(2)
                retry += 1
            else:
                logging.info(f"Inspect trax container {self.job_name}")
                break
        if stderr:
            logging.error(
                f"Stderr not empty when getting Docker port for {self.job_name}: {stderr}"
            )
            # Raise an error with content of the stderr slurm file
            raise slurm_errors.TraxUnreachable(stderr=self.stderr_slurm.read_text())
        json_stdout = json.loads(stdout)
        docker_port = int(
            json_stdout[0]["NetworkSettings"]["Ports"]["80/tcp"][0]["HostPort"]
        )
        return docker_port
