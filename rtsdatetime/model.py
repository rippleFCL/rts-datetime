import datetime
import json
import time
from typing import Any, Callable, Literal, Protocol, Self, runtime_checkable, dataclass_transform
from rtsdatetime.default_units import RSTUnits
from .units import RTSTimeUnits


class RTSTimeDelta[T: RTSTimeUnits]:
    def __init__(self, timediff: int, time_units: type[T]):
        self.timediff = timediff
        self._time_units = time_units

    @classmethod
    def from_units(
        cls,
        units: T,
    ):
        timediff = units.timestamp
        return cls(int(timediff), units.__class__)

    @property
    def units(self):
        return self._time_units.from_timestamp(self.timediff)

    def __add__(self, other):
        if type(other) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeDelta' and '{type(other)}'")
        return RTSTimeDelta(self.timediff + other.timediff, self._time_units)

    def __sub__(self, other):
        if type(other) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeDelta' and '{type(other)}'")
        return RTSTimeDelta(self.timediff - other.timediff, self._time_units)


@runtime_checkable
class TimestampInterface(Protocol):
    name: str

    def __set_name__(self, owner: type["RTSDateTime"], name: str): ...

    def __get__(self, obj: "RTSDateTime", objtype: type["RTSDateTime"] | None = None) -> float: ...


class Timestamp(TimestampInterface):
    def __init__(self):
        pass

    def __set_name__(self, owner: type["RTSDateTime"], name: str):
        self.name = name

    def __get__(self, obj: "RTSDateTime | None", objtype: Any = None) -> float:
        if obj is None and issubclass(objtype, RTSDateTime):
            return 0
        if obj is None or not issubclass(objtype, RTSDateTime):
            raise AttributeError("RTSTCTimestamp can only be accessed through RTSDateTime objects")
        value = getattr(obj, f"_{self.name}", None)
        if value is None:
            return 0
        if not isinstance(value, float):
            raise ValueError(f"RTSTCTimestamp {self.name} must be of type float")
        return value

    def __set__(self, obj: "RTSDateTime", value: datetime.datetime | RTSTimeUnits):
        if isinstance(value, datetime.datetime):
            timestamp = value.timestamp()
        elif isinstance(value, RTSTimeUnits):
            if value.seconds_ratio is None:
                raise AttributeError("RTSTimeUnits must have a seconds_ratio attribute")
            timestamp = value.timestamp * value.seconds_ratio + value.epoch.timestamp()
        else:
            raise ValueError(f"RTSTCTimestamp {self.name} must be of type datetime.datetime or RTSTimeUnits")
        setattr(obj, f"_{self.name}", timestamp)


@dataclass_transform(field_specifiers=(Timestamp,))
class RTSDateTime(object):
    def __init_subclass__(cls) -> None:
        def __init__(self: "RTSDateTime", **kwargs):
            timestamps = self._timestamp_map.keys()
            for key, value in kwargs.items():
                if key not in timestamps:
                    raise ValueError(f"Unknown timestamp '{key}'")
                setattr(self, key, value)
        cls.__init__ = __init__

    @classmethod
    def _component_map(cls):
        units_map: dict[str, TimeComponent] = {}
        vars = cls.__class__.__dict__.copy()
        vars.update(cls.__dict__)
        for key, value in vars.items():
            if isinstance(value, TimeComponent):
                units_map[key] = value
        return units_map

    @classmethod
    def dump_json(cls):
        return json.dumps({key: value.to_dict() for key, value in cls._component_map().items()})

    @classmethod
    def load_json(cls, json_string: str):
        class DynRTSDateTime(cls):
            pass
        new_cls: type[Self] = DynRTSDateTime # type: ignore
        data = json.loads(json_string)
        timestamp_map: dict[str, TimestampInterface] = {}
        for key, value in data.items():
            new_component, timestamp_map = TimeComponent.construct_from_dict(value, timestamp_map)
            setattr(new_cls, key, new_component)
        for key, value in timestamp_map.items():
            setattr(new_cls, key, value)
            value.__set_name__(new_cls, key)
        return new_cls

    @property
    def _timestamp_map(self):
        timestamp_map: dict[str, TimestampInterface] = {}
        vars = self.__class__.__dict__.copy()
        vars.update(self.__dict__)
        for key, value in vars.items():
            if isinstance(value, TimestampInterface):
                timestamp_map[key] = value
        return timestamp_map

    @property
    def timestamp_map(self):
        return {key: value.__get__(self, self.__class__) for key, value in self._timestamp_map.items()}

    @property
    def units_map(self):
        units_map: dict[str, RSTUnits] = {}
        vars = self.__class__.__dict__.copy()
        vars.update(self.__dict__)
        for key, value in vars.items():
            if isinstance(value, TimeComponent):
                units_map[key] = value.__get__(self, self.__class__)
        return units_map

    def __getitem__(self, key: str):
        return self.units_map[key]


class TimeComponent[T: RTSTimeUnits]:
    def __init__(self, units: type[T], timestamp: TimestampInterface, init: Literal[False] = False):
        self.init = init
        self.timestamp = timestamp
        self.units = units

    def __get__(self, obj: RTSDateTime | None, objtype=None):
        if objtype is None or not issubclass(objtype, RTSDateTime):
            raise AttributeError("RTSTime component blah blah only can be used from rtsdatetime")
        timestamp = self.timestamp.__get__(obj, objtype)
        return self.units.from_utc_timestamp(timestamp)

    def __set_name__(self, owner: type[RTSDateTime], name: str):
        self.name = name

    @classmethod
    def construct_from_dict(
        cls: "type[TimeComponent[RTSTimeUnits]]", data: dict[str, Any], timestamp_map: dict[str, TimestampInterface]
    ):
        timestamp = timestamp_map.get(data["timestamp"])
        if not timestamp:
            timestamp = Timestamp()
            timestamp_map[data["timestamp"]] = timestamp
        return cls(RTSTimeUnits.construct_from_dict(data["units"]), timestamp), timestamp_map

    def to_dict(self):
        return {"units": self.units.to_dict(), "timestamp": self.timestamp.name}


def rtsdatetime[T](cls: type[T]) -> type[T]:
    return cls


#
# class RTSTimeComponent[T: RTSTimeUnits](object):
#
#     def __post_init__(self, timestamp: int, name: str, time_units: T):
#         self.name = name
#         self.timestamp = timestamp
#         self._time_unit = time_units
#         # rst date
#
#     @classmethod
#     def now(cls, name: str, epoch: int):
#         time = (datetime.datetime.now().timestamp() - epoch) / cls.BEAT_LENGTH_SECOND
#         return cls(int(time), name)
#
#     @classmethod
#     def from_timestamp(cls, timestamp: str):
#         if not re.match("^\w+:\-?\d+$", timestamp):
#             raise ValueError(f"Invalid timestamp: {timestamp}")
#         name, timestamp = timestamp.split(":")
#         timestamp_value = int(timestamp)
#         return cls(timestamp_value, name)
#
#     @classmethod
#     def from_units(
#         cls,
#         name: str,
#         quadrennials: int = 0,
#         years: int = 0,
#         days: int = 0,
#         octas: int = 0,
#         hexas: int = 0,
#         taps: int = 0,
#         decitaps: int = 0,
#         beats: int = 0,
#         hours: int = 0,
#         minutes: int = 0,
#         seconds: int = 0,
#     ):
#         timestamp: float = 0
#         # rst date
#         timestamp += quadrennials * UNIT_BEATS[TimeUnits.QUADRENNIAL]
#         timestamp += years * UNIT_BEATS[TimeUnits.YEAR]
#         timestamp += days * UNIT_BEATS[TimeUnits.DAY]
#         # rst time
#         timestamp += octas * UNIT_BEATS[TimeUnits.OCTA]
#         timestamp += hexas * UNIT_BEATS[TimeUnits.HEXA]
#         timestamp += taps * UNIT_BEATS[TimeUnits.TAP]
#         timestamp += decitaps * UNIT_BEATS[TimeUnits.DECITAP]
#         timestamp += beats * UNIT_BEATS[TimeUnits.BEAT]
#
#         # utc time
#         timestamp += seconds * UNIT_BEATS[TimeUnits.SECONDS]
#         timestamp += minutes * UNIT_BEATS[TimeUnits.MINUTE]
#         timestamp += hours * UNIT_BEATS[TimeUnits.HOUR]
#         return cls(ceil(timestamp), name)
# ]
#     @classmethod
#     def from_time_component(cls, time_component: "RTSTimeComponent", name: str | None = None):
#         return cls(time_component.timestamp, name if name is not None else time_component.name)
#
#     def _timestamp_to_unit(self, unit: TimeUnits):
#         timestamp = self.timestamp + 1 if self.timestamp < 0 else self.timestamp
#         if UNIT_LENGTHS[unit]:
#             positive_unit = int(abs(timestamp) // UNIT_BEATS[unit] % UNIT_LENGTHS[unit])
#         else:
#             positive_unit = int(abs(timestamp) // UNIT_BEATS[unit])
#         if self.timestamp < 0:
#             return UNIT_LENGTHS[unit] - positive_unit - self.UNIT_NEGATIVE_OFFSET[unit]
#         return positive_unit
#
#     def add(self, timedelta: RTSTimeDelta, new_name: str | None = None):
#         if type(timedelta) is not RTSTimeDelta:
#             raise TypeError(f"unsupported operand type(s) for +: 'RSTimeComponent' and '{type(timedelta)}'")
#         return RTSTimeComponent(
#             self.timestamp + timedelta.timediff,
#             self.name if new_name is None else new_name,
#         )
#
#     def sub(self, timedelta: RTSTimeDelta, new_name: str | None = None):
#         if type(timedelta) is not RTSTimeDelta:
#             raise TypeError(f"unsupported operand type(s) for +: 'RSTimeComponent' and '{type(timedelta)}'")
#         return RTSTimeComponent(self.timestamp - timedelta.timediff, self.name if new_name is None else new_name)
#
#     def format(self, format_str):
#         fmt_values = {
#             f"[{self.name}.QU]": str(self.quadrennial),
#             f"[{self.name}.YE]": str(self.year),
#             f"[{self.name}.DA]": str(self.day),
#             f"[{self.name}.OC]": str(self.octa),
#             f"[{self.name}.HE]": str(self.hexa),
#             f"[{self.name}.TA]": str(self.tap),
#             f"[{self.name}.DE]": str(self.decitap).rjust(2, "0"),
#             f"[{self.name}.BE]": str(self.beat).rjust(2, "0"),
#             f"[{self.name}.SE]": str(self.seconds).rjust(2, "0"),
#             f"[{self.name}.MI]": str(self.minute).rjust(2, "0"),
#             f"[{self.name}.HO]": str(self.hour).rjust(2, "0"),
#             f"[{self.name}.RH]": str(self.rolling_hour),
#             f"[{self.name}.RO]": str(self.rolling_octa),
#         }
#
#         for key, value in fmt_values.items():
#             format_str = format_str.replace(key, str(value))
#         return format_str
#
#     def to_timestamp(self):
#         return f"{self.name}:{self.timestamp}"
#
#     def __add__(self, other):
#         return self.add(other)
#
#     def __sub__(self, other):
#         return self.sub(other)
#
#     def __eq__(self, value: object) -> bool:
#         if type(value) is not RTSTimeComponent:
#             return False
#         return self.timestamp == value.timestamp
#
#     def __repr__(self):
#         quadrennials = f"quadrennials={self.quadrennial}, " if self.quadrennial else ""
#         days = f"days={self.day}, " if self.day else ""
#         years = f"years={self.year}, " if self.year else ""
#         octas = f"octas={self.octa}, " if self.octa else ""
#         hexas = f"hexas={self.hexa}, " if self.hexa else ""
#         taps = f"taps={self.tap}, " if self.tap else ""
#         decitaps = f"decitaps={self.decitap}, " if self.decitap else ""
#         beats = f"beats={self.beat}, " if self.beat else ""
#         comp_str = f"{quadrennials}{days}{years}{octas}{hexas}{taps}{decitaps}{beats}"[:-2]
#         return f"RSTimeComponent.from_units({comp_str})"


# class RTSDateTime(object):
#     def __init__(self, time_components: list[RTSTimeComponent], static_time_components: list[RTSTimeComponent]):
#         self._ticking_components = time_components
#         self._static_components = static_time_components
#         self._components = {component.name: component for component in self._ticking_components + self._static_components}
#
#     @classmethod
#     def from_timestamp(cls, timestamp: str):
#         ticking_components, static_components = timestamp.split(".")
#         return cls(
#             [RTSTimeComponent.from_timestamp(component) for component in ticking_components.split(",") if component],
#             [RTSTimeComponent.from_timestamp(component) for component in static_components.split(",") if component],
#         )
#
#     def __add__(self, other):
#         if type(other) is not RTSTimeDelta:
#             raise TypeError(f"unsupported operand type(s) for +: 'RSTimeDate' and '{type(other)}'")
#         return RTSDateTime(
#             [component + other for component in self._ticking_components],
#             self._static_components,
#         )
#
#     def __sub__(self, other):
#         if type(other) is not RTSTimeDelta:
#             raise TypeError(f"unsupported operand type(s) for -: 'RSTimeDate' and '{type(other)}'")
#         return RTSDateTime(
#             [component - other for component in self._ticking_components],
#             self._static_components,
#         )
#
#     def format(self, format_str: str):
#         for component in self._ticking_components + self._static_components:
#             format_str = component.format(format_str)
#         return format_str
#
#     def to_timestamp(self):
#         component_str = ",".join([component.to_timestamp() for component in self._ticking_components])
#         static_component_str = ",".join([component.to_timestamp() for component in self._static_components])
#         return f"{component_str}.{static_component_str}"
#
#     def __getitem__(self, key: str):
#         return self._components[key]
#
#     def __repr__(self):
#         return f"RSTimeDate({self._ticking_components}, {self._static_components})"
