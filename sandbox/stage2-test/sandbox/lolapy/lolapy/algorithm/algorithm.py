#!#!/usr/bin/env python3

"""Module to manage Algorithm information"""


from __future__ import annotations
from enum import Enum
import json
from pathlib import Path

from pydantic import BaseModel, validator
import pydantic

from lolapy.algorithm import errors
from lolapy.tools import settings


class CONST_ALGORITHM:
    """Store constante information on algorithm"""

    algo_recipe_file = "algo_recipe.json"


class ParameterAvailableTypes(Enum):
    """Enumeration of all parameter types available for an algorithm.

    Attributes:
        int: integer value
        float: float value
        bool: boolean value
        string: string value
        choices: choices value. Must be associated with a 'choices' field
            (ie. AlgorithmParameter cannot be None if 'choices' is selected)
    """

    int = "int"
    float = "float"
    bool = "bool"
    string = "string"
    choices = "choices"

    def get_value(self) -> str:
        """Return the value of the Enumerate.

        This ensure the same interface than InputValue and OutputValue with
        get_value() method
        Returns:
            str: The value associated to the enumerate
        """
        return self.value


class InputValue(BaseModel):
    """Special variable for InputValue used in algorithm template.

    Such as input/output. This object match the field of an 'Enum'. So we can use
    SpecialVariable.get_value() like as ParameterAvailableTypes.get_value()
    Examples:
       >>> foo = algorithm.ParameterAvailableTypes.int
       >>> foo.get_value()
       'int'

       >>> bar = algorithm.InputValue(value="input_")
       >>> bar.get_value()
       'input_'
    """

    input_value: str

    def get_value(self) -> str:
        """Getter for InputValue.value.

        Assure compatibility with ParameterAvailableTypes.get_value()
        """
        return self.input_value


class OutputValue(BaseModel):
    """Special variable for OutputValue used in algorithm template.

    Such as input/output. This object match the field of an 'Enum'. So we can use
    SpecialVariable.get_value() like as ParameterAvailableTypes.get_value()
    Examples:
       >>> foo = algorithm.ParameterAvailableTypes.int
       >>> foo.get_value()
       'int'

       >>> bar = algorithm.OutputValue(value="output_")
       >>> bar.get_value()
       'output_'
    """

    output_value: str

    def get_value(self) -> str:
        """Getter for OutputValue.value.

        Assure compatibility with ParameterAvailableTypes.get_value()
        """
        return self.output_value


class AlgorithmParameter(BaseModel):
    """Serialize/deserialize information for Parameter of Algorithm.

    These information are 'normally' stored in the algo_recipe.json
    Attributes:
        name: Name of the parameter
        description: Short description of the parameter. Short help.
        variable_name: Name of the variable in the 'command' field in algo_recipe.json
        type: Type of the variable. Can be a ParameterAvailableTypes for classic types (string, int, ...) or
            a SpecialVariable for type like input or output
        editable: If the argument must be edited in the web-interface. False is usually for SpecialVariable
        default: Default value of the parameter. Can be something of None
    """

    name: str
    description: str
    variable_name: str
    choices: list[str] | None = None
    type: ParameterAvailableTypes | OutputValue | InputValue
    editable: bool
    default: str | None = None

    def json(self) -> str:
        """Overwrite the original json method.

        Used to correctly expand the `type` attribute.
        Returns:
            str: the json serialized into string
        """
        json_data = self.dict()
        json_data["type"] = self.type.get_value()
        return json.dumps(json_data)

    @validator("choices")
    def check_choices(cls, value):
        """Validate value of choices field.

        Validate only if its None (non-set) or a list[str]

        Args:
            value: special arg from pydantic. Here, it's the value of choices field.
        Returns:
            None | list[str]: Returns the value of `value` after validation.
        Raises:
            AlgorithmParameterFieldWrongFormat: If there is a miss-match between `type` field
                and `choices` field.
        """

        def is_list_str(lst) -> bool:
            """Check if `lst` is type list[str].

            Args:
                lst: the value to test
            Returns:
                bool: True if `lst` is list[str]. False otherwise
            """
            if not isinstance(lst, str) and all(isinstance(elem, str) for elem in lst):
                return True
            return False

        if value == None or not is_list_str(value):
            raise errors.AlgorithmParameterFieldWrongFormat(
                field="choices",
                value=value,
                additionnal_msg="Parameter field 'choices' must be none if the parameter type is not 'choices', or a list[str]",
            )
        return value

    @validator("type", pre=True)
    def check_type(cls, value, values):
        """Check if 'type' field is correct."""

        # Check that the choices field is validated if type is choices
        if value == "choices":
            if not "choices" in values or values["choices"] == None:
                raise errors.AlgorithmParameterFieldWrongFormat(
                    field="choices",
                    value=value,
                    additionnal_msg="Parameter type 'choices' must be set with 'choices' field as list[string]",
                )

        if value.startswith("input_"):
            return InputValue(input_value=value)
        elif value.startswith("output_"):
            return OutputValue(output_value=value)
        for avail_type in ParameterAvailableTypes:
            if avail_type.get_value() == value:
                return avail_type
        raise errors.AlgorithmParameterFieldWrongFormat("type", value)

    @staticmethod
    def from_json(json_data: dict) -> Self:
        """Build a [AlgorithmParameter] from json data.

        Args:
            json_data: json data to deserialize
        Returns:
            Self: Instance of [AlgorithmParameter]
        Raises:
            AlgorithmParameterWrongFormat: if the parameter is not well formated
        """
        try:
            return AlgorithmParameter(**json_data)
        except pydantic.error_wrappers.ValidationError as e:
            raise errors.AlgorithmParameterMissingField(json_data, e)


class AlgorithmRecipe(BaseModel):
    name: str
    description: str
    command: str
    harbor_url: str
    parameters: list[AlgorithmParameter]

    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        """Build a [AlgorithmFormat] from json data.

        Args:
            json_data: json data to deserialize
        Returns:
            Self: Instance of [AlgorithmFormat]
        Raises:
            AlgorithmParameterWrongFormat: if the parameter is not well formated
        """
        try:
            return cls(**json_data)
        except pydantic.error_wrappers.ValidationError as e:
            raise errors.AlgorithmRecipeMissingField(json_data, e)

    @classmethod
    def from_file(cls, algo_recipe: Path) -> Self:
        """Read the algo_recipe and extract data.

        Args:
            algo_recipe: Path of the algo_recipe.json file
        Returns:
            Instance of AlgorithmFormat
        Raises:
            AlgorithmParameterWrongFormat: if the parameter is not well formated
        """
        try:
            json_data = json.load(open(algo_recipe))  # Don't catch this !
            # The file is ensure during installation
            return cls(**json_data)
        except pydantic.error_wrappers.ValidationError as e:
            raise errors.AlgorithmRecipeMissingField(json_data, e)


class Algorithm(BaseModel):
    """Instance of Algorithm.

    Use this structure as an entrypoint for all stuff related to an algorithm

    Attributes:
        hash: Hash unique of the algorithm
        algo_path: Complete Path of the algorithm
        algo_recipe_path: Complete Path of the algo_recipe
    """

    hash: str
    algo_path: Path
    algo_recipe_path: Path
    algo_recipe: AlgorithmRecipe | None

    @staticmethod
    def _build_algorithm(algo_hash: str, algo_path: Path, check_exists: bool = True) -> Algorithm:
        """'Meta-Constructor' for Algorithm.

        This method is used to avoid code duplication in `from_hash` and `from_path`.
        Args:
            algo_hash: Hash unique of the algorithm
            check_exists: If True, check if the algorithm exist. If no, does not check anything
        Returns:
            Self: Instance of [Algorithm]
        Raises:
            AlgorithmNotExist: if the path of the algorithm does not exist
            InstallationMissingRequiredFile: if the algo_recipe.json is missing
        """

        algo_recipe = algo_path / CONST_ALGORITHM.algo_recipe_file

        if not check_exists:
            return Algorithm(
                hash=algo_hash,
                algo_path=algo_path,
                algo_recipe_path=algo_recipe,
                algo_recipe=None,
            )

        if not algo_path.exists():
            raise errors.AlgorithmNotExist(algo_path)
        if not algo_recipe.exists():
            raise errors.InstallationMissingRequiredFile(
                algorithm=algo_hash, filename=CONST_ALGORITHM.algo_recipe_file
            )

        return Algorithm(
            hash=algo_hash,
            algo_path=algo_path,
            algo_recipe_path=algo_recipe,
            algo_recipe=AlgorithmRecipe.from_file(algo_recipe),
        )


    @classmethod
    def from_hash(cls, algo_hash: str, check_exists: bool = True) -> Self:
        """Create an [Algorithm] instance from hash.

        Args:
            algo_hash: Hash unique of the algorithm
            check_exists: If True, check if the algorithm exist. If no, does not check anything
        Returns:
            Self: Instance of [Algorithm]
        Raises:
            AlgorithmNotExist: if the path of the algorithm does not exist
            InstallationMissingRequiredFile: if the algo_recipe.json is missing
        """

        app_settings = settings.get()
        algo_path = app_settings.nextflow_algorithm_dir / algo_hash
        return cls._build_algorithm(algo_hash=algo_hash, algo_path=algo_path, check_exists=check_exists)

    @classmethod
    def from_path(cls, algo_path: Path, check_exists: bool = True) -> Self:
        """Constructor for Algorithm from the path of the algorithm.

        Same constructor than `from_hash` but does not rely on settings and algorithm_directory.
        This method is not used (yet) in lolapy but can be used in sandbox or else.

        Args:
            algo_hash: Hash unique of the algorithm
            check_exists: If True, check if the algorithm exist. If no, does not check anything
        Returns:
            Self: Instance of [Algorithm]
        Raises:
            AlgorithmNotExist: if the path of the algorithm does not exist
            InstallationMissingRequiredFile: if the algo_recipe.json is missing
        """
        return cls._build_algorithm(algo_hash=algo_path.name, algo_path=algo_path, check_exists=check_exists)

    def get_recipe(self) -> AlgorithmRecipe:
        """Return the Algorithm Recipe of the Algorithm.

        Returns:
            AlgorithmRecipe: algo_recipe.json of the algorithm
        """
        return AlgorithmRecipe.from_file(self.algo_recipe_path)
