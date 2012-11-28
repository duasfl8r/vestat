function url_do_dia(data) {
    var parts = data.split("/");
    var ano = parts[2], mes = parts[1], dia = parts[0];
    return "/caixa/" + ano + "/" + mes + "/" + dia + "/";
}

$(document).ready(function() {
    $("a.remover").click(function(e) {
        if (! confirm("Deseja mesmo remover esse item?")) {
            e.preventDefault();
        }
    });

    $("a#remover_dia").click(function(e) {
        if (! confirm("Deseja mesmo remover esse dia?")) {
            e.preventDefault();
        }
    });

    $("#anotacoes_trunc a#expandir").click(function(e) {
        $("#anotacoes").removeClass("hide");
        $("#anotacoes_trunc").addClass("hide");
        e.preventDefault();
    });

    $("#anotacoes a#contrair").click(function(e) {
        $("#anotacoes_trunc").removeClass("hide");
        $("#anotacoes").addClass("hide");
        e.preventDefault();
    });
});
