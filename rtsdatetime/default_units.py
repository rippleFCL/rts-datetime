import datetime
from .units import RTSTimeUnits, RTSUnit
from dataclasses import dataclass


@dataclass
class RSTUnits(RTSTimeUnits):
    beat: RTSUnit = RTSUnit(1, 40)
    decitap: RTSUnit = RTSUnit(40, 10)
    tap: RTSUnit = RTSUnit(400, 6)
    hexa: RTSUnit = RTSUnit(2400, 8)
    octa: RTSUnit = RTSUnit(19200, 6)
    rolling_octa: RTSUnit = RTSUnit(19200, 0)
    day: RTSUnit = RTSUnit(115200, 0)
    year: RTSUnit = RTSUnit(42077520, 0)
    quadrennial: RTSUnit = RTSUnit(168310080, 0)
    seconds_ratio: float = 3/4
    epoch = datetime.datetime(2005, 3, 16)


@dataclass
class RSTStandardUnits(RTSTimeUnits):
    seconds: RTSUnit = RTSUnit(4 / 3, 60)
    minute: RTSUnit = RTSUnit(80, 60)
    hour: RTSUnit = RTSUnit(4800, 24)
    rolling_hour: RTSUnit = RTSUnit(4800, 0)
    seconds_ratio: float = 1
    epoch = datetime.datetime(2005, 3, 16)


@dataclass
class StandardUnits(RTSTimeUnits):
    seconds: RTSUnit = RTSUnit(1, 60)
    minute: RTSUnit = RTSUnit(60, 60)
    hour: RTSUnit = RTSUnit(3600, 24)
    day: RTSUnit = RTSUnit(86400, 365)
    year: RTSUnit = RTSUnit(31536000, 0)
    quad: RTSUnit = RTSUnit(4 / 3, 0)
    seconds_ratio: float = 1

