setInterval(update, 1000);
var updateInProgress = false

var connected = false
function eventDisconnected() {
    if (!connected) return
    connected = false
    $("#connection-status").removeClass("connection-status-connected")
    console.log("disconnected")
}

function eventConnected() {
    if (connected) return
    connected = true
    $("#connection-status").addClass("connection-status-connected")
    console.log("connected")
}

function update() {
    if (updateInProgress)
        return

    updateInProgress = true
    fetch("/telemetry")
        .then(res => {
            if (res.ok) {
                return res.json()
            } else {
                eventDisconnected()
            }
        })
        .then(json => {
            eventConnected()
            if (typeof (json) != "undefined") {
                plotTelemetry(json)
                parseTelemetry(json)
            }
        })
        .catch(error => {
            console.log(error)
        });
    updateInProgress = false
}

function parseTelemetry(json) {
    $("#destination-remove").prop('disabled', json["epn"]["destination"] === null)

    anyVirtual = false
    for (let static of json["env"]["statics"]) {
        if (static["category"] == "virtual") {
            anyVirtual = true
            break
        }
    }
    $("#virtual-static-remove-all").prop('disabled', !anyVirtual)
}

function setDestination(coords) {
    fetch("/destination/set", {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(coords),
    }).then(res => {
        interactions.clear()
    })
}

function removeDestination(coords) {
    fetch("/destination/remove", {
        method: 'POST',
    })
}


function placeVirtualStatic(vertices) {
    fetch("/virtual_static/place", {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(vertices),
    }).then(res => {
        interactions.clear()
    })
}

function removeAllVirtualStatics() {
    fetch("/virtual_static/remove_all", {
        method: 'POST',
    })
}
