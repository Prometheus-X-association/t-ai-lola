#!/usr/bin/env nextflow
/*
 * Process to retrieve data from the LRS
*/

/*
 * Format the header of the request based on given parameters
 * It generate a string like : '--headers param1=value1 param2=value2 ...'
/*/
if (params.headers) {
    header_parameter = "--header " + params.headers.join(" ")
} else {
    header_parameter = ""
}

/*
 * Format the parameters of the request
 * It generate a string like : '--parameters param1=value1 param2=value2 ...'
/*/
if (params.parameters) {
    request_parameter = "--parameters " + params.parameters.join(" ")
} else {
    request_parameter = ""
}

process requestData{
    container = "recom:latest"

    cpus 1
    memory '500 MB'

    output:
    path "xapi_data.csv", emit: xapiData

"""
request.py $header_parameter \
           $request_parameter \
           --auth "$params.lrsUser:$params.lrsPassword" \
           --url $params.lrsHost --port $params.lrsPort --csv xapi_data.csv
"""
}
