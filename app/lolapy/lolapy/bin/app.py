#!/usr/bin/env python3

import json
import logging
import logging.config
import traceback
import sys

import flask
from flask import Flask, request
from flask.wrappers import Response
from flasgger import Swagger

from lolapy.bin import async_tasks
from lolapy.errors import LolapyGlobalError, handle_api_errors
from lolapy.tools import settings
from lolapy.tools import logs
from lolapy.tools import health
from lolapy.dataset import errors as dataset_error
from lolapy.algorithm import errors as algorithm_error
from lolapy.scenario import errors as scenario_errors
from lolapy.tools.check_startup import CheckInstallation

from setup import lolapy_version

flask_app = Flask(__name__)
APP_VERSION = lolapy_version

# Manage cache system
#   Read information in tools/cache.py for more information
from flask_caching import Cache
from lolapy.tools import cache
cache.cache_object.init_app(flask_app)

# Imports routes
from lolapy.blueprints import algorithm_blueprint, scenario_blueprint, dataset_blueprint
flask_app.register_blueprint(algorithm_blueprint)
flask_app.register_blueprint(scenario_blueprint)
flask_app.register_blueprint(dataset_blueprint)
flask_app.register_blueprint

# Config swagger routes
flask_app.config["SWAGGER"] = {
    "title": "Lolapy API",
}
Swagger(flask_app, template_file="../../docs/swagger.yaml")

# Config cache system

@flask_app.before_request
def before_request():
    """
    Executed before each request to log the route
    """
    method = request.method
    route = request.url_rule
    access_adress = "->".join(request.access_route)
    data = request.data if request.data else ""
    logging.debug(f"{access_adress} {method} {route} {data}")


@flask_app.after_request
def after_request(response):
    """
    Executed after each request to log the response
    """
    method = request.method
    route = request.url_rule
    access_adress = "->".join(request.access_route)
    logging.debug(f"{access_adress} {method} {route} {response.status_code}")

    return response





@flask_app.route("/version", methods=["GET"])
def version():
    """Return the Lolapy version"""
    return json.dumps(APP_VERSION)


@flask_app.route("/ping", methods=["GET"])
def ping_lolapy():
    """Send boolean to validate that the backend is ready"""
    return Response(status=200)


@flask_app.route("/test_log", methods=["GET"])
def test_log():
    """Return True in any case. Use this route to test local logs"""
    logging.debug("This is a DEBUG log test")
    logging.info("This is a INFO log test")
    logging.warning("This is a WARNING log test")
    logging.error("This is a ERROR log test")
    logging.critical("This is a CRITICAL log test")
    return Response(status=200)


@flask_app.route("/test_log_async", methods=["GET"])
def test_async_log():
    async_tasks.test_async_logs()
    return Response(status=200)


@flask_app.route("/health", methods=["GET"])
def get_health():
    try:
        health_status = health.Health.check_status()
    except Exception as error:
        return handle_api_errors(error)

    return json.dumps(health_status)


@flask_app.route("/nf_logs", methods=["POST"])
def parse_nextflow_logs():
    """Process logs from nextflow.

    Function to extract logs from nextflow, filter them and
    send them to the frontend
    """
    json_data = request.get_json()
    async_tasks.parse_nextflow_logs(json_data)
    return Response(status=200)


@flask_app.route("/site-map")
def site_map():
    print(flask_app.url_map)
    return Response(status=200)


if __name__ == "__main__":
    app_settings = settings.get()  # First initialisation of the env
    app_port = app_settings.lolapy_host_port
    logs.LolapyLogs.configure_logs()
    app_settings.print()
    logging.info(f"API READY FOR DEBUG ON PORT {app_port}")
    flask_app.run(host='0.0.0.0', debug=None, port=app_port)

if __name__ != "__main__":
    app_settings = settings.get()  # First initialisation of the env
    try:
        logs.LolapyLogs.configure_logs()
        CheckInstallation.check()
    except LolapyGlobalError as error:
        logging.error(error.message)
        sys.exit(1)
    logging.info("API READY FOR PRODUCTION")
