from dataclasses import dataclass
import datetime
from typing import Any


class GeneratedRSTUnit:
    def __init__(self, timestamp: float, length: float, wrap: int = 0):
        self.length = length
        self.timestamp = timestamp
        self.wrap = wrap

    def _absolute_unit(self, timestamp: float) -> int:
        if self.wrap:
            unit = int(abs(timestamp) // self.length % self.wrap)
        else:
            unit = int(abs(timestamp) // self.length)
        if timestamp < 0:
            return -unit
        return unit

    @property
    def absolute_unit(self):
        return self._absolute_unit(self.timestamp)

    @property
    def visual_unit(self):
        visual_timestamp = self.timestamp + 1 if self.timestamp < 0 else self.timestamp
        negative_offset = 1 if self.wrap == 0 else 0
        absolute_unit = self._absolute_unit(visual_timestamp)
        if absolute_unit < 0:
            return self.wrap - absolute_unit - negative_offset
        return absolute_unit

    def __repr__(self):
        return str(self.absolute_unit)


class RTSTimeUnits:
    timestamp: float = 0
    seconds_ratio = None
    epoch: datetime.datetime = datetime.datetime(1970, 1, 1)
    null = False

    def __post_init__(self):
        self.unit_map = self._gen_unit_map()
        if self.seconds_ratio is None:
            raise AttributeError("RTSTimeUnits must have a seconds_ratio attribute")

    @classmethod
    def from_seconds(cls, timestamp: float):
        new_cls = cls.__new__(cls)
        new_cls.__post_init__()
        if new_cls.seconds_ratio is None:
            raise AttributeError("RTSTimeUnits must have a seconds_ratio attribute")
        new_cls.timestamp = timestamp / new_cls.seconds_ratio
        return new_cls

    @classmethod
    def from_datetime(cls, dt: datetime.datetime):
        return cls.from_utc_timestamp(dt.timestamp())

    @classmethod
    def from_utc_timestamp(cls, timestamp: float):
        return cls.from_seconds(timestamp - cls.epoch.timestamp())

    @classmethod
    def from_timestamp(cls, timestamp: float):
        new_cls = cls.__new__(cls)
        new_cls.__post_init__()
        new_cls.timestamp = timestamp
        return new_cls

    def _gen_unit_map(self):
        unit_map: dict[str, GeneratedRSTUnit] = {}
        vars = self.__class__.__dict__.copy()
        vars.update(self.__dict__)
        for key, value in vars.items():
            if isinstance(value, RTSUnit):
                unit_map[key] = value.generate_unit(self.timestamp)
        return unit_map

    def __getitem__(self, name: str) -> Any:
        return self.unit_map[name]

    def __iter__(self):
        return iter(self.unit_map)

    def units(self):
        return list(self.unit_map.items())


class RTSUnit:
    def __init__(self, length: float, wrap: int = 0) -> None:
        self.length = length
        self.wrap = wrap

    def _make_unit(self, timestamp: float) -> GeneratedRSTUnit:
        return GeneratedRSTUnit(timestamp, self.length, self.wrap)

    def generate_unit(self, timestamp: int) -> GeneratedRSTUnit:
        return self._make_unit(timestamp)

    def __get__(self, obj: RTSTimeUnits, objtype=None) -> GeneratedRSTUnit:
        if objtype is None or not issubclass(objtype, RTSTimeUnits):
            raise AttributeError("RSTUnit can only be accessed through RSTimeUnits")
        if obj is None:
            return 0
        return self._make_unit(obj.timestamp)

    def __set__(self, obj, value: int):
        if not isinstance(obj, RTSTimeUnits):
            raise AttributeError("RSTUnit can only be accessed through RSTimeUnits")
        if not hasattr(obj, "timestamp"):
            obj.timestamp = 0
        obj.timestamp += int(value * self.length)
