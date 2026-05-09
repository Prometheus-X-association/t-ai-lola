#!/usr/bin/env python3

import pytest

from lolapy.tools import settings
from lolapy.tools import docker
from lolapy.algorithm import algorithm
from lolapy.scenario import scenario


@pytest.mark.usefixtures("fixture_write_full_scenario")
def test_dockerimage_from_params_json(fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        my_scenario: scenario.Scenario = scenario.Scenario.from_hash(fixture_scenario_hash)
        images = my_scenario.scenario_recipe.docker_images
        assert images[0] == docker.DockerImage(
            name="recom:latest",
            url="http://lola.lhs.loria.fr:4443/lola/recommandation:1.1.0_switchable",
        )


@pytest.mark.usefixtures("fixture_algo_dir_complete")
def test_dockerimage_from_algo_recipe(fixture_NEXTFLOW_ALGO_DIR, fixture_algo_hash):
    with settings.EditSettings():
        settings.get().nextflow_algorithm_dir = fixture_NEXTFLOW_ALGO_DIR
        my_algorithm: algorithm.Algorithm = algorithm.Algorithm.from_hash(fixture_algo_hash)
        images = docker.GetImageList.from_algo_recipe(my_algorithm.algo_recipe)
        assert images[0] == docker.DockerImage(
            name=None, url="lola-localharbor.lhs.loria.fr/my_group/my_image:1.0.0"
        )


def test_PullDockerImages_sanitizeurl():
    def check_url(initial_url):
        with settings.EditSettings():
            settings.get().harbor_host = initial_url
            url = docker.SanitizeDockerUrl(
                "https://lola.lhs.loria.fr:4443/dir/image:tag"
            ).sanitize()
            assert url == f"{initial_url}/dir/image:tag"

    check_url("http://my_harbor_url.fr")
    check_url("http://my_harbor_url.fr:80")
    check_url("http://0.0.0.0")
    check_url("http://0.0.0.0:4443")
