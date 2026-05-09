#!/usr/bin/env python3

from __future__ import annotations
from pathlib import Path

from lolapy.scenario import errors
from lolapy.scenario import scenario

class ScenarioTemplate:
    """ScenarioTemplate store the text of a template

    Attributes:
        template: Text of the scenario template
        template_path: Path to the template file
    """

    def __init__(self, template: str, template_path):
        """Constructor of the ScenarioTemplate class.

        Args:
            template: Text of the template
            template_path: Path of the template file
        """
        self.template: str = template
        self.template_path: Path = template_path

    @classmethod
    def from_path(cls, template_file: str, scenario_path: Path) -> Self:
        """Create a ScenarioTemplate from the template_file sended by the frontend.

        Args:
            template_file: Name of the template file contained in the params.json of the scenario
            scenario_path: Full path of the scenario
        """
        template_path = scenario_path / template_file
        try:
            return cls(template=template_path.read_text(), template_path=template_path)
        except FileNotFoundError:
            raise errors.ScenarioTemplateNotExist(template_file=template_path, scenario=scenario_path)

    @classmethod
    def from_nf_variable(cls, scenario: scenario.Scenario, nf_variable: str) -> Self:
        """Return the template based on the nf_variable and the scenario_recipe.

        Args:
            scenario: Instance of Scenario to access all information
            nf_variable: identifier used in template AND algorithm for completion
        """
        if not scenario.scenario_recipe:
            # Used to help the linter. scenario_recipe must be not None
            raise NotImplementedError

        for switchable_algorithm in scenario.scenario_recipe.switchable_algorithms:
            if switchable_algorithm.nf_variable == nf_variable:
                return ScenarioTemplate.from_path(template_file=str(switchable_algorithm.template), scenario_path=scenario.scenario_path)
        # TODO: raise a correct error
        # "nf_variable 'blabla' does not match any switchable algorithm in the scenario 'scenario_name'"
