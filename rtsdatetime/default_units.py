import datetime
import secrets
from .units import RTSTimeUnits, RTSUnit
from dataclasses import dataclass


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
    seconds_ratio = 3/4
    epoch = datetime.datetime(2005, 3, 16)


class RSTStandardUnits(RTSTimeUnits):
    seconds: RTSUnit = RTSUnit(1, 60)
    minute: RTSUnit = RTSUnit(60, 60)
    hour: RTSUnit = RTSUnit(3600, 24)
    rolling_hour: RTSUnit = RTSUnit(3600, 0)
    seconds_ratio = 1
    epoch = datetime.datetime(2005, 3, 16)


class StandardUnits(RTSTimeUnits):
    year: RTSUnit = RTSUnit(31536000, 0)
    day: RTSUnit = RTSUnit(86400, 365)
    hour: RTSUnit = RTSUnit(3600, 24)
    minute: RTSUnit = RTSUnit(60, 60)
    second: RTSUnit = RTSUnit(1, 60)
    seconds_ratio = 1
    epoch = datetime.datetime.fromtimestamp(0)
     
