#!/usr/bin/env python3

import pytest

from lolapy.scenario.scenario import CONST_SCENARIO, Scenario, ScenarioParameter, ScenarioRecipe, Readme
from lolapy.scenario import errors
from lolapy.tools import settings


def test_scenario_good_recipe(fixture_write_full_scenario):
    scenario_recipe = fixture_write_full_scenario / CONST_SCENARIO.scenario_recipe_file

    my_scenario_recipe: ScenarioRecipe = ScenarioRecipe.from_file(scenario_recipe=scenario_recipe)
    assert len(my_scenario_recipe.switchable_algorithms) == 2
    assert len(my_scenario_recipe.parameters) == 5

def test_scenario_all_files(fixture_scenario_hash, fixture_write_full_scenario, fixture_NEXTFLOW_SCENARIO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        my_scenario = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)

def test_scenario_recipe_no_name(fixture_scenario_hash, fixture_full_scenario_recipe_no_name, fixture_NEXTFLOW_SCENARIO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        with pytest.raises(errors.ScenarioRecipeMissingField):
            _ = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)

def test_scenario_recipe_missing_field(fixture_scenario_hash, fixture_full_scenario_recipe_missing_field, fixture_NEXTFLOW_SCENARIO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        with pytest.raises(errors.ScenarioRecipeMissingField):
            _ = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)

def test_scenario_parameter_wrong_choices():
    parameter = {
        "name": "rmse",
        "description": "The name of the indicator RMSE",
        "type": "choices",
        # "choices": ["1", "2", "3"],    # Missing choices field
        "default": "1",
    }

    with pytest.raises(errors.ScenarioParameterFieldWrongFormat):
        _ = ScenarioParameter.from_json(parameter)

def test_scenario_parameter_choices_list():
    parameter = {
        "name": "rmse",
        "description": "The name of the indicator RMSE",
        "type": "choices",
        "choices": "Hello, world!",    # choices must be a list[str]
        "default": "1",
    }
    with pytest.raises(errors.ScenarioParameterFieldWrongFormat):
        _ = ScenarioParameter.from_json(parameter)

def test_scenario_parameter_unknow_type():
    parameter = {
        "name": "rmse",
        "description": "The name of the indicator RMSE",
        "type": "Hello Type",
        "default": "1",
    }

    with pytest.raises(errors.ScenarioParameterFieldWrongFormat):
        _ = ScenarioParameter.from_json(parameter)


def test_scenario_parameter_missing_field():
    parameter = {
        "description": "The name of the indicator RMSE",
        "type": "int",
        "default": "1",
    }

    with pytest.raises(errors.ScenarioParameterMissingField):
        _ = ScenarioParameter.from_json(parameter)

@pytest.mark.usefixtures("fixture_scenario_missing_template")
def test_scenario_missing_template(fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        with pytest.raises(errors.ScenarioTemplateNotExist):
            _ = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)


def test_scenario_not_exists(fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    """Check that ScenarioNotExist raised if scenario does not exist"""
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        with pytest.raises(errors.ScenarioNotExist):
            _ = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)


def test_scenario_missing_main_nf(fixture_write_full_scenario, fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    # Remove main.nf
    scenario_path = fixture_write_full_scenario
    scenario_path.joinpath("main.nf").unlink()

    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        with pytest.raises(errors.ScenarioMissingFile) as e:
            _ = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)
            assert "main.nf" in str(e)

def test_scenario_missing_recipe(fixture_write_full_scenario, fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    # Remove main.nf
    scenario_path = fixture_write_full_scenario
    scenario_path.joinpath("params.json").unlink()

    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        with pytest.raises(errors.ScenarioMissingFile) as e:
            _ = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)
            assert "params.json" in str(e)

@pytest.mark.usefixtures("fixture_write_full_scenario")
def test_readme_search(fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        my_scenario = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)
        my_readme = Readme.search(path=my_scenario.scenario_path)
        assert my_readme.file_path
        my_readme.read()

def test_readme_no_readme(fixture_write_full_scenario, fixture_scenario_hash, fixture_NEXTFLOW_SCENARIO_DIR):
    # Remove readme file
    scenario_path = fixture_write_full_scenario
    scenario_path.joinpath("README.md").unlink()

    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        my_scenario = Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=False)
        my_readme = Readme.search(my_scenario.scenario_path)

        assert not my_readme.file_path
        assert "No Readme" in my_readme.read()
