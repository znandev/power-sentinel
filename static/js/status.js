const power = document.getElementById("power");

power.classList.remove("on", "off");

if(data.power === "ON"){

    power.classList.add("on");

}
else if(data.power === "OFF"){

    power.classList.add("off");

}

function renderStatus(data){

    document.getElementById("power").innerText =
        data.power;

    document.getElementById("status").innerText =
        data.running
            ? "Shutdown Countdown"
            : "No Countdown";

    document.getElementById("countdown").innerText =
        data.running
            ? data.countdown
            : "IDLE";

    document.getElementById("esp").innerText =
        data.esp_online
            ? "ONLINE"
            : "OFFLINE";

    document.getElementById("device").innerText =
        data.device;

    document.getElementById("model").innerText =
        data.model;

    document.getElementById("firmware").innerText =
        data.firmware;

}