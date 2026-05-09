#!/usr/bin/env python3

import pytest

from lolapy.algorithm.manage import InstallAlgorithm
from lolapy.algorithm import errors
from lolapy.tools import settings
from lolapy.tools.errors import SSHConnectionError


@pytest.mark.usefixtures("fixture_algo_dir_complete")
def test_remove_algorthm(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        settings.get().frontend_api_fake = True
        InstallAlgorithm.remove(algo_hash=fixture_algo_hash)


@pytest.mark.slow
def test_install_algorithm(fixture_NEXTFLOW_ALGO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        my_algo = InstallAlgorithm(
            repository_url="https://gitlab+deploy-token-444:Mrg9eZgrr3eBBV-yXxcC@gitlab.inria.fr/lola/algorithmes/svdpp",
            algo_hash="Ablipbloup",
            git_version="master",
        )
        with pytest.raises(SSHConnectionError) as _:
            # Catch error for SSHConnectionError because to pull docker image, the backend need to connect
            # to the cluster server. This should be removed later and execute on localhost
            my_algo.install()


@pytest.mark.usefixtures("fixture_algo_dir_complete")
def test_install_algorithm_not_empty(fixture_algo_hash, fixture_NEXTFLOW_ALGO_DIR):
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        my_algo = InstallAlgorithm(
            repository_url="https://gitlab+deploy-token-444:Mrg9eZgrr3eBBV-yXxcC@gitlab.inria.fr/lola/algorithmes/svdpp",
            algo_hash=fixture_algo_hash,
            git_version="master",
        )
        with pytest.raises(errors.InstallationDirNotEmpty) as _:
            # Catch error for SSHConnectionError because to pull docker image, the backend need to connect
            # to the cluster server. This should be removed later and execute on localhost
            my_algo.install()
