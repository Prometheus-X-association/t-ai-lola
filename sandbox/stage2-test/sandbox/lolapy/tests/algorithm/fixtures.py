#!/usr/bin/env python3

import json
from uuid import uuid4
from _pytest.tmpdir import tmp_path_factory

import pytest


@pytest.fixture(scope="session")
def fixture_missing_variable_algo_parameter():
    param = {
        "name": "limit",
        "description": "limite number of element to compute ",
        "type": "int",
        "default": "5",
    }
    return param


@pytest.fixture(scope="session")
def fixture_algo_parameter():
    param = {
        "name": "limit",
        "description": "limite number of element to compute ",
        "type": "int",
        "default": "5",
        "editable": True,
        "variable_name": "toto",
    }
    return param


@pytest.fixture(scope="session")
def fixture_algo_parameter_choices():
    param = {
        "name": "list of option",
        "description": "Choose a good option",
        "variable_name": "options",
        "choices": ["1", "2"],
        "type": "choices",
        "editable": True,
    }
    return param


@pytest.fixture(scope="session")
def fixture_algo_parameter_wrong_type(fixture_algo_parameter):
    param = fixture_algo_parameter.copy()
    param["type"] = "NOT_GOOD_TYPE"
    return param


@pytest.fixture(scope="session")
def fixture_data_algo_recipe():
    param = {
        "name": "My awsome algorithm",
        "description": "This is an algorithm doing ...",
        "harbor_url": "https://lola.lhs.loria.fr:4443/my_group/my_image:1.0.0",
        "command": "cat {{ input_file }} {{ input_test_data }} | echo {{ limit }} {{ float_variable }} > {{ output_file }}",
        "parameters": [
            {
                "name": "limit",
                "description": "limite number of element to compute ",
                "variable_name": "limit",
                "type": "int",
                "default": "5",
                "editable": True,
            },
            {
                "name": "input_data_file",
                "description": "input data file",
                "variable_name": "input_file",
                "type": "input_file_1",
                "editable": False,
            },
            {
                "name": "My float",
                "description": "Float value to test",
                "variable_name": "float_variable",
                "type": "float",
                "default": "1.0",
                "editable": True,
            },
            {
                "name": "input test data",
                "description": "input data to test. Provided by the scenario",
                "variable_name": "input_test_data",
                "type": "input_file_2",
                "editable": False,
            },
            {
                "name": "output_data_file",
                "description": "output data file",
                "variable_name": "output_file",
                "type": "output_file_1",
                "editable": False,
            },
            {
                "name": "Label",
                "description": "Data label",
                "variable_name": "DATA_LABEL",
                "type": "string",
                "editable": True,
            },
        ],
    }
    return param


@pytest.fixture(scope="session")
def fixture_data_algo_recipe_wrong(fixture_data_algo_recipe):
    """Missing 'name' field"""
    param = fixture_data_algo_recipe.copy()
    param.pop("name")
    return param


@pytest.fixture(scope="session")
def fixture_algo_recipe_file(tmpdir_factory, fixture_data_algo_recipe):
    """Create a fake algo_recipe file with good date inside"""
    file_path = tmpdir_factory.mktemp("test_algo_recipe").join("algo_recipe.json")
    file_path.write(json.dumps(fixture_data_algo_recipe))
    return file_path


@pytest.fixture(scope="session")
def fixture_algo_bad_recipe_file(tmpdir_factory, fixture_data_algo_recipe_wrong):
    """Create a fake algo_recipe file with bad date inside"""
    file_path = tmpdir_factory.mktemp("test_algo_recipe").join("algo_recipe.json")
    file_path.write(json.dumps(fixture_data_algo_recipe_wrong))
    return file_path


@pytest.fixture(scope="function")
def fixture_algo_hash():
    return f"{str(uuid4())}"


@pytest.fixture(scope="session")
def fixture_NEXTFLOW_ALGO_DIR(tmp_path_factory):
    """Generate a directory to store all algorithm"""
    algorithm_directory = tmp_path_factory.mktemp("algorithm_path")
    return algorithm_directory


@pytest.fixture(scope="function")
def fixture_algo_dir_complete(
    fixture_NEXTFLOW_ALGO_DIR, fixture_algo_hash, fixture_data_algo_recipe
):
    """Generate a complete directory for a complete algorithm

    .
    └── algorithm_path
        ├── algo_recipe.json
        └── Readme.md
    """

    algo_path = fixture_NEXTFLOW_ALGO_DIR / fixture_algo_hash
    algo_path.mkdir()
    algo_recipe_path = algo_path / "algo_recipe.json"
    readme_path = algo_path / "Readme.md"
    algo_recipe_path.write_text(json.dumps(fixture_data_algo_recipe))
    readme_path.write_text("# Header 1 of the readme\n## Header2 \nSome text")


@pytest.fixture(scope="function")
def fixture_algo_userModel_complete(fixture_NEXTFLOW_ALGO_DIR, fixture_algo_hash):
    algo_recipe = {
        "name": "SVDpp",
        "description": "SVDpp algorithm to build model for recommandation",
        "command": "svdpp.py --p {{ n_factors }} {{ n_epochs }} 0 0 0 0 None None None None None None None None None None None --a {{ INPUT_DATA }} --m {{ OUTPUT_DATA }}",
        "harbor_url": "lola.lhs.loria.fr/lola/svdpp_recom:latest",
        "parameters": [
            {
                "name": "input data file",
                "description": "input data file",
                "variable_name": "INPUT_DATA",
                "type": "input_file_1",
                "editable": False,
            },
            {
                "name": "output data file",
                "description": "output data file",
                "variable_name": "OUTPUT_DATA",
                "type": "output_file_1",
                "editable": False,
            },
            {
                "name": "n factors",
                "description": "n factors",
                "variable_name": "n_factors",
                "type": "float",
                "editable": True,
                "default": "20.0",
            },
            {
                "name": "n epochs",
                "description": "n epochs",
                "variable_name": "n_epochs",
                "type": "int",
                "editable": True,
                "default": "20",
            },
        ],
    }
    algo_path = fixture_NEXTFLOW_ALGO_DIR / fixture_algo_hash
    algo_path.mkdir()
    algo_recipe_path = algo_path / "algo_recipe.json"
    readme_path = algo_path / "Readme.md"
    algo_recipe_path.write_text(json.dumps(algo_recipe))
    readme_path.write_text("# Header 1 of the readme\n## Header2 \nSome text")
    return fixture_algo_hash


@pytest.fixture(scope="function")
def fixture_algo_userTest_complete(fixture_NEXTFLOW_ALGO_DIR):
    algo_recipe = {
        "name": "Test-model",
        "description": "Test model and recommand stuff",
        "command": "model_test.py --m {{ INPUT_TRAINED_MODEL }} --t {{ INPUT_DATA_TEST }} --f {{ OUTPUT_PREDICTED_DATA }}",
        "harbor_url": "lola.lhs.loria.fr/lola/test_recom:latest",
        "parameters": [
            {
                "name": "input_trained_model",
                "description": "Path of the input trained model to use",
                "variable_name": "INPUT_TRAINED_MODEL",
                "type": "input_file_1",
                "editable": False,
            },
            {
                "name": "input_data_to_test",
                "description": "Path of the input data to test",
                "variable_name": "INPUT_DATA_TEST",
                "type": "input_file_2",
                "editable": False,
            },
            {
                "name": "output_data_predicted",
                "description": "Path to the output with data predicted",
                "variable_name": "OUTPUT_PREDICTED_DATA",
                "type": "output_file_1",
                "editable": False,
            },
        ],
    }

    algo_hash = str(uuid4())
    algo_path = fixture_NEXTFLOW_ALGO_DIR / algo_hash
    algo_path.mkdir()
    algo_recipe_path = algo_path / "algo_recipe.json"
    readme_path = algo_path / "Readme.md"
    algo_recipe_path.write_text(json.dumps(algo_recipe))
    readme_path.write_text("# Header 1 of the readme\n## Header2 \nSome text")
    return algo_hash
