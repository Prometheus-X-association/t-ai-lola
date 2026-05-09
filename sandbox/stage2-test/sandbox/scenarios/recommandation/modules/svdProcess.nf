#!/usr/bin/env nextflow
/*
 * Process to train SVD model on data collected from the LRS
*/
process svd_train{
    container = "recom:latest"
    input:
      path xapi_data
    output:
      path generated_model, emit: svdtrainedmodel

    """
    svd_train.py --parameters $params.svd_n_factors $params.svd_n_epochs $params.svd_biased $params.svd_init_mean $params.svd_init_std_dev $params.svd_lr_all $params.svd_reg_all $params.svd_lr_bu $params.svd_lr_bi $params.svd_lr_pu $params.svd_lr_qi $params.svd_reg_bu $params.svd_reg_bi $params.svd_reg_pu $params.svd_reg_qi $params.svd_random_state \
                 --input ${xapi_data} \
                 --model generated_model
    """
}

