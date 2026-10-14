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


class CreateDatasetJSON(BaseModel):
    dataset: str
    user: str
    contract: str
    resource: str
    purpose_id: str | None = None
    resource_id: str | None = None


@dataset_blueprint.route("/create", methods=["POST"])
@validate_json(CreateDatasetJSON)
def create_dataset():
    """Create and fetch a dataset from PDC."""
    data: CreateDatasetJSON = g.request_data
    async_tasks.fetch_and_import_dataset_pdc(
        dataset_hash=data.dataset,
        user_hash=data.user,
        contract=data.contract,
        resource=data.resource,
        purpose_id=data.purpose_id,
        resource_id=data.resource_id,
    )
    return Response(status=200)


class ImportDatasetJSON(BaseModel):
    dataset: str
    user: str | None = None
    contract: str | None = None
    resource: str | None = None
    purpose_id: str | None = None
    resource_id: str | None = None

@dataset_blueprint.route("/import", methods=["POST"])
@validate_json(ImportDatasetJSON)
def import_dataset():
    """Import a dataset either via PDC or local archive."""
    data: ImportDatasetJSON = g.request_data
    if data.contract and data.resource and data.user:
        async_tasks.fetch_and_import_dataset_pdc(
            dataset_hash=data.dataset,
            user_hash=data.user,
            contract=data.contract,
            resource=data.resource,
            purpose_id=data.purpose_id,
            resource_id=data.resource_id,
        )
    else:
        async_tasks.import_dataset(Path(data.dataset))
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
