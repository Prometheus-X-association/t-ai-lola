#!/usr/bin/env python3

import pytest

from lolapy.bin.app import flask_app

@pytest.fixture()
def fixture_flask_app():
    flask_app.config.update({
        "TESTING": True,
    })

    yield flask_app

@pytest.fixture()
def flask_request_context(fixture_flask_app):
    """Generate a fake context for a request.

    Example:
        >>> from flask import request
        >>> with flask_request_context("/my_fake_route", method="POST", json={"data": "aeiou"}):
        ...    json_data = request.get_json()
        ...    assert json_data == {"data": "aeiou"}
    """
    return fixture_flask_app.test_request_context

@pytest.fixture()
def flask_client(fixture_flask_app):
    """Generate a fake client to test requests.

    Example:
        >>> response = flask_client.get("/health")
        >>> assert response.data is dict()
    """
    return fixture_flask_app.test_client()
