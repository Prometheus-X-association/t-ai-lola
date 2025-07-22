#!/usr/bin/env python3

from flask import g
from flask.wrappers import Response
import json
from pathlib import Path

from pydantic import BaseModel

from lolapy.bin import app
from lolapy.blueprints import dataset_blueprint
from lolapy.blueprints.request_validation import validate_json
from lolapy.dataset import dataset_information
from lolapy.bin import async_tasks

class ImportDatasetJSON(BaseModel):
    dataset: Path

@dataset_blueprint.route("/import", methods=["POST"])
@validate_json(ImportDatasetJSON)
def import_dataset():
    """Import a dataset
    After checking the dataset file with xapi file (must exist and have valid json data),
    create a databases and populate it with the dataset given
    This request should come from the same server

    The function import an crypted and compressed file into a trax database.
    The archive contains a bordereau (json file with information on user/database) and a dataset in xapi format
    1. Check if the dataset contains xapi data. Do nothing if it's not the case
    2. decrypt dataset
    3. extract archive
    4. read bordereau
    5. Validate bordereau with frontend
    6. Integrate dataset in trax db
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
    """Return 5 samples tatements and databases stats

    After checking the user can read the database (call to frontend api to avoid someone catching request)
    the request return 5 statements and informations about the database
    """
    # retrieve data from the request
    data: GetDatasetJSON = g.request_data
    try:
        my_dataset = dataset_information.DatasetInformation(dataset_hash=data.dataset)
        info = my_dataset.get_dataset_info(user_hash=data.user)
    except Exception as error:
        return app.handle_api_errors(error)
    return json.dumps(info)


@dataset_blueprint.route("/remove", methods=["POST"])
@validate_json(GetDatasetJSON)
def dataset_remove():
    """Remove a Trax database in the MySQL server.

    The request must contain user's hash and database's hash.
    A verification is send to the api frontend to check if user have access to the database
    Curl example :
    `
    curl --location --request POST 'http://<server>:<port>/dataset/remove/' \
      --header 'Accept: application/json' \
      --header 'Content-Type: application/json' \
      --data-raw '{
        "user": "<hash_user>",
        "dataset": "<hash_dataset>"
    }'
    `
    """
    # retrieve data from the request
    data: GetDatasetJSON = g.request_data
    try:
        my_dataset = dataset_information.DatasetRemove(dataset_hash=data.dataset)
        my_dataset.remove(user_hash=data.user)
    except Exception as error:
        return app.handle_api_errors(error)
    return Response(status=200)
