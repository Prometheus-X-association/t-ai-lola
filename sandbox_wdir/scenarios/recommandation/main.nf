/* 
 * enables modules 
 */
// Include the process to request Data
include { requestData } from "./modules/requestData"

// Include the SVD related Processes: Train, Test , Evaluate
include { svd_train } from "./modules/svdProcess"
include { model_test as svd_test } from "./modules/testProcess"
include { predictionEvaluation as svd_eval} from "./modules/predictionEvaluation"

// Include the process to merge all results in one file
include { mergeResProcess } from "./modules/aggregateResults"

// Load user algorithms
if (params.userModel && params.userTest) {
    include { userModel } from "${params.userModel}"
    include { userTest } from "${params.userTest}"
    include { predictionEvaluation as userEval} from "./modules/predictionEvaluation"
}

workflow {
    /*
    *   Define Channels
    */
    // Contains the path of the test data
    testdataChannel=Channel.from(params.test_data)
    // Contains the path of the true labels
    truelabelsChannel=Channel.from(params.true_labels)
    //create channel that points out the name of the results filename
    fileResultChannel=Channel.from(params.fileResults)

    /*
    *    Computations
    */
   
    requestData()

    svd_train(requestData.out.xapiData)
    svd_test(svd_train.out.svdtrainedmodel, testdataChannel)
    svd_eval(truelabelsChannel, svd_test.out.modelpredictions, "svd")
    svdresultChannel = svd_eval.out.DataEvaluation

    if (params.userModel && params.userTest) {
        userModel(requestData.out.xapiData)
        userTest(userModel.out.user_model, testdataChannel)
        userEval(truelabelsChannel, userTest.out.user_predictions, "user")
        userEvaluationChannel = userEval.out.DataEvaluation
    } else {
        userEvaluationChannel = Channel.empty()
    }

    /*
    * Aggregate Results in one File
    */
    resultChannel = svdresultChannel.mix(userEvaluationChannel)
    
    mergeResProcess(resultChannel.toList())
}
