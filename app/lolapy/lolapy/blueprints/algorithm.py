#!/usr/bin/env python3

import json
from pathlib import Path

from flask import g
from flask.wrappers import Response
from pydantic import BaseModel
from lolapy.algorithm.algorithm import Algorithm

from lolapy.blueprints import algorithm_blueprint
from lolapy.blueprints.request_validation import validate_json
from lolapy.bin import async_tasks
from lolapy.errors import handle_api_errors
from lolapy.algorithm import manage
from lolapy.scenario.scenario import Readme


class AlgorithmRemoveJSON(BaseModel):
    algorithm_hash: str


@algorithm_blueprint.route("/remove", methods=["POST"])
@validate_json(AlgorithmRemoveJSON)
def algorithm_remove():
    """Remove an algorithm."""
    data: AlgorithmRemoveJSON = g.request_data
    try:
        manage.InstallAlgorithm.remove(data.algorithm_hash)
    except Exception as error:
        return handle_api_errors(error)


class AlgorithmAddJSON(BaseModel):
    algorithm_hash: str
    algorithm_url_repository: str
    git_version: str


@algorithm_blueprint.route("/add", methods=["POST"])
@validate_json(AlgorithmAddJSON)
def algorithme_add():
    """Request to install an algorithm."""
    data: AlgorithmAddJSON = g.request_data
    async_tasks.install_algorithm(algo_hash=data.algorithm_hash, git_version=data.git_version, url=data.algorithm_url_repository)
    return Response(status=200)


class AlgorithmImportJSON(BaseModel):
    dataset: Path


class AlgorithmParametersJSON(BaseModel):
    algorithm_hash: str


@algorithm_blueprint.route("/parameters", methods=["POST"])
@validate_json(AlgorithmParametersJSON)
def algorithm_parameters():
    """Return the Readme and parameters of an algorithm."""
    data: AlgorithmParametersJSON = g.request_data
    try:
        my_algo: Algorithm = Algorithm.from_hash(data.algorithm_hash)
        parameters = [json.loads(param.json()) for param in my_algo.algo_recipe.parameters]
        my_readme_txt = Readme.search(my_algo.algo_path).read()
        json_reponse = {"parameters": parameters, "readme": my_readme_txt}
    except Exception as error:
        return handle_api_errors(error)
    return json.dumps(json_reponse)
