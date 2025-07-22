#!/usr/bin/env python3

import json
import logging

from flask import Response

from lolapy.bin import app
from lolapy.blueprints import server_blueprint
from lolapy.slurm.usage import ClusterUsage
from lolapy.tools import cache

print(id(cache.cache_object))

@server_blueprint.route("/usage")
@cache.cache_object.cached(timeout=60)
def usage():
    logging.info("Compute usage of the cluster. Not cached")

    server_usage = ClusterUsage.get()
    # return json.dumps(server_usage)
    return server_usage.json()
