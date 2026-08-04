function renderStatistics(data){

    document.getElementById("power-loss").innerText =
        data.power_lost_today;

    document.getElementById("shutdown").innerText =
        data.shutdown_today;

    document.getElementById("total-events").innerText =
        data.total_events;

}