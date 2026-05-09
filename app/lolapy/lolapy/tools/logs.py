#!/usr/bin/env python3

"""Module to configure logs for Lolapy.

Use LolapyLogs.configure_logs as entrypoint to configure logs for the entire API.
Use the method only once.

It create a logging for the entire API. For more information about logging: https://docs.python.org/3/library/logging.html
3 handlers are availables (see _gen_dict_logs_parameters for more details):
 - console: to print to stdout
 - file: to print into a file
 - frontend_api: to send information to frontend api log

The frontend_api log is edited after creation to put it into a queue and avoid blocking step. Moreover,
this handler is not blocking if frontend api is unavailable. The 2 others handlers are not in the queue system.

To use logging, in a module, import logging and use just with `logging.info("blablabla")`
"""

import asyncio
import json
import logging, logging.handlers, logging.config
from pathlib import Path
from queue import Queue
import uuid

import flask
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from lolapy.tools import settings
from lolapy.tools import logs  # keep it here. Used in _gen_dict_logs_parameters


class LolapyLogs:
    """Configure logs for the entire API.

    Use configure_logs() method as an entrypoint of the object.
    Attributes:
        frontend_url: url of the frontend
        log_file: Path of the log file where to store logs


    """

    def __init__(self):
        """Constructor for the LolapyLogs object."""
        app_settings = settings.get()
        self.frontend_url: str = self._gen_frontend_url()
        self.log_file: str = str(app_settings.lolapy_log_file)
        self.log_file_async: str = self.log_file + ".async"
        self.log_level: str = app_settings.lolapy_log_level.value
        self.log_to_fronted: bool = app_settings.lolapy_disable_frontend_logs
        LolapyLogs.__instance__ = self

    def _gen_dict_logs_parameters(self) -> dict:
        """Return the full configuration for logger format, output, etc ...

        :return: dict: The dictionnary schema for logger configuration
        """
        logger_config = {
            "version": 1,
            "formatters": {
                "default": {
                    "()": ColoredFormatter,
                    "format": "%(asctime)s::%(levelname)s::%(request_id)s::%(name)s.%(module)s.%(funcName)s::%(message)s",
                },
                "async_tasks": {
                    "()": ColoredFormatter,
                    "format": "%(asctime)s::%(levelname)s::WORKER-ID::%(name)s.%(module)s.%(funcName)s::%(message)s",
                },
                "frontend_format": {
                    "format": json.dumps(
                        {
                            "type": "%(name)s.%(module)s.%(funcName)s",
                            "message": "%(message)s",
                            "details": "%(request_id)s",
                        }
                    ),
                },
            },
            "filters": {
                "request_id": {
                    "()": "lolapy.tools.logs.RequestIdFilter",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.log_level,
                    "filters": ["request_id"],
                },
                "async_console": {
                    "class": "logging.StreamHandler",
                    "formatter": "async_tasks",
                    "level": self.log_level,
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": self.log_file,
                    "level": self.log_level,
                    "filters": ["request_id"],
                },
                "async_file": {
                    "class": "logging.FileHandler",
                    "formatter": "async_tasks",
                    "filename": self.log_file_async,
                    "level": self.log_level,
                },
                "frontend_api": {
                    "class": "lolapy.tools.logs.CustomHttpHandler",
                    "formatter": "frontend_format",
                    "level": "INFO",
                    "url": f"{self.frontend_url}",
                },
            },
            "loggers": {
                "huey": {
                    "handlers": ["async_file", "async_console"],
                    "level": "INFO",
                },
                "root": {
                    "handlers": ["console", "file", "frontend_api"],
                    "level": "DEBUG",
                },
            },
            "root": {"handlers": ["console", "file", "frontend_api"], "level": "DEBUG"},
        }
        if not self.log_to_fronted:
            logger_config["root"]["handlers"].remove("frontend_api")
        return logger_config

    def _gen_frontend_url(self) -> str:
        """Generate frontend api log URL based on env vars.

        Add http:// at the beginning of the url if not present.
        Concatenate host_server, port and url of the log

        :return: str: url of the frontend log in the format http://<server>:<port>/<url>
        """
        app_settings = settings.get()
        frontend_host: str = app_settings.frontend_api_ip
        if not frontend_host.startswith("http"):
            frontend_host = f"http://{frontend_host}"
        frontend_port: int = app_settings.frontend_api_port
        frontend_url: str = app_settings.frontend_api_log_url
        if not frontend_url.startswith("/"):
            frontend_url = f"/{frontend_url}"
        url = f"{frontend_host}:{frontend_port}{frontend_url}"

        return url

    @staticmethod
    def configure_logs():
        """Configure log for lolapy.

        Entrypoint of the object. Should be run only once at the start of the API
        """
        log = LolapyLogs()
        logging_conf = log._gen_dict_logs_parameters()
        logging.config.dictConfig(logging_conf)
        root = logging.getLogger()
        root.setLevel("DEBUG")
        toto = logging.getLogger("huey")
        toto.setLevel("INFO")
        tutu = logging.getLogger("huey.consumer")
        tutu.setLevel("INFO")

        ## Tricky part
        ## It remove the frontend_api handler to put it into a queue
        ## It avoid to block request to the frontend
        ## I created the config with dictConfig to remove it later cause I don't know how to manage
        ## queue and queuelistener in dictConfig
        handler_frontend_api = root.handlers[
            -1
        ]  # according to the logger_config, frontend is the last one
        queue = Queue()
        handler = LocalQueueHandler(queue)

        handler.set_name("frontend_api_queue")
        root.addHandler(handler)
        root.removeHandler(handler_frontend_api)

        listener = logging.handlers.QueueListener(
            queue, handler_frontend_api, respect_handler_level=True
        )
        listener.start()
        logging.info(f"Log level set to {log.log_level}")


class ColoredFormatter(logging.Formatter):
    color_codes = {
        logging.DEBUG: '\033[0m',    # white
        logging.INFO: '\033[32m',    # Vert
        logging.WARNING: '\033[33m', # Jaune
        logging.ERROR: '\033[31m',   # Rouge
        logging.CRITICAL: '\033[31m' # Rouge
    }

    def format(self, record):
        log_level = record.levelno
        color = self.color_codes.get(log_level, '\033[0m')  # Réinitialisation des couleurs
        log_level_name = logging.getLevelName(log_level)
        message = super().format(record)
        formatted_message = f'{color}{log_level_name}: {message}\033[0m'  # Applique la couleur au message
        return formatted_message


class CustomHttpHandler(logging.Handler):
    def __init__(self, url: str, enabled: bool = True):
        """Initialize the custom http handler.

        :param url: str: The URL that the logs will be sent to
        :param enabled: bool: If False, it does not log on url (avoid http logging on failure and infinite loop)
        """
        self.url = url

        # sets up a session with the server
        self.MAX_POOLSIZE = 100
        self.session = session = requests.Session()
        session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=5, backoff_factor=0.5, status_forcelist=[403, 500]
                ),
                pool_connections=self.MAX_POOLSIZE,
                pool_maxsize=self.MAX_POOLSIZE,
            ),
        )

        super().__init__()

    def emit(self, record):
        """This function gets called when a log event gets emitted.

        It recieves a record, formats it and sends it to the url
        :param record: a log record from logging
        """
        logEntry = self.format(record)
        try:
            self.session.post(self.url, data=logEntry)
        except requests.exceptions.ConnectionError as e:
            # handle exception when frontend is not available
            with DisableCustomHttphandler() as _:
                # Use ContextManager to disable the logging to http
                # log only backend side
                logging.warning(f"Unable to etablish connection to {self.url}: {e}")


class LocalQueueHandler(logging.handlers.QueueHandler):
    """Custom localQueue to hold calls to frontend handler."""

    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)


class DisableCustomHttphandler:
    def __init__(self):
        self.custom_handler = None

    def __enter__(self):
        """Disable the handler to log to the frontend.

        Based on contexteManager. NOTE: The handler must have "frontend_api_queue" as name
        It disable the logging to the frontend when using like:
        with DisableCustomHttphandler() as _:
           do something
        """
        root = logging.getLogger()
        # Search for frontend_api handler
        for handler in root.handlers:
            if handler._name == "frontend_api_queue":
                self.custom_handler = handler
                root.removeHandler(handler)
                return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        """Re-enable again the handler to log to the frontend."""
        root = logging.getLogger()
        root.addHandler(self.custom_handler)


class LolapyLogsFiltersTools:
    """Methods use to filter or give information to RequestIdFilter."""

    @staticmethod
    def generate_request_id(self, original_id: str = "") -> str:
        """Generate a unique request ID.

        Use to identify request. It uses uuid to avoid collision. If original_id is given
        concatains original_id and the new one.
        :param original_id: str: Original ID, defaults to ""
        :return: str: The new request ID
        """
        new_id = str(uuid.uuid4())
        return new_id

    @staticmethod
    def request_id() -> str:
        """Return the current request ID or a new one if there is none.

        In order of preference:
            - If we've already created a request ID and stored it in the flask.g context local, use that
            - If a client has passed in the X-Request-Id header, create a new ID with that prepended
            - Otherwise, generate a request ID and store it in flask.g.request_id
        """
        if getattr(flask.g, "request_id", None):
            return flask.g.request_id

        headers = flask.request.headers
        original_request_id = headers.get("X-Request-Id")
        new_uuid = LolapyLogsFiltersTools.generate_request_id(original_request_id)
        flask.g.request_id = new_uuid

        return new_uuid


class RequestIdFilter(logging.Filter):
    """Filter logs for flask requests.

    This is a logging filter that makes the request ID available for use in
    the logging format.
    Note that we're checking if we're in a request
    context, as we may want to log things before Flask is fully loaded.
    """

    def filter(self, record):
        record.request_id = (
            LolapyLogsFiltersTools.request_id() if flask.has_request_context() else ""
        )
        return True
