import json
import threading
import time
from turbo_flask import Turbo
from flask import Flask, render_template, request

from common import logging
from common.environment import virtual
from common.units import toDD

from .telemetry import Telemetry
from .client import CLIENT_FUNCTIONS

TURBO_REFRESH_HZ = 1

log = logging.getLogger(__name__)

app = Flask(__name__)
turbo = Turbo(app)

telemetry = Telemetry()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/telemetry")
def telemetry_endpoint():
    return json.dumps(telemetry.serialize())


@app.route("/destination/set", methods=["POST"])
def destination_set_endpoint():
    destination = request.json
    log.info(f"Got destination request {toDD(*destination)}")
    telemetry('destination_set', destination)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/destination/remove", methods=["POST"])
def destination_remove_endpoint():
    log.info("Got destination remove request")
    telemetry('destination_remove')
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/virtual_static/place", methods=["POST"])
def virtual_static_place_endpoint():
    vertices = request.json
    log.info("Placed virtual static")
    telemetry('virtual_static_place', virtual(vertices))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/virtual_static/remove_all", methods=["POST"])
def virtual_static_remove_all_endpoint():
    log.info("Removed all virtual statics")
    telemetry('virtual_static_remove_all')
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.context_processor
def inject():
    return telemetry.serialize() | CLIENT_FUNCTIONS


def update():
    with app.app_context():
        while True:
            time.sleep(1 / TURBO_REFRESH_HZ)
            turbo.push(turbo.replace(render_template('epn/vessel-info.html'), 'vessel-info'))
            turbo.push(turbo.replace(render_template('epn/path-info.html'), 'path-info'))
            turbo.push(turbo.replace(render_template('details/details.html'), 'details'))
            turbo.push(turbo.replace(render_template('status.html'), 'status'))


@app.before_first_request
def before_first_request():
    threading.Thread(target=update).start()
