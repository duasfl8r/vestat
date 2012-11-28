$(document).ready(function() {
    // Colocar hora atual
    var agora = new Date();
    var horas = agora.getHours();
    var minutos = agora.getMinutes();
    if (minutos < 10) { minutos = "0" + minutos; }
    if (horas < 10) { horas = "0" + horas; }

    value = $("#id_hora_entrada").val()
    if (value) {
        $("#id_hora_entrada").mask("99:99");
        $("#id_hora_entrada").val(value);
    } else {
        $("#id_hora_entrada").mask("99:99");
        $("#id_hora_entrada").val(horas + ":" + minutos);
    }
});
