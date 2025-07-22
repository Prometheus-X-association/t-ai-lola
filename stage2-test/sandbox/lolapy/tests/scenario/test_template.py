#!/usr/bin/env python3

import pytest

from lolapy.tools import settings
from lolapy.scenario import scenario
from lolapy.scenario import template

@pytest.mark.usefixtures("fixture_write_full_scenario")
def test_scenario_template_from_nf_variable(fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash):
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        my_scenario: scenario.Scenario = scenario.Scenario.from_hash(fixture_scenario_hash)
        nf_variable = my_scenario.scenario_recipe.switchable_algorithms[0].nf_variable
        template.ScenarioTemplate.from_nf_variable(nf_variable=nf_variable, scenario=my_scenario)

@pytest.mark.usefixtures("fixture_write_full_scenario")
def test_scenario_template_from_nf_variable_notimplemented(fixture_NEXTFLOW_SCENARIO_DIR, fixture_scenario_hash):
    """When searching for a ScenarioTemplate from nf_variable, if Scenario.scenario_recipe is None, should raise an error"""
    with settings.EditSettings():
        settings.get().nextflow_scenario_dir = fixture_NEXTFLOW_SCENARIO_DIR
        my_scenario: scenario.Scenario = scenario.Scenario.from_hash(fixture_scenario_hash)
        my_scenario.scenario_recipe = None
        with pytest.raises(NotImplementedError):
            template.ScenarioTemplate.from_nf_variable(nf_variable="fake_nf_variable", scenario=my_scenario)
