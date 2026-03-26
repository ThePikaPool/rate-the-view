$(document).ready(function() {

    function checkPasswords() {
        const password1 = $("#password1").val();
        const password2 = $("#password2").val();
        
        if (!password1 && !password2) {
            $("#password-message").text("");
        } else if (password1 === password2) {
            $("#password-message").text("Passwords match").css("color", "green");
        } else {
            $("#password-message").text("Passwords do not match").css("color", "red");
        }
    }

    $("#password1, #password2").on("keyup", checkPasswords);

    $("form").on("submit", function(e) {
    if ($("#password1").val() !== $("#password2").val()) {
        e.preventDefault();
        $("#password-message").text("Passwords must match before submitting").css("color", "red");
    }
    });
});