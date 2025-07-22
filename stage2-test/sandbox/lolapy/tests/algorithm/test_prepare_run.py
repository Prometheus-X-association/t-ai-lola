#!/usr/bin/env python3

import pytest

from lolapy.algorithm.prepare_run import PrepareAlgorithms
from lolapy.blueprints.scenario import ScenarioExecuteJSON
from lolapy.scenario.run_scenario import SetupRunWorkdir
from lolapy.scenario import scenario
from lolapy.tools import settings


def test_prepare_algorithm(
    fixture_scenario_hash,
    fixture_write_full_scenario,
    fixture_NEXTFLOW_SCENARIO_DIR,
    fixture_NEXTFLOW_ALGO_DIR,
    fixture_algo_userModel_complete,
    fixture_algo_userTest_complete,
        fixture_nf_work_dir,
        fixture_run_hash
):
    json_data = {
        "tag_hash": "Tba833f9dc0c5f70de2f3ab058e6eda886365d010",
        "run_hash": f"{fixture_run_hash}",
        "user_hash": "Uecf3dc9d5768b3ccf86455756a0772d11c66b348",
        "dataset_hash": "D1c9952cd29b1e2f7f7b9935d83fe414909001b4e",
        "parameters": {
            "fcp": "fcp",
            "mae": "mae",
            "mse": "mse",
            "rmse": "rmse",
            "datasetName": "oulad",
        },
        "algorithms": [
            {
                "algorithm_hash": fixture_algo_userModel_complete,
                "nf_variable": "userModel",
                "parameters": {"n_factors": "40", "n_epochs": "1", "cpu_limit": "2"},
            },
            {
                "algorithm_hash": fixture_algo_userTest_complete,
                "nf_variable": "userTest",
                "parameters": [],
            },
        ],
    }
    json_data = ScenarioExecuteJSON(**json_data)
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        settings.get().nextflow_workdir = fixture_nf_work_dir
        run_workdir = SetupRunWorkdir.from_id(json_data.run_hash)
        run_workdir.mkdir()
        my_scenario = scenario.Scenario.from_hash(fixture_scenario_hash)
        PrepareAlgorithms.from_dict(
            algorithms=json_data.algorithms,
            my_scenario=my_scenario,
            run_workdir=run_workdir.run_workdir
        )
