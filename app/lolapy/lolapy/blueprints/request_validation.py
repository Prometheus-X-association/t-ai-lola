#!/usr/bin/env python3

from functools import wraps
import logging

from flask import request, abort, g
import pydantic
from werkzeug.exceptions import BadRequest

from lolapy.blueprints.errors import BadRequestFormat


def validate_json(structure):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            try:
                data = request.get_json()
            # occurs when the request is a POST without Content-Type: application/json
            except BadRequest:
                data = {}
            # Convert missing data (None) to dict
            # so it will raise an error during validation
            if data is None:
                data = {}

            try:
                data = structure(**data)
            except pydantic.ValidationError as e:
                bad_request = BadRequestFormat.from_ValidationError(request, e)
                logging.error(bad_request.message)
                return abort(400, bad_request.public_message)

            g.request_data = data

            return f(*args, **kwargs)
        return decorated_function
    return decorator
