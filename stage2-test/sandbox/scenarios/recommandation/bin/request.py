#!/usr/bin/env python3

from typing import Tuple, List
import sys
import argparse
import requests
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class AppError(Exception):
    def __init__(self, error: str = ""):
        self.error = error

    def __str__(self):
        return self.error


def parse_var(s) -> Tuple[str, str]:
    try:
        key, value = s.split("=")
        return (key, value)
    except ValueError:
        raise AppError(f"Cannot parse {s} parameter. Missing '='. Required format : 'item=value'")


def parse_vars(items):
    """
    Parse a series of key-value pairs and return a dictionary
    """
    # Empty element
    if not items:
        return {}
    d = {}

    for item in items:
        key, value = parse_var(item)
        d[key] = value
    return d


def parse_auth(auth_string: str) -> tuple:
    """Parse and format the authentication given in CLI parameters

    :param auth_string: str: The string given in input of the CLI.
    :return tuple: (user, password)
    :raise AppError: if the format of the auth_string is not correct
    """
    try:
        user, password = auth_string.split(":")
    except ValueError:
        raise AppError("Cannot parse authentification parameter. Use 'user:password' format")
    if not user or not password:
        raise AppError("Empty user or password authentication. Use '--auth user:password'")
    return (user, password)


def fetch_xapi_data(headers: dict, params: dict, auth: tuple, url: str, port: int):
    """Generator which get xAPI data on the LRS.

    Yield dictionnary of data instead of pulling the whole xapi dataset into a list
    Avoid saturating memory (for a 500k statements dataset, decrease memory consumption from 1GB to 120MB)
    """
    if not url.startswith("http"):
        url = f"http://{url}"
    response = requests.get(url=f"{url}:{port}/trax/api/gateway/clients/default/stores/default/xapi/statements", auth=auth, headers=headers, params=params)
    if response.status_code != 200:
        raise AppError(f"Request '{response.request.url}' response: {response.status_code}. Reason: {response.text} ")
    data = response.json()
    if not data:
        raise AppError(f"Request '{response.request.url}' no json data. Reason: {response.text} ")
    yield data["statements"]
    while data.get("more"):
        response = requests.get(url=url+data["more"], auth=auth, headers=headers, params=params)
        data = response.json()
        yield data["statements"]



def parse_data(xapi_data) -> List[Tuple[str, str, int]]:
    """Extract data from xAPI statements.

    Get actor, item, and click number.

    :return: list(tuple(str, str, int)): A list of elements: (actor, item, click_number)
    """
    all_data = []
    
    for statement in xapi_data:
        try:
            actor = statement["actor"]["mbox"]
            item = statement["object"]["id"]
            
            clicks_str = statement["object"]["definition"]["extensions"].get("https://w3id.org/xapi/dod-isd/clicks", "0")
            clicks = int(clicks_str) if isinstance(clicks_str, str) and clicks_str.isdigit() else int(clicks_str) if isinstance(clicks_str, int) else 0
            
            statement_fields = (actor, item, clicks)
            all_data.append(statement_fields)

        except KeyError as e:

            identifier = statement.get("id", "UNKNOWN_ID")
            print(f"Warning: when parsing statement '{identifier}': missing key {e}. Statement ignored.", file=sys.stderr)
    return all_data



def prepare_dataframe(data: List[Tuple[str, str, int]]) -> pd.DataFrame:
    """Generate dataframe based on extracted data.

    :param data: list: List of tuple(str, str, int)
    :return: pandas.DataFrame: the pandas dataframe normalized
    """
    df = pd.DataFrame(data, columns=["actor", "item", "num_click"])
    df[["num_click"]] = MinMaxScaler().fit_transform(df[["num_click"]])

    return df


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description="Request GET to Trax LRS and extract required features from the database"
    )
    argument_parser.add_argument(
        "--headers",
        metavar="KEY=VALUE",
        nargs="+",
        default="X-Experience-API-Version=1.0.3",
        help="headers of the GET request",
    )
    argument_parser.add_argument("-p", "--parameters", metavar="KEY=VALUE", nargs="+", help="Parameters of the requets")

    # Define default as testsuite:password because it's the default for TRAX LRS
    # It's not a good practice to define static value in a script but this program
    # will mainly serve on the LOLA platform
    # changed by azim
    argument_parser.add_argument(
        "-a",
        "--auth",
        metavar="user:password",
        type=str,
        default="traxlrs:aaaaaaaa",
        help="Basic Authentication colon separated",
    )
    argument_parser.add_argument("--url", type=str, help="TRAX LRS url", required=True)
    argument_parser.add_argument("--port", type=str, help="TRAX LRS port", required=True)
    argument_parser.add_argument(
        "-c",
        "--csv",
        type=str,
        required=True,
        help="Path to the CSV Ouptut File",
    )
    if len(sys.argv) == 1:
        argument_parser.print_help()
        sys.exit()
    args = argument_parser.parse_args()
    all_data: List[Tuple[str, str, int]] = []

    try:
        data_generator = fetch_xapi_data(
            headers=parse_vars(args.headers),
            params=parse_vars(args.parameters),
            auth=parse_auth(args.auth),
            url=args.url,
            port=args.port,
        )
        for xapi_data in data_generator:
            all_data.extend(parse_data(xapi_data))
        dataframe = prepare_dataframe(all_data)
        dataframe.to_csv(args.csv, index=False)
        print(f"{dataframe.size} statements saved")
    except AppError as e:
        print(f"Error : {e}", file=sys.stderr)
        sys.exit(1)
