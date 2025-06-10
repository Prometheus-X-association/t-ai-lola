#!/usr/bin/env python3

"""
This file allow context manager for fixtures.
For example, when invoquing 'from tests.tools.fixtures import *', you can then invoque fixtures in your tests
with:
    @pytest.mark.usefixtures("fixture_algo_recipe")
    def test_dockerimage_from_algo_recipe(fixture_algo_recipe):
        pass

Ensure that "fixture_algo_recipe" is the same than the:
  - function name in fixtures.py file
  - the usefixtures decorator invok the same function name
  - the parameter of the function to test uses the same name
It's speficity of pytests functions. It's ugly but it's how it works!
"""

import os

from tests.tools.fixtures import *
from tests.algorithm.fixtures import *
from tests.scenario.fixtures import *
from tests.blueprints.fixtures import *
from tests.nextflow.fixtures import *


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration test. Required the full stack (use in CI/CD) (deselect with '-m \"not integration\"')"
    )


def fixture_env_file():
    if "ENV_FILE" not in os.environ:
        os.environ["ENV_FILE"] = str(
            Path(".env.sample").resolve()
        )  # path to ROOT_DIR/.env.sample


fixture_env_file()
