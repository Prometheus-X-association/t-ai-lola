# SVDpp Algorithm for Recommandation scenario

Use this algorithm with 

## Requirements

Use the Dockerfile or install environment with dependencies (see Dockerfile for information)

## Build docker image

``` sh
docker build -t svdpp_recom .
```

## Usage

``` sh
./svdpp_train.py --p 20 20 0 0.1 0.007 0.02 None None None None None None None None None None None --a input_data.csv --m output_model 
```
