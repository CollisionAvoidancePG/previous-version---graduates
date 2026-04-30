from . import Serializable


def serialize_list(serializables: list[Serializable]) -> list[dict]:
    """Serialize a list of objects"""
    return [i.serialize() for i in serializables]


def deserialize_list(dicts: list[dict], new: type) -> list[Serializable]:
    """Deserialize a list of dictionaries"""
    return [new.from_dict(i) for i in dicts]
