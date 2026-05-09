#!/usr/bin/env python3

"""Module to store fixtures.
Used for development purpose.
"""

from __future__ import annotations
from datetime import datetime, timedelta
import logging
from pathlib import Path

from lolapy.nextflow import nextflow_logs


class DatetimeSingleton:
    """Object that hold a datetime and increase it after each invocation.

    The first time the class is called, it save the current datetime. Next times, it increase the
    saved datetime by X seconds
    Be careful. This is not a Singleton thread-safe. Implement a threading.Lock for this class if necessary
    """

    local_datetime: datetime | None = None

    @staticmethod
    def get_datetime():
        """Get the "local" datetime and increase the datetime for next invocation."""
        if not DatetimeSingleton.local_datetime:
            DatetimeSingleton.local_datetime = datetime.now()
        else:
            DatetimeSingleton.local_datetime = (
                DatetimeSingleton.local_datetime + timedelta(seconds=5)
            )
        return DatetimeSingleton.local_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")


class FakeStatements:
    data = [
        {
            "id": "6af1e5c7-31d2-3eb2-9725-efa1f6b8b108",
            "verb": {
                "id": "http://example.com/xapi/submitted",
                "display": {"en-US": "submitted"},
            },
            "actor": {
                "mbox": "mailto:user3@LRS.net",
                "name": "user3",
                "objectType": "Agent",
            },
            "object": {
                "id": "http://example.com/xapi/submitted",
                "definition": {
                    "name": {"en-US": "activity"},
                    "description": {"en-US": "Testing Example"},
                },
                "objectType": "Activity",
            },
            "stored": "2022-04-21T10:26:28.7991Z",
            "version": "1.0.0",
            "authority": {
                "account": {"name": "traxlrs", "homePage": "http://trax.test"},
                "objectType": "Agent",
            },
            "timestamp": "2022-04-21T10:26:28.7991Z",
        },
        {
            "id": "75b93ba7-04c9-3c7d-940e-f33c4e6fc6b2",
            "verb": {
                "id": "http://example.com/xapi/viewed",
                "display": {"en-US": "viewed"},
            },
            "actor": {
                "mbox": "mailto:user1@LRS.net",
                "name": "user1",
                "objectType": "Agent",
            },
            "object": {
                "id": "http://example.com/xapi/viewed",
                "definition": {
                    "name": {"en-US": "course"},
                    "description": {"en-US": "Testing Example"},
                },
                "objectType": "Activity",
            },
            "stored": "2022-04-21T10:26:28.8284Z",
            "version": "1.0.0",
            "authority": {
                "account": {"name": "traxlrs", "homePage": "http://trax.test"},
                "objectType": "Agent",
            },
            "timestamp": "2022-04-21T10:26:28.8284Z",
        },
        {
            "id": "e1ccd015-798e-35e8-ad5e-aea385125555",
            "verb": {
                "id": "http://example.com/xapi/added",
                "display": {"en-US": "added"},
            },
            "actor": {
                "mbox": "mailto:user4@LRS.net",
                "name": "user4",
                "objectType": "Agent",
            },
            "object": {
                "id": "http://example.com/xapi/added",
                "definition": {
                    "name": {"en-US": "exercice1"},
                    "description": {"en-US": "Testing Example"},
                },
                "objectType": "Activity",
            },
            "stored": "2022-04-21T10:26:28.8384Z",
            "version": "1.0.0",
            "authority": {
                "account": {"name": "traxlrs", "homePage": "http://trax.test"},
                "objectType": "Agent",
            },
            "timestamp": "2022-04-21T10:26:28.8384Z",
        },
        {
            "id": "080966f3-19f9-3937-8e36-d890681d7eaf",
            "verb": {
                "id": "http://example.com/xapi/viewed",
                "display": {"en-US": "viewed"},
            },
            "actor": {
                "mbox": "mailto:user1@LRS.net",
                "name": "user1",
                "objectType": "Agent",
            },
            "object": {
                "id": "http://example.com/xapi/viewed",
                "definition": {
                    "name": {"en-US": "course"},
                    "description": {"en-US": "Testing Example"},
                },
                "objectType": "Activity",
            },
            "stored": "2022-04-21T10:26:28.8439Z",
            "version": "1.0.0",
            "authority": {
                "account": {"name": "traxlrs", "homePage": "http://trax.test"},
                "objectType": "Agent",
            },
            "timestamp": "2022-04-21T10:26:28.8439Z",
        },
        {
            "id": "31643470-1254-3790-80a6-ea68b5ca02c4",
            "verb": {
                "id": "http://example.com/xapi/submitted",
                "display": {"en-US": "submitted"},
            },
            "actor": {
                "mbox": "mailto:user3@LRS.net",
                "name": "user3",
                "objectType": "Agent",
            },
            "object": {
                "id": "http://example.com/xapi/submitted",
                "definition": {
                    "name": {"en-US": "activity"},
                    "description": {"en-US": "Testing Example"},
                },
                "objectType": "Activity",
            },
            "stored": "2022-04-21T10:26:28.8481Z",
            "version": "1.0.0",
            "authority": {
                "account": {"name": "traxlrs", "homePage": "http://trax.test"},
                "objectType": "Agent",
            },
            "timestamp": "2022-04-21T10:26:28.8481Z",
        },
    ]


from enum import Enum, auto


class FakeNextflowLogType(Enum):
    workflow_run = auto()
    workflow_done = auto()
    workflow_error = auto()
    process_submit = auto()
    process_run = auto()
    process_done = auto()
    process_error = auto()


class FakeNextflowLog:
    _workflow_run: nextflow_logs.NextflowLogWorkflow = {
        "logType": "workflow",
        "logEvent": "run",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "eventTime": "1970-01-01T00:01:02Z",
        "errorReport": "",
    }
    _workflow_done: nextflow_logs.NextflowLogWorkflow = {
        "logType": "workflow",
        "logEvent": "done",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "eventTime": "1970-01-01T00:01:02Z",
        "errorReport": "",
    }
    _workflow_error: nextflow_logs.NextflowLogWorkflow = {
        "logType": "workflow",
        "logEvent": "error",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "eventTime": "1970-01-01T00:01:02Z",
        "errorReport": "There is an error, sure it's a problem from the frontend (lol)",
    }
    _process_done: nextflow_logs.NextflowLogProcess = {
        "logType": "process",
        "logEvent": "done",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "processName": "First-process",
        "eventTime": "1970-01-01T00:01:02Z",
        "workDir": "/tmp/wdir",
        "statistics": {
            "cpu": 90.5,
            "memory": 10.0,
            "ioWrite": 1032,
            "ioRead": 65536,
            "duration": 123456789,
        },
    }
    _process_submit: nextflow_logs.NextflowLogProcess = {
        "logType": "process",
        "logEvent": "submit",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "processName": "First-process",
        "eventTime": "1970-01-01T00:01:02Z",
        "workDir": "/tmp/wdir",
        "statistics": None,
    }
    _process_run: nextflow_logs.NextflowLogProcess = {
        "logType": "process",
        "logEvent": "run",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "processName": "First-process",
        "eventTime": "1970-01-01T00:01:02Z",
        "workDir": "/tmp/wdir",
        "statistics": None,
    }
    _process_error: nextflow_logs.NextflowLogProcess = {
        "logType": "process",
        "logEvent": "error",
        "runHash": "Rf53ce97606fd82c13a3b87e205f3577724191474",
        "processName": "First-process",
        "eventTime": "1970-01-01T00:01:02Z",
        "workDir": "/tmp/wdir",
        "statistics": None,
    }
    local_datetime = None

    def __init__(
        self,
        log_type: nextflow_logs.NextflowLogProcess | nextflow_logs.NextflowLogWorkflow,
    ):
        logging.warning(type(log_type))
        self.log = log_type.copy()
        self._init_event_time()

    def _init_event_time(self):
        self.log["eventTime"] = DatetimeSingleton.get_datetime()

    @classmethod
    def workflow_run(cls) -> cls:
        return cls(cls._workflow_run)

    @classmethod
    def workflow_done(cls) -> cls:
        return cls(cls._workflow_done)

    @classmethod
    def workflow_error(cls) -> cls:
        return cls(cls._workflow_error)

    @classmethod
    def process_submit(cls) -> cls:
        return cls(cls._process_submit)

    @classmethod
    def process_run(cls) -> cls:
        return cls(cls._process_run)

    @classmethod
    def process_done(cls) -> cls:
        return cls(cls._process_done)

    @classmethod
    def process_error(cls) -> cls:
        return cls(cls._process_error)

    def _edit_field(self, field: str, value: str):
        try:
            self.log[field] = value
        except KeyError:
            raise KeyError(
                f"Implementation Error: There is no key '{field}' in structure '{type(self.log)}"
            )

    def processName(self, process_name: str) -> Self:
        self._edit_field("processName", process_name)
        return self

    def eventTime(self, event_time: str) -> Self:
        self._edit_field("eventTime", event_time)
        return self

    def workDir(self, work_dir: str) -> Self:
        self._edit_field("workDir", work_dir)
        return self

    def runHash(self, run_hash: str) -> Self:
        self._edit_field("runHash", run_hash)
        return self

    def errorReport(self, error_report: str) -> Self:
        self._edit_field("errorReport", error_report)
        return self


class FakeReadme:
    @staticmethod
    def get_readme_or():
        README_FILE = Path("docs/scenario_template/Readme.md")
        try:
            with open(README_FILE) as readme:
                return readme.read()
        except IOError as io_error:
            logging.error(f"Error on file '{str(README_FILE)}': {io_error}")
        return f"There is an empty Readme. Use {README_FILE} for a real one"


class FakeScenarioInformation:
    # TODO: generate a real markdown
    # TODO: Generate a complexe parameter
    data = {
        "readme": FakeReadme.get_readme_or(),
        "output": ["results.json"],
        "description": "This is a fake scenario. It cannot do a lot of things, but use it wisely.",
        "scenario_name": "Fake_Scenario",
        "docker_images": [
            {
                "harbor_url": "https://fake_url.fake/my_docker_image_1:latest",
                "full_name": "my_docker_image_1:latest",
            }
        ],
        "parameters": [
            {
                "name": "limit",
                "description": "limit to request",
                "type": "int",
                "default": 5,
            },
            {
                "name": "cluster-algo",
                "description": "Algorithme to use",
                "type": "choices",
                "default": "kmeans",
                "choices": ["kmeans", "dbscan", "mean"],
            },
            {
                "name": "no-gpu",
                "description": "Don't use GPU to compute the model",
                "type": "bool",
            },
            {
                "name": "Index_int",
                "description": "Test parameter for integer",
                "type": "int",
            },
            {
                "name": "Index_float",
                "description": "Test parameter for float",
                "type": "float",
            },
        ],
        "switchable_algorithms": [
            {
                "name": "algorithm_1",
                "description": "This is a fake algorithm, it does ... nothing",
                "template": "/template.nf",
                "nf_variable": "ALGO_1",
            },
            {
                "name": "algorithm_2",
                "description": "This is a fake algorithm, it does ... nothing too",
                "template": "/template2.nf",
                "nf_variable": "ALGO_2",
            },
        ],
    }


class FakeAlgorithmParameter:
    data = {"parameters": FakeScenarioInformation.data["parameters"]}
