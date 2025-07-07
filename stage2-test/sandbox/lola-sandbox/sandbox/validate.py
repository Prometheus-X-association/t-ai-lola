#!/usr/bin/env python3

from __future__ import annotations
from abc import ABC, abstractmethod
import argparse
import logging
import sys
from pathlib import Path

from lolapy.tools import settings
from lolapy.scenario import scenario
from lolapy.algorithm import algorithm
from lolapy.errors import LolapyGlobalError

from sandbox import app

class ValidateObject(ABC):
    @classmethod
    @abstractmethod
    def from_args(cls, args):
        pass

    @abstractmethod
    def validate(self):
        pass

class ValidateScenario(ValidateObject):
    def __init__(self, scenario_path: Path):
        self.scenario_path = scenario_path

    @classmethod
    def from_args(cls, args) -> Self:
        return cls(scenario_path=args.scenario_path)

    def validate(self):
        fake_nf_scenario_dir = self.scenario_path.absolute().parent
        settings.AppSettingsBuilder.build_default()
        with settings.EditSettings():
            settings.get().nextflow_scenario_dir = fake_nf_scenario_dir
            scenario.Scenario.from_hash(scenario_hash=self.scenario_path.name, check_exists=True)


class ValidateAlgorithm(ValidateObject):
    def __init__(self, algorithm_path: Path):
        self.algorithm_path = algorithm_path

    @classmethod
    def from_args(cls, args) -> Self:
        return cls(algorithm_path=args.algorithm_path)

    def validate(self):
        fake_nf_algorithm_dir = self.algorithm_path.absolute().parent
        settings.AppSettingsBuilder.build_default()
        with settings.EditSettings():
            settings.get().nextflow_algorithm_dir = fake_nf_algorithm_dir
            algorithm.Algorithm.from_hash(algo_hash=self.algorithm_path.name, check_exists=True)


validate_parser = argparse.ArgumentParser(
    description="Manage validation of 'Object' (scenario, algorithm) for the Lola platform",
    add_help=False,
)

validate_parser.add_argument("-h", "--help", action=app._HelpAction, help="Show this help message and exit")

subparsers = validate_parser.add_subparsers(help="validation of scenario help")

scenario_validation_parser = subparsers.add_parser("scenario", allow_abbrev=False)
scenario_validation_parser.add_argument("--scenario-path", help="Path of the scenario to validate", required=True, type=Path)
scenario_validation_parser.set_defaults(func=ValidateScenario.from_args)

algorithm_validation_parser = subparsers.add_parser("algorithm", allow_abbrev=False)
algorithm_validation_parser.add_argument("--algorithm-path", help="Path of the algorithm to validate", required=True, type=Path)
algorithm_validation_parser.set_defaults(func=ValidateAlgorithm.from_args)


def parse_args_from_app(remains_args: list):
    if not remains_args:
        validate_parser.print_help()
        sys.exit(0)
    my_args = validate_parser.parse_args(remains_args)
    # Call the function stored in *_validation_parser.set_defaults()
    validate_instance: ValidateAlgorithm | ValidateScenario = my_args.func(my_args)
    try:
        validate_instance.validate()
    except LolapyGlobalError as e:
        logging.error(e.message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        validate_parser.print_help()
        sys.exit(0)

    my_args = validate_parser.parse_args()
    # Call the function stored in *_validation_parser.set_defaults()
    validate_instance: ValidateAlgorithm | ValidateScenario = my_args.func(my_args)
    validate_instance.validate()
