#!/usr/bin/env python3

"""This module generate Nextflow Template for Switchable Algorithms.

For more information on switchable algorith, see algorithm.py

The Nextflow Template (NfT)

Nextflow templates are nextflow files that allow the use of algorithms. They are
stored in the scenario repository as jinja2 files
(https://jinja.palletsprojects.com). When running a scenario, the frontend sends
a json to the backend containing the information for each interchangeable
algorithm, more information in `prepare_run.py`. Each NfT must contain jinja2
`command` and `docker_image` fields. The `command` and `docker_image` are stored
in the `algo_recipe.json` file that comes with each algorithm. These fields are
replaced when the nextflow file is generated.

Generally, the `command` field also contains template fields in the form:
`my_script.py --input {{ input_file }} --ouput {{ output_file }} --param
{{ parameter_1 }}`. These fields can be parameters to be modified by the user
(`parameters` in the frontend response) or special variables in the script
(inputs/outputs)
"""

from abc import ABC, abstractmethod
from pathlib import Path
import json

from jinja2 import Template, StrictUndefined
import jinja2
from pydantic import BaseModel, ConfigDict

from lolapy.algorithm.algorithm import AlgorithmRecipe, InputValue, OutputValue
from lolapy.algorithm.errors import (
    AlgorithmCommandTemplateExpansion,
    AlgorithmNextflowTemplateExpansion,
)
from lolapy.scenario.template import ScenarioTemplate


class ExpandText(ABC):
    def __init__(self, template_txt: str, parameters: dict):
        self.template_txt = template_txt
        self.parameters = parameters
        self.template = self._gen_template()

    def _gen_template(self) -> Template:
        """Generate a Template object"""
        return Template(self.template_txt, undefined=StrictUndefined)

    @abstractmethod
    def expand(self) -> str:
        """Abstract method to expand"""


class ExpandCommand(ExpandText):
    """Expand text contained in 'command' field in the algo_recipe."""

    def __init__(self, command_txt: str, parameters: dict):
        """Constructor for [ExpandCommand].

        Inherit from [ExpandText]
        Args:
            command_txt: text of the command to expand
            parameters: dictionnary of parameters to use in the expansion
        """
        super().__init__(template_txt=command_txt, parameters=parameters)

    def expand(self) -> str:
        """Expand the text of the command.

        Raises:
            AlgorithmCommandTemplateExpansion: If there is a missing variable during expansion
        Returns:
            str: The rendered template
        """
        try:
            return self.template.render(**self.parameters)
        except jinja2.exceptions.UndefinedError as e:
            raise AlgorithmCommandTemplateExpansion(
                validation_error=e, command=self.template_txt
            )


class ExpandTemplate(ExpandText):
    def __init__(self, template_txt: str, parameters: dict, template_filename: str):
        self.template_filename = template_filename
        super().__init__(template_txt=template_txt, parameters=parameters)

    def expand(self) -> str:
        try:
            return self.template.render(**self.parameters)
        except jinja2.exceptions.UndefinedError as e:
            raise AlgorithmNextflowTemplateExpansion(
                validation_error=e, nf_template=self.template_filename
            )


class CreateNFscript(BaseModel):
    """Generate nf script based on the scenario template and the algo_params.json.

    Attributes:
        algo_recipe_data: AlgorithmRecipe structure
        scenario_template: ScenarioTemplate structure
        algorithm_parameters: Dictionnary of all data for the algorithm
        output_template: Path to the output template
    """

    algo_recipe_data: AlgorithmRecipe
    scenario_template: ScenarioTemplate
    algorithm_parameters: dict = None or {}
    output_template: Path

    model_config = ConfigDict(arbitrary_types_allowed=True)  # required to validate ScenarioTemplate

    def gen_template(self):
        """Generate and write the new nf file based of the template."""

        # Expand self.algorithm_params with input/output of the scenario
        for param in self.algo_recipe_data.parameters:
            match param.type:
                case InputValue():
                    self.algorithm_parameters[
                        param.variable_name
                    ] = f"${{{param.type.get_value()}}}"
                case OutputValue():
                    self.algorithm_parameters[
                        param.variable_name
                    ] = param.type.get_value()
                case _:
                    pass
        # Expand self.algorithm_params with docker url for template
        self.algorithm_parameters["docker_image"] = self.algo_recipe_data.harbor_url

        # Expand command line
        command: str = ExpandCommand(
            command_txt=self.algo_recipe_data.command,
            parameters=self.algorithm_parameters,
        ).expand()
        self.algorithm_parameters["command"] = command

        # Expand template
        rendered_template: str = ExpandTemplate(
            template_filename=self.scenario_template.template_path.name,
            parameters=self.algorithm_parameters,
            template_txt=self.scenario_template.template,
        ).expand()

        with open(self.output_template, "w") as f:
            f.write(rendered_template)
