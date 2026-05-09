#!/usr/bin/env python3

import logging
import time

from dataclasses import dataclass

import mysql.connector
import mysql.connector.errors as mysql_error

from lolapy.tools import settings
from lolapy.dataset import errors as dataset_error


class MySQL:
    """MySQL object used to communicate and run command to a MySQL server.

    The object will read in env variable to find information such as:
    - SQL_HOST_IP: ip adress of the mysql server
    - SQL_HOST_PORT: port of the mysql server
    - SQL_ROOT_USER: username of root account
    - SQL_ROOT_PASSWORD: password for root user
    """

    def __init__(self, database: str = None):
        """Create a MySQL object.

        The constructor need the name of the database.
        The name can be None in order to run command on the whole server (like DB DROP)

        :param database: name of the database to connect.[Default: None]
        :type database: str
        :raise dataset.errors.MySQLConnectionError: If there is an error when trying
        to connecting to the database
        """
        app_settings = settings.get()
        self.host = app_settings.sql_host_ip
        self.port = app_settings.sql_host_port
        self.user = app_settings.sql_root_user
        self.password = app_settings.sql_root_password
        self.database = database
        self.connection = self.__connection_to_mysql()

    def __connection_to_mysql(self) -> mysql.connector.MySQLConnection:
        """Connect to a MySQL database.

        return a mysql.connector.MySQLConnection if success
        """

        timeout = 0
        max_timeout = 5
        mysql_config = {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }
        if self.database:
            mysql_config["database"] = self.database

        while True:
            try:
                cnx = mysql.connector.connect(**mysql_config)
                logging.debug(
                    f"Connection successful to SQL server '{self.host}:{self.port}' with database: '{self.database}'"
                )
                return cnx

            except (
                ConnectionRefusedError,
                mysql_error.InterfaceError,
                mysql_error.DatabaseError,
            ) as err:
                # Problem encounter when MySQL container just start and MySQL is not ready yet
                if timeout == max_timeout:
                    raise dataset_error.MySQLConnectionError(self, str(err))
                else:
                    ## Log something
                    timeout += 1
                    time.sleep(2)

    def run_cmd(self, cmd: str) -> "SQLResults":
        """Run command on a MySQL server.

        Return a SQLResults which hold data
        :param cmd: str MySQL command to run
        :return: docker_trax.mysql_connect.SQLResults: an SQLResults holding data
        :raise:
            error.MySQLCommandError: if there are mistakes in the MySQL command
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(cmd)
            return SQLResults(success=True, data=cursor.fetchall())
        except mysql.connector.errors.ProgrammingError:
            raise dataset_error.MySQLCommandError(cmd)
        except mysql.connector.errors.InterfaceError as e:
            # "No result set to fetch" in request return means that the request have no data to fetch
            # like 'DROP DATABASE ...' request. So return a SQLResults with no data and just success=True
            if "No result set to fetch" not in str(e):
                raise dataset_error.MySQLCommandError(cmd)
            return SQLResults(success=True, data=None)


class TraxDB:
    @staticmethod
    def list_trax_db() -> list:
        MY_SQL_CMD = "SHOW DATABASES"
        mysql = MySQL()
        all_db = mysql.run_cmd(MY_SQL_CMD)
        # the previous command return a list of tuple
        flatten_db = [ii[0] for ii in all_db.data]
        return flatten_db

    @staticmethod
    def create_trax_db(db_name: str):
        MY_SQL_CMD = f"CREATE DATABASE {db_name}"
        mysql = MySQL()
        _ = mysql.run_cmd(MY_SQL_CMD)
        return True


@dataclass
class SQLResults:
    """
    Hold data of MySQL query results.
    data field can be None for request like 'DROP DATABASE' or 'CREATE DATABASE'
    """

    success: bool
    data: list

    def is_success(self):
        return self.success

    def get_data(self):
        return self.data

    def get_integer(self) -> int:
        """Return a unique integer.

        Use this method when sql request return a unique value
        :return: int: unique integer
        """
        return int(self.data[0][0])
