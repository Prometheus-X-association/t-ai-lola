#!#!/usr/bin/env python3

"""Module to test Algorithm module"""

from pathlib import Path

import pytest

from lolapy.algorithm import algorithm
from lolapy.algorithm.errors import (
    AlgorithmNotExist,
    AlgorithmParameterFieldWrongFormat,
    AlgorithmParameterMissingField,
    AlgorithmRecipeMissingField,
    InstallationMissingRequiredFile,
)
from lolapy.scenario.scenario import Readme
from lolapy.tools import settings


def test_wrong_dict_to_AlgorithmParameter(fixture_missing_variable_algo_parameter):
    with pytest.raises(AlgorithmParameterMissingField) as _:
        algorithm.AlgorithmParameter.from_json(fixture_missing_variable_algo_parameter)


def test_good_dict_to_AlgorithmParameter(fixture_algo_parameter):
    algorithm.AlgorithmParameter.from_json(fixture_algo_parameter)


def test_good_dict_to_AlgorithmFormat(fixture_data_algo_recipe):
    algorithm.AlgorithmRecipe.from_json(fixture_data_algo_recipe)


def test_AlgorithmParameter_to_json(fixture_algo_parameter):
    algorithm.AlgorithmParameter.from_json(fixture_algo_parameter).json()


def test_wrong_dict_to_AlgorithmRecipe(fixture_data_algo_recipe_wrong):
    with pytest.raises(AlgorithmRecipeMissingField) as _:
        algorithm.AlgorithmRecipe.from_json(fixture_data_algo_recipe_wrong)


def test_good_read_algo_recipe(fixture_algo_recipe_file):
    algorithm.AlgorithmRecipe.from_file(fixture_algo_recipe_file)


def test_bad_read_algo_recipe(fixture_algo_bad_recipe_file):
    with pytest.raises(AlgorithmRecipeMissingField) as _:
        algorithm.AlgorithmRecipe.from_file(fixture_algo_bad_recipe_file)


def test_AlgoParameter_wrong_field_type(fixture_algo_parameter_wrong_type):
    with pytest.raises(AlgorithmParameterFieldWrongFormat) as _:
        algorithm.AlgorithmParameter.from_json(fixture_algo_parameter_wrong_type)


@pytest.mark.usefixtures("fixture_algo_dir_complete")
def test_Algorithm_from_hash(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    """

    Call fixture_algo_dir_complete (but not use it) to force creating files
    """
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        my_algo: algorithm.Algorithm = algorithm.Algorithm.from_hash(fixture_algo_hash)
        my_readme = Readme.search(my_algo.algo_path).read()


@pytest.mark.usefixtures("fixture_algo_dir_complete")
def test_Algorithm_from_hash_not_exists(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    """

    Call fixture_algo_dir_complete (but not use it) to force creating files
    """
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = Path("THIS_DIR_NOT_EXIST")
        with pytest.raises(AlgorithmNotExist) as _:
            algorithm.Algorithm.from_hash(fixture_algo_hash)


def test_Algorithm_from_hash_no_recipe(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    """
    Call fixture_algo_dir_complete (but not use it) to force creating files
    """
    with settings.EditSettings():
        # Don't check if files exists (they are not)
        my_algo = algorithm.Algorithm.from_hash(fixture_algo_hash, check_exists=False)
        # Validate that a missing Readme returns the correct string
        assert "Missing Readme in the Algorithm", my_algo.get_readme()

        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR

        # Create an empty directory for the algorithm
        algo_path = fixture_NEXTFLOW_ALGO_DIR / fixture_algo_hash
        algo_path.mkdir()

        # Validate that missings files return the correct error when
        # check_exists is set to True (default value)
        with pytest.raises(InstallationMissingRequiredFile) as _:
            algorithm.Algorithm.from_hash(fixture_algo_hash)


def test_Algorithm_no_check(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    """Test if the check_exists=False works for Algorithm

    This test must fail in other case because there is no algo_recipe file
    """
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        algo_path = fixture_NEXTFLOW_ALGO_DIR / fixture_algo_hash
        algo_path.mkdir()
        algorithm.Algorithm.from_hash(algo_hash=fixture_algo_hash, check_exists=False)


def test_AlgorithmParameter_good_choices(fixture_algo_parameter_choices):
    """Good if choices is well formated"""
    algorithm.AlgorithmParameter.from_json(fixture_algo_parameter_choices)


def test_AlgorithmParameter_bad_choices(fixture_algo_parameter_choices):
    """Should fail is choices is not set and 'type' field is set to 'choices'"""
    fixture_algo_parameter_choices.pop("choices")
    with pytest.raises(AlgorithmParameterFieldWrongFormat) as _:
        algorithm.AlgorithmParameter.from_json(fixture_algo_parameter_choices)


def test_AlgorithmParameter_choices_none(fixture_algo_parameter_choices):
    """Should fail if choices is None"""
    fixture_algo_parameter_choices["choices"] = None
    with pytest.raises(AlgorithmParameterFieldWrongFormat) as _:
        algorithm.AlgorithmParameter.from_json(fixture_algo_parameter_choices)


def test_AlgorithmParameter_choices_dict(fixture_algo_parameter_choices):
    """Should fail if choices is a dictionnary and not a list[str]"""
    param = fixture_algo_parameter_choices.copy()
    param["choices"] = {"toto": "tutu"}
    with pytest.raises(AlgorithmParameterFieldWrongFormat) as _:
        algorithm.AlgorithmParameter.from_json(param)


@pytest.mark.usefixtures("fixture_algo_dir_complete")
def test_Algorithm_get_algo_recipe(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        algo = algorithm.Algorithm.from_hash(fixture_algo_hash)
        algo_recipe = algo.get_recipe()
        assert algo_recipe.name == "My awsome algorithm"
        assert algo_recipe.parameters[4].type == algorithm.OutputValue(
            output_value="output_file_1"
        )
        assert algo_recipe.parameters[3].type == algorithm.InputValue(
            input_value="input_file_2"
        )
