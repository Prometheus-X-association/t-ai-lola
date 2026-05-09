#!/usr/bin/env python3

"""Module to Manage information of Slurm jobs.

This module mainly uses the 'sacct' command to get information
"""

from enum import Enum, auto
import time

from lolapy.slurm import errors as slurm_errors
from lolapy.tools import shell_command


class SacctField:
    """Fields of the sacct -l command"""

    FIELD = {
        "JobID": 0,
        "JobIDRaw": 1,
        "JobName": 2,
        "Partition": 3,
        "MaxVMSize": 4,
        "MaxVMSizeNode": 5,
        "MaxVMSizeTask": 6,
        "AveVMSize": 7,
        "MaxRSS": 8,
        "MaxRSSNode": 9,
        "MaxRSSTask": 10,
        "AveRSS": 11,
        "MaxPages": 12,
        "MaxPagesNode": 13,
        "MaxPagesTask": 14,
        "AvePages": 15,
        "MinCPU": 16,
        "MinCPUNode": 17,
        "MinCPUTask": 18,
        "AveCPU": 19,
        "NTasks": 20,
        "AllocCPUS": 21,
        "Elapsed": 22,
        "State": 23,
        "ExitCode": 24,
        "AveCPUFreq": 25,
        "ReqCPUFreqMin": 25,
        "ReqCPUFreqMax": 26,
        "ReqCPUFreqGov": 27,
        "ReqMem": 28,
        "ConsumedEnergy": 29,
        "MaxDiskRead": 30,
        "MaxDiskReadNode": 31,
        "MaxDiskReadTask": 32,
        "AveDiskRead": 33,
        "MaxDiskWrite": 34,
        "MaxDiskWriteNode": 35,
        "MaxDiskWriteTask": 36,
        "AveDiskWrite": 37,
        "AllocGRES": 38,
        "ReqGRES": 39,
        "ReqTRES": 40,
        "AllocTRES": 41,
        "TRESUsageInAve": 42,
        "TRESUsageInMax": 43,
        "TRESUsageInMaxNode": 44,
        "TRESUsageInMaxTask": 45,
        "TRESUsageInMin": 46,
        "TRESUsageInMinNode": 47,
        "TRESUsageInMinTask": 48,
        "TRESUsageInTot": 49,
        "TRESUsageOutMax": 50,
        "TRESUsageOutMaxNode": 51,
        "TRESUsageOutMaxTask": 52,
        "TRESUsageOutAve": 53,
        "TRESUsageOutTot": 54,
    }


class SacctJobStatus(Enum):
    """Conversion of the Job status given by sacct and the real status.

    5 status are finally available:
    - failed
    - cancelled
    - completed
    - running
    - pending
    """

    RUNNING = auto()
    FAILED = auto()
    CANCELLED = auto()
    COMPLETED = auto()
    PENDING = auto()

    @staticmethod
    def from_sacct_status(status: str) -> "SacctJobStatus":
        STATUS = {
            "RUNNING": SacctJobStatus.RUNNING,
            "COMPLETED": SacctJobStatus.COMPLETED,
            "PENDING": SacctJobStatus.PENDING,
            "REQUEUED": SacctJobStatus.PENDING,
            "RESIZING": SacctJobStatus.PENDING,
            "BOOT_FAIL": SacctJobStatus.FAILED,
            "DEADLINE": SacctJobStatus.FAILED,
            "FAILED": SacctJobStatus.FAILED,
            "NODE_FAIL": SacctJobStatus.FAILED,
            "OUT_OF_MEMORY": SacctJobStatus.FAILED,
            "PREEMPTED": SacctJobStatus.FAILED,
            "TIMEOUT": SacctJobStatus.FAILED,
            "CANCELLED": SacctJobStatus.CANCELLED,
        }
        return STATUS[status]


class SlurmJobInfo:
    def __init__(self, job_name: str):
        self.job_name: str = job_name
        self.job_info: list = self.__sacct_info()

    def __sacct_info(self) -> list:
        """Extract information by running sacct and filter according to job_name.

        Running 'sacct -pnl' generate a oneliner information for each jobs. The '-p' option add '|' delimiters between fields.
        The '-n' disable the header and '-l' is to print all values on one line.

        :raise: SacctMissingJob: If no job is available
        :return: str: Information on the job in a one liner format
        """
        command = "sacct -pnl"
        retry = 0
        # Sometimes slurm takes time to queue jobs
        while retry < 5:
            command_result = shell_command.ShellCommand.new(command=command, on_localhost=True).run()
            for line in command_result.stdout.split("\n"):
                # return the job match
                if self.job_name in line:
                    return line.split("|")
            time.sleep(2)
            retry += 1
        raise slurm_errors.JobInfoMissingJob(self.job_name)

    def get_info(self, field: str) -> str:
        """Extract the information from the one liner job get from sacct command.

        :param field: str: Label of the information to get from sacct command

        :raise: JobInfoFieldError: If the field does not exist
        :return: str: Return the value associated to the field.
        """
        if field not in SacctField.FIELD:
            raise slurm_errors.JobInfoFieldError(field)
        return self.job_info[SacctField.FIELD[field]]

    @staticmethod
    def get_job_status(job_name: str) -> "SacctJobStatus":
        """Extract the status name of a job.

        Available status: "failed", "canceled", "completed", "running", "pending"

        :job_name: str: name of the job. Should be unique to avoid conflict.

        :return: str: Status of the job
        """
        job_filter = SlurmJobInfo(job_name)
        slurm_complex_status = job_filter.get_info("State")
        return SacctJobStatus.from_sacct_status(slurm_complex_status)


class SlurmControllerInfo:
    @staticmethod
    def is_idle() -> bool:
        """Check the status of the first node.

        Return True if the status is idle. False otherwise.
        :return: bool: True if the node is in 'idle' state.
        """
        command = "sinfo -lh"
        command_result = shell_command.ShellCommand.new(command=command, on_localhost=True).run()
        if command_result.stdout.split()[8].startswith("idle"):
            return True
        return False
