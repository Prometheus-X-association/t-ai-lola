#!/usr/bin/env python3

"""Module used to manage and get information on the computing cluster

It run slurm commands (squeue, sinfo) on the local machine in order to get information on the
cluster usage.

LIMITATIONS:
    - Works only if 1 cluster is register on the platform. See TODO for info

TODO: Manage multiple cluster servers.
    Actually, getting cpu_information and memory_information return only one
    line (because there is only 1 cluster on the platform) so it works. But in
    case of multiple cluster, it's needed to parse all lines and associates
    cpu/memory information to the good machine.
    This can be solved by mapping the cluster_name with informations. But it
    requires to update the frontend parser.
"""

from __future__ import annotations
import logging
from typing import Tuple, Dict

from pydantic import BaseModel

from lolapy.tools import shell_command


class ClusterUsage(BaseModel):
    slurm_pending_job: int | None
    slurm_running_job: int | None
    cpu_total: int | None
    cpu_usage: int | None
    memory_usage: float | None
    memory_total: float | None

    @staticmethod
    def _cpu_information() -> Tuple[int | None, int | None]:
        """Run slurm command to get the cpu usage.

        If encounter an error, return (None, None) and log to the warning

        Returns:
            Return a tuple with (cpu_used, cpu_total). If there is an error,
            returns (None, None).
        """
        # -o to get information on all CPUs
        # -h to remove the header of the command
        # The command return A/I/O/T
        # A: Allocated
        # I: Idle (waiting CPUs)
        # O: Other (don't know what that mean)
        # T: Total
        command = "sinfo -o %C -h"
        try:
            cmd_result = shell_command.ShellCommand.new(command=command, on_localhost=True).run()
        except FileNotFoundError:
            logging.error(f"Error when fetching cluster information. No `sinfo` command on the localmachine")
            return (None, None)
        if cmd_result.exit_code != 0:
            logging.warning(f"Error while running sinfo command ({command}) : {cmd_result.stderr}")
            return (None, None)
        try:
            a_value, _i_value, _o_value, t_value = [int(ii) for ii in cmd_result.stdout.split("/")]
        except ValueError:
            logging.warning(
                f"Error while parsing sinfo return ({command}) : {cmd_result.stdout}. Expect int/int/int/int"
            )
            return (None, None)

        return (a_value, t_value)

    @staticmethod
    def _memory_information() -> Tuple[int | None, int | None]:
        """Run slurm command to get the memory usage.

        If encounter an error, return (None, None) and log to the warning

        Returns:
            Return a tuple with (memory_used, memory_total). If there is an error,
            returns (None, None).
        """
        # -O to get information on all CPUs
        # -h to remove the header of the command
        # The command return "M          T"
        # M: Memory used on the cluster (by slurm, not real memory)
        # T: Total memory
        command = "sinfo -O AllocMem,Memory -h"
        try:
            cmd_result = shell_command.ShellCommand.new(command=command, on_localhost=True).run()
        except FileNotFoundError:
            logging.error(f"Error when fetching cluster information. No `sinfo` command on the localmachine")
            return (None, None)
        if cmd_result.exit_code != 0:
            logging.warning(f"Error while running sinfo command ({command}) : {cmd_result.stderr}")
            return (None, None)
        try:
            # string.split() removes all whitespaces
            m_value, t_value = [int(ii) for ii in cmd_result.stdout.split()]
        except ValueError:
            logging.warning(
                f"Error while parsing sinfo return ({command}) : {cmd_result.stdout}. Expect 'int      int'"
            )
            return (None, None)

        return (m_value, t_value)

    @staticmethod
    def _slurm_job_information() -> Dict[str, int|None]:
        """Run slurm command to get the number of pending/running slurm job.

        If encounter an error, return {"pending": None, "running": None} and
        log to the warning

        Returns:
            Return a dict with "pending" and "running" keys and number of jobs (int) as items.
            If there is an error, returns {"pending": None, "running": None}.
        """
        # -t: filters jobs. Avoid cancelled jobs
        # -r: array to force printing 1 job per line
        # -h: to remove the header of the command
        # The command return
        #   237   compute   stress lolauser PD       0:00      1 (Resources)
        #   238   compute   stress lolauser PD       0:00      1 (Priority)
        #   235   compute   stress lolauser  R       0:32      1 cluster-lola
        #   236   compute   stress lolauser  R       0:32      1 cluster-lola
        #   231   compute   stress lolauser  R       0:36      1 cluster-lola
        #   ...
        # 5th fields is the status of the job
        #   PD: Pending
        #   R : Running
        jobs_status = {"pending": 0, "running": 0}
        command = "squeue -t pending,running -h -r"
        try:
            cmd_result = shell_command.ShellCommand.new(command=command, on_localhost=True).run()
        except FileNotFoundError:
            logging.error(f"Error when fetching cluster information. No `squeue` command on the localmachine")
            return dict.fromkeys(jobs_status, None)
        if cmd_result.exit_code != 0:
            logging.warning(f"Error while running squeue command ({command}) : {cmd_result.stderr}")
            return dict.fromkeys(jobs_status, None)
        stdout_lines = [ii for ii in cmd_result.stdout.splitlines()]
        for line in stdout_lines:
            # string.split() removes all whitespaces
            splitted_line = line.split()
            match splitted_line[5]:
                case "PD":
                    jobs_status["pending"] += 1
                case "R":
                    jobs_status["running"] += 1
                case _:
                    logging.debug(f"Job {line} has an unsupported status : {splitted_line[5]}")
        return jobs_status

    @classmethod
    def get(cls):
        """Build a new ClusterUsage object and get all information.

        This should be cached to avoid running a lot of commands in parallel.
        """

        cpu_usage, cpu_total = cls._cpu_information()
        mem_usage, mem_total = cls._memory_information()
        job_status = cls._slurm_job_information()

        return cls(
            slurm_pending_job=job_status["pending"],
            slurm_running_job=job_status["running"],
            cpu_total=cpu_total,
            cpu_usage=cpu_usage,
            memory_usage=mem_usage,
            memory_total=mem_total,
        )
