#!/usr/bin/env python3

from pathlib import Path

import pytest

from lolapy.algorithm import extend_template
from lolapy.algorithm.algorithm import AlgorithmRecipe
from lolapy.algorithm.errors import (
    AlgorithmNextflowTemplateExpansion,
    AlgorithmCommandTemplateExpansion,
)
from lolapy.scenario.template import ScenarioTemplate


def test_gen_template(fixture_write_full_scenario, fixture_algo_recipe_file):

    scenario_dir = fixture_write_full_scenario
    template_file_1 = scenario_dir / "templates" / "user_model.nf.j2"
    scenario_template = ScenarioTemplate.from_path(
        scenario_path=scenario_dir, template_file=template_file_1
    )

    algorithm_recipe = AlgorithmRecipe.from_file(fixture_algo_recipe_file)

    extend_template.CreateNFscript(
        algo_recipe_data=algorithm_recipe,
        algorithm_parameters={"limit": 5, "float_variable": 5.4, "cpu_limit": 1},
        output_template=Path("/tmp/toto.nf"),
        scenario_template=scenario_template,
    ).gen_template()


def test_gen_template_missing_command_variable(
    fixture_write_full_scenario, fixture_algo_recipe_file
):
    scenario_dir = fixture_write_full_scenario
    template_file_1 = scenario_dir / "templates" / "user_model.nf.j2"
    scenario_template = ScenarioTemplate.from_path(
        scenario_path=scenario_dir, template_file=template_file_1
    )

    algorithm_recipe = AlgorithmRecipe.from_file(fixture_algo_recipe_file)

    nf_script = extend_template.CreateNFscript(
        algo_recipe_data=algorithm_recipe,
        algorithm_parameters={},
        output_template=Path("/tmp/toto2.nf"),
        scenario_template=scenario_template,
    )
    with (pytest.raises(AlgorithmCommandTemplateExpansion) as _):
        nf_script.gen_template()


def test_gen_template_missing_template_variable(
    fixture_write_full_scenario, fixture_algo_recipe_file
):
    scenario_dir = fixture_write_full_scenario
    template_file_1 = scenario_dir / "templates" / "user_model.nf.j2"
    scenario_template = ScenarioTemplate.from_path(
        scenario_path=scenario_dir, template_file=template_file_1
    )

    algorithm_recipe = AlgorithmRecipe.from_file(fixture_algo_recipe_file)

    nf_script = extend_template.CreateNFscript(
        algo_recipe_data=algorithm_recipe,
        algorithm_parameters={"limit": 5, "float_variable": 5.4},
        output_template=Path("/tmp/toto2.nf"),
        scenario_template=scenario_template,
    )
    with (pytest.raises(AlgorithmNextflowTemplateExpansion) as _):
        nf_script.gen_template()


def test_gen_template_abstractmethod():
    with pytest.raises(TypeError) as _:
        extend_template.ExpandText(template_txt="", parameters={})
