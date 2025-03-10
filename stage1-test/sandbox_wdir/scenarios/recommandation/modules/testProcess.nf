#!/usr/bin/env nextflow
/*
 * Process to test models on datasets 
*/

process model_test{
    container = "recom:latest"
    input:
      path trained_model
      path data_to_test
    output:
      path "svd_predictions.csv" , emit: modelpredictions
    """
    model_test.py --model ${trained_model} --data-test ${data_to_test} --output svd_predictions.csv
    """
}
