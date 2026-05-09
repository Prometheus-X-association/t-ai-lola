$(document).ready(function () {

    /*
     * activate datatable for the element with .dt-basic class'
     */
    $(".dt-basic").DataTable({
        "stateSave": true,
        "pageLength": 25
    });
    /*
     * activate select2 component for all dropdown
     */
    $("select").select2({
        dropdownAutoWidth: true
    });

    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: 'textarea:not(.no-richtext)',
            height: "500"
        });
    }

    /*
     * activate popover everywhere
     */
    $(function () {
        $('[data-toggle="popover"]').popover({
            html: true
        });
    })

    /**
     * Apply json formatting
     */
    function isJsonString(str) {
        try {
            JSON.parse(str);
        } catch (e) {
            return false;
        }
        return true;
    }    
    $(".format_json").each(function () {
        let data = $(this).html();
        if( isJsonString(data) ) {
            $(this).html(syntaxHighlight(JSON.stringify($.parseJSON(data), undefined, 4)));
        }       
    });

    function sanitize(string) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            "/": '&#x2F;',
        };
        const reg = /[&<>"'/]/ig;
        return string.replace(reg, (match) => (map[match]));
    }

    function syntaxHighlight(json) {
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            var cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    $("a[id^='button_modal_dataset_']").on('click', function () {

        let hash = $(this).attr('data-hash');

        $.ajax({
            url: window.location.origin + "/dashboard/dataset/ajax/show/" + hash,
            method: "GET",
            dataType: "json",
            complete: function (data) {
                if (isJsonString(data.responseText)) { 
                    let datasetStat = $.parseJSON(data.responseText);
                    if (datasetStat !== null) {
                        $("#modal_dataset_detail_totalstatements_" + hash).html("<strong>Statements</strong> : " + datasetStat.statements_number);
                        $("#modal_dataset_detail_uniqueactor_" + hash).html("<strong>Nombre d'acteurs</strong> : " + datasetStat.unique_actor_number);
                        $("#modal_dataset_detail_uniqueverb_" + hash).html("<strong>Nombre d'objets</strong> : " + datasetStat.unique_verbs_number);
                            $("#modal_dataset_detail_statements_" + hash).html(syntaxHighlight(JSON.stringify(datasetStat.statements, undefined, 4)));
                    } else {
                        $("#modal_dataset_detail_totalstatements_" + hash).html("<strong>-</strong>");
                        $("#modal_dataset_detail_uniqueactor_" + hash).html("<strong>-</strong>");
                        $("#modal_dataset_detail_uniqueverb_" + hash).html("<strong>-</strong>");
                        $("#modal_dataset_detail_statements_" + hash).html("Une erreur est survenue lors de la récupération des données. API non disponible.");
                    }
                }
            }
        })
    });

    // selection of the dataset before the execution of a scenario
    // and check if the button to next step must be activated
    $(".btn-scenario-execute-dataset").on('click', function () {
        selectedDataset = $(this);
        $(".btn-scenario-execute-dataset").each(function () {
            $(this).addClass("btn-outline-success");
            $(this).removeClass("btn-success");
            $(this).removeClass("btn-success");
        });
        selectedDataset.removeClass("btn-outline-success");
        selectedDataset.addClass("btn-success");

        // check if dataset + tag are selected to enable the button to next step
        $(".btn-scenario-execute-dataset").each(function () {
            $("#hidden_tag_hash").val($('input[name=tag]:checked', '#radioTag').attr('data-hash'));
            if( $(this).hasClass("btn-success") && $.type($('input[name=tag]:checked', '#radioTag').attr('data-hash')) !== 'undefined' ) {
                $("#btn_scenario_execute_step2").prop('disabled', false);
                // set the hidden field
                $("#hidden_dataset_hash").val($(this).attr('data-hash'));
            }
        });
    });
    
    // check if the button to next step must be activated
    $("input[name=tag]").on('click', function () {        
        $(".btn-scenario-execute-dataset").each(function () {
            $("#hidden_tag_hash").val($('input[name=tag]:checked', '#radioTag').attr('data-hash'));
            if( $(this).hasClass("btn-success") && $.type($('input[name=tag]:checked', '#radioTag').attr('data-hash')) !== 'undefined' ) {
                $("#btn_scenario_execute_step2").prop('disabled', false);
                // set the hidden field
                $("#hidden_dataset_hash").val($(this).attr('data-hash'));
            }
        });
    });

});