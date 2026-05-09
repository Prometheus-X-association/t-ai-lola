#!/usr/bin/env nextflow
/*
 * Process to evaluate the model ability to predict on unkown data 
*/

process predictionEvaluation {
  
   container = "recom:latest"
    input:
      path real_labels
      path predicted_data
      val path_label  // used to avoid collision in output filename
    output:
    path "evaluation_data_${path_label}.json", emit: DataEvaluation

    """
    evaluate.py --real-labels ${real_labels} \
                --predicted ${predicted_data} \
                --output "evaluation_data_${path_label}.json" \
                --indicators $params.rmse $params.fcp $params.mae $params.mse
    """
}
