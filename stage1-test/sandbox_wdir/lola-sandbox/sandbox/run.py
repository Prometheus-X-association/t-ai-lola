#!/usr/bin/env python3

"""This is the file containing all information on how to run a nextflow experiment"""
import argparse
import json
import logging
from pathlib import Path
import re
import uuid
import shutil
import sys, os

from pydantic import BaseModel, root_validator
from lolapy import errors as lolapy_errors
from lolapy.scenario import scenario
from lolapy.scenario import errors as scenario_errors
from lolapy.tools import settings
from lolapy.nextflow import nextflow
from lolapy.algorithm import algorithm, extend_template
import pydantic

from sandbox import app
from sandbox import errors
from sandbox import lrs
from sandbox.algorithm_parameters import ManageAlgorithmParameters
from sandbox.error_parsing_config import SanitizePydanticError
from sandbox.searching_files import SearchFiles

class GlobalSandboxRun:
    """Store global variables for Sandbox Run.

    Attributes:
        nextflow_path_env_variable: Environment variable which contains the Path of the
            nextflow executable.
        nextflow_exec_name: Name of the executable of nextflow.
    """

    nextflow_path_env_variable = "NF_EXECUTABLE"
    nextflow_exec_name = "nextflow"
    scenario_config_file = "params.json"
    algorithm_config_file = "algo_recipe.json"


class ConfigSwitchableAlgorithm(BaseModel):
    """Serialize/Deserialize config switchable algorithm.

    Used with 'ConfigJson' class
    Attributes:
        algorithm_path: Full Path of the algorithm
        nf_variable: Name of the nextflow variable used in the scenario (workflow)
        parameters: dictionnary that contains nextflow parameters to use algorithm template
    """

    algorithm_path: Path
    nf_variable: str
    parameters: dict[str, int | str] | None

    @root_validator
    def expand_algorithm_path(cls, values):
        """Expand fullpath of `algorithm_path` in the object

        It expands user home directory if the user uses `~/` and expand full path
        in case of relative Path like `../`.
        """
        if "algorithm_path" in values:
            values["algorithm_path"] = values["algorithm_path"].expanduser().absolute()
        return values

class ConfigJson(BaseModel):
    """Serialize/Deserialize config file to run scenario.

    Attributes:
        scenario_path: Full Path of the scenario directory
    """

    scenario_path: Path
    scenario_parameters: dict[str, int | str]
    algorithms: list[ConfigSwitchableAlgorithm]

    @root_validator
    def expand_scenario_path(cls, values):
        """Expand fullpath of `scenario_path` in the object

        It expands user home directory if the user uses `~/` and expand full path
        in case of relative Path like `../`.
        """
        if "scenario_path" in values:
            values["scenario_path"] = values["scenario_path"].expanduser().absolute()
        return values

class ValidateArguments:
    """Parse and prepare arguments for the scenario run"""

    def __init__(self, config: ConfigJson, config_path: Path, lrs_url: lrs.LRSUrl, workdir: Path, no_lrs: bool):
        self.config: ConfigJson = config
        self.config_path: Path = config_path
        self.lrs_url: lrs.LRSUrl = lrs_url
        self.workdir: Path = workdir
        self.scenario_path = self.config.scenario_path
        self.no_lrs: bool = no_lrs

    @staticmethod
    def _validate_directories(dirname: Path, pre_msg: str = ""):
        """Check if the directory `dirname` exists.

        Args:
            dirname: Path: Path of the directory to check
            pre_msg: str: Message to add to the error message if the workdir is missing.
                See documentation on SandboxErrors for more information. Default, ""
        Raises:
            errors.MissingDir: if the directory does not exist
        """
        if not dirname.exists():
            raise errors.MissingDir(dirname).pre_msg(pre_msg)

    @classmethod
    def from_argparse(cls, arguments: argparse.Namespace) -> "ValidateArguments":
        """Constructor for `ValidateArguments` from argparse arguments.

        Stop the execution if the config file is badly formatted.
        Args:
            arguments: argparse namespace (got from command line) that contains all
                variables of the CLI.
        Returns:
            ValidateArguments: The object built
        """

        # Generate ConfigJson structure from the json file
        if not arguments.json_config.exists():
            raise errors.MissingFile(arguments.json_config).pre_msg("Config file (--json-config) : ")
        arguments.json_config = arguments.json_config.absolute().resolve()
        with open(arguments.json_config) as config_file:
            try:
                config = ConfigJson(**json.loads(config_file.read()))
            except pydantic.ValidationError as e:
                SanitizePydanticError(pydantic_error=e, filename=arguments.json_config).sanitize()
                sys.exit(1)
            except json.decoder.JSONDecodeError as e:
                raise errors.ParseJsonError(error_msg=str(e), json_path=str(arguments.json_config))
        # Validate directories
        workdir = arguments.workdir.expanduser().absolute()
        cls._validate_directories(workdir, "Workding Directory : ")
        # Validate LRS connection
        if arguments.lrs_host and not arguments.no_lrs:
            logging.debug(f"Check access to LRS at adress: '{arguments.lrs_host}'")
            arguments.lrs_host.ping()
        else:
            logging.debug("Disable check of LRS because '--no-lrs' is set")
        return cls(
            config_path=arguments.json_config,
            config=config, lrs_url=arguments.lrs_host, workdir=workdir,
            no_lrs=arguments.no_lrs,
        )


class RunScenario:
    """Run a scenario with the "sandbox".

    Manage the Nextflow execution and the complete run.

    Attributes:
        lrs_host: LRSUrl: Structure LRSUrl containing information of the
            LRS connection.
        workdir: Path: Path of the working directory. Where to store run.
        full_config: ConfigJson: Configuration file for algorithm.
        nf_exe_path: Path: Path of the nextflow executable.
        run_id: str | None: Unique identifier of the run.
        final_workdir: Path: Path where the run will be stored. Usually,
            it's a concatenation of the workdir and the run_id.
    """

    def __init__(
            self, lrs_host: lrs.LRSUrl, workdir: Path, full_config: ConfigJson, config_path: Path, nf_exe_path: Path, run_id: str | None = None
    ):
        """
        Args:
            lrs_host: LRSUrl: Structure LRSUrl containing information of the LRS connection.
            workdir: Path: Path of the working directory. Where to store run.
            full_config: ConfigJson: Configuration file for algorithm.
            config_path: Path: Path of the configuration file used in the sandbox.
            nf_exe_path: Path: Path of the nextflow executable.
            run_id: str | None: Unique identifier of the run.
        """

        self.lrs_host = lrs_host
        self.workdir = workdir
        self.full_config: ConfigJson = full_config
        self.config_path: Path = config_path
        self.nf_exe_path = nf_exe_path
        self.run_id = run_id or str(uuid.uuid4())
        # Add 'R' (for Run) at the begin of the run name to avoid error with nextflow
        self.run_id = "R" + self.run_id
        self.final_workdir: Path = self.workdir / self.run_id  # Path where all files will be stored
        if not self.final_workdir.exists():
            self.final_workdir.mkdir()
            logging.debug(f"Create the directory {self.final_workdir}")

    def _extend_scenario_parameter(self) -> dict:
        """Add extra parameters for nextflow (lrsHost and lrsPort)."""
        parameters = self.full_config.scenario_parameters.copy()
        parameters.update({"lrsHost": self.lrs_host.url, "lrsPort": self.lrs_host.port})
        return parameters

    @classmethod
    def from_cli_args(cls, args: ValidateArguments) -> "RunScenario":
        """Construct a `RunScenario` object from `ValidateArguments`

        Args:
            args: ValidateArgumnets object that contains all information
        Returns:
            RunScenario
        """
        return cls(
            lrs_host=args.lrs_url,
            workdir=args.workdir,
            full_config=args.config,
            config_path=args.config_path,
            nf_exe_path=get_nextflow_executable(),
        )

    def prepare_algorithm(self, my_scenario: scenario.Scenario) -> dict:
        """Parse the 'algorithms' got in the POST request to run the scenario.

        For each algorithms in the json-config file, generate the nextflow file
        Args:
            my_scenario: Scenario: The Scenario structure to use. prepare_algorithm
                will extract path of template files required to create algorithm nextflow
                files.
        """
        all_parameters = {}  # Store all parameters used when running nextflow

        # Generate template for all algorithm
        for this_algorithm in self.full_config.algorithms:
            template = scenario.ScenarioTemplate.from_nf_variable(
                nf_variable=this_algorithm.nf_variable, scenario=my_scenario
            )
            output_nf_script = self.final_workdir / f"algo_{this_algorithm.algorithm_path.name}.nf"
            # Get the recipe of the algorithm
            this_algorithm_recipe: algorithm.AlgorithmRecipe = algorithm.Algorithm.from_path(
                this_algorithm.algorithm_path
            ).algo_recipe
            # Merge default parameters of the algorithm with parameters given in the json-config
            this_algorithm_parameters = ManageAlgorithmParameters(
                recipe=this_algorithm_recipe,
                algorithm=this_algorithm
            ).get_parameters()
            # Generate the nextflow template of the algorithm
            algorithm_to_render: extend_template.CreateNFscript = extend_template.CreateNFscript(
                algo_recipe_data=this_algorithm_recipe,
                algorithm_parameters=this_algorithm_parameters,
                output_template=output_nf_script,
                scenario_template=template,
            )
            algorithm_to_render.gen_template()
            logging.debug(f"Nextflow file '{algorithm_to_render.output_template}'for algorithm {this_algorithm.nf_variable} generated")
            all_parameters[this_algorithm.nf_variable] = str(algorithm_to_render.output_template)

        # Add parameters in the list of parameters to nextflow
        return all_parameters

    def log_output_files(self, file_list: list[str]):
        """Log.info the files path of the result listed in scenario parameters."""
        output_files = SearchFiles(files=file_list, source=self.final_workdir).search()
        logging.info("Result files should be in :")
        for file_path in output_files:
            logging.info(f"  {file_path}")

    def check(self, scenario: scenario.Scenario):
        """All steps check for a good run.

        Declare a variable `is_error` that live during the whole function. If the variable is
        True at the end of the function, exit the program with exit(1).
        It allows to check all steps
        """

        is_error = False

        ## Check consistency for number of switchable algorithms between all files
        if not scenario.scenario_recipe:
            logging.error(f"Config file '{GlobalSandboxRun.scenario_config_file}' cannot be found for scenario {scenario.scenario_path}")
            is_error = True
        elif len(self.full_config.algorithms) != len(scenario.scenario_recipe.switchable_algorithms):
            is_error = True
            logging.error(f"""There is a mismatch between '{GlobalSandboxRun.scenario_config_file}' and {self.config_path} :
            '{len(self.full_config.algorithms)}' switchable algorithm(s) are defined in {self.config_path}
            '{len(scenario.scenario_recipe.switchable_algorithms)}' switchable algorithm(s) are defined in {scenario.scenario_recipe_path}""")

        if is_error:
            logging.error("Stop program due to previous error(s)")
            sys.exit(1)

    def run(self):
        """Run the nextflow/scenario.

        The method does not raise exceptions by itself but other called methods will.
        """
        fake_nf_scenario_dir = self.full_config.scenario_path.absolute().parent

        # Avoid loading .env file required in lolapy
        settings.AppSettingsBuilder.build_default()
        
        with settings.EditSettings():
            settings.get().nextflow_scenario_dir = fake_nf_scenario_dir
            settings.get().nextflow_executable = self.nf_exe_path
            settings.get().nextflow_workdir = Path(self.workdir)

            my_scenario = scenario.Scenario.from_hash(
                scenario_hash=self.full_config.scenario_path.name, check_exists=True
            )

            self.check(scenario=my_scenario)
            algorithm_parameters = self.prepare_algorithm(my_scenario=my_scenario)
            
            my_nextflow_checker = nextflow.NextflowCheckEnv.from_env(
                run_workdir=self.final_workdir, run_id=self.run_id
            )
            
            # Create backend_docker.config dynamically
            config_path = Path(my_nextflow_checker.run_work_dir) / "backend_docker.config"
            self._generate_docker_config(config_path)

            extended_parameters = self._extend_scenario_parameter()
            extended_parameters.update(algorithm_parameters)

            extended_parameters["-c"] = str(config_path)

            logging.debug(f"Parameters used in the scenario: {extended_parameters}")

            my_nf_run = nextflow.RunNextflow(
                nextflow_env=my_nextflow_checker,
                scenario=my_scenario,
                parameters=extended_parameters,
                background=False
            )

            my_nf_run.run()

        logging.info(f"Results and data of the run stored in '{my_nextflow_checker.run_work_dir}'")
        self.log_output_files(my_scenario.scenario_recipe.output)

    def _generate_docker_config(self, config_path: Path):
        """Generate a Nextflow config file for Docker execution."""
        config_content = """\
    profiles {
        docker {
            process.executor = 'docker'
            docker.enabled = true
            docker.runOptions = '--rm'
            docker.autoMounts = true
            docker.forcePull = false
        }
    }
    """
        try:
            with open(config_path, "w") as f:
                f.write(config_content)
            logging.info(f"Generated Nextflow Docker config at: {config_path}")
        except Exception as e:
            logging.error(f"Failed to generate Nextflow Docker config: {e}")


# Static part of the file
# Generate command line option for running scenario
run_parser = argparse.ArgumentParser(
    description="Manage run of nextflow scenario",
    add_help=False,
)
run_parser.add_argument("-h", "--help", action=app._HelpAction, help="Show this help message and exit")
run_parser.add_argument(
    "--lrs-host",
    type=lrs.LRSUrl.validate_url,
    help="Host and port of the lrs server in the format http(s)://{host}:{port}",
    default=None,
)
run_parser.add_argument(
    "-w", "--workdir", type=Path, help="Path where to store the multiple runs", default=Path("/tmp")
)
run_parser.add_argument(
    "-C", "--json-config", dest="json_config", type=Path, help="Path to the complete json configuration file"
)
run_parser.add_argument(
    "--no-lrs", dest="no_lrs", default=False, action="store_true", required=False, help="If option is used, the program will not check for Lrs instance. Use this option if you have your data locally"
)


def get_nextflow_executable() -> Path:
    """Search for Nextflow executable in the PATH or env variable.

    Raises:
        errors.NextflowExecutableNotFound: If the executable cannot be found
    Returns:
        Path of the 'nextflow' executable
    """
    nf_exec_env_name = GlobalSandboxRun.nextflow_path_env_variable
    nf_exec_name = GlobalSandboxRun.nextflow_exec_name
    if nf_exec := (os.environ.get(nf_exec_env_name) or shutil.which(nf_exec_name)):
        logging.debug(f"Nextflow executable found: {nf_exec}")
        return Path(nf_exec)
    raise errors.NextflowExecutableNotFound()

def check_docker():
    """Check if docker is installed and with good version"""
    minimal_version = (20, 00, 1)
    import subprocess
    try:
        processes = subprocess.run("docker --version".split(), capture_output=True, text=True)
    except FileNotFoundError:
        raise errors.RequirementsError("Docker not found in the PATH.")
    matches = re.search(r"([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2})", processes.stdout)
    if not matches:
        logging.warning("Docker founded but cannot extract version number or version don't match requirement.")
    version = matches.group(1)
    version_int = tuple(map(int, (version.split("."))))
    if version_int < minimal_version:
        raise errors.RequirementsError(f"Current docker version '{version}' does not match requirements (need >= {'.'.join(map(str, minimal_version))})")

def parse_args_from_app(remains_args: list):
    """Entrypoint for run.py with remaining command line arguments.

    The function will run the complete "pipeline" of the run.py file.
    Use this function from another python file (for example app.py).
    Args:
        remains_args: list of argument from the CLI.
    """
    try:
        # If the list is empty
        if not remains_args:
            run_parser.print_help()
            sys.exit(0)
        my_args = run_parser.parse_args(remains_args)
        cli_args = ValidateArguments.from_argparse(my_args)
        print(vars(cli_args))
        check_docker()
        my_run = RunScenario.from_cli_args(cli_args)
        my_run.run()
    except (lolapy_errors.LolapyGlobalError, errors.SandboxErrors) as e:
        logging.error(f"{e.message}")
        logging.error("Exit due to previous error(s)")
        sys.exit(1)
