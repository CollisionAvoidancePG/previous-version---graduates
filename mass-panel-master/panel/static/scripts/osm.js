var source;
var map;
var typeSelect;
var draw;
var env = new ol.Collection();
var interactions = new ol.Collection();

var entityCategoryStyles = {
    'island': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0000'
        }),
        fill: new ol.style.Fill({
            color: '#00b30970'
        })
    }),
    'land': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0000'
        }),
        fill: new ol.style.Fill({
            color: '#00b30970'
        })
    }),
    'detected': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0000'
        }),
        fill: new ol.style.Fill({
            color: '#00740670'
        })
    }),
    'virtual': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0000'
        }),
        fill: new ol.style.Fill({
            color: '#00000000'
        })
    }),
    'boat': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0000'
        }),
        fill: new ol.style.Fill({
            color: '#ffffffff'
        })
    }),
}

var styles = {
    'safe_zone': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0000'
        }),
        fill: new ol.style.Fill({
            color: '#b3000070'
        })
    }),
    "user": new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({
                color: '#3399CC',
            }),
            stroke: new ol.style.Stroke({
                color: '#fff',
                width: 2,
            })
        }),
    }),
    "vessel": new ol.style.Style({
        image: new ol.style.RegularShape({
            radius: 10,
            points: 3,
            rotation: 0,
            angle: 0,
            scale: [0.7, 1.2],
            fill: new ol.style.Fill({
                color: '#cc3333',
            }),
            stroke: new ol.style.Stroke({
                color: '#fff',
                width: 1,
            })
        }),
    }),
    "destination": new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({
                color: '#ccbd33',
            }),
            stroke: new ol.style.Stroke({
                color: '#fff',
                width: 2,
            })
        }),
    }),
    "path_global": new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#B40404',
            width: 2
        })
    }),
    "path_local": new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#0433b4',
            width: 2
        })
    }),
    "vessel_history": new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#33333333',
            width: 2
        })
    })
}


function DD(latitude, longitude) {
    return ol.proj.transform([longitude, latitude], 'EPSG:4326', 'EPSG:3857')
}

function setDestinationEvent(event) {
    console.log(event)
    alert(event)
}

var destinationInteraction = null
function toggleDestinationInteraction() {
    if (virtualStaticInteraction !== null)
        return

    if (destinationInteraction === null) {
        $("#destination-set").html("Abort")
        $("#virtual-static-place").prop('disabled', true)
        destinationInteraction = new ol.interaction.Draw({
            features: interactions,
            type: 'Point',
            style: styles['destination'],
        });
        destinationInteraction.on('drawend', function (event) {
            $("#destination-set").html("Set")
            $("#virtual-static-place").prop('disabled', false)
            interactions.clear()
            destinationInteraction.finishDrawing()
            map.removeInteraction(destinationInteraction)
            destinationInteraction = null
            setDestination(event.feature.getGeometry().getCoordinates());
        })
        map.addInteraction(destinationInteraction)
    }
    else {
        $("#destination-set").html("Set")
        $("#virtual-static-place").prop('disabled', false)
        map.removeInteraction(destinationInteraction)
        destinationInteraction = null
    }
}

var virtualStaticInteraction = null
function toggleVirtualStaticInteraction() {
    if (destinationInteraction !== null)
        return

    if (virtualStaticInteraction === null) {
        $("#virtual-static-place").html("Abort")
        $("#destination-set").prop('disabled', true)
        virtualStaticInteraction = new ol.interaction.Draw({
            features: interactions,
            type: 'Polygon'
        });
        virtualStaticInteraction.on('drawend', function (event) {
            $("#virtual-static-place").html("Place")
            $("#destination-set").prop('disabled', false)
            interactions.clear()
            virtualStaticInteraction.finishDrawing()
            map.removeInteraction(virtualStaticInteraction)
            virtualStaticInteraction = null
            placeVirtualStatic(event.feature.getGeometry().getCoordinates()[0]);
        })
        map.addInteraction(virtualStaticInteraction)
    }
    else {
        $("#virtual-static-place").html("Place")
        $("#destination-set").prop('disabled', false)
        map.removeInteraction(virtualStaticInteraction)
        virtualStaticInteraction = null
    }
}

function vesselHistoryClear() {
    fetch("/vessel_history/clear", {
        method: "POST",
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
}

function init() {
    map = new ol.Map({
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            new ol.layer.Vector({
                source: new ol.source.Vector({
                    features: env,
                })
            }),
            new ol.layer.Vector({
                source: new ol.source.Vector({
                    features: interactions,
                })
            }),
        ],
        target: 'map',
    });

    centerOn(DD(54.3592, 18.51591))
}

function plot(geometry, style) {
    let feature = new ol.Feature({
        geometry: geometry,
    })
    feature.setStyle(style)
    env.push(feature);
    return feature
}

function plotEntity(entity) {
    plot(new ol.geom.Polygon([entity["safe_zone"]]), styles["safe_zone"])
    plot(new ol.geom.Polygon([entity["model"]]), entityCategoryStyles[entity["category"]])
}

function plotPath(path, style) {
    nodes = []
    for (let node of path["nodes"])
        nodes.push(node["position"])
    plot(new ol.geom.LineString(nodes), style)
}

var vesselPos = null;
var userPos = null;
function plotTelemetry(json) {
    env.clear();

    if (json["env"] !== null) {
        for (let entity of json["env"]["statics"])
            plotEntity(entity)
        for (let entity of json["env"]["dynamics"]) {
            plotEntity(entity)
        }
    }

    if (json["vessel"] !== null)
        style = styles["vessel"]
        style.image_.rotation_ = json["vessel"]["course"] * (Math.PI / 180)
        plot(new ol.geom.Point(json["vessel"]["position"]), style)
    if (json["epn"]["destination"] !== null)
        plot(new ol.geom.Point(json["epn"]["destination"]), styles["destination"])
    if (userPos !== null)
        plot(new ol.geom.Point(userPos), styles["user"])

    if (json["epn"]["global_path"] !== null)
        plotPath(json["epn"]["global_path"], styles["path_global"])
    if (json["epn"]["local_path"] !== null)
        plotPath(json["epn"]["local_path"], styles["path_local"])
    if (json["vessel_history"] !== null)
        plotPath(json["vessel_history"], styles["vessel_history"])
}

function centerOn(position, zoom = 18) {
    map.setView(new ol.View({
        center: position,
        zoom: zoom
    }));
}

function centerOnVessel() {
    if (vesselPos !== null)
        centerOn(vesselPos)
}

function centerOnUser() {
    // TODO: https://openlayers.org/en/latest/examples/geolocation.html
    navigator.geolocation.getCurrentPosition(position => {
        userPos = DD(position.coords.latitude, position.coords.longitude)
        centerOn(userPos)
        plotUserPosition()
    })
}
