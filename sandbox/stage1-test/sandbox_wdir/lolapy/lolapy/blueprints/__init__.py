#!/usr/bin/env python3

from flask import Blueprint
# Initialise the blueprint
algorithm_blueprint = Blueprint('algorithm_blueprint', __name__, url_prefix="/algorithm")
scenario_blueprint = Blueprint('scenario_blueprint', __name__, url_prefix="/scenario")
dataset_blueprint = Blueprint('dataset_blueprint', __name__, url_prefix="/dataset")
server_blueprint = Blueprint('server_blueprint', __name__, url_prefix="/server")

# Import all dependencies of the blueprint to initialize all routes
from lolapy.blueprints.algorithm import *
from lolapy.blueprints.scenario import *
from lolapy.blueprints.dataset import *
from lolapy.blueprints.server import *
