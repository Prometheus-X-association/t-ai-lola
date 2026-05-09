#!/usr/bin/env python3

from pathlib import Path
import uuid

import pytest

from lolapy.nextflow import nextflow
from lolapy.nextflow import errors
from lolapy.scenario.run_scenario import SetupRunWorkdir
from lolapy.tools import settings
from lolapy.scenario import scenario

def test_nextflowcheck_check(fixture_fake_nf_executable):
    with settings.EditSettings():
        settings.get().nextflow_executable = Path(fixture_fake_nf_executable)
        settings.get().nextflow_workdir = Path("/tmp")
        fake_run_id = str(uuid.uuid4())
        my_nf_checker = nextflow.NextflowCheckEnv.from_env(run_id=fake_run_id, run_workdir=settings.get().nextflow_workdir)
        my_nf_checker.check()

def test_nextflowcheck_nf_executable_permission_denied(fixture_fake_nf_executable):
    fixture_fake_nf_executable.chmod(0o600) # remove permission
    with settings.EditSettings():
        settings.get().nextflow_executable = Path(fixture_fake_nf_executable)
        settings.get().nextflow_workdir = Path("/tmp")
        fake_run_id = str(uuid.uuid4())
        my_nf_checker = nextflow.NextflowCheckEnv.from_env(run_id=fake_run_id, run_workdir=settings.get().nextflow_workdir)
        with pytest.raises(errors.NextflowExecutableError):
            my_nf_checker.check()

def test_nextflowcheck_nf_executable_file_not_found():
    with settings.EditSettings():
        settings.get().nextflow_executable = Path("/blabla/fake-executable")
        settings.get().nextflow_workdir = Path("/tmp")
        fake_run_id = str(uuid.uuid4())
        my_nf_checker = nextflow.NextflowCheckEnv.from_env(run_id=fake_run_id, run_workdir=settings.get().nextflow_workdir)
        with pytest.raises(errors.NextflowExecutableError):
            my_nf_checker.check()

def test_nextflowcheck_nf_executable_return_error(fixture_fake_nf_executable_return_1):
    with settings.EditSettings():
        settings.get().nextflow_executable = Path(fixture_fake_nf_executable_return_1)
        settings.get().nextflow_workdir = Path("/tmp")
        fake_run_id = str(uuid.uuid4())
        my_nf_checker = nextflow.NextflowCheckEnv.from_env(run_id=fake_run_id, run_workdir=settings.get().nextflow_workdir)
        with pytest.raises(errors.NextflowExecutableError):
            my_nf_checker.check()

def test_nextflowcheck_gen_docker_config(fixture_fake_nf_executable, fixture_nf_work_dir):
    with settings.EditSettings():
        settings.get().nextflow_executable = Path(fixture_fake_nf_executable)
        settings.get().nextflow_workdir = Path(fixture_nf_work_dir)
        fake_run_id = str(uuid.uuid4())
        run_workdir = SetupRunWorkdir.from_id(fake_run_id)
        run_workdir.mkdir()
        my_nf_checker = nextflow.NextflowCheckEnv.from_env(
            run_id=fake_run_id, run_workdir=run_workdir.run_workdir
        )
        my_nf_checker.check()

@pytest.mark.usefixtures("fixture_install_scenario")
def test_nextflow_run(fixture_nf_work_dir, fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        settings.get().nextflow_executable = Path("/usr/local/bin/nextflow")
        settings.get().nextflow_workdir = fixture_nf_work_dir

        fake_run_id = str(uuid.uuid4())
        run_workdir = SetupRunWorkdir.from_id(fake_run_id)
        run_workdir.mkdir()

        my_scenario = scenario.Scenario.from_hash(scenario_hash=fixture_scenario_hash, check_exists=True)
        my_nextflow_checker = nextflow.NextflowCheckEnv.from_env(run_id=fake_run_id, run_workdir=run_workdir.run_workdir)
        my_nextflow_checker.check()
        my_nf_run = nextflow.RunNextflow(
            nextflow_env=my_nextflow_checker,
            scenario=my_scenario,
            parameters={"lrsHost": "http://garimpeiro12.loria.fr", "lrsPort": 81},
            background=False,
        )
        my_nf_run.run()
