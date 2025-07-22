#!/usr/bin/env python3

import pytest
from werkzeug.exceptions import BadRequest

from lolapy.blueprints.request_validation import validate_json
from lolapy.blueprints.algorithm import AlgorithmParametersJSON

def test_validate_false_json(flask_request_context):
    with flask_request_context('/fake_request', method="POST", json={'format': 'short'}):
        def foo():  # fake function to pass to the decorator
            return None
        with pytest.raises(BadRequest):
            foo1 = validate_json(AlgorithmParametersJSON)(foo)
            foo1()

def test_validate_good_json(flask_request_context):
    with flask_request_context('/fake_request', json={'algorithm_hash': 'aeiou'}):
        def foo():  # fake function to pass to the decorator
            return None
        foo1 = validate_json(AlgorithmParametersJSON)(foo)
        foo1()

def test_validate_missing_json(flask_request_context):
    """Test if the flask request abort correctly if there are no json in the request"""
    with flask_request_context('/fake_request', content_type="application/json"):
        def foo():  # fake function to pass to the decorator
            return None
        with pytest.raises(BadRequest):
            foo1 = validate_json(AlgorithmParametersJSON)(foo)
            foo1()
