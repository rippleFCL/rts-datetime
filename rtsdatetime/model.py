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


class RTSDateTime(object):
    @property
    def unit_map(self):
        return self._gen_unit_map()

    def _gen_unit_map(self):
        unit_map: dict[str, RSTUnits] = {}
        vars = self.__class__.__dict__.copy()
        vars.update(self.__dict__)
        for key, value in vars.items():
            if isinstance(value, RTSTimeComponent):
                unit_map[key] = value.get_unit(self)
        return unit_map

    def __getitem__(self, key: str):
        return self.unit_map[key]


class RTSTCTimestamp:
    def __init__(self):
        pass

    def __set_name__(self, owner: RTSDateTime, name: str):
        self.name = name

    def __get__(self, obj: RTSDateTime, objtype=None):
        if obj is None or not issubclass(objtype, RTSDateTime):
            raise AttributeError("RTSTCTimestamp can only be accessed through RTSDateTime objects")
        value = getattr(obj, f"_{self.name}", None)
        if value is None:
            raise ValueError(f"RTSTCTimestamp {self.name} is not set")
        if not isinstance(value, float) and not isinstance(value, int):
            raise ValueError(f"RTSTCTimestamp {self.name} must be of type float or int")
        return value

    def __set__(self, obj: RTSDateTime, value: float | int | RTSTimeUnits):
        setattr(obj, f"_{self.name}", value)


class RTSTimeComponent[T: RTSTimeUnits]:
    def __init__(self, units: type[T], timestamp: RTSTCTimestamp, locked: bool = False):
        self.timestamp = timestamp
        self.units = units
        self.locked = locked

    def __get__(self, obj: RTSDateTime | None, objtype=None):
        if objtype is None or not issubclass(objtype, RTSDateTime):
            raise AttributeError("RTSTime component blah blah only can be used from rtsdatetime")
        timestamp = self.timestamp.__get__(obj, objtype)
        return self.units.from_utc_timestamp(timestamp)


    def __set_name__(self, owner: RTSDateTime, name: str):
        self.name = name

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
