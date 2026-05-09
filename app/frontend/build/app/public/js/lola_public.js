$(document).ready(function () {

    $("#tab-1").click(function() {
       $("#login-wrap").css("min-height","520px");
    });

    $("#tab-2").click(function() {
       let size = $("#formHasError").val() === "1" ? "850px" : "760px";
       $("#login-wrap").css("min-height", size);
    });

});

// Registering error on form
if( $("#formHasError").val() === "1" ) {
    $("#tab-2").click();
    $("#login-wrap").css("min-height","850px");
}
