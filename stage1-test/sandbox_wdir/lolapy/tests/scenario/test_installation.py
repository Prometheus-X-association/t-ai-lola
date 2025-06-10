#!/usr/bin/env python3

import pytest

from lolapy.tools import settings
from lolapy.scenario import installation
from lolapy.scenario import errors

@pytest.mark.slow
def test_installation_scenario(
    fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash, fixture_scenario_repository
):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        settings.get().harbor_pull_images = False  # Disable image pulling to avoid errors with missing instance
        settings.get().frontend_api_fake = True  # Disable connection to the frontend used after deletion
        scenario_installation = installation.InstallScenario.build(
            hash=fixture_scenario_hash,
            repository_url=fixture_scenario_repository,
            tag_name="master",
        )
        scenario_installation.install()

@pytest.mark.usefixtures("fixture_write_full_scenario")
def test_installation_not_empty(fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash, fixture_scenario_repository):
    """Use fixtures to create a real scenario and try to install a new one inside"""
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        settings.get().frontend_api_fake = True  # Disable connection to the frontend used after deletion

        with pytest.raises(errors.InstallationDirNotEmpty):
            scenario_installation = installation.InstallScenario.build(
                hash=fixture_scenario_hash,
                repository_url=fixture_scenario_repository,
                tag_name="master",
            )
            scenario_installation.install()

@pytest.mark.usefixtures("fixture_write_full_scenario")
def test_remove_scenario(fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        settings.get().frontend_api_fake = True  # Disable connection to the frontend
        installation.InstallScenario.remove(scenario_hash=fixture_scenario_hash)

def test_remove_scenario_does_not_exist(fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        settings.get().frontend_api_fake = True  # Disable connection to the frontend used after deletion
        with pytest.raises(errors.ScenarioNotExist):
            installation.InstallScenario.remove(scenario_hash=fixture_scenario_hash)
