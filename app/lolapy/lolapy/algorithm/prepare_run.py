#!/usr/bin/env python3

"""Prepare algorithms for the run of a scenario.

Before running a scenario, make sure to prepare the algorithms chosen by the user.
In the request to run a scenario, there is a list of 'algorithms' as follows:
  "algorithms": [
    {
      "algorithm_hash": "string",
      "nf_variable": "userModel",
      "parameter": {
        "param_1": 5,
        "...": "..."
      }
    }
  ]
'algorithm_hash': The unique hash of the scenario. With the AlgorithmInformation object, we can find the path to the location of the algorithm.
nf_variable': Variable used at scenario launch to specify where to look for the nextflow file. When launching a scenario with nextflow, you will get this command: `nextflow run my_scenario --userModel PathNFfile`
parameter': List of parameters for the algorithm. Will be used in the command line for nextflow

Each element of the 'algorithms' list corresponds to an algorithm that needs to be "prepared".
The preparation consists in generating a nextflow file (.nf) which will be used by the scenario to launch the algorithm.

The [[extend_template]] module generates Nextflow files for each algorithm and returns a dictionary of parameters
which will be used when the scenario is launched
"""

from __future__ import annotations
from pathlib import Path

from lolapy.algorithm.algorithm import Algorithm, AlgorithmRecipe
from lolapy.algorithm.extend_template import CreateNFscript
from lolapy.blueprints.scenario import AlgorithmExecuteJson
from lolapy.scenario.scenario import Scenario
from lolapy.scenario.template import ScenarioTemplate
import logging


class PrepareAlgorithms:
    @staticmethod
    def from_dict(algorithms: list[AlgorithmExecuteJson], my_scenario: Scenario, run_workdir: Path):
        """Generate nextflow template for each `algorithms`.

        Args:
            algorithms: list[AlgorithmExecuteJson]: list of algorithms used in the
                scenario.
            my_scenario: Scenario: Scenario object.
            run_workdir: Path: Full Path of the directory where to store the files
                generated during a scenario run.
        """
        all_parameters = {}  # Store all parameters used when running nextflow
        logging.info(algorithms)
        # Generate template for all algorithm
        for algorithm in algorithms:
            template = ScenarioTemplate.from_nf_variable(nf_variable=algorithm.nf_variable, scenario=my_scenario)
            output_nf_script = run_workdir / f"{algorithm.algorithm_hash}"
            logging.debug(f"output:{output_nf_script}")
            current_algorithm: AlgorithmRecipe = Algorithm.from_hash(
                algorithm.algorithm_hash
            ).algo_recipe
            algorithm_to_render: CreateNFscript = CreateNFscript(
                algo_recipe_data=current_algorithm,
                algorithm_parameters=algorithm.parameters,
                output_template=output_nf_script,
                scenario_template=template,
            )
            algorithm_to_render.gen_template()
            all_parameters[algorithm.nf_variable] = str(output_nf_script)
        # Add parameters in the list of parameters to nextflow
        return all_parameters
