#!/usr/bin/env nextflow
/*
 * Process to aggregate results for one Algorithm
*/

process mergeResProcess {
    container = "recom:latest"
    input:
    path indicators_values
    output:
    path "output.json" , emit: alg_FinalResults
"""
mergeResults.py --results ${indicators_values} --output output.json
"""
}
