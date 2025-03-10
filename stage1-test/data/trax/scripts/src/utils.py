#!/usr/bin/env python3

import os
import logging
import shlex
from subprocess import Popen, PIPE
import argparse

from src import error, warning


def is_port_available(port):
    """
    Run a netcat command to see is port is used or not

    :param port: port to check
    :type port: int
    :return: True if port is available and not used. False otherwise
    :rtype: bool
    """
    command = f"nc -zv 127.0.0.1 {port}"
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if "refused" in stderr:
        return False
    return True


def find_empty_port(min_port=8080, max_port=8081):
    """
    Find an available port in the range
    """
    for port in range(min_port, max_port+1):
        if is_port_available(port):
            return port


def is_file_readable(filename):
    """
    Test if a file exist and is readable
    Stop the program in case of error
    """
    if not os.path.isfile(filename):
        error(f"'{filename}' does not exist")
    if not os.access(filename, os.R_OK):
        error(f"'{filename}' is not readable")
    return True


def bash_cmd(cmd):
    """
    Execture the cmd (command) into a Python subprocess
    Return the stdout and stderr

    :param cmd: command to run
    :type cmd: str
    :return: return in bytes string format in a tupule stdin and stderr
    :rtype: tuple<str, str>
    """
    # remove multiple spaces. Keep spaces between quotes
    command = shlex.split(cmd)
    logging.debug(command)
    my_cmd = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = my_cmd.communicate()
    return (stdout, stderr)


def print_bash(msg: str, loglevel=logging.info):
    """
    Format Bash outputs stdout and stderr
    Remove empty lines

    :param msg: String to print
    :type msg: str
    :param loglevel: function logging to apply. Default: logging.info
    :type loglevel: a function of logging level (see https://docs.python.org/3/library/logging.html#logging.debug)
    """
    for line in msg.split("\n"):
        line = line.split()
        line = " ".join(line)
        if line:
            loglevel(line)


class _HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                print("---\n\033[0;32mCommand '{}'\033[0m".format(choice))
                print(subparser.format_help())

        parser.exit()
