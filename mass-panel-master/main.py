import random
import threading
import time

from common.environment import Environment, boat, Path, Node, virtual
from common.units import DD, deg
from osm import OSMSupplier
from panel import app, telemetry

# telemetry mocks
states = ['idle', 'global_epn', 'local_epn', 'cruising']
telemetry.vessel.position = DD(54.3592, 18.51591)
telemetry.env = Environment(
    statics=OSMSupplier(telemetry.vessel.position, 150).get_entities(),
    dynamics=[
        boat(DD(54.3592, 18.51541), 1, 180 * deg)
    ]
)
telemetry.epn.destination = DD(54.3592, 18.51501)
telemetry.epn.global_path = Path([
    Node(DD(54.3592, 18.51591), 0),
    Node(DD(54.35921, 18.51541), 0),
    Node(DD(54.3592, 18.51501), 0)
])

telemetry.epn.local_path = Path([
    Node(DD(54.3592, 18.51591), 0),
    Node(DD(54.35921, 18.51541), 0),
])


def destination_set(coords):
    telemetry.epn.destination = coords


def virtual_static_place(vertices):
    telemetry.env.statics.append(virtual(vertices))


def virtual_static_remove_all():
    for static in telemetry.env.statics:
        if static.category == 'virtual':
            telemetry.env.statics.remove(static)


telemetry.on('destination_set', destination_set)
telemetry.on('virtual_static_place', virtual_static_place)
telemetry.on('virtual_static_remove_all', virtual_static_remove_all)


def update():
    while True:
        telemetry.vessel.velocity = random.random() * 100
        telemetry.vessel.course += 1
        telemetry.pixhawk.voltage = 11 + random.random()
        telemetry.epn.state = states[telemetry.vessel.course % 4]
        time.sleep(5)


threading.Thread(target=update).start()


app.run(host="0.0.0.0", port=5123, debug=True)
