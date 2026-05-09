#!/usr/bin/env python3

import pytest
from uuid import uuid4

@pytest.fixture(scope="function")
def fixture_fake_nf_executable(tmp_path_factory):
    "Generate a script bash to execute that return 0"
    stored_executable = tmp_path_factory.mktemp("nextflow_dir")
    fake_nf_exe = stored_executable / "fake_nf"

    fake_nf_content = """#!/bin/bash
# This is a fake nf-script
exit 0"""
    fake_nf_exe.write_text(fake_nf_content)
    fake_nf_exe.chmod(0o700)
    return fake_nf_exe

@pytest.fixture(scope="function")
def fixture_fake_nf_executable_return_1(tmp_path_factory):
    "Generate a script bash to execute that return 1 -> means error on program"
    stored_executable = tmp_path_factory.mktemp("nextflow_dir")
    fake_nf_exe = stored_executable / "fake_nf"

    fake_nf_content = """#!/bin/bash
# This is a fake nf-script
exit 1"""
    fake_nf_exe.write_text(fake_nf_content)
    fake_nf_exe.chmod(0o700)
    return fake_nf_exe

@pytest.fixture(scope="function")
def fixture_nf_work_dir(tmp_path_factory):
    "Generate a folder wich will store nextflow files"
    nf_workdir = tmp_path_factory.mktemp("nextflow_workdir")

    return nf_workdir

@pytest.fixture(scope="function")
@pytest.mark.slow
def fixture_install_scenario(
    fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash, fixture_scenario_repository
):
    from lolapy.tools import settings
    from lolapy.scenario import installation

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
    return scenario_installation.scenario.scenario_path

@pytest.fixture(scope="function")
def fixture_run_hash():
    return f"R{str(uuid4())}"

