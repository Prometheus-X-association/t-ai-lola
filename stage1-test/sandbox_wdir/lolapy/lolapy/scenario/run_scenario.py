#!/usr/bin/env python3

"""Handle all methods to run/stop scenarios"""

import logging
import time
from pathlib import Path

from lolapy.algorithm.prepare_run import PrepareAlgorithms
from lolapy.blueprints.scenario import AlgorithmExecuteJson
from lolapy.dataset.errors import DatasetPermissionDenied
from lolapy.nextflow import errors as nextflow_errors
from lolapy.nextflow import nextflow
from lolapy.scenario.scenario import Scenario
from lolapy.slurm import sbatch, slurm_job
from lolapy.tools import settings
from lolapy.tools.frontend_api import FrontendRequest


class SetupRunWorkdir:
    """Object to create and manage the workding directory of a run."""

    def __init__(self, run_workdir: Path, run_id: str):
        """Constructor for SetupRunWorkdir.

        Args:
            run_workdir: Path: FullPath of the work directory of the run
        """
        self.run_workdir = run_workdir
        self.run_id = run_id

    @classmethod
    def from_id(cls, run_id: str) -> "SetupRunWorkdir":
        """Return the name of the working directory from its id.

        Args:
            run_id: str: Unique identifier of the run
        Returns:
            Path: FullPath of the run workding directory
        """
        return cls(run_workdir=settings.get().nextflow_workdir / run_id, run_id=run_id)

    def mkdir(self):
        """Create the run working directory.

        Raises:
            NextflowWorkDirExists: if the directory already exists
        TODO: Handle exception to create work dir
        """
        if self.run_workdir.exists():
            raise nextflow_errors.NextflowWorkDirExists(work_dir=self.run_workdir, identifier=self.run_id)
        self.run_workdir.mkdir()

class RunScenario:
    """Main object to start manage scenario.

    Attributes:
        run_id: str: UUID use to label and track scenario
        scenario: Scenario: Instance of Scenario that keep information on the scenario (path, recipe, ...)
        user: str: Hash identifier of the user. Used to check if this user can run scenario on the dataset
        dataset: str: Hash identifier of the dataset. Used in complement with the user for permission access
        parameters: dict: All parameters given to the scenario
        algorithm: dict: All information on users's algorithm used in the scenario
    """

    def __init__(
        self,
        run_id: str,
        scenario: Scenario,
        user: str,
        dataset: str,
        parameters: dict | None = None,
        algorithm: list[AlgorithmExecuteJson] | None = None,
    ):
        """Create a Scenario object which handle and execute all tasks.

        Args:
            run_id: str: UUID use to label and track the scenario
            scenario: str: Name of the scenario to execute. Usually it's the tag of the scenario
            user: str: Hash identifier of the user. Used to check if this user can run scenario on the dataset
            dataset: str: Hash identifier of the dataset. Used in complement with the user for permission access
            parameters: dict: All parameters given to the scenario
            algorithm: dict: All information on users's algorithm used in the scenario
        """
        self.run_id = run_id
        self.scenario = scenario
        self.user = user
        self.dataset = dataset
        self.parameters = parameters or {}
        self.algorithm = algorithm or []

    def run(self):
        """Run a scenario with all steps before and after.

        This method should be runned in a Queue system or in background because it can take a lot
        of time to run.

        1.   Check the user can run this scenario on this dataset
        2.   Manage algorithm and generate nextflow files for switchable algorithms
        3.   Start trax instance with correct dataset
        4.     Wait until trax is started
        5.   Run scenario
        6.   Api is collecting logs (not manage by Scenario object)
        7.   Stop trax instance
        """
        if not FrontendRequest.dataset_permission(self.user, self.dataset):
            raise DatasetPermissionDenied(self.user, self.dataset)

        # Generate the working directory for the run. All files will be stored inside it
        setup_workdir = SetupRunWorkdir.from_id(self.run_id)
        setup_workdir.mkdir()

        run_workdir = setup_workdir.run_workdir

        # Algorithm part. Get parameters for all algorithm as dict
        algorithm_parameters = PrepareAlgorithms.from_dict(
            algorithms=self.algorithm, my_scenario=self.scenario, run_workdir=run_workdir
        )

        # Scenario part
        # Use a try/finally case to stop trax or slurm if something gone wrong
        try:
            # Start Trax container on the cluster
            my_trax = slurm_job.SlurmTrax(
                self.run_id,
                database_name=self.dataset,
                sbatch_type=sbatch.SbatchScript.START_TRAX,
            )
            my_trax.start()
            logging.info(
                f"Run ID: {self.run_id}. Reserve the Trax instance for dataset {self.dataset}"
            )
            if my_trax.is_pending():
                logging.info(f"Run ID: {self.run_id}. Trax dataset is pending by slurm")
            while my_trax.is_pending():
                time.sleep(60)

            # Get information on running Trax container
            trax_port = my_trax.get_docker_port()
            logging.info(
                f"Run ID: {self.run_id}. Trax instance running for dataset {self.dataset} on port {trax_port}"
            )

            # Start the Nextflow workflow
            logging.info(
                f"Run ID: {self.run_id}. Start the nextflow scenario {self.scenario}"
            )
            self.parameters["lrsPort"] = str(trax_port)
            self.parameters["lrsHost"] = "0.0.0.0"
            # Expand the list of scenario parameters with the algorithms parameters
            self.parameters.update(
                algorithm_parameters
            )
            # Check the nextflow environment
            my_nextflow_env = nextflow.NextflowCheckEnv.from_env(
                run_workdir=run_workdir, run_id=self.run_id
            )
            my_nextflow_env.check()
            # Start Nextflow
            my_nextflow = nextflow.RunNextflow(
                nextflow_env=my_nextflow_env,
                scenario=self.scenario,
                parameters=self.parameters,
            )
            my_nextflow.run()
            # Stop Trax server at the end of the process
            my_trax.stop()
        finally:
            RunScenario.stop_scenario(self.run_id)

    @staticmethod
    def stop_scenario(run_id: str):
        """Stop a running scenario.

        Currently, it only stop a Trax container

        :param run_id: str: Unique identifier of the run. Can be found in nextflow logs
        """
        slurm_job.SlurmTrax(run_id).stop()
        ## TODO: Stop a running Nextflow
