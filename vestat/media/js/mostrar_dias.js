$(document).ready(function() {
        $(".mostrar_dias").click(function(e) {
            $(this).next("table").toggleClass("hide");
            e.preventDefault();
        });
});
