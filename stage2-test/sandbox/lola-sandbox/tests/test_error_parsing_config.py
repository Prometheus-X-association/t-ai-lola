#!/usr/bin/env python3

"""Module used to test the parsing of errors raised for config
parsing.
"""

import copy
import json
from pathlib import Path
from tempfile import mkstemp
import logging

import pydantic

from sandbox.error_parsing_config import SanitizePydanticError
from sandbox.run import ConfigJson

FULL_CONFIG = {
    "scenario_path": "/home/my-user/my_scenario/",
    "scenario_parameters": {"fcp": "fcp", "mae": "mae", "mse": "mse", "rmse": "rmse", "datasetName": "oulad"},
    "algorithms": [
        {
            "algorithm_path": "/home/my-user/algo/generate-model/",
            "nf_variable": "userModel",
            "parameters": {"knn_k": "40", "knn_k_min": "1"},
        },
        {"algorithm_path": "/home/my-user/algo/test-model", "nf_variable": "userTest", "parameters": {}},
    ],
}

MISSING_SCENARIO_PATH = copy.deepcopy(FULL_CONFIG)
MISSING_SCENARIO_PATH.pop("scenario_path")
MISSING_NF_VARIABLE_ALGO = copy.deepcopy(FULL_CONFIG)
MISSING_NF_VARIABLE_ALGO["algorithms"][0].pop("nf_variable")


def write_config_file(config_text: str) -> Path:
    """Write a fake config file.

    Args:
        config_text: str: The text to write in the file
    Returns:
        str: the name of the created file.
    """
    _, tmp_filename = mkstemp()
    with open(tmp_filename, "w") as file_handler:
        file_handler.write(config_text)
    logging.info(f"Write '{tmp_filename}' file for tests")
    return Path(tmp_filename)


def test_full_config():
    # Write full config file
    logging.info(FULL_CONFIG)
    config_file = write_config_file(json.dumps(FULL_CONFIG))
    config = ConfigJson(**json.loads(config_file.read_text()))
    assert config


def test_missing_scenario_path():
    try:
        config_file = write_config_file(json.dumps(MISSING_SCENARIO_PATH))
        with open(config_file) as cf:
            config = ConfigJson(**json.loads(cf.read()))
    except pydantic.ValidationError as e:
        sanitized_message = SanitizePydanticError(filename=Path(str(config_file)), pydantic_error=e).sanitize()
        sanitized_message.log()
        assert "require" in sanitized_message.sanitized_message


def test_missing_algo_param():
    try:
        config_file = write_config_file(json.dumps(MISSING_NF_VARIABLE_ALGO))
        with open(config_file) as cf:
            config = ConfigJson(**json.loads(cf.read()))
    except pydantic.ValidationError as e:
        sanitized_message = SanitizePydanticError(filename=Path(str(config_file)), pydantic_error=e).sanitize()
        sanitized_message.log()
        error = sanitized_message.sanitized_message
    assert "nested" in error
