import datetime
import enum
from math import ceil
import re


class TimeUnits(enum.Enum):
    BEAT = 1
    DECITAP = 2
    TAP = 3
    HEXA = 4
    OCTA = 5
    ROLLING_OCTA = 6
    DAY = 7
    YEAR = 8
    QUADRENNIAL = 9
    SECONDS = 10
    MINUTE = 11
    HOUR = 12
    ROLLING_HOUR = 13


UNIT_LENGTHS = {
    TimeUnits.BEAT: 40,
    TimeUnits.DECITAP: 10,
    TimeUnits.TAP: 6,
    TimeUnits.HEXA: 8,
    TimeUnits.OCTA: 6,
    TimeUnits.ROLLING_OCTA: 0,
    TimeUnits.DAY: 0,
    TimeUnits.YEAR: 0,
    TimeUnits.QUADRENNIAL: 0,
    TimeUnits.SECONDS: 60,
    TimeUnits.MINUTE: 60,
    TimeUnits.HOUR: 24,
    TimeUnits.ROLLING_HOUR: 0,
}

UNIT_BEATS = {
    TimeUnits.BEAT: 1,
    TimeUnits.DECITAP: 40,
    TimeUnits.TAP: 400,
    TimeUnits.HEXA: 2400,
    TimeUnits.OCTA: 19200,
    TimeUnits.ROLLING_OCTA: 19200,
    TimeUnits.DAY: 115200,
    TimeUnits.YEAR: 42077520,
    TimeUnits.QUADRENNIAL: 168310080,
    TimeUnits.SECONDS: 4 / 3,
    TimeUnits.MINUTE: 80,
    TimeUnits.HOUR: 4800,
    TimeUnits.ROLLING_HOUR: 4800,
}


class RTSTimeDelta(object):
    def __init__(self, timediff: int):
        self.timediff = timediff
        self.quadrennial = self._timestamp_to_unit(TimeUnits.QUADRENNIAL)
        self.year = self._timestamp_to_unit(TimeUnits.YEAR)
        self.day = self._timestamp_to_unit(TimeUnits.DAY)

        # rst time
        self.octa = self._timestamp_to_unit(TimeUnits.OCTA)
        self.hexa = self._timestamp_to_unit(TimeUnits.HEXA)
        self.tap = self._timestamp_to_unit(TimeUnits.TAP)
        self.decitap = self._timestamp_to_unit(TimeUnits.DECITAP)
        self.beat = self._timestamp_to_unit(TimeUnits.BEAT)

        # utc time
        self.seconds = self._timestamp_to_unit(TimeUnits.SECONDS)
        self.minute = self._timestamp_to_unit(TimeUnits.MINUTE)
        self.hour = self._timestamp_to_unit(TimeUnits.HOUR)

    @classmethod
    def from_units(
        cls,
        quadrennials: float = 0,
        years: float = 0,
        days: float = 0,
        octas: float = 0,
        hexas: float = 0,
        taps: float = 0,
        decitaps: float = 0,
        beats: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
    ):
        timediff: float = 0
        # rst date
        timediff += quadrennials * UNIT_BEATS[TimeUnits.QUADRENNIAL]
        timediff += years * UNIT_BEATS[TimeUnits.YEAR]
        timediff += days * UNIT_BEATS[TimeUnits.DAY]

        # rst time
        timediff += octas * UNIT_BEATS[TimeUnits.OCTA]
        timediff += hexas * UNIT_BEATS[TimeUnits.HEXA]
        timediff += taps * UNIT_BEATS[TimeUnits.TAP]
        timediff += decitaps * UNIT_BEATS[TimeUnits.DECITAP]
        timediff += beats * UNIT_BEATS[TimeUnits.BEAT]

        # utc time
        timediff += seconds * UNIT_BEATS[TimeUnits.SECONDS]
        timediff += minutes * UNIT_BEATS[TimeUnits.MINUTE]
        timediff += hours * UNIT_BEATS[TimeUnits.HOUR]
        return cls(int(timediff))

    def _timestamp_to_unit(self, unit: TimeUnits):
        if UNIT_LENGTHS[unit]:
            positive_unit = int(abs(self.timediff) // UNIT_BEATS[unit] % UNIT_LENGTHS[unit])
        else:
            positive_unit = int(abs(self.timediff) // UNIT_BEATS[unit])
        if self.timediff < 0:
            return -positive_unit
        return positive_unit

    def __add__(self, other):
        if type(other) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeDelta' and '{type(other)}'")
        return RTSTimeDelta(self.timediff + other.timediff)

    def __sub__(self, other):
        if type(other) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeDelta' and '{type(other)}'")
        return RTSTimeDelta(self.timediff - other.timediff)


class RTSTimeComponent(object):
    UNIT_NEGATIVE_OFFSET = {
        TimeUnits.BEAT: 1,
        TimeUnits.DECITAP: 1,
        TimeUnits.TAP: 1,
        TimeUnits.HEXA: 1,
        TimeUnits.OCTA: 1,
        TimeUnits.ROLLING_OCTA: 0,
        TimeUnits.DAY: 1,
        TimeUnits.YEAR: 0,
        TimeUnits.QUADRENNIAL: 0,
        TimeUnits.SECONDS: 1,
        TimeUnits.MINUTE: 1,
        TimeUnits.HOUR: 1,
        TimeUnits.ROLLING_HOUR: 0,
    }

    BEAT_LENGTH_SECOND = 0.75

    def __init__(self, timestamp: int, name: str):
        self.name = name
        self.timestamp = timestamp
        # rst date
        self.quadrennial = self._timestamp_to_unit(TimeUnits.QUADRENNIAL)
        self.year = self._timestamp_to_unit(TimeUnits.YEAR)
        self.day = self._timestamp_to_unit(TimeUnits.DAY)

        # rst time
        self.rolling_octa = self._timestamp_to_unit(TimeUnits.ROLLING_OCTA)
        self.octa = self._timestamp_to_unit(TimeUnits.OCTA)
        self.hexa = self._timestamp_to_unit(TimeUnits.HEXA)
        self.tap = self._timestamp_to_unit(TimeUnits.TAP)
        self.decitap = self._timestamp_to_unit(TimeUnits.DECITAP)
        self.beat = self._timestamp_to_unit(TimeUnits.BEAT)

        # utc time
        self.seconds = self._timestamp_to_unit(TimeUnits.SECONDS)
        self.minute = self._timestamp_to_unit(TimeUnits.MINUTE)
        self.hour = self._timestamp_to_unit(TimeUnits.HOUR)
        self.rolling_hour = self._timestamp_to_unit(TimeUnits.ROLLING_HOUR)

    @classmethod
    def now(cls, name: str, epoch: int):
        time = (datetime.datetime.now().timestamp() - epoch) / cls.BEAT_LENGTH_SECOND
        return cls(int(time), name)

    @classmethod
    def from_timestamp(cls, timestamp: str):
        if not re.match("^\w+:\-?\d+$", timestamp):
            raise ValueError(f"Invalid timestamp: {timestamp}")
        name, timestamp = timestamp.split(":")
        timestamp_value = int(timestamp)
        return cls(timestamp_value, name)

    @classmethod
    def from_units(
        cls,
        name: str,
        quadrennials: int = 0,
        years: int = 0,
        days: int = 0,
        octas: int = 0,
        hexas: int = 0,
        taps: int = 0,
        decitaps: int = 0,
        beats: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        timestamp: float = 0
        # rst date
        timestamp += quadrennials * UNIT_BEATS[TimeUnits.QUADRENNIAL]
        timestamp += years * UNIT_BEATS[TimeUnits.YEAR]
        timestamp += days * UNIT_BEATS[TimeUnits.DAY]

        # rst time
        timestamp += octas * UNIT_BEATS[TimeUnits.OCTA]
        timestamp += hexas * UNIT_BEATS[TimeUnits.HEXA]
        timestamp += taps * UNIT_BEATS[TimeUnits.TAP]
        timestamp += decitaps * UNIT_BEATS[TimeUnits.DECITAP]
        timestamp += beats * UNIT_BEATS[TimeUnits.BEAT]

        # utc time
        timestamp += seconds * UNIT_BEATS[TimeUnits.SECONDS]
        timestamp += minutes * UNIT_BEATS[TimeUnits.MINUTE]
        timestamp += hours * UNIT_BEATS[TimeUnits.HOUR]
        return cls(ceil(timestamp), name)

    @classmethod
    def from_time_component(cls, time_component: "RTSTimeComponent", name: str | None = None):
        return cls(time_component.timestamp, name if name is not None else time_component.name)

    def _timestamp_to_unit(self, unit: TimeUnits):
        timestamp = self.timestamp + 1 if self.timestamp < 0 else self.timestamp
        if UNIT_LENGTHS[unit]:
            positive_unit = int(abs(timestamp) // UNIT_BEATS[unit] % UNIT_LENGTHS[unit])
        else:
            positive_unit = int(abs(timestamp) // UNIT_BEATS[unit])
        if self.timestamp < 0:
            return UNIT_LENGTHS[unit] - positive_unit - self.UNIT_NEGATIVE_OFFSET[unit]
        return positive_unit

    def add(self, timedelta: RTSTimeDelta, new_name: str | None = None):
        if type(timedelta) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeComponent' and '{type(timedelta)}'")
        return RTSTimeComponent(
            self.timestamp + timedelta.timediff,
            self.name if new_name is None else new_name,
        )

    def sub(self, timedelta: RTSTimeDelta, new_name: str | None = None):
        if type(timedelta) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeComponent' and '{type(timedelta)}'")
        return RTSTimeComponent(self.timestamp - timedelta.timediff, self.name if new_name is None else new_name)

    def format(self, format_str):
        fmt_values = {
            f"[{self.name}.QU]": self.quadrennial,
            f"[{self.name}.YE]": self.year,
            f"[{self.name}.DA]": self.day,
            f"[{self.name}.OC]": self.octa,
            f"[{self.name}.HE]": self.hexa,
            f"[{self.name}.TA]": self.tap,
            f"[{self.name}.DE]": self.decitap,
            f"[{self.name}.BE]": self.beat,
            f"[{self.name}.SE]": self.seconds,
            f"[{self.name}.MI]": self.minute,
            f"[{self.name}.HO]": self.hour,
            f"[{self.name}.RH]": self.rolling_hour,
            f"[{self.name}.RO]": self.rolling_octa,
        }
        for key, value in fmt_values.items():
            format_str = format_str.replace(key, str(value))
        return format_str

    def to_timestamp(self):
        return f"{self.name}:{self.timestamp}"

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    def __eq__(self, value: object) -> bool:
        if type(value) is not RTSTimeComponent:
            return False
        return self.timestamp == value.timestamp

    def __repr__(self):
        quadrennials = f"quadrennials={self.quadrennial}, " if self.quadrennial else ""
        days = f"days={self.day}, " if self.day else ""
        years = f"years={self.year}, " if self.year else ""
        octas = f"octas={self.octa}, " if self.octa else ""
        hexas = f"hexas={self.hexa}, " if self.hexa else ""
        taps = f"taps={self.tap}, " if self.tap else ""
        decitaps = f"decitaps={self.decitap}, " if self.decitap else ""
        beats = f"beats={self.beat}, " if self.beat else ""
        comp_str = f"{quadrennials}{days}{years}{octas}{hexas}{taps}{decitaps}{beats}"[:-2]
        return f"RSTimeComponent.from_units({comp_str})"


class RTSDateTime(object):
    def __init__(self, time_components: list[RTSTimeComponent], static_time_components: list[RTSTimeComponent]):
        self._ticking_components = time_components
        self._static_components = static_time_components
        self._components = {component.name: component for component in self._ticking_components + self._static_components}

    @classmethod
    def from_timestamp(cls, timestamp: str):
        ticking_components, static_components = timestamp.split(".")
        return cls(
            [RTSTimeComponent.from_timestamp(component) for component in ticking_components.split(",") if component],
            [RTSTimeComponent.from_timestamp(component) for component in static_components.split(",") if component],
        )

    def __add__(self, other):
        if type(other) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for +: 'RSTimeDate' and '{type(other)}'")
        return RTSDateTime(
            [component + other for component in self._ticking_components],
            self._static_components,
        )

    def __sub__(self, other):
        if type(other) is not RTSTimeDelta:
            raise TypeError(f"unsupported operand type(s) for -: 'RSTimeDate' and '{type(other)}'")
        return RTSDateTime(
            [component - other for component in self._ticking_components],
            self._static_components,
        )

    def format(self, format_str: str):
        for component in self._ticking_components + self._static_components:
            format_str = component.format(format_str)
        return format_str

    def to_timestamp(self):
        component_str = ",".join([component.to_timestamp() for component in self._ticking_components])
        static_component_str = ",".join([component.to_timestamp() for component in self._static_components])
        return f"{component_str}.{static_component_str}"

    def __getitem__(self, key: str):
        return self._components[key]

    def __repr__(self):
        return f"RSTimeDate({self._ticking_components}, {self._static_components})"
