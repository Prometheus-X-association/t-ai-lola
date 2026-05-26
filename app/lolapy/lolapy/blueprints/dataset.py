#!/usr/bin/env python3

from flask import g
from flask.wrappers import Response
import json
from pathlib import Path

from pydantic import BaseModel

from lolapy.errors import handle_api_errors
from lolapy.blueprints import dataset_blueprint
from lolapy.blueprints.request_validation import validate_json
from lolapy.dataset import dataset_information
from lolapy.bin import async_tasks

from flask import request
import logging


class ImportDatasetJSON(BaseModel):
    dataset: Path

@dataset_blueprint.route("/import", methods=["POST"])
@validate_json(ImportDatasetJSON)
def import_dataset():
    """Import a dataset stored in an encrypted acrchive
    This request should come from the same server

    The function import an crypted and compressed file into a specifi directory.
    The archive contains a bordereau (json file with information on user/database) and a dataset file
    1. decrypt dataset
    2. extract archive
    3. read bordereau
    4. validate bordereau with frontend
    5. copy dataset to lolapy_dataset_path/<dataset_hash>
    6. send progress update to frontend
    During all steps, the function must send information to the frontend to give the import status to the user
    """
    # retrieve data from the request
    data: ImportDatasetJSON = g.request_data

    async_tasks.import_dataset(data.dataset)
    return Response(status=200)


class GetDatasetJSON(BaseModel):
    user: str
    dataset: str


@dataset_blueprint.route("/get", methods=["POST"])
@validate_json(GetDatasetJSON)
def get_dataset_info():
    """Return basic information on a dataset

     Returned data include:
        - size_mb: size of dataset folder in MB
        - files: list of {name, size_bytes}

    Access is validated via frontend permission API.
    """
    # retrieve data from the request
    data: GetDatasetJSON = g.request_data
    try:
        my_dataset = dataset_information.DatasetInformation(dataset_hash=data.dataset)
        info = my_dataset.get_dataset_info(user_hash=data.user)
    except Exception as error:
        return handle_api_errors(error)
    return json.dumps(info)


@dataset_blueprint.route("/remove", methods=["POST"])
@validate_json(GetDatasetJSON)
def dataset_remove():
    """Remove a dataset from filesystem.

    The request must contain user's hash and database's hash.
    A verification is send to the api frontend to check if user have access to the database
    """
    # retrieve data from the request
    data: GetDatasetJSON = g.request_data
    try:
        my_dataset = dataset_information.DatasetRemove(dataset_hash=data.dataset)
        my_dataset.remove(user_hash=data.user)
    except Exception as error:
        return handle_api_errors(error)
    return Response(status=200)
