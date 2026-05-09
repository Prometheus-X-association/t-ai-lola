#!/usr/bin/env python3
import argparse
import ast
import pickle
import sys

import pandas as pd
from surprise import SVD, Dataset, Reader

def train_svd(alg_params, train_data, trained_model_name):
    # Create model instance using Surprise library
    model_svd = SVD(
        n_factors=int(alg_params[0]),
        n_epochs=int(alg_params[1]),
        biased=alg_params[2],
        init_mean=int(alg_params[3]),
        init_std_dev=float(alg_params[4]),
        lr_all=float(alg_params[5]),
        # reg_all=float(alg_params[6]),
        reg_all=float(alg_params[6]) if alg_params[6] not in [None, "None"] else 0.0,  # Default to 0.0
        lr_bu=ast.literal_eval(alg_params[7]),
        lr_bi=ast.literal_eval(alg_params[8]),
        lr_pu=ast.literal_eval(alg_params[9]),
        lr_qi=ast.literal_eval(alg_params[10]),
        reg_bu=ast.literal_eval(alg_params[11]),
        reg_bi=ast.literal_eval(alg_params[12]),
        reg_pu=ast.literal_eval(alg_params[13]),
        reg_qi=ast.literal_eval(alg_params[14]),
        random_state=ast.literal_eval(alg_params[15]),
    )
    df_train = pd.read_csv(train_data)
    # As we're loading a custom dataset, we need to define a reader.
    reader = Reader(line_format="user item rating", sep=",", rating_scale=(0, 1))
    data = Dataset.load_from_df(df_train, reader=reader)
    trainset = data.build_full_trainset()
    model_svd.fit(trainset)
    pickle.dump(model_svd, open(trained_model_name, "wb"))


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Train the svd model")
    argument_parser.add_argument(
        "-p",
        "--parameters",
        action="store",
        required=True,
        type=str,
        nargs="*",
        default=[],
        help="List params of the algorithm",
    )
    argument_parser.add_argument("-i", "--input", required=True, type=str, help="Path of input csv file")
    argument_parser.add_argument(
        "-m", "--model", required=True, type=str, help="Path of the generated model in Pickle Python format"
    )
    if len(sys.argv) == 1:
        argument_parser.print_help()
        sys.exit()

    args = argument_parser.parse_args()
    train_svd(alg_params=args.parameters, train_data=args.input, trained_model_name=args.model)
