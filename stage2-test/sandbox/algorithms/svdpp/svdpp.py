#!/usr/bin/env python3

from surprise import SVDpp
import pickle
import argparse
import pandas as pd
import sys
from surprise import Reader
from surprise import Dataset

def train_svdpp(alg_params, train_data,trained_model_name):
    model_svdpp = SVDpp(n_factors=int(alg_params[0]),
        n_epochs=int(alg_params[1]),
        init_mean=int(alg_params[2]),
        init_std_dev =float(alg_params[3]),
        lr_all=float(alg_params[4]),
        reg_all=float(alg_params[5]),
        lr_bu=eval(alg_params[6]),
        lr_bi=eval(alg_params[7]),
        lr_pu=eval(alg_params[8]),
        lr_qi=eval(alg_params[9]),
        lr_yj=eval(alg_params[10]),
        reg_bu=eval(alg_params[11]),
        reg_bi=eval(alg_params[12]),
        reg_pu=eval(alg_params[13]),
        reg_qi=eval(alg_params[14]),
        reg_yj=eval(alg_params[15]),
        random_state=eval(alg_params[16]))

    df_train=pd.read_csv(train_data)
    # As we're loading a custom dataset, we need to define a reader.
    reader = Reader(line_format='user item rating', sep=',',rating_scale=(0, 1))
    data = Dataset.load_from_df(df_train, reader=reader)
    trainset=data.build_full_trainset()
    model_svdpp.fit(trainset)
    #save the trained model
    pickle.dump(model_svdpp, open(trained_model_name, 'wb'))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train the svdpp model')
    parser.add_argument("--p", action='store', dest='listparamsAlg',type=str, nargs='*', default=[],help="List params of the algorithm")
    parser.add_argument("--a",type=str,help=" The Path to trainset file")
    parser.add_argument("--m", type=str, help="The filename to save the trained model")
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    train_svdpp(alg_params=args.listparamsAlg,
        train_data=args.a,
        trained_model_name=args.m
        )
