$(document).ready(function() {
    $("a#mudar_dia").click(function(e) {
        var re = /^\d{2}\/\d{2}\/\d{4}$/
        var dia = prompt("Qual data? (DD/MM/YYYY)");
        while (dia && !dia.match(re)) {
            dia = prompt("Qual data? (DD/MM/YYYY)", dia);
        }
        if (!dia) return false;
        document.location.pathname = url_do_dia(dia)
        e.preventDefault();
    });
});
