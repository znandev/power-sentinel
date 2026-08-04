function renderEvents(data){

    let html="";

    data.forEach(e=>{

        html += `

        <div class="event">

            <div class="event-time">

                ${e.timestamp}

            </div>

            <div class="event-message">

                ${e.message}

            </div>

        </div>

        `;

    });

    document.getElementById("events").innerHTML =
        html;

}