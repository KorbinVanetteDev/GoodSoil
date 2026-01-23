var gamer = document.getElementById("gamer");

// Dont judge I want to have fun too.
var buttonBabyyy = document.getElementById("buttonbabyyy")

var span = document.getElementsByClassName("close")[0];

buttonBabyyy.onlick = function() {
    gamer.style.display = "block";
}

span.onclick = function() {
    gamer.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == gamer) {
        gamer.style.display = "none";
    }
}