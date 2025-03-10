# Algorithm for tests Data for Recommandation scenario

Use this algorithm with [recommendation new version](https://gitlab.inria.fr/lola/scenarios/recommendation_new_version)

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
