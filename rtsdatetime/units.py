from dataclasses import InitVar, dataclass
import datetime
import json
from typing import Any, Self, dataclass_transform


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


@dataclass_transform(kw_only_default=True)
class RTSTimeUnits:
    timestamp: float = 0
    seconds_ratio: None | float = None
    epoch: datetime.datetime = datetime.datetime(1970, 1, 1)

    def __init_subclass__(cls: type["RTSTimeUnits"]) -> None:
        if cls.seconds_ratio is None:
            raise AttributeError("RTSTimeUnits must have a seconds_ratio attribute")

        def __init__(self: "RTSTimeUnits", **kwargs):
            for unit_name, unit_value in kwargs.items():
                if getattr(self, unit_name, None) is None:
                    raise TypeError(f"RTSTimeUnits has no keyword argument {unit_name}")
                setattr(self, unit_name, unit_value)

        def __str__(self: "RTSTimeUnits"):
            components = [f"{unit_name}={unit_value.visual_unit}" for unit_name, unit_value in self.units.items()]
            return f"{self.__class__.__name__}({', '.join(components)})"

        def __repr__(self: "RTSTimeUnits"):
            return f"{self.__class__.__name__}.from_timestamp({self.timestamp})"

        cls.__repr__ = __repr__
        cls.__str__ = __str__
        cls.__init__ = __init__

    @classmethod
    def from_seconds(cls, seconds: float):
        new_cls: type[RTSTimeUnits] = cls.__new__(cls)  # type: ignore
        if new_cls.seconds_ratio is None:
            raise AttributeError("RTSTimeUnits must have a seconds_ratio attribute")
        new_cls.timestamp = seconds * new_cls.seconds_ratio
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

    @classmethod
    def unit_map(cls):
        unit_map: dict[str, RTSUnit] = {}
        vars = cls.__class__.__dict__.copy()
        vars.update(cls.__dict__)
        for key, value in vars.items():
            if isinstance(value, RTSUnit):
                unit_map[key] = value
        return unit_map

    @classmethod
    def construct_from_dict(cls: type[Self], data: dict[str, Any]) -> type[Self]:
        class DynRTSTimeUnits(cls):
            epoch = datetime.datetime.fromtimestamp(data["epoch"])
            seconds_ratio = data["seconds_ratio"]
            pass

        new_cls: type[Self] = DynRTSTimeUnits  # type: ignore
        new_cls.__name__ = data["name"]
        for unit_name, unit_data in data["units"].items():
            if getattr(new_cls, unit_name, None) is None:
                setattr(new_cls, unit_name, RTSUnit.from_dict(unit_data))
        return new_cls

    def __getitem__(self, name: str) -> Any:
        return self.units[name]

    def __iter__(self):
        return iter(self.units)

    @classmethod
    def to_dict(cls):
        return {
            "units": {key: value.to_dict() for key, value in cls.unit_map().items()},
            "epoch": cls.epoch.timestamp(),
            "seconds_ratio": cls.seconds_ratio,
            "name": cls.__name__,
        }

    @property
    def units(self):
        unit_map: dict[str, GeneratedRSTUnit] = {}
        vars = self.__class__.__dict__.copy()
        vars.update(self.__dict__)
        for key, value in vars.items():
            if isinstance(value, RTSUnit):
                unit_map[key] = value.generate_unit(self.timestamp)
        return unit_map


class RTSUnit:
    def __init__(self, length: float, wrap: int = 0) -> None:
        self.length = length
        self.wrap = wrap

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(**data)

    def _make_unit(self, timestamp: float) -> GeneratedRSTUnit:
        return GeneratedRSTUnit(timestamp, self.length, self.wrap)

    def generate_unit(self, timestamp: float) -> GeneratedRSTUnit:
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

    def to_dict(self):
        return {"length": self.length, "wrap": self.wrap}
