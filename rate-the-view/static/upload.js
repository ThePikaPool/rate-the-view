$(document).ready(function() {
    $("#id_image").change(function() {
        const file = this.files[0];

        if (file && file.type.startsWith("image/")) {
            $("#image-preview")
                .attr("src", URL.createObjectURL(file))
                .show();
        } else {
            $("#image-preview").hide();
        }
    });
});