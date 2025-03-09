#!/usr/bin/env python3

import sys
import os
import logging
import __main__


def error(msg):
    #msg = "{}: [Error] {}".format(os.path.basename(__main__.__file__), msg)
    logging.error(msg)
    sys.exit(1)


def warning(msg):
    #msg = "{}: [Warning] {}".format(os.path.basename(__main__.__file__), msg)
    logging.warning(msg, file=sys.stderr)
