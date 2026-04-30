import socket

from common import logging
from common.serialization import RecurrentSerializable
from common.environment import Environment, DynamicEntity, Path, boat
from common.types import Coords

log = logging.getLogger(__name__)


class EPNData(RecurrentSerializable):
    destination: Coords = None
    global_path: Path = None
    local_path: Path = None
    state: str = 'unknown'


class PowerData(RecurrentSerializable):
    temperature: float = 0.0
    voltage: float = 0.0
    current: float = 0.0
    power: float = 0.0


class RemoteData(RecurrentSerializable):
    signal: float = 0.0


class Telemetry(RecurrentSerializable):
    host: str = socket.gethostname()
    env: Environment = None
    vessel: DynamicEntity = boat((0, 0), 0, 0)
    vessel_history: Path = None
    epn: EPNData = EPNData()
    jetson: PowerData = PowerData()
    pixhawk: PowerData = PowerData()
    remote: RemoteData = RemoteData()

    def __init__(self) -> None:
        super().__init__()
        self.__event_handlers = {}

    def __call__(self, event, *args, **kwargs):
        handler = self.__event_handlers.get(event)
        if handler is not None:
            return handler(*args, **kwargs)
        else:
            log.warning(f'Unhandled event {event}')

    def serialize(self) -> dict:
        if self.env is not None:
            for dynamic in self.env.dynamics:
                dynamic.resolve()
        return super().serialize()

    def on(self, event, callback):
        self.__event_handlers[event] = callback

    def un(self, event):
        self.__event_handlers.pop(event)
