#!/usr/bin/env python3

from pathlib import Path

import pytest

@pytest.fixture()
def fixture_GitRepo_clone_empty_dir(tmp_path):
    """Create a temporary directory without file to test if git clone success"""
    dir_path = tmp_path / "git_clone_empty"
    dir_path.mkdir()
    return dir_path


@pytest.fixture()
def fixture_GitRepo_clone_create_dir(fixture_GitRepo_clone_empty_dir):
    return fixture_GitRepo_clone_empty_dir / "non_created_dir"


@pytest.fixture()
def fixture_GitRepo_clone_full_dir(tmp_path):
    """Create a temporary directory with 1 file to test if git clone fails"""
    dir_path = tmp_path / "test_non_empty"
    dir_path.mkdir()
    filename = dir_path / Path("foofile.txt")
    filename.write_text("Hello, World!")
    return dir_path


@pytest.fixture()
def fixture_GitRepo_clone_dest_no_permission(fixture_GitRepo_clone_empty_dir):
    """Create a temp dir based on fixture_GitRepo_clone_empty_dir and change permission to disallow
    writing in the directory.
    """
    old_stat = fixture_GitRepo_clone_empty_dir.stat().st_mode
    fixture_GitRepo_clone_empty_dir.chmod(0o555)
    # Here use yield to return the Path of the file. And after treatment, come back
    # here to change the permission.
    # Used to avoid permission denied where deleting the file
    yield fixture_GitRepo_clone_empty_dir / "test"
    fixture_GitRepo_clone_empty_dir.chmod(old_stat)


@pytest.fixture()
def fixture_env_file_complete(tmp_path_factory):
    complete_env_file = """FRONTEND_API_IP=127.0.0.1
FRONTEND_API_PORT=80
FRONTEND_API_LOG_URL=/api/lolapi/log
FRONTEND_API_FAKE=False
FRONTEND_API_PREPARE_RESULT_COMPLETE_URL=/api/scenario/results/complete
FRONTEND_API_PREPARE_RESULT_ERROR_URL=/api/scenario/results/error
LOLAPY_HOST_PORT=5000
LOLAPY_HOST_IP=0.0.0.0
LOLAPY_ASYNC_QUEUE_FILE=/tmp/huey_queue.sqlite
LOLAPY_LOG_FILE=/tmp/lolapy.log
LOLAPY_LOG_LEVEL=DEBUG
LOLAPY_DATASET_DECRYPT_KEY=path_to_my_key
LOLAPY_DATASET_PATH=/tmp/sftp_path/
LOLAPY_DISABLE_FRONTEND_LOGS=false
SQL_HOST_IP=0.0.0.0
SQL_HOST_PORT=3307
SQL_ROOT_USER=root
SQL_ROOT_PASSWORD=mil8puk7
NEXTFLOW_EXECUTABLE=/usr/local/bin/nextflow
NEXTFLOW_LOG_LISTENER_HOST=http://${LOLAPY_HOST_IP}:${LOLAPY_HOST_PORT}/nf_logs
NEXTFLOW_WORKDIR=/home/lolauser/nf-workdir
NEXTFLOW_SCENARIO_DIR=/home/lolauser/scenario
NEXTFLOW_ALGORITHM_DIR=/home/lolauser/algorithm
HARBOR_HOST=lola-localharbor.lhs.loria.fr
HARBOR_USER=blabla
HARBOR_PASSWORD=blabla
HARBOR_PULL_IMAGES=true
CLUSTER_HOST="bouh"
CLUSTER_TYPE=local
K8S_PVC_NAME=lola-pvc
K8S_MOUNT_PATH=/home/lolauser/nf-workdir
K8S_NAMESPACE=default
K8S_SERVICE_ACCOUNT=default
HTTP_PROXY=this_is_a_fake_proxy
    """
    directory = tmp_path_factory.mktemp("tmp_dir")
    env_file: Path = directory / "env_file"
    env_file.write_text(complete_env_file)
    return env_file


@pytest.fixture()
def fixture_env_file_missing_variable(tmp_path_factory):
    complete_env_file = """FRONTEND_API_IP=127.0.0.1
FRONTEND_API_PORT=80
FRONTEND_API_LOG_URL=/api/lolapi/log
FRONTEND_API_PREPARE_RESULT_COMPLETE_URL=/api/scenario/results/complete
FRONTEND_API_PREPARE_RESULT_ERROR_URL=/api/scenario/results/error
LOLAPY_HOST_PORT=5000
LOLAPY_ASYNC_QUEUE_FILE=/tmp/huey_queue.sqlite
LOLAPY_LOG_FILE=/tmp/lolapy.log
LOLAPY_LOG_LEVEL=DEBUG
LOLAPY_DATASET_DECRYPT_KEY=path_to_my_key
LOLAPY_DATASET_PATH=/tmp/sftp_path/
LOLAPY_DISABLE_FRONTEND_LOGS=false
SQL_HOST_IP=0.0.0.0
SQL_HOST_PORT=3307
SQL_ROOT_USER=root
SQL_ROOT_PASSWORD=mil8puk7
NEXTFLOW_LOG_LISTENER_HOST=http://${LOLAPY_HOST_IP}:${LOLAPY_HOST_PORT}/nf_logs
NEXTFLOW_WORKDIR=/home/lolauser/nf-workdir
NEXTFLOW_SCENARIO_DIR=/home/lolauser/scenario
HTTP_PROXY=this_is_a_fake_proxy
    """
    directory = tmp_path_factory.mktemp("tmp_dir")
    env_file: Path = directory / "env_file"
    env_file.write_text(complete_env_file)
    return env_file
