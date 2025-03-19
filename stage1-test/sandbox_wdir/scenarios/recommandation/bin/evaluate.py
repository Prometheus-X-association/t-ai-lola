#!/usr/bin/env python3

from typing import List
from surprise import accuracy
import argparse
import sys
import pandas as pd
import re
import json

class Indicators:
    indicators = {
        "rmse": accuracy.rmse,
        "fcp": accuracy.fcp,
        "mae": accuracy.mae,
        "mse": accuracy.mse,
    }

    @classmethod
    def get_indicators(cls) -> List[str]:
        """Return the list of available and supported indicators"""
        return list(cls.indicators.keys())

    @classmethod
    def method_from_indicator(cls, indicator: str) -> callable:
        """Return the compute method associated with the indicator"""
        if indicator not in cls.indicators:
            raise KeyError(f"The '{indicator}' is not supported")
        return cls.indicators[indicator]


def calculate_indicators(true_labels, predicted_labels, filenameResults, listIndicators):
    counter = re.search(r"(\w*)_(\w*)", predicted_labels)
    counter_str = counter.group(1)
    df_true_label = pd.read_csv(true_labels, delimiter=";")
    df_predicted = pd.read_csv(predicted_labels)
    df_predicted["rui"] = df_true_label["rui"]

    dataJson = {}
    dataJson[counter_str] = []
    for indicator in listIndicators:
        method_indicator = Indicators.method_from_indicator(indicator)
        calculate_indicator(df_predicted, indicator.upper(), method_indicator, dataJson[counter_str])

    with open(filenameResults, "w") as outfile:
        json.dump(dataJson, outfile, indent=4)


def calculate_indicator(predict_df, indicator, func, datadf):
    data = []
    predict_list = predict_df.values.tolist()
    computedindicator = func(predict_list)
    data.append([1, computedindicator])
    df_path = pd.DataFrame(data, columns=["predicted_labels", indicator])
    datadf.append({indicator: df_path[indicator].tolist()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate  indicators")
    parser.add_argument("-r", "--real-labels", required=True, type=str, help="Path of CSV file with real labels")
    parser.add_argument("-p", "--predicted", required=True, type=str, help="Path of file with predictions")
    parser.add_argument("-o", "--output", required=True, type=str, help="Path of the output file with evaluation")
    parser.add_argument(
        "-i",
        "--indicators",
        choices=Indicators.get_indicators(),
        required=True,
        type=str,
        nargs="*",
        help="List of indicators to calculate",
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()
    calculate_indicators(
        true_labels=args.real_labels, predicted_labels=args.predicted, filenameResults=args.output, listIndicators=args.indicators
    )
