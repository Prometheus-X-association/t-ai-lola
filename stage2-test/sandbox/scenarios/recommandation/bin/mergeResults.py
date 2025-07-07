#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

def merge_Final_results(resultFiles, algFileName):
    output_list = {}
    for input_file in resultFiles:
        with open(input_file, "rb") as infile:
            data = json.load(infile)
            output_list.update(data)

    with open(algFileName, "w") as outfile:
        json.dump(output_list, outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate Results of all the algorithms in One File")
    parser.add_argument("-o", "--output", type=Path, help="Path of the final result file")
    parser.add_argument(
        "-r", "--results",
        action="store",
        help="Results of indicators evaluation to compile in json format. This option accept multiple files",
        dest="listparamsindicators",
        type=Path,
        nargs="*",
        default=[],
    )
    args = parser.parse_args()
    merge_Final_results(resultFiles=args.listparamsindicators, algFileName=args.output)
