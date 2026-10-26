#!/usr/bin/env python3

from pathlib import Path
import logging
import traceback

from huey import SqliteHuey

from lolapy.blueprints.scenario import AlgorithmExecuteJson
from lolapy.errors import LolapyGlobalError
from lolapy.dataset import import_db
from lolapy.dataset import errors as dataset_error
from lolapy.dataset.pdc import PdcImporter
import uuid
from lolapy import tools
from lolapy.scenario.scenario import Scenario
from lolapy.tools import settings
from lolapy.tools import logs
from lolapy.tools import frontend_api
from lolapy.algorithm import manage
from lolapy.nextflow import nextflow_logs
from lolapy.scenario import run_scenario, installation
from lolapy.nextflow import results

# Configure logs
app_settings = settings.get()
huey = SqliteHuey(filename=app_settings.lolapy_async_queue_file)


@huey.on_startup()
def init_logs():
    """Configure logs on startup.
    This is used to avoid a double imports from lolapy.py
    """
    logs.LolapyLogs.configure_logs()


@huey.task()
def huey_work():
    """Used in the /health resource.

    Return True anytime if huey works
    :return: bool: True if huey works, nothing otherwise
    """
    return True


@huey.task()
def parse_nextflow_logs(json_data):
    nextflow_logs.ProcessNextflowLogs.process(json_data)


@huey.task()
def test_async_logs():
    logging.debug("This is a DEBUG log test")
    logging.info("This is a INFO log test")
    logging.warning("This is a WARNING log test")
    logging.error("This is a ERROR log test")
    logging.critical("This is a CRITICAL log test")


@huey.task()
def start_scenario(
    scenario_hash: str,
    run_hash: str,
    user_hash: str,
    dataset_hash: str,
    parameters: dict,
    algorithm: list[AlgorithmExecuteJson],
):
    """Async function to start a scenario.

    Args:
        scenario_hash: Hash unique of the scenario
        run_hash: Hash unique of the run
        user_hash: Hash unique of the user. Used to check permission of the user on the dataset
        dataset_hash: Hash unique of the dataset.
        parameters: dictionnary of str containing parameters used for the nextflow scenario
        algorithm: list of dictionnary of switchable algorithm used in the scenario
        """
    try:
        my_scenario = Scenario.from_hash(scenario_hash)
        run_scenario.RunScenario(
            run_id=run_hash,
            scenario=my_scenario,
            user=user_hash,
            dataset=dataset_hash,
            parameters=parameters,
            algorithm=algorithm,
        ).run()
    except LolapyGlobalError as lolapy_error:
        logging.exception(lolapy_error.message)
        frontend_api.FrontendRequest.log(
            "Error",
            message=tools.object_fullname(lolapy_error),
            details=lolapy_error.message,
        )
        ## Send error to the frontend on the scenario
        frontend_api.FrontendRequest.get(f"/api/scenario/error/{run_hash}")
    except Exception as e:
        logging.exception("Unexpected error in run_scenario: %s", e)
        frontend_api.FrontendRequest.get(f"/api/scenario/error/{run_hash}")


@huey.task()
def install_scenario(scenario_hash: str, git_tag: str, repository_url: str):
    """Async function to install a scenario.

    Args:
        scenario_hash: Hash unique of the scenario
        git tag: Git tag of the repository to clone
        repository_url: Url of the git repository
    """
    try:
        # Don't check scenario now because it's not already installed
        my_scenario = Scenario.from_hash(scenario_hash=scenario_hash, check_exists=False)
        installation.InstallScenario(
            repository_url=repository_url,
            scenario=my_scenario,
            tag_name=git_tag,
            hash=scenario_hash,
        ).install()
    except LolapyGlobalError as lolapy_error:
        logging.exception(lolapy_error.message)
        frontend_api.FrontendRequest.log(
            "Error",
            message=tools.object_fullname(lolapy_error),
            details=lolapy_error.message,
        )
        ## Send error to the frontend on the scenario
        frontend_api.FrontendRequest.post(
            url="/api/tag/error",
            data={"tag": scenario_hash, "error": lolapy_error.public_message},
        )
    except Exception as e:
        logging.exception("Unexpected error in install_scenario: %s", e)
        frontend_api.FrontendRequest.post(
            url="/api/tag/error",
            data={"tag": scenario_hash, "error": LolapyGlobalError.standard_public_message},
        )


@huey.task()
def install_algorithm(algo_hash: str, git_version: str, url: str):
    try:
        manage.InstallAlgorithm(
            repository_url=url, algo_hash=algo_hash, git_version=git_version
        ).install()
    except LolapyGlobalError as lolapy_error:
        logging.exception(lolapy_error.message)
        frontend_api.FrontendRequest.log(
            "Error",
            message=tools.object_fullname(lolapy_error),
            details=lolapy_error.message,
        )
        ## Send error to the frontend on the scenario
        frontend_api.FrontendRequest.post(
            url="/api/algorithm/error",
            data={"algorithm_hash": algo_hash, "error": lolapy_error.public_message},
        )
    except Exception as e:
        logging.exception("Unexpected error in install_algorithm: %s", e)
        frontend_api.FrontendRequest.log(
            "Error", message=tools.object_fullname(e), details=str(e)
        )
        frontend_api.FrontendRequest.post(
            url="/api/algorithm/error",
            data={
                "algorithm_hash": algo_hash,
                "error": LolapyGlobalError.standard_public_message,
            },
        )


@huey.task()
def import_dataset(data_path):

    data_path = Path(data_path)
    installation = import_db.InstallDataset(data_path)
    try:
        # TODO: Change this to log all request to frontend here !!
        # For example, create a function to extract_from_archive, then send /api/dataset//start and then
        # method install()
        installation.install_from_archive()
        frontend_api.FrontendRequest.post(
            f"/api/dataset/{installation.dataset_hash}/complete/{installation.import_id}",
            data={"size": 10},
        )
    except LolapyGlobalError as lolapy_error:
        frontend_api.FrontendRequest.log(
            "Error",
            message=tools.object_fullname(lolapy_error),
            details=lolapy_error.message,
        )
        if installation.dataset_hash:
            frontend_api.FrontendRequest.get(
                url=f"/api/dataset/{installation.dataset_hash}/error/{installation.import_id}"
            )
        logging.exception(lolapy_error.message)
    except Exception as e:
        frontend_api.FrontendRequest.log(
            "Error", message=str(e.__class__), details=str(e)
        )
        if installation.dataset_hash:
            frontend_api.FrontendRequest.get(
                url=f"/api/dataset/{installation.dataset_hash}/error/{installation.import_id}"
            )
        logging.exception("Unexpected error in import_dataset: %s", e)
        frontend_api.FrontendRequest.log(
            "Error", message=tools.object_fullname(e), details=str(e)
        )


@huey.task()
def fetch_and_import_dataset_pdc(
    dataset_hash: str,
    user_hash: str,
    contract: str,
    resource: str,
    purpose_id: str | None = None,
    resource_id: str | None = None,
):
    """Async function to fetch a dataset via PDC according to data-import logic."""
    import_id = str(uuid.uuid4())
    logging.info(f"Starting PDC fetch for dataset={dataset_hash}, user={user_hash}, contract={contract}, resource={resource}, purpose_id={purpose_id}, resource_id={resource_id}")
    frontend_api.FrontendRequest.log(
        log_type="ImportDataset",
        message=f"API start to import a dataset via PDC ({dataset_hash})",
        details=f"Dataset temporary ID={import_id}, Resource={resource}",
    )

    try:
        # Check permissions
        has_permission = frontend_api.FrontendRequest.dataset_permission(user_hash, dataset_hash)
        if not has_permission:
            raise dataset_error.DatasetPermissionDenied(dataset=dataset_hash, user=user_hash)

        # Notify frontend start
        frontend_api.FrontendRequest.get(f"/api/dataset/{dataset_hash}/start/{import_id}")

        settings_app = settings.get()
        dataset_dir = settings_app.lolapy_dataset_path / dataset_hash
        dataset_dir.mkdir(parents=True, exist_ok=True)
        target_path = dataset_dir / Path(resource).name

        importer = PdcImporter(
            contract=contract,
            resource=resource,
            purpose_id=purpose_id,
            resource_id=resource_id,
        )
        importer.login_pdc()
        importer.process_exchange()
        importer.login_receiver()
        importer.get_from_receiver()

        def on_progress(pct: float):
            frontend_api.FrontendRequest.get(f"/api/dataset/{dataset_hash}/progress/{pct:.2f}")

        bytes_written = importer.download_data(target_path, progress_callback=on_progress)
        size_mb = max(1, round(bytes_written / (1024 * 1024)))

        # Notify frontend completion
        frontend_api.FrontendRequest.post(
            f"/api/dataset/{dataset_hash}/complete/{import_id}",
            data={"size": size_mb, "storagePath": str(target_path)},
        )
        frontend_api.FrontendRequest.log(
            log_type="ImportDataset",
            message=f"Dataset {dataset_hash} imported via PDC successfully",
            details=f"Saved to {target_path} ({size_mb} MB)",
        )
    except LolapyGlobalError as lolapy_error:
        frontend_api.FrontendRequest.log(
            "Error",
            message=tools.object_fullname(lolapy_error),
            details=lolapy_error.message,
        )
        frontend_api.FrontendRequest.get(
            url=f"/api/dataset/{dataset_hash}/error/{import_id}"
        )
        logging.exception(lolapy_error.message)
    except Exception as e:
        frontend_api.FrontendRequest.log(
            "Error", message=tools.object_fullname(e), details=str(e)
        )
        frontend_api.FrontendRequest.get(
            url=f"/api/dataset/{dataset_hash}/error/{import_id}"
        )
        logging.exception("Unexpected error in fetch_and_import_dataset_pdc: %s", e)


@huey.task()
def prepare_results(working_directories: list, run_hash: str, tag_hash: str):
    """Prepare result in asynchronous way

    Send complete or error to the frontend
    :param working_directory: list: List of all working directories of all processes of the run
    :param run_hash: str: Hash unique of the nextflow run
    :param tag_hash: str: Hash unique of the scenario tag
    """
    try:
        path_working_directories: list[Path] = [
            Path(workdir) for workdir in working_directories
        ]
        # Extract list of required output files
        my_scenario: Scenario = Scenario.from_hash(check_exists=True, scenario_hash=tag_hash)
        # scenario_recipe is not None because check_exists is True
        list_output_files = my_scenario.scenario_recipe.output
        # list, filter and compress result files
        prepare_results = results.PrepareResults(run_hash, path_working_directories)
        prepare_results.filter(list_output_files)
        prepare_results.compress()
        frontend_url = app_settings.frontend_api_prepare_result_complete_url
    except LolapyGlobalError as lolapy_error:
        logging.exception(lolapy_error.message)
        frontend_url = app_settings.frontend_api_prepare_result_error_url
    except Exception as error:
        logging.exception("Unexpected error in prepare_results: %s", error)
        frontend_url = app_settings.frontend_api_prepare_result_error_url
    # Send GET request to frontend to url like /api/scenario/results/{complete,error}/<run_hash>
    # Can be success or failure depending
    frontend_api.FrontendRequest.get(url=f"{frontend_url}/{run_hash}")
