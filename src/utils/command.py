from enum import Enum


class Command(Enum):
    HELLOW = {"value": "hellow"}
    STATUS = {"value": "status"}
    HELP = {"value": "help"}
    UNKNOWN = {"value": "unknown"}

    @classmethod
    def search_by_key(cls, key):
        try:
            return cls[key]
        except KeyError:
            return None

    @classmethod
    def search_by_value(cls, value):
        return next((item for item in cls if item.value["value"] == value), None)

    @classmethod
    def search_value(cls, value):
        if isinstance(value, cls):  # Verificar si es una instancia de la enumeración
            value = value.value["value"]
        return next(
            (item.value for item in cls if item.value["value"] == value),
            {"value": None, "method": None, "endpoint": None},
        )
