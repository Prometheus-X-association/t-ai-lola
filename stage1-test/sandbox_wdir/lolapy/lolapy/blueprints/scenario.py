# /usr/bin/env python3

"""Blueprints for all routes related to /scenario"""

from flask import g, send_file
from flask.wrappers import Response
import json
from pydantic import BaseModel

from lolapy.bin import async_tasks
from lolapy.bin import app
from lolapy.blueprints import scenario_blueprint
from lolapy.blueprints.request_validation import validate_json
from lolapy.scenario import installation
from lolapy.nextflow import results
from lolapy.scenario.scenario import Readme, Scenario, ScenarioRecipe

class AlgorithmExecuteJson(BaseModel):
    """Json model for Algorithm to run.

    Used in /scenario/execute to validate the algorithm part of the Json model.
    """
    nf_variable: str
    algorithm_hash: str
    parameters: dict

class ScenarioExecuteJSON(BaseModel):
    """Json model for Scenario to run.

    Used in /scenario/execute to validate the request and the Json model."""
    tag_hash: str
    run_hash: str
    user_hash: str
    dataset_hash: str
    parameters: dict
    algorithms: list[AlgorithmExecuteJson]

@scenario_blueprint.route("/execute", methods=["POST"])
@validate_json(ScenarioExecuteJSON)
def start_scenario():
    """Start a nextflow scenario."""
    data: ScenarioExecuteJSON = g.request_data
    async_tasks.start_scenario(
        scenario_hash=data.tag_hash,
        run_hash=data.run_hash,
        user_hash=data.user_hash,
        dataset_hash=data.dataset_hash,
        parameters=data.parameters,
        algorithm=data.algorithms
    )
    return Response(status=200)


class ScenarioHashJSON(BaseModel):
    tag_hash: str


@scenario_blueprint.route("/parameters", methods=["POST"])
@validate_json(ScenarioHashJSON)
def scenario_parameters():
    """Send the list of parameters and the readme for a given scenario
    `
    curl --location --request POST 'http://<server>:<port>/scenario/parameters' \
      --header 'Accept: application/json' \
      --header 'Content-Type: application/json' \
      --data-raw '{
        "tag_hash": "<tag_hash>",
    }'
    `
    """
    data: ScenarioHashJSON = g.request_data
    try:
        my_scenario: Scenario = Scenario.from_hash(scenario_hash=data.tag_hash, check_exists=True)
        scenario_recipe: ScenarioRecipe = my_scenario.scenario_recipe # scenario_recipe cannot be None with check_exists to True
        ##  json() for a BaseModel return a string, so serialize and deserialize it to add the Readme.
        ##  Cannot use dict() (wich do deserialization) because it cannot deserialize PosixPath and ParameterAvailableTypes
        ##  correctly (this is a limitation of Pydantic. See https://github.com/pydantic/pydantic/issues/1409)
        ##  TODO: Write a proper serializer (recursively)
        json_response = json.loads(scenario_recipe.json())
        # Read and store Readme content in the json
        json_response["readme"] = Readme.search(my_scenario.scenario_path).read()

    except Exception as error:
        return app.handle_api_errors(error)
    return json.dumps(json_response)


class InstallScenarioJSON(BaseModel):
    tag_hash: str
    tag_name: str
    scenario_url_repository: str


@scenario_blueprint.route("/tag/add", methods=["POST"])
@validate_json(InstallScenarioJSON)
def install_scenario():
    """Install a scenario Tag."""
    data: InstallScenarioJSON = g.request_data
    async_tasks.install_scenario(
        scenario_hash=data.tag_hash, git_tag=data.tag_name, repository_url=data.scenario_url_repository
    )

    return Response(status=200)


@scenario_blueprint.route("/tag/remove", methods=["POST"])
@validate_json(ScenarioHashJSON)
def remove_scenario():
    data: ScenarioHashJSON = g.request_data
    try:
        installation.InstallScenario.remove(scenario_hash=data.tag_hash)
    except Exception as error:
        return app.handle_api_errors(error)

    return Response(status=200)


class RunHashJSON(BaseModel):
    """Store data for a Run."""

    run_hash: str


@scenario_blueprint.route("/get_archive", methods=["POST"])
@validate_json(RunHashJSON)
def scenario_get_archive():
    """Return an archive of the results in response.

    The archive results should be prepared before with /scenario/prepare_results
    After checking the file exits, return the zip file
    Curl example :
    ```
      curl --location --request POST 'http://<server>:<port>/scenario/get_archive' \
        --header 'Accept: application/json' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "run_hash":"Hash run"
        }'
    ```
    """
    data: RunHashJSON = g.request_data
    try:
        archive_path = results.PrepareResults(run_hash=data.run_hash, working_directories=None).prepare_send_archive()
        return send_file(archive_path, download_name="result.zip", mimetype="application/zip")
    # TODO: app.handle missing archive file for missing run_hash
    except Exception as error:
        return app.handle_api_errors(error)


class PrepareResultsJSON(BaseModel):
    """Data used in /scenario/prepare_results route"""

    workdir: list[str]
    run_hash: str
    tag_hash: str


@scenario_blueprint.route("/prepare_results", methods=["POST"])
@validate_json(PrepareResultsJSON)
def scenario_prepare_results():
    """Prepare archive to download results
    Curl example :
    `
      curl --location --request POST 'http://<server>:<port>/scenario/prepare_results' \
        --header 'Accept: application/json' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "workdir": ["/path_workdir_process_1", "/path_workdir_process_2", ...],
            "run_hash": "Hash run",
            "tag_hash": "hash of the scenario tag"
        }'
    `
    """
    # retrieve data from the request
    data: PrepareResultsJSON = g.request_data
    # Prepare results with in async way
    async_tasks.prepare_results(working_directories=data.workdir, run_hash=data.run_hash, tag_hash=data.tag_hash)
    return Response(status=200)
