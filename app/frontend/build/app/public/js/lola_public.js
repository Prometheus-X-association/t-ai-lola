$(document).ready(function () {
    let loginWrap = $("#login-wrap");

    function updateAuthTabs() {
        let registerIsActive = $("#tab-2").prop("checked");

        $("#tab-login").attr("aria-selected", registerIsActive ? "false" : "true");
        $("#tab-register").attr("aria-selected", registerIsActive ? "true" : "false");
        $("#login-panel").attr("aria-hidden", registerIsActive ? "true" : "false");
        $("#register-panel").attr("aria-hidden", registerIsActive ? "false" : "true");
    }

    if ($("#formHasError").val() === "1") {
        loginWrap.addClass("register-has-error");
        $("#tab-2").prop("checked", true);
    }

    $("#tab-1, #tab-2").on("change click", function() {
       loginWrap.css("min-height", "");
       updateAuthTabs();
    });

    updateAuthTabs();
});
