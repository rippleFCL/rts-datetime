import pytest
from rtsdatetime.model import RTSTimeDelta


def timedelta_tester(rst_time_delta, test_results):
    assert rst_time_delta.timediff == test_results.get("timediff", 0)

    # rst date
    assert rst_time_delta.year == test_results.get("year", 0)
    assert rst_time_delta.quadrennial == test_results.get("quadrennial", 0)
    assert rst_time_delta.day == test_results.get("day", 0)

    # rst time
    assert rst_time_delta.octa == test_results.get("octa", 0)
    assert rst_time_delta.hexa == test_results.get("hexa", 0)
    assert rst_time_delta.tap == test_results.get("tap", 0)
    assert rst_time_delta.decitap == test_results.get("decitap", 0)
    assert rst_time_delta.beat == test_results.get("beat", 0)

    # utc time
    assert rst_time_delta.hour == test_results.get("hour", 0)
    assert rst_time_delta.minute == test_results.get("minute", 0)
    assert rst_time_delta.seconds == test_results.get("seconds", 0)


def test_rstimedelta():
    test_data = [
        (
            {"days": 367, "octas": 2, "hexas": 3, "taps": 4, "decitaps": 5, "beats": 6},
            {
                "timediff": 42325806,
                "year": 1,
                "day": 367,
                "octa": 2,
                "hexa": 3,
                "tap": 4,
                "decitap": 5,
                "beat": 6,
                "hour": 9,
                "minute": 52,
                "seconds": 34,
            },
        ),
        (
            {"beats": -4},
            {
                "timediff": -4,
                "beat": -4,
                "seconds": -3,
            },
        ),
        (
            {"days": -2, "octas": 2, "hexas": 3, "taps": 4, "decitaps": 5, "beats": 6},
            {
                "timediff": -182994,
                "day": -1,
                "octa": -3,
                "hexa": -4,
                "tap": -1,
                "decitap": -4,
                "beat": -34,
                "hour": -14,
                "minute": -7,
                "seconds": -25,
            },
        ),
        (
            {"days": -2, "octas": -2, "hexas": 3, "taps": 4, "decitaps": 5, "beats": 6},
            {
                "timediff": -259794,
                "day": -2,
                "octa": -1,
                "hexa": -4,
                "tap": -1,
                "decitap": -4,
                "beat": -34,
                "hour": -6,
                "minute": -7,
                "seconds": -25,
            },
        ),
        (
            {"days": -2, "octas": -2},
            {
                "timediff": -268800,
                "day": -2,
                "octa": -2,
                "hour": -8,
            },
        ),
        (
            {"days": -2, "octas": -2, "hexas": -3, "taps": -4, "decitaps": -5, "beats": -6},
            {
                "timediff": -277806,
                "day": -2,
                "octa": -2,
                "hexa": -3,
                "tap": -4,
                "decitap": -5,
                "beat": -6,
                "hour": -9,
                "minute": -52,
                "seconds": -34,
            },
        ),
    ]
    # test all units existing
    for test_args, test_results in test_data:
        rst_time_delta = RTSTimeDelta.from_units(**test_args)
        timedelta_tester(rst_time_delta, test_results)


def test_subtraction():
    subtractions = [
        (
            {"beats": 15, "octas": 2},
            {"beats": 15, "octas": 2},
            {},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1},
            {"beats": 15, "octas": 2},
            {
                "timediff": 115200,
                "day": 1,
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1},
            {"beats": 15, "octas": 4},
            {
                "timediff": 76800,
                "octa": 4,
                "hour": 16,
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1},
            {"beats": 15, "octas": 4, "days": 1},
            {
                "timediff": -38400,
                "octa": -2,
                "hour": -8,
            },
        ),
    ]

    for test_comargs, test_diffargs, test_results in subtractions:
        base = RTSTimeDelta.from_units(**test_comargs)
        adder = RTSTimeDelta.from_units(**test_diffargs)
        new_date = base - adder

        timedelta_tester(new_date, test_results)
        with pytest.raises(TypeError):
            base - 1
        with pytest.raises(TypeError):
            base - 1.0
        with pytest.raises(TypeError):
            base - "abc"


def test_addition():
    additions = [
        (
            {"beats": 15, "octas": 2},
            {"beats": 15, "octas": 2},
            {
                "timediff": 76830,
                "octa": 4,
                "beat": 30,
                "hour": 16,
                "seconds": 22,
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1},
            {"beats": 15, "octas": 2},
            {
                "timediff": 192030,
                "octa": 4,
                "day": 1,
                "beat": 30,
                "hour": 16,
                "seconds": 22,
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1},
            {"beats": 15, "octas": 4},
            {
                "timediff": 230430,
                "seconds": 22,
                "day": 2,
                "beat": 30,
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1},
            {"beats": 15, "octas": 4, "days": 1},
            {
                "timediff": 345630,
                "day": 3,
                "beat": 30,
                "seconds": 22,
            },
        ),
    ]

    for test_comargs, test_diffargs, test_results in additions:
        base = RTSTimeDelta.from_units(**test_comargs)
        adder = RTSTimeDelta.from_units(**test_diffargs)
        new_date = base + adder

        timedelta_tester(new_date, test_results)
        with pytest.raises(TypeError):
            base + 1
        with pytest.raises(TypeError):
            base + 1.0
        with pytest.raises(TypeError):
            base + "abc"
