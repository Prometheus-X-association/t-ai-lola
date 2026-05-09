#!/usr/bin/env python3

from __future__ import annotations

import json
import logging
import queue
import threading
import time
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Callable

from flasgger import Swagger
from flask import Flask, Response, request, send_file
from lolapy.bin.app import APP_VERSION
from lolapy.dataset import dataset_information, import_db
from lolapy.nextflow.nextflow_logs import NextflowLogProcess, NextflowLogWorkflow
from lolapy.tools import settings, fixtures
from lolapy.tools.frontend_api import FrontendRequest
from lolapy.tools.health import Health

flask_app = Flask(__name__)

flask_app.config["SWAGGER"] = {
    "title": "Lolapy API",
}
Swagger(flask_app, template_file="../../docs/swagger.yaml")

root_logger = logging.getLogger()
root_logger.setLevel("INFO")

# Read environment file to get Data
app_settings = settings.get()


@flask_app.before_request
def before_request():
    """
    Executed before each request to log the route
    """
    method = request.method
    route = request.url_rule
    access_adress = "->".join(request.access_route)
    data = request.data if request.data else ""
    logging.info(f"{access_adress} {method} {route} {data}")


@flask_app.after_request
def after_request(response):
    """
    Executed after each request to log the response
    """
    method = request.method
    route = request.url_rule
    access_adress = "->".join(request.access_route)
    logging.info(f"{access_adress} {method} {route} {response.status_code}")

    return response


class QueueFakeAsync:
    """Class used to manage fake asynchrone tasks.

    DO NOT USE IT IN PRODUCTION!!!!
    This class mimic is used to mimic the behaviour of the huey runner used
    by lolapy. Just add the task as lambda call (https://docs.python.org/3/reference/expressions.html#lambda)
    Don't forget to call start() after to start the first task.
    Every task will be run sequentially with a sleep(2) between each
    Example:
      bg_tasks = FakeAsync()
      bg_tasks.push(task=lambda: print("hello, ", "world!"))
      bg_tasks.push(task=lambda: FrontendRequest.post(url=frontend_nf_logs_url, data=fixtures.FakeNextflowLogProcess.done))
      bg_tasks.start()
    """

    def __init__(self):
        self.queue = queue.Queue()

    def push(self, task: Callable):
        """Add a task in the queue.

        :param task: Callable: Use a lambda like 'lambda: print("Hello,", "World!")'
        """
        self.queue.put(task)

    def start(self):
        """Start the execution of tasks in background."""
        worker = threading.Thread(
            target=QueueFakeAsync._runner, args=(self.queue,), daemon=True
        )
        worker.start()

    @staticmethod
    def _runner(queue, **kwargs):
        """Internal runner for thread tasks.

        Don't use it directly. Read doc of QueueFakeAsync before
        """
        while True:
            task = queue.get()
            time.sleep(2)
            task_is_callable = True
            while task_is_callable:
                task_is_callable = callable(task())
            queue.task_done()


@flask_app.route("/version", methods=["GET"])
def version():
    """Return the Lolapy version"""
    return json.dumps(APP_VERSION)


@flask_app.route("/ping", methods=["GET"])
def ping_lolapy():
    """Send boolean to validate that the backend is ready"""
    return Response(status=200)


@flask_app.route("/health", methods=["GET"])
def get_health():
    """Return the status of services in lolapy.

    It should return something True for all services.
    """
    health_status = Health().health_status
    return json.dumps(health_status)


@flask_app.route("/dataset/get", methods=["POST"])
def get_dataset_info():
    """Return data of a non-existing dataset.

    All data are fake and statics
    """
    json_data = request.get_json()
    dataset_hash = json_data["dataset"]  # don't check type here
    user_hash = json_data["user"]  # don't check type here

    # Generate fake data for a dataset
    fake_dataset: dataset_information.DataStatements = {
        "unique_actor_number": 666,
        "unique_verbs_number": 123,
        "statements_number": 123456890,
        "statements": fixtures.FakeStatements.data,
    }

    return json.dumps(fake_dataset)


def _put_nf_log_into_queue(bg_tasks: QueueFakeAsync, nf_log: dict):
    frontend_nf_logs_url = ""
    # TODO: Short fix waiting "workflow" remove logType and logEvent
    match nf_log["logType"]:
        case "workflow":
            match nf_log["logEvent"]:
                case "run":
                    frontend_nf_logs_url = (
                        f"/api/scenario/workflow/run/{nf_log['runHash']}"
                    )
                case "done":
                    frontend_nf_logs_url = (
                        f"/api/scenario/workflow/done/{nf_log['runHash']}"
                    )
                case "error":
                    frontend_nf_logs_url = (
                        f"/api/scenario/workflow/error/{nf_log['runHash']}"
                    )
        case "process":
            match nf_log["logEvent"]:
                case "run":
                    frontend_nf_logs_url = (
                        f"/api/scenario/process/run/{nf_log['runHash']}"
                    )
                case "done":
                    frontend_nf_logs_url = (
                        f"/api/scenario/process/done/{nf_log['runHash']}"
                    )
                case "error":
                    frontend_nf_logs_url = (
                        f"/api/scenario/process/error/{nf_log['runHash']}"
                    )
                case "submit":
                    frontend_nf_logs_url = (
                        f"/api/scenario/process/submit/{nf_log['runHash']}"
                    )
    bg_tasks.push(
        lambda: FrontendRequest.post(
            url=frontend_nf_logs_url,
            data=nf_log,
        )
    )


@flask_app.route("/scenario/execute", methods=["POST"])
def scenario_execute():
    """Start a nextflow scenario.

    If you want to change the type of logs, Success or Error, see below under
    the '###### START Async part' and comment/uncomment function calls
    """
    json_data = request.get_json()
    try:
        tag_hash = json_data["tag_hash"]
        run_hash = json_data["run_hash"]
        user_hash = json_data["user_hash"]
        dataset_hash = json_data["dataset_hash"]
        parameters = json_data["parameters"]
        algorithms = json_data["algorithms"]
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)

    def workflow_run(bg_tasks: QueueFakeAsync, run_hash):
        # Send log to inform the frontend that the scenario is started
        bg_tasks.push(
            lambda: FrontendRequest.get(f"/api/scenario/start/nextflow/{run_hash}")
        )
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.workflow_run().runHash(run_hash).log
        )
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.process_submit().runHash(run_hash).log
        )
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.process_run().runHash(run_hash).log
        )

    def workflow_success(bg_tasks: QueueFakeAsync, run_hash):
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.process_done().runHash(run_hash).log
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_submit()
            .processName("Second-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_run()
            .processName("Second-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_done()
            .processName("Second-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_submit()
            .processName("third-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_submit()
            .processName("fourth-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_run()
            .processName("fourth-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_run()
            .processName("third-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_done()
            .processName("fourth-Process")
            .runHash(run_hash)
            .log,
        )
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.workflow_done().runHash(run_hash).log
        )
        _put_nf_log_into_queue(
            bg_tasks,
            fixtures.FakeNextflowLog.process_done()
            .processName("third-Process")
            .runHash(run_hash)
            .log,
        )
        # Informs frontend that scenario complete without errors
        bg_tasks.push(
            lambda: FrontendRequest.get(
                url=f"/api/scenario/complete/nextflow/{run_hash}"
            )
        )

    def workflow_error(bg_tasks: QueueFakeAsync, run_hash):
        ## Failure
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.process_error().runHash(run_hash).log
        )
        _put_nf_log_into_queue(
            bg_tasks, fixtures.FakeNextflowLog.workflow_error().runHash(run_hash).log
        )
        # Inform frontend that scenario is in error state
        bg_tasks.push(
            lambda: FrontendRequest.get(url=f"/api/scenario/error/{run_hash}")
        )

    bg_tasks = QueueFakeAsync()
    ###### START Async part
    # Check permission of the user on the dataset
    bg_tasks.push(lambda: FrontendRequest.dataset_permission(user_hash, dataset_hash))
    # Comment or uncomment function calls below to change behavior
    workflow_run(bg_tasks, run_hash)
    workflow_success(bg_tasks, run_hash)
    # workflow_error(bg_tasks, run_hash)
    ##### END Async part
    bg_tasks.start()
    return Response(status=200)


@flask_app.route("/scenario/parameters", methods=["POST"])
def scenario_parameters():
    """Get parameters of a scenario.

    Take a json in entry:
    {
        "tag_hash": "string"
    }
    See swagger doc for more information
    """
    json_data = request.get_json()
    try:
        tag_hash = json_data["tag_hash"]  # hash unique of the tag
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)

    return json.dumps(fixtures.FakeScenarioInformation.data)


@flask_app.route("/scenario/tag/add", methods=["POST"])
def scenario_tag_add():
    """Install a new tag (version) of a scenario.

    ASYNC Request
    Take a json in entry:
    {
        "tag_hash": "Tdfgsdfjsfsf54ds6f4sd6f4sdf",
        "tag_name": "1.1.0",
        "scenario_url_repository": "https://gitlab.inria.fr/lola/scenarios/template-scenario"
    }
    """
    json_data = request.get_json()
    try:
        tag_hash = json_data["tag_hash"]  # hash unique of the tag
        _ = json_data["tag_name"]
        _ = json_data["scenario_url_repository"]
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)

    bg_tasks = QueueFakeAsync()
    #########
    # comment or uncomment following function calls
    #########
    # Success
    bg_tasks.push(lambda: FrontendRequest.get(url=f"/api/tag/{tag_hash}/complete"))
    # failure
    # bg_tasks.push(
    #     lambda: FrontendRequest.post(
    #         url="/api/tag/error", data={"tag": tag_hash, "error": "Test error message when adding Tag"}
    #     )
    # )

    bg_tasks.start()
    return Response(status=200)


@flask_app.route("/scenario/tag/remove", methods=["POST"])
def remove_scenario():
    """Remove a specific tag of a scenario.

    Take a json in entry
    {
        "tag_hash": "Tdfgsdfjsfsf54ds6f4sd6f4sdf"
    }
    """
    json_data = request.get_json()
    try:
        algorithm_hash = json_data["tag_hash"]  # hash unique of the tag
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)
    return Response(status=200)


@flask_app.route("/algorithm/add", methods=["POST"])
def algorithme_add():
    """Install a new version of algorithm.
    ASYNC Request
    """
    json_data = request.get_json()
    try:
        algorithm_hash = json_data["algorithm_hash"]  # hash unique of the tag
        algorithm_url_repository = json_data["algorithm_url_repository"]
        git_version = json_data["git_version"]
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)

    bg_tasks = QueueFakeAsync()
    #########
    # comment or uncomment following function calls
    #########
    # Success
    bg_tasks.push(
        lambda: FrontendRequest.get(url=f"/api/algorithm/{algorithm_hash}/complete")
    )
    # failure
    # bg_tasks.push(
    #     lambda: FrontendRequest.post(
    #         url="/api/algorithm/error",
    #         data={"algorithm_hash": "{algorithm_hash}", "error": "Test error message when adding algorithm"},
    #     )
    # )

    bg_tasks.start()
    return Response(status=200)


@flask_app.route("/algorithm/remove", methods=["POST"])
def algorithm_remove():
    json_data = request.get_json()
    try:
        algorithm_hash = json_data["algorithm_hash"]  # hash unique of the tag
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)
    return Response(status=200)


@flask_app.route("/algorithm/parameters", methods=["POST"])
def algorithm_parameters():
    """Return the parameters of an algorithm."""
    json_data = request.get_json()
    try:
        tag_hash = json_data["algorithm_hash"]  # hash unique of the tag
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)

    return json.dumps(fixtures.FakeAlgorithmParameter.data)


@flask_app.route("/dataset/remove", methods=["POST"])
def dataset_remove():
    return Response(status=200)


@flask_app.route("/scenario/prepare_results", methods=["POST"])
def scenario_prepare_results():
    """Prepare the archive result.

    After the success of a scenario, the frontend send a request to prepare the result files.
    The fake-lolapy, send a request to confirm the end of the preparation.
    A fake archive is then available with the resource /scenario/get_archive
    """
    json_data = request.get_json()
    try:
        run_hash: str = json_data["run_hash"]
        _ = json_data["tag_hash"]
        _ = json_data["workdir"]
    except (TypeError, KeyError) as e:
        logging.error(e)
        # Wrong formatted request
        return Response("Bad request error", status=400)

    # If success
    frontend_url = app_settings.frontend_api_prepare_result_complete_url
    # If fail
    # frontend_url = app_settings.frontend_api_prepare_result_error_url

    FrontendRequest.get(url=f"{frontend_url}/{run_hash}")
    return Response(status=200)


@flask_app.route("/scenario/get_archive", methods=["POST"])
def scenario_get_archive():
    """Return a fake file."""

    json_data = request.get_json()
    try:
        run_hash = json_data["run_hash"]
    except (TypeError, KeyError) as e:
        # Wrong formatted request
        logging.error(str(e))
        return Response("Bad request error", status=400)

    def gen_fake_archive() -> Path:
        fake_result = Path("/tmp/result.txt")
        fake_archve = Path("/tmp/result.zip")
        fake_result.write_text("This is a result!")
        with zipfile.ZipFile(fake_archve, "w", zipfile.ZIP_DEFLATED) as zf:
            filename_in_archive = str(fake_result).replace("/tmp", "")
            zf.write(fake_result, filename_in_archive)
        return fake_archve

    fake_archive = gen_fake_archive()
    return send_file(
        fake_archive, download_name="result.zip", mimetype="application/zip"
    )


@flask_app.route("/dataset/import", methods=["POST"])
def import_dataset():
    json_data = request.get_json()
    try:
        archive_path = json_data["dataset"]  # Path of the archive of the dataset
    except (TypeError, KeyError):
        ## Missing fields in the JSON
        message = f"Wrong request (?) in '{request.full_path}'"
        logging.error(message)
        return Response(status=400, response=message)

    installation = import_db.InstallDataset(archive_path)

    installation.dataset_hash = archive_path

    bg_tasks = QueueFakeAsync()
    #########
    # comment or uncomment following function calls
    #########
    # Should be set every time (or disable it for tests)
    bg_tasks.push(
        lambda: FrontendRequest.get(
            f"/api/dataset/{installation.dataset_hash}/start/{installation.import_id}"
        )
    )
    bg_tasks.push(
        lambda: FrontendRequest.get(
            f"/api/dataset/{installation.dataset_hash}/progress/20.0"
        )
    )
    bg_tasks.push(
        lambda: FrontendRequest.get(
            f"/api/dataset/{installation.dataset_hash}/progress/40.0"
        )
    )
    bg_tasks.push(
        lambda: FrontendRequest.get(
            f"/api/dataset/{installation.dataset_hash}/progress/60.0"
        )
    )
    bg_tasks.push(
        lambda: FrontendRequest.get(
            f"/api/dataset/{installation.dataset_hash}/progress/80.0"
        )
    )
    # Success
    bg_tasks.push(
        lambda: FrontendRequest.post(
            f"/api/dataset/{installation.dataset_hash}/complete/{installation.import_id}",
            data={"size": 123},
        )
    )
    # Failure
    # bg_tasks.push(lambda: FrontendRequest.get(url=f"/api/dataset/{installation.dataset_hash}/error/{installation.import_id}"))
    bg_tasks.start()
    #########
    return Response(status=200)


@flask_app.route("/server/usage", methods=["GET"])
def server_usage():
    """Return the usage of the server"""
    from lolapy.slurm.usage import ClusterUsage
    import random
    # usage/total
    cpu_possibility = [(2, 4), (10, 1000), (0, 50), (None, None)]
    # running/pending
    slurm_possibility = [(0, 50), (4, 1), (None, None), (1, 1000)]
    # usage/total in MB
    memory_possibility = [(25_000, 100_000), (None, None), (0, 100)]

    memory = random.choice(memory_possibility)
    slurm = random.choice(slurm_possibility)
    cpu = random.choice(cpu_possibility)

    return ClusterUsage(
            slurm_running_job=slurm[0],
            slurm_pending_job=slurm[1],
            cpu_usage=cpu[0],
            cpu_total=cpu[1],
            memory_usage=memory[0],
            memory_total=memory[1],
    ).json()


if __name__ == "__main__":
    app_settings = settings.get()
    app_settings.print()
    app_port = app_settings.lolapy_host_port
    logging.info(f"API READY FOR DEBUG ON PORT {app_port}")
    flask_app.run(host=app_settings.lolapy_host_ip, debug=True, port=app_port)
