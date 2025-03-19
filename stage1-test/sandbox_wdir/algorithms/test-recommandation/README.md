# Algorithm for tests Data for Recommandation scenario

## Requirements

Use the Dockerfile or install environment with dependencies (see Dockerfile for information)

## Build docker image

``` sh
docker build -t test_recom .
```

## Usage

``` sh
model_test.py --m path_input_trained_model --t path_input_data_to_test --f path_prediction_output
```
