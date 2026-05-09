#!/usr/bin/env python3

from __future__ import annotations
from lolapy.algorithm import algorithm

from sandbox import run

class ManageAlgorithmParameters():
    """Manage the paremeters of Algorithm from Recipe to given parameters

    Attributes:
        recipe: AlgorithmRecipe: The recipe of the algorithm (extracted
            from the algo_recipe.json)
        algorithm: ConfigSwitchableAlgorithm: The configuration of the algorithm
            given by the user in the json-config
    """
    def __init__(self, recipe: algorithm.AlgorithmRecipe, algorithm: run.ConfigSwitchableAlgorithm):
        self.recipe = recipe
        self.algorithm = algorithm

    def get_default_parameters(self) -> dict[str, str | int]:
        """Extract default parameters from an algorithm recipe.

        If a parameter have no default, does not add it in the final dict
        Args:
            algorithm_recipe: Recipe of the algorithm
        Returns:
            dict[str, str]: The default parameters
        """
        default_parameters: dict[str, str | int] = {}
        for parameter in self.recipe.parameters:
            if parameter.default:
                default_parameters[parameter.variable_name] = parameter.default
        return default_parameters

    def get_parameters(self) -> dict[str, str | int]:
        """Generate the list of parameters to use for the sandbox algorithm.

        First extract default parameters from the Algorithm recipe, then add
        parameters got from the json config file (--json-config).

        Returns:
            dict[str, str]: The list of parameters of the current algorithm with default
        """
        default_parameters = self.get_default_parameters()
        if self.algorithm.parameters:
            return default_parameters | self.algorithm.parameters
        return default_parameters
