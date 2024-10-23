from curses.ascii import RS
from re import T
from rtsdatetime.model import RTSDateTime, RTSTimeComponent, RTSTimeDelta


def test_init():
    base = RTSTimeComponent.from_units("base", beats=31)
    com1 = base.sub(RTSTimeDelta.from_units(beats=12), "com1")
    com2 = base.sub(RTSTimeDelta.from_units(beats=12, octas=2), "com2")
    scom1 = base.sub(RTSTimeDelta.from_units(beats=12, octas=2), "scom1")

    datetime = RTSDateTime(
        [base, com1, com2],
        [scom1],
    )

    assert base == datetime["base"]
    assert com1 == datetime["com1"]
    assert com2 == datetime["com2"]
    assert scom1 == datetime["scom1"]


def test_to_timestamp():
    base = RTSTimeComponent.from_units("base", beats=31)
    com1 = base.sub(RTSTimeDelta.from_units(beats=12), "com1")
    com2 = base.sub(RTSTimeDelta.from_units(beats=12, octas=2), "com2")
    scom1 = base.sub(RTSTimeDelta.from_units(beats=12, octas=3), "scom1")
    scom2 = base.sub(RTSTimeDelta.from_units(beats=12, octas=4), "scom2")

    datetime = RTSDateTime(
        [base, com1, com2],
        [scom1, scom2],
    )

    assert datetime.to_timestamp() == "base:31,com1:19,com2:-38381.scom1:-57581,scom2:-76781"


def test_from_timestamp():
    base = RTSTimeComponent.from_units("base", beats=31)
    com1 = base.sub(RTSTimeDelta.from_units(beats=12), "com1")
    com2 = base.sub(RTSTimeDelta.from_units(beats=12, octas=2), "com2")
    scom1 = base.sub(RTSTimeDelta.from_units(beats=12, octas=3), "scom1")
    scom2 = base.sub(RTSTimeDelta.from_units(beats=12, octas=4), "scom2")

    datetime = RTSDateTime.from_timestamp("base:31,com1:19,com2:-38381.scom1:-57581,scom2:-76781")

    assert base == datetime["base"]
    assert com1 == datetime["com1"]
    assert com2 == datetime["com2"]
    assert scom1 == datetime["scom1"]
    assert scom2 == datetime["scom2"]
