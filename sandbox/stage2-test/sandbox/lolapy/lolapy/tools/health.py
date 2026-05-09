#!/usr/bin/env python3

"""Module to get health of lolapy.

It returns the status of the backend.
Actually, there are the following tests:
- Test if the async controller work
- Test if lolapy can access to the sql server
- Test if the slurm controller works

Examples:
    >>> Health.check_status()
    {
        "async_controller": self.async_controller,
        "sql_controller": self.sql_controller,
        "slurm_controller": self.slurm_controller,
    }
"""


import logging
import time

from lolapy.dataset import mysql_connect
from lolapy.dataset import errors as dataset_error
from lolapy.slurm import job_info
from lolapy.bin import async_tasks


class Health:
    def __init__(self):
        """Constructor of Health structure.

        By default, all values are True and will be set to False if the service does not work
        """
        self.async_controller = True
        self.sql_controller = True
        self.slurm_controller = True

    def to_dict(self) -> dict:
        """Serialize the structure into dictionnary"""
        return {
            "async_controller": self.async_controller,
            "sql_controller": self.sql_controller,
            "slurm_controller": self.slurm_controller,
        }

    def _check_database(self) -> bool:
        """Test connection to the database"""
        try:
            mysql_connect.MySQL()
        except dataset_error.MySQLConnectionError:
            logging.warning("Problem to the connection to SQL server")
            return False
        return True

    def _check_slurm_controller(self) -> bool:
        """Test connection of the slurm controller, if slurm is available"""
        try:
            if not job_info.SlurmControllerInfo.is_idle():
                return False
        except FileNotFoundError as e:
            # handle 'sinfo command not found'
            logging.warning(f"Command to check slurm status not available: {str(e)}")
            return False
        return True

    def _check_async_controller(self) -> bool:
        """Test async controller.

        Returns:
            bool: `True` if the controller works, False otherwise.
        """

        # Test if huey works (async tasks)
        # TODO: Rework this method to check status of huey
        # It can fail if huey is really busy
        async_is_running = async_tasks.huey_work()
        attempt = 0
        while attempt < 5:
            attempt += 1
            time.sleep(1)  # Sleep to avoid race condition
            if not async_is_running.get():
                return False
            else:
                return True
        return False

    @staticmethod
    def check_status() -> dict:
        """Test status of the API.

        See docstring of the module to see what the method check
        TODO: manage exceptions in case of unhandled problem
        Returns:
            dict: A dictionnary with all elements tested. The dict has the format of self.health_status
        """
        # Instanciate Class Health
        my_health = Health()
        # test connection to the sql database
        my_health.sql_controller = my_health._check_database()
        # Test slurm controller
        my_health.slurm_controller = my_health._check_slurm_controller()
        # Test async controller
        my_health.async_controller = my_health._check_async_controller()

        return my_health.to_dict()
