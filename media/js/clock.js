function updateClock() {
    var currentTime = new Date();
    var currentHours = currentTime.getHours();
    var currentMinutes = currentTime.getMinutes();
    var currentSeconds = currentTime.getSeconds();
    currentHours = ( currentHours < 10 ? "0" : "" ) + currentHours;
    currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
    var currentTimeString = currentHours + ":" + currentMinutes;
    document.getElementById("clock").firstChild.nodeValue = currentTimeString;
}

$(document).ready(function() {
    updateClock();
    setInterval('updateClock()', 1000 );
});
