import datetime
from rtsdatetime.model import Timestamp, RTSDateTime, TimestampInterface
from typing import Callable
from rtsdatetime.default_units import StandardUnits


class TimestampTransformer(TimestampInterface):
    def __init__(self, base: Timestamp, transformer: Callable[[float], float] | None = None):
        self.base = base
        self.transformer_cb = transformer or self.transformer

    def __set_name__(self, owner: type[RTSDateTime], name: str):
        self.name = name

    def __get__(self, obj: RTSDateTime, objtype: type[RTSDateTime] | None = None) -> float:
        if obj is None or not issubclass(objtype, RTSDateTime):
            raise AttributeError("TimestampTransformer can only be accessed through RTSDateTime objects")
        return self.transformer_cb(self.base.__get__(obj, objtype))

    def __set__(self, obj: RTSDateTime, value: float):
        raise AttributeError("TimestampTransformer is read-only")

    @staticmethod
    def transformer(timestamp: float) -> float:
        raise NotImplementedError(
            "TimestampTransformer must have 'transformer' overridden in subclasses or provided in initializer/"
        )


class SUTimestampTransformer(TimestampTransformer):
    @staticmethod
    def transformer(timestamp: float) -> float:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return StandardUnits(year=dt.year, day=dt.day, hour=dt.hour, minute=dt.minute, second=dt.second).timestamp
