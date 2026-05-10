#!/usr/bin/env python3

"""Module to process nextflow logs.

Lolapy catch logs from nextflow, filters information and send to the frontend where
data will be stored. Lolapy don't store logs information.
The entrypoint is the ProcessNextflowLogs object

Nextflow logs -> lolapy -> frontend
"""

from enum import Enum
import logging
from typing import TypedDict

from lolapy.tools import frontend_api


class NextflowLogType(Enum):
    """Enumerate to hold the type of log sended by nextflow.

    Nextflow can send 3 types of logs:
    - Logs for WORKFLOW (or scenario) used to give information on the whole workflow (begin, stop, where to find temporary files).
    - Logs for PROCESS (or algorithm) used to give information of one step of the workflow
    - Logs for ERROR generated when process raise error. These logs are ignored and not processed
    """

    WORKFLOW = 1
    PROCESS = 2
    ERROR = 3


class NextflowLogEvent(Enum):
    """Enumerate to hold the Event type of log.

    Nextflow can send 4 types of event:
    - SUBMIT (only for process). Means that nextflow will process the Job. These logs are ignored
    - RUN (for workflow and process). Means the workflow/process starts
    - DONE (for workflow and process). Means the workflow/process terminates
    - ERROR (for workflow and process). Means the workflow/process got an error
    """

    SUBMIT = 1
    RUN = 2
    DONE = 3
    ERROR = 4


class NextflowLogWorkflow(TypedDict):
    """Format data of Nextflow Workflow logs"""

    logType: str  # type of the log, based on NextflowLogType
    # should be WORKFLOW here
    logEvent: str  # Nextflow event type based on NextflowLogEvent structure
    runHash: str  # Hash unique of the run. Used to identify the run
    eventTime: str  # When the log was generated
    errorReport: str  # Contain the error of the execution


class NextflowLogProcessStatistics(TypedDict):
    """Format data of Nextflow Process statistics"""

    cpu: float  # % of cpu usage
    memory: float  # % of memory usage
    ioWrite: int  # bytes written
    ioRead: int  # bytes read
    duration: int  # process duration in milliseconds


class NextflowLogProcess(TypedDict):
    """Format data of Nextflow Process logs"""

    processName: str  # Name of the process given by Nextflow
    runHash: str  # Hash unique of the run. Used to identify the run
    eventTime: str  # When the log was generated
    workDir: str  # working directory of the process
    statistics: NextflowLogProcessStatistics | None  # statistics of the process
    # If the Process log is SUBMIT or RUN, there is no statistics
    # statistics are defined by NextflowLogProcessStatistics structure


class ProcessNextflowLogs:
    """Main object to process nextflow logs data."""

    @staticmethod
    def process(json_data: dict):
        """Process json data from nextflow and process them according to the environment.

        Entrypoint of the nextflow_logs module.

        :param json_data: dict: Json data from nextflow as dict object
        """
        # Check if the logs have to be processed

        nextflow_log = NextflowLog(json_data=json_data)
        filtered_logs = nextflow_log.filter()
        if filtered_logs:
            logging.info(
                f"Got a nextflow log: {nextflow_log.log_type.name}:{nextflow_log.log_event.name}"
            )
            match nextflow_log.log_type:
                # If there is an error. Trigger event to stop execution
                case NextflowLogType.WORKFLOW:
                    match nextflow_log.log_event:
                        case NextflowLogEvent.ERROR:
                            logging.warning(
                                f"THERE IS AN ERROR IN THE JOB: {filtered_logs['errorReport']}"
                            )  # No problem with errorReport because checked before
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/workflow/error/{filtered_logs['runHash']}",
                                filtered_logs,
                            )
                            frontend_api.FrontendRequest.get(
                                f"/api/scenario/error/{filtered_logs['runHash']}"
                            )
                        case NextflowLogEvent.RUN:
                            logging.info(
                                f"The workflow is running: {filtered_logs['runHash']}"
                            )
                            frontend_api.FrontendRequest.get(
                                f"/api/scenario/start/nextflow/{filtered_logs['runHash']}"
                            )
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/workflow/run/{filtered_logs['runHash']}",
                                filtered_logs,
                            )
                        case NextflowLogEvent.DONE:
                            logging.info(
                                f"The workflow is complete: {filtered_logs['runHash']}"
                            )
                            frontend_api.FrontendRequest.get(
                                f"/api/scenario/complete/nextflow/{filtered_logs['runHash']}"
                            )
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/workflow/done/{filtered_logs['runHash']}",
                                filtered_logs,
                            )
                case NextflowLogType.PROCESS:
                    match nextflow_log.log_event:
                        case NextflowLogEvent.SUBMIT:
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/process/submit/{filtered_logs['runHash']}",
                                filtered_logs,
                            )
                        case NextflowLogEvent.RUN:
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/process/run/{filtered_logs['runHash']}",
                                filtered_logs,
                            )
                        case NextflowLogEvent.DONE:
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/process/done/{filtered_logs['runHash']}",
                                filtered_logs,
                            )
                        case NextflowLogEvent.ERROR:
                            frontend_api.FrontendRequest.post(
                                f"/api/scenario/process/error/{filtered_logs['runHash']}",
                                filtered_logs,
                            )


class NextflowLog:
    """Class used to parse and store nextflow log."""

    def __init__(self, json_data: dict):
        """Create a NextflowLog object.

        :param json_data: dict: json nextflow log
        """
        self.json_data = json_data
        self.log_type = self._get_log_type()
        self.log_event = self._get_log_event()

    def _get_log_type(self) -> "NextflowLogType":
        """Return the type of nextflow log.

        If the json contains the label "metadata", it's log about the workflow.
        If it contains the label "trace", it's log for process.
        Otherwise it's log for ERROR

        :return: NextflowLogType: the type of the log
        """
        if "metadata" in self.json_data.keys():
            return NextflowLogType.WORKFLOW
        if "trace" in self.json_data.keys():
            return NextflowLogType.PROCESS
        return NextflowLogType.ERROR

    def _get_log_event(self) -> "NextflowLogEvent":
        """Return the event of the nextflow log.

        :return: NextflowLogEvent: the event log of the log
        """
        status_to_event = {
            "process_completed": NextflowLogEvent.DONE,
            "completed": NextflowLogEvent.DONE,
            "error": NextflowLogEvent.ERROR,
            "process_started": NextflowLogEvent.RUN,
            "started": NextflowLogEvent.RUN,
            "process_submitted": NextflowLogEvent.SUBMIT,
        }

        log_event = status_to_event[self.json_data["event"]]

        # When nextflow has process/workflow FAILED, it send a complete event
        # So we have to check DONE event is really done and not ERROR
        if log_event == NextflowLogEvent.DONE:
            if (
                self.log_type == NextflowLogType.WORKFLOW
                and self.json_data["metadata"]["workflow"]["errorMessage"]
            ):
                return NextflowLogEvent.ERROR
            if (
                self.log_type == NextflowLogType.PROCESS
                and self.json_data["trace"]["status"] == "FAILED"
            ):
                return NextflowLogEvent.ERROR

        return log_event

    def filter(self):
        """Filter information from the JSON to send to the frontend.

        Entrypoint to the NextflowLog object. Used to
        remove sensitive data. Return None if there is no json to process.
        """
        if self.log_type == NextflowLogType.PROCESS:
            return self._filter_process_logs()
        elif self.log_type == NextflowLogType.WORKFLOW:
            return self._filter_workflow_logs()
        else:
            return None

    def _filter_workflow_logs(self) -> NextflowLogWorkflow:
        """Filter information for WORKFLOW logs.

        Example of logs for workflow: https://www.nextflow.io/docs/latest/tracing.html#weblog-started-example-message
        Return a json in the format
        {
          "logType": "workflow",
          "logEvent": "run"|"done"|"error",
          "runHash": "name of the run given by the frontend (hash identifier)",
          "eventTime": "YYYY-MM-DDTHH:MM:SSZ",
          "errorReport": null|"Error message or error logs"
        }
        """
        output_log: NextflowLogWorkflow = {
            "logType": self.log_type.name.lower(),
            "logEvent": self.log_event.name.lower(),
            "runHash": self.json_data["runName"],
            "eventTime": self.json_data["utcTime"],
            "errorReport": self.json_data["metadata"]["workflow"]["errorReport"],
        }

        return output_log

    def _filter_process_logs(self) -> NextflowLogProcess:
        """Filter information for PROCESS logs.

        Example log for process https://www.nextflow.io/docs/latest/tracing.html#weblog-completed-example-message
        {
          "runHash": "name of the run given by the frontend (hash identifier)",
          "eventTime": "YYYY-MM-DDTHH:MM:SSZ",
          "workDir": "path of the working directory. Used to find output results",
          "statistics": null|{
            "%cpu": float,
            "%memory": float,
            "ioWrite": int,
            "ioRead": int,
            "duration": int,
          }
        }
        """
        logging.warning(self.json_data)
        # machine traces are only available when job complete
        log_statistics: NextflowLogProcessStatistics | None = None
        if self.log_event == NextflowLogEvent.DONE:
            log_statistics: NextflowLogProcessStatistics | None = {
                "cpu": self.json_data["trace"]["%cpu"],
                "memory": self.json_data["trace"]["%mem"],
                "ioWrite": self.json_data["trace"]["write_bytes"],
                "ioRead": self.json_data["trace"]["read_bytes"],
                "duration": self.json_data["trace"]["duration"],
            }
        output_log: NextflowLogProcess = {
            "processName": self.json_data["trace"]["process"],
            "runHash": self.json_data["runName"],
            "eventTime": self.json_data["utcTime"],
            "workDir": self.json_data["trace"]["workdir"],
            "statistics": log_statistics,
        }

        return output_log
