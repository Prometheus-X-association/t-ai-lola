#!/usr/bin/env python3

import pickle
import argparse
import pandas as pd
import sys
import os

def model_test(trained_model, test_data, predictions_file):
    df_test = pd.read_csv(test_data, delimiter=";")
    testset = df_test.to_records(index=False)
    result = list(testset)
    loaded_model = pickle.load(open(trained_model, "rb"))
    # faire des prédictions en utilisant ce modèle
    predictions = list()
    for i in range(len(result)):
        print(result[i][0], result[i][1])
        predictions.append(loaded_model.predict(result[i][0], result[i][1]))

    df = pd.DataFrame(predictions, columns=["uid", "iid", "rui", "est", "details"])
    df.to_csv(predictions_file, index=False)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Test a final model")
    argument_parser.add_argument("-m", "--model", required=True, type=str, help="Path of the model in Pickle Python format")
    argument_parser.add_argument("-t", "--data-test", required=True, type=str, help="Path of the input data to test in CSV format")
    argument_parser.add_argument("-o", "--output", required=True, type=str, help="Path of the output file with predicted labels")

    if len(sys.argv) == 1:
        argument_parser.print_help()
        sys.exit()
    args = argument_parser.parse_args()
    
    # Test the model and generates predictions
    model_test(trained_model=args.model, test_data=args.data_test, predictions_file=args.output)
