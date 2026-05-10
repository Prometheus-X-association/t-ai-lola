"""
Global error for lolapy API

LolapyGlobalError is the master Error of Lolapy. It inherit from Exception and implement:
- self.message: Message to log on the backend server
- self.public_message: Message which can be send to the user on the frontend. Password, PATH, user_id, ... must be hidden in this message.

All other error implement in lolapy must inherit from LolapyGlobalError
To log error on the backend. Log the error when raising it. Can be done with:
```
try:
  something_wrong()
except PythonError as e:
  error = error.MyLolapyError(parameters...)
  logging.error(error)
  raise error
```
"""

from typing import List
import logging
import re

import pydantic
import jinja2

from lolapy import tools


class LolapyGlobalError(Exception):
    standard_public_message = "Internal Server Error"

    def __init__(self):
        """Constructor of LolapyGlobalError."""
        self.message = None
        self.public_message = None
        self.__ensure_attributes()

    def __ensure_attributes(self):
        """Ensure all attributes are set."""
        try:
            assert self.message
            assert self.public_message
        except AssertionError:
            logging.error(
                f"Missing 'message' or 'public_message' attribute(s) in {tools.object_fullname(self)}"
            )
            raise LolapyErrorOnError(tools.object_fullname(self))

    def __str__(self) -> str:
        """Representation of the error.

        Return public_message instead of message to avoid leaking sensitive data.
        If your want to see real log, use self_error.message
        """
        self.__ensure_attributes()
        # linters and lsp server can raise an error with next line because self.public_message can be
        # None instead of str. The self.__ensure_attributes() call ensure that self.public_message is not None
        return str(self.public_message)


class LolapyErrorOnError(LolapyGlobalError):
    """Error raise when problem in the interface of a custom Error."""

    def __init__(self, class_name: str):
        self.message = f"Error on the interface for '{class_name}' object"
        self.public_message = LolapyGlobalError.standard_public_message


def extract_missing_fields(
    error: pydantic.ValidationError | jinja2.exceptions.UndefinedError,
) -> List[str]:
    """Extract missing field of the pydantic.ValidationError."""
    if isinstance(error, pydantic.ValidationError):
        all_missing_fields = []
        for missing_field in error.errors():
            # Pydantic error can be in the following format:
            # ValidationError(
            #   model='ScenarioRecipe', errors=[
            #     {'loc': ('switchable_algorithms', 0, 'nf_variable'), 'msg': 'field required', 'type': 'value_error.missing'},
            #     {'loc': ('switchable_algorithms', 1, 'nf_variable'), 'msg': 'field required', 'type': 'value_error.missing'}
            #   ])
            # So we have to extract all fields in loc. Here is means that there is a missing field in the sub-field switchable_algorithms
            # They will be concatened with ' -> ' to produce the message 'switchable_algorithms -> 0 -> nf_variable'
            sanitized_loc = [str(field) for field in missing_field["loc"]]
            all_missing_fields.append(" -> ".join(sanitized_loc))
        return all_missing_fields
    elif isinstance(error, jinja2.exceptions.UndefinedError):
        # Error with jinja2 are in format "'{__missing_field}' is undefined"
        # so extract it with a regex
        extract_field = re.compile("'([a-zA-Z_0-9]*)'")
        matches = re.match(extract_field, str(error))
        if matches:
            return [matches[1]]
    return ["Unable to find the missing field. Check the format of your file"]

def handle_api_errors(error: Exception) -> "flask.Response":
    """Convert Lolapy catched errors to the correct respond code"""
    import flask
    from flask.wrappers import Response
    import lolapy.dataset.errors as dataset_error
    import lolapy.algorithm.errors as algorithm_error
    import lolapy.scenario.errors as scenario_errors
    import logging
    import traceback

    match error:
        case LolapyGlobalError():
            internal_message = error.message
            public_message = error.public_message
            response_code = 500
            match error:
                case dataset_error.DatasetDoesNotExist():
                    response_code = 404
                case dataset_error.DatasetPermissionDenied():
                    response_code = 403
                case scenario_errors.ScenarioNotExist():
                    response_code = 404
                case algorithm_error.AlgorithmNotExist():
                    response_code = 404
        case _:
            logging.error(traceback.format_exc())
            internal_message = str(error)
            public_message = LolapyGlobalError.standard_public_message
            response_code = 500

    logging.error(internal_message)
    return Response(status=response_code, response=public_message)
