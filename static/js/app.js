async function refreshStatus() {

    try {

        const res = await fetch("/status");

        const data = await res.json();

        renderStatus(data);

    }

    catch(err){

        console.log(err);

    }

}

async function refreshEvents(){

    try{

        const res = await fetch("/events");

        const data = await res.json();

        renderEvents(data);

    }

    catch(err){

        console.log(err);

    }

}

async function refreshStatistics(){

    try{

        const res = await fetch("/statistics");

        const data = await res.json();

        renderStatistics(data);

    }

    catch(err){

        console.log(err);

    }

}

async function refreshDashboard(){

    await refreshStatus();

    await refreshEvents();

    await refreshStatistics();

} 

refreshDashboard();

setInterval(refreshStatus,1000);

setInterval(refreshEvents,2000);

setInterval(refreshStatistics,5000);