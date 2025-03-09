#!/usr/bin/env python3

from src import *


class Env:
    """
    Object holding variables of the env files
    Read the file first and store vars in a dictionnary
    Use the get method to access variables

    The .env file should be in the format
    '''
    #comment
    myvariable=myvalue
    blablabla=5

    tutu=./home/toto
    '''
    """

    def __init__(self, env_file: str):
        """
        Constructor for the Env object
        :param env_file: Path of the environment file
        :type env_file: str
        """

        self.__env_file = env_file
        self.__env_variables = self.__read_file()

    def __read_file(self):
        """
        Read env file and extract variables
        :return: Variables of the file
        :rtype: dict
        """
        env_vars = {}
        try:
            with open(self.__env_file) as i_buffer:
                for line in i_buffer:
                    if line.startswith("#") or not line.strip() or line.startswith(" "):
                        continue
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
        except OSError as e:
            error("When reading env file: '{}': {}".format(self.__env_file, e))
        except ValueError as e:
            warning(
                "Cannot parse line: '{}' in env file '{}'".format(line, self.__enf_file)
            )

        return env_vars

    def get(self, key):
        """
        Obtain value of the variables in the env file
        Return values as string

        :param key: Variable to search
        :type key: str
        :return: Values
        :rtype: str
        """
        if key not in self.__env_variables:
            error("'{}' not in env file".format(key))

        return self.__env_variables[key]
