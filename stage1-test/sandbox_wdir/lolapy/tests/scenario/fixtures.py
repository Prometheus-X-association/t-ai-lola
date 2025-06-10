#!/usr/bin/env python3

import json
from uuid import uuid4

import pytest

from lolapy.scenario.scenario import CONST_SCENARIO

@pytest.fixture(scope="function")
def fixture_scenario_repository() -> str:
    return "https://gitlab+deploy-token-378:MGD-fdYz_2PXrcmkcEes@gitlab.inria.fr/lola/scenarios/recommendation_new_version"

@pytest.fixture(scope="session")
def fixture_param_json_txt():
    param_json = {
        "name": "First Technical Scenario",
        "description": "This scenario is used for recommendation... ",
        "output": ["output.json"],
        "docker_images": [
            {
                "name": "recom:latest",
                "url": "http://lola.lhs.loria.fr:4443/lola/recommandation:1.1.0_switchable",
            }
        ],
        "switchable_algorithms": [
            {
                "name": "Generate model",
                "description": "Algorithm used to generate a model. The algorithm must connect to a trax database to fetch data.\n The algorithm generate a model in output.",
                "template": "templates/user_model.nf.j2",
                "nf_variable": "userModel",
            },
            {
                "name": "Test data",
                "description": "Algorithm to test data on model generated before. The algorithm must take:\n input model\ninput file containing data (see Readme of this scenario)\nGenerate a list of data",
                "template": "templates/user_test.nf.j2",
                "nf_variable": "userTest",
            },
        ],
        "parameters": [
            {
                "name": "datasetName",
                "description": "The name of the dataset to be used with this scenario",
                "type": "string",
                "default": "oulad",
            },
            {
                "name": "rmse",
                "description": "The name of the indicator RMSE",
                "type": "choices",
                "choices": ["1", "2", "3"],
                "default": "1",
            },
            {
                "name": "fcp",
                "description": "The name of the indicator FCP",
                "type": "string",
                "default": "fcp",
            },
            {
                "name": "mae",
                "description": "The name of the indicator MAE",
                "type": "string",
                "default": "mae",
            },
            {
                "name": "mse",
                "description": "The name of the indicator MSE",
                "type": "string",
                "default": "mse",
            },
        ],
    }
    return param_json


@pytest.fixture(scope="session")
def fixture_template1_txt():
    """Add a 'cpu_limit' variable in the template"""

    template_txt = """#!/usr/bin/env nextflow

process userModel {
    container = "{{ docker_image }}"

    cpus {{ cpu_limit }}
    memory '500 MB'

    input:
        path input_file_1

    output:
        path output_file_1, emit: user_model
\"""
{{ command }}
\"""
}
"""
    return template_txt


@pytest.fixture(scope="session")
def fixture_template2_txt():
    template_txt = """#!/usr/bin/env nextflow

process userTest {
    container = "{{ docker_image }}"

    cpus 1
    memory '500 MB'

    input:
        path input_file_1
        path input_file_2

    output:
        path output_file_1, emit: user_predictions
\"""
{{ command }}
\"""
}
"""
    return template_txt


@pytest.fixture(scope="function")
def fixture_scenario_hash():
    return f"S{str(uuid4())}"


@pytest.fixture(scope="session")
def fixture_NEXTFLOW_SCENARIO_DIR(tmp_path_factory):
    """Generate a directory to store all scenario"""
    scenario_directory = tmp_path_factory.mktemp("scenario_path")
    return scenario_directory

@pytest.fixture(scope="function")
def fixture_create_scenario_dir(fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    """Generate dictory to store one scenario based on scenario_hash"""
    scenario_directory = fixture_NEXTFLOW_SCENARIO_DIR / fixture_scenario_hash
    scenario_directory.mkdir()
    return scenario_directory


@pytest.fixture(scope="function")
def fixture_write_full_scenario(
    fixture_create_scenario_dir,
    fixture_template1_txt,
    fixture_template2_txt,
    fixture_param_json_txt,
):
    scenario_directory = fixture_create_scenario_dir
    # Create templates directory
    template_dir = scenario_directory.joinpath("templates")
    template_dir.mkdir()
    # Write template file 2
    template_dir.joinpath("user_model.nf.j2").write_text(fixture_template1_txt)
    # Write template file 1
    template_dir.joinpath("user_test.nf.j2").write_text(fixture_template2_txt)
    # Write main.nf
    scenario_directory.joinpath(CONST_SCENARIO.nextflow_main).write_text("Hello, world!")
    # Write readme.md
    scenario_directory.joinpath("README.md").write_text("# This is a Readme file")
    # Write params.json file
    scenario_directory.joinpath(CONST_SCENARIO.scenario_recipe_file).write_text(json.dumps(fixture_param_json_txt))

    return scenario_directory

@pytest.fixture(scope="function")
def fixture_full_scenario_recipe_no_name(
    fixture_create_scenario_dir,
    fixture_template1_txt,
    fixture_template2_txt,
    fixture_param_json_txt: dict,
):
    """Remove the field 'name' in params.json"""

    scenario_directory = fixture_create_scenario_dir
    # Create templates directory
    template_dir = scenario_directory.joinpath("templates")
    template_dir.mkdir()
    # Write template file 2
    template_dir.joinpath("user_model.nf.j2").write_text(fixture_template1_txt)
    # Write template file 1
    template_dir.joinpath("user_test.nf.j2").write_text(fixture_template2_txt)
    # Write main.nf
    scenario_directory.joinpath(CONST_SCENARIO.nextflow_main).write_text("Hello, world!")
    # Write readme.md
    scenario_directory.joinpath("README.md").write_text("# This is a Readme file")

    # Write params.json file
    param_json_txt: dict = fixture_param_json_txt.copy()
    param_json_txt.pop("name")
    scenario_directory.joinpath(CONST_SCENARIO.scenario_recipe_file).write_text(json.dumps(param_json_txt))

    return scenario_directory

@pytest.fixture(scope="function")
def fixture_full_scenario_recipe_missing_field(
    fixture_create_scenario_dir,
    fixture_template1_txt,
    fixture_template2_txt,
    fixture_param_json_txt: dict,
):
    """Remove the field 'description' in params.json"""
    scenario_directory = fixture_create_scenario_dir
    # Create templates directory
    template_dir = scenario_directory.joinpath("templates")
    template_dir.mkdir()
    # Write template file 2
    template_dir.joinpath("user_model.nf.j2").write_text(fixture_template1_txt)
    # Write template file 1
    template_dir.joinpath("user_test.nf.j2").write_text(fixture_template2_txt)
    # Write main.nf
    scenario_directory.joinpath(CONST_SCENARIO.nextflow_main).write_text("Hello, world!")
    # Write readme.md
    scenario_directory.joinpath("README.md").write_text("# This is a Readme file")
    # Write params.json file
    param_json_txt: dict = fixture_param_json_txt.copy()
    param_json_txt.pop("description")
    scenario_directory.joinpath(CONST_SCENARIO.scenario_recipe_file).write_text(json.dumps(param_json_txt))

    return scenario_directory

@pytest.fixture(scope="function")
def fixture_scenario_missing_template(
        fixture_create_scenario_dir,
    fixture_template1_txt,
    fixture_param_json_txt: dict,
):
    """Remove a template file to check if the missing file is correctly catched"""
    scenario_directory = fixture_create_scenario_dir
    # Create templates directory
    template_dir = scenario_directory.joinpath("templates")
    template_dir.mkdir()
    # Write template file 1
    template_dir.joinpath("user_model.nf.j2").write_text(fixture_template1_txt)
    # Template 2 not written
    # template_dir.joinpath("user_test.nf.j2").write_text(fixture_template2_txt)
    # Write main.nf
    scenario_directory.joinpath(CONST_SCENARIO.nextflow_main).write_text("Hello, world!")
    # Write readme.md
    scenario_directory.joinpath("README.md").write_text("# This is a Readme file")
    # Write params.json file
    scenario_directory.joinpath(CONST_SCENARIO.scenario_recipe_file).write_text(json.dumps(fixture_param_json_txt))

    return scenario_directory

