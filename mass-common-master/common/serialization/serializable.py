import json
from pathlib import Path

ENCODING = 'utf-8'

JSON = '.json'
KNOWN_EXTENSIONS = {JSON}


class UnknownExtensionError(Exception):
    """Trying to read or write to unknown file type"""


def load_from_file(path: str) -> dict:
    path = Path(path)

    suffix = path.suffix
    if suffix not in KNOWN_EXTENSIONS:
        raise UnknownExtensionError()

    with open(path, 'r', encoding=ENCODING) as file:
        data = file.read()

    if suffix == JSON:
        return json.loads(data)


class Serializable:
    """Object that can be serialized and deserialized"""

    def serialize(self) -> dict:
        """Object serialization"""
        return self.__dict__

    def to_file(self, path: str):
        """Object serialization to file"""
        path = Path(path)
        dictionary = self.serialize()

        if path.suffix == JSON:
            data = json.dumps(dictionary, sort_keys=True, indent=4)
        else:
            raise UnknownExtensionError()

        with open(path, 'w', encoding=ENCODING) as file:
            file.write(data)

    def deserialize(self, dictionary: dict):
        """Object deserialization"""
        for key, value in dictionary.items():
            setattr(self, key, value)

    def deserialize_from_file(self, path: str):
        """Object deserialization from file"""
        self.deserialize(load_from_file(path))

    @classmethod
    def from_dict(cls, dictionary: dict):
        """Create object with deserialization"""
        c = object.__new__(cls)
        c.deserialize(dictionary)
        return c

    @classmethod
    def from_file(cls, path: str):
        """Create object with deserialization from file"""
        c = object.__new__(cls)
        c.deserialize(load_from_file(path))
        return c


class RecurrentSerializable(Serializable):
    def serialize(self) -> dict:
        def serialized(v):
            return v.serialize() if isinstance(v, Serializable) else v

        attrs = filter(lambda attr: not callable(
            getattr(self, attr)), dir(self))
        attrs = filter(lambda attr: not attr.startswith('__'), attrs)
        attrs = filter(lambda attr: not attr.startswith(f'_{self.__class__.__name__}'), attrs)
        return {k: serialized(getattr(self, k)) for k in [*attrs]}
