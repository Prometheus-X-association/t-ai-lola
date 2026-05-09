#!/usr/bin/env python3

"""Fetch information on Dataset."""

import json
from typing import TypedDict

from lolapy.tools.frontend_api import FrontendRequest
from lolapy.dataset import errors as dataset_error
from lolapy.dataset import mysql_connect


class DataStatements(TypedDict):
    """Data returned by the object DatasetInformation to the frontend.

    Use type definition on it to avoid messing between None values and real values
    """

    statements_number: int | None
    statements: list[dict] | None
    unique_actor_number: int | None
    unique_verbs_number: int | None


class DatasetInformation:
    """Object use to fetch information on a database based on its name."""

    def __init__(self, dataset_hash: str):
        """Constructor of DatasetInformation.

        Fetch data on a specific dataset.
        :dataset_hash: str: Hash unique of the dataset
        """
        self.dataset_hash = dataset_hash
        # Instanciate to None all fields. They will be set in get_dataset_information method
        self.dataset_information: DataStatements = {
            "statements_number": None,
            "statements": None,
            "unique_actor_number": None,
            "unique_verbs_number": None,
        }

    def get_size(self) -> int:
        """Return the complete size of the database for the dataset.

        Returns:
            int: Size of the database in MegaBytes
        """
        sql_connect = mysql_connect.MySQL()

        raw_statements = sql_connect.run_cmd(
            f'SELECT table_schema, ROUND(SUM(data_length + index_length) / 1024 / 1024, 1)\
        "DB Size in MB"  FROM information_schema.tables WHERE table_schema="{self.dataset_hash}";'
        )

        # sql return a tuple of tuple. So we have to flat to get the information
        # All statements have to be deserialize in json (json.loads) to avoid problems when serialize in the request response
        return int(raw_statements.data[0][1])

    def get_dataset_info(self, user_hash: str) -> DataStatements:
        """Return 5 statements on a dataset and unique terms.

        Used by the frontend to print a preview of a dataset. The method
        connects directly to the database and does not use Trax API.

        return a dictionnary with following information
            dataset_information = {
                "statements_number": int (number of statements),
                "statements": dict (statements),
                "unique_actor_number": int (number of unique actors),
                "unique_verbs_number": int (number of unique verbs),
            }

        :param user_hash: str: Hash unique of the user. Used when checking permission
        :return: DataStatements: the dictionnary presented above
        :raise error.DatasetPermissionDenied: If the user have no permission on the dataset
        """

        # Check if the user have permissions on the database
        # If frontend api return a 200, data are good, otherwise it will return 400
        has_permission = FrontendRequest.dataset_permission(
            user_hash, self.dataset_hash
        )
        if not has_permission:
            raise dataset_error.DatasetPermissionDenied(
                dataset=self.dataset_hash, user=user_hash
            )

        if not self.dataset_hash in mysql_connect.TraxDB.list_trax_db():
            raise dataset_error.DatasetDoesNotExist(self.dataset_hash)

        self.dataset_information["statements"] = self.get_statements(5)
        self.dataset_information["statements_number"] = self.get_number_statements()
        self.dataset_information["unique_actor_number"] = self.get_number_actors()
        self.dataset_information["unique_verbs_number"] = self.get_number_verbs()

        return self.dataset_information

    def get_statements(self, number: int) -> "list[dict]":
        sql_connect = mysql_connect.MySQL(database=self.dataset_hash)

        # Extract 5 first statements
        raw_statements = sql_connect.run_cmd(
            f"SELECT data FROM trax_xapiserver_statements LIMIT {number}"
        )

        # sql return a tuple of tuple. So we have to flat to get the information
        # All statements have to be deserialize in json (json.loads) to avoid problems when serialize in the request response
        statements = [json.loads(jj[0]) for jj in raw_statements.data]
        return statements

    def get_number_verbs(self) -> int:
        """Return the number of unique verbs in the dataset."""
        return self.__get_into_mysql("SELECT COUNT(*) FROM trax_xapiserver_activities")

    def get_number_actors(self) -> int:
        """Return the number of unique actors in the dataset."""
        return self.__get_into_mysql("SELECT COUNT(*) FROM trax_xapiserver_agents")

    def get_number_statements(self) -> int:
        """Return the number of statements in the dataset."""
        return self.__get_into_mysql("SELECT COUNT(*) FROM trax_xapiserver_statements")

    def __get_into_mysql(self, sql_request: str) -> int:
        """Execute the simple mysql request and extract the return integer."""
        sql_connect = mysql_connect.MySQL(database=self.dataset_hash)
        raw_statements = sql_connect.run_cmd(sql_request)
        return raw_statements.get_integer()


class DatasetRemove:
    def __init__(self, dataset_hash: str):
        self.dataset_hash = dataset_hash

    def remove(self, user_hash: str):
        # Check if the user have permissions on the database
        # If frontend api return a 200, data are good, otherwise it will return 400
        has_permission = FrontendRequest.dataset_permission(
            user_hash, self.dataset_hash
        )
        if not has_permission:
            raise dataset_error.DatasetPermissionDenied(
                dataset=self.dataset_hash, user=user_hash
            )

        if not self.dataset_hash in mysql_connect.TraxDB.list_trax_db():
            raise dataset_error.DatasetDoesNotExist(self.dataset_hash)

        sql_connect = mysql_connect.MySQL(database=self.dataset_hash)
        _ = sql_connect.run_cmd(f"DROP DATABASE {self.dataset_hash}")
