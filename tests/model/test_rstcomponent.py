from curses.ascii import RS
from re import T
import pytest
from rtsdatetime.model import RTSTimeComponent, RTSTimeDelta


def component_tester(rst_component: RTSTimeComponent, test_results: dict[str, int]):
    assert rst_component.timestamp == test_results.get("timestamp", 0)
    # rst date
    assert rst_component.year == test_results.get("year", 0)
    assert rst_component.quadrennial == test_results.get("quadrennial", 0)
    assert rst_component.day == test_results.get("day", 0)

    # rst time
    assert rst_component.rolling_octa == test_results.get("rolling_octa", 0)
    assert rst_component.octa == test_results.get("octa", 0)
    assert rst_component.hexa == test_results.get("hexa", 0)
    assert rst_component.tap == test_results.get("tap", 0)
    assert rst_component.decitap == test_results.get("decitap", 0)
    assert rst_component.beat == test_results.get("beat", 0)

    # utc time
    assert rst_component.rolling_hour == test_results.get("rolling_hour", 0)
    assert rst_component.hour == test_results.get("hour", 0)
    assert rst_component.minute == test_results.get("minute", 0)
    assert rst_component.seconds == test_results.get("seconds", 0)
    assert rst_component.name == test_results.get("name", "")


def test_timestamp():
    timestamps = [
        ("test", 12345678),
        ("test2", 20),
        ("test3", 1234567),
        ("test4", 3475753),
        ("test5", 3475753),
        ("test6", -1234567),
        ("test7", -3475753),
        ("test8", -3475753),
    ]
    for name, timestamp in timestamps:
        rst_component = RTSTimeComponent.from_timestamp(f"{name}:{timestamp}")
        assert rst_component.timestamp == timestamp
        assert rst_component.name == name

    timestamps = ["test:1234a5678", "12312323", "test:123451a", "test:123451 a", "test:123451 test:123451", "test:--123421313"]
    for timestamp in timestamps:
        with pytest.raises(ValueError):
            rst_component = RTSTimeComponent.from_timestamp(timestamp)


def test_from_units():
    test_data = [
        (
            {"days": 367, "octas": 2, "hexas": 3, "taps": 4, "decitaps": 5, "beats": 6, "name": "test"},
            {
                "timestamp": 42325806,
                "year": 1,
                "day": 367,
                "rolling_octa": 2204,
                "octa": 2,
                "hexa": 3,
                "tap": 4,
                "decitap": 5,
                "beat": 6,
                "rolling_hour": 8817,
                "hour": 9,
                "minute": 52,
                "seconds": 34,
                "name": "test",
            },
        ),
        (
            {"name": "test"},
            {"name": "test"},
        ),
        (
            {"days": -1, "beats": 2, "name": "test"},
            {
                "timestamp": -115198,
                "day": -1,
                "rolling_octa": -5,
                "beat": 2,
                "rolling_hour": -23,
                "seconds": 2,
                "name": "test",
            },
        ),
        (
            {"days": -1, "beats": -2, "name": "test"},
            {
                "timestamp": -115202,
                "day": -2,
                "rolling_octa": -6,
                "octa": 5,
                "hexa": 7,
                "tap": 5,
                "decitap": 9,
                "beat": 38,
                "rolling_hour": -24,
                "hour": 23,
                "minute": 59,
                "seconds": 59,
                "name": "test",
            },
        ),
        (
            {"days": 1, "hours": 20, "minutes": 50, "seconds": 10, "name": "test"},
            {
                "timestamp": 215214,
                "day": 1,
                "rolling_octa": 11,
                "octa": 5,
                "hexa": 1,
                "tap": 4,
                "beat": 14,
                "rolling_hour": 44,
                "hour": 20,
                "minute": 50,
                "seconds": 10,
                "name": "test",
            },
        ),
        (
            {"years": 1, "name": "test"},
            {
                "timestamp": 42077520,
                "year": 1,
                "day": 365,
                "rolling_octa": 2191,
                "octa": 1,
                "hexa": 4,
                "tap": 1,
                "decitap": 8,
                "rolling_hour": 8766,
                "hour": 6,
                "minute": 9,
                "name": "test",
            },
        ),
    ]
    # test all units existing
    for test_args, test_results in test_data:
        rst_component = RTSTimeComponent.from_units(**test_args)
        component_tester(rst_component, test_results)


def test_addition():
    additions = [
        (
            {"beats": 15, "octas": 2, "name": "test"},
            {"beats": 15, "octas": 2},
            {
                "timestamp": 76830,
                "beat": 30,
                "octa": 4,
                "rolling_octa": 4,
                "rolling_hour": 16,
                "hour": 16,
                "minute": 0,
                "seconds": 22,
                "name": "test",
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 2},
            {
                "timestamp": 192030,
                "beat": 30,
                "octa": 4,
                "day": 1,
                "rolling_octa": 10,
                "rolling_hour": 40,
                "hour": 16,
                "minute": 0,
                "seconds": 22,
                "name": "test",
            },
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 4},
            {
                "timestamp": 230430,
                "beat": 30,
                "day": 2,
                "rolling_octa": 12,
                "rolling_hour": 48,
                "hour": 0,
                "minute": 0,
                "seconds": 22,
                "name": "test",
            },
        ),
    ]

    for test_comargs, test_diffargs, test_results in additions:
        date = RTSTimeComponent.from_units(**test_comargs)
        adder = RTSTimeDelta.from_units(**test_diffargs)

        new_date = date + adder
        component_tester(new_date, test_results)

        new_date = date.add(adder, "new_name")
        test_results["name"] = "new_name"
        component_tester(new_date, test_results)

        with pytest.raises(TypeError):
            date + 1
        with pytest.raises(TypeError):
            date + 1.0
        with pytest.raises(TypeError):
            date + "abc"


def test_subtraction():
    subtractions = [
        (
            {"beats": 15, "octas": 2, "name": "test"},
            {"beats": 15, "octas": 2},
            {"name": "test"},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 2},
            {"timestamp": 115200, "day": 1, "rolling_octa": 6, "rolling_hour": 24, "name": "test"},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 4},
            {"timestamp": 76800, "rolling_octa": 4, "octa": 4, "rolling_hour": 16, "hour": 16, "name": "test"},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 4, "days": 1},
            {"timestamp": -38400, "rolling_octa": -1, "day": -1, "octa": 4, "rolling_hour": -7, "hour": 16, "name": "test"},
        ),
    ]

    for test_comargs, test_diffargs, test_results in subtractions:
        date = RTSTimeComponent.from_units(**test_comargs)
        adder = RTSTimeDelta.from_units(**test_diffargs)
        new_date = date - adder
        component_tester(new_date, test_results)

        new_date = date.sub(adder, "new_name")
        test_results["name"] = "new_name"
        component_tester(new_date, test_results)

        with pytest.raises(TypeError):
            date - 1
        with pytest.raises(TypeError):
            date - 1.0
        with pytest.raises(TypeError):
            date - "abc"


def test_equality():
    equal = [
        (
            {"beats": 15, "octas": 2, "name": "test"},
            {"beats": 15, "octas": 2, "name": "test"},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
        ),
    ]

    for test_a, test_b in equal:
        tast_tc1 = RTSTimeComponent.from_units(**test_a)
        test_tc2 = RTSTimeComponent.from_units(**test_b)
        assert tast_tc1 == test_tc2

    not_equal = [
        (
            {"beats": 15, "octas": 2, "name": "test"},
            {"beats": 14, "octas": 2, "name": "test"},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 3, "days": 1, "name": "test"},
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            {"beats": 15, "octas": 2, "days": 2, "name": "test"},
        ),
    ]

    for test_a, test_b in not_equal:
        tast_tc1 = RTSTimeComponent.from_units(**test_a)
        test_tc2 = RTSTimeComponent.from_units(**test_b)
        assert tast_tc1 != test_tc2

    test_false = [
        ({"beats": 15, "octas": 2, "name": "test"}, 0),
        ({"beats": 15, "octas": 2, "days": 1, "name": "test"}, "a"),
        ({"beats": 15, "octas": 2, "days": 1, "name": "test"}, 0.1),
    ]
    for test_a, value in test_false:
        tast_tc1 = RTSTimeComponent.from_units(**test_a)
        assert tast_tc1 != value


def test_repr():
    values = [
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            "RSTimeComponent.from_units(days=1, octas=2, beats=15)",
        ),
        (
            {"beats": 15, "octas": 2, "days": 1, "name": "test"},
            "RSTimeComponent.from_units(days=1, octas=2, beats=15)",
        ),
        (
            {"beats": 19, "octas": 4, "days": 13, "name": "test"},
            "RSTimeComponent.from_units(days=13, octas=4, beats=19)",
        ),
        (
            {"beats": 19, "octas": 4, "hexas":3, "decitaps": 1, "days": 13, "name": "test"},
            "RSTimeComponent.from_units(days=13, octas=4, hexas=3, decitaps=1, beats=19)",
        ),
    ]
    for args, expected in values:
        test_tc = RTSTimeComponent.from_units(**args)
        assert repr(test_tc) == expected


def test_from_timecomponent():
    test_tc = RTSTimeComponent(134566, "base")

    new_tc = RTSTimeComponent.from_time_component(test_tc)

    assert new_tc == test_tc
    assert new_tc.name == "base"

    test_tc = RTSTimeComponent(134566, "base")

    new_tc = RTSTimeComponent.from_time_component(test_tc, "test")

    assert new_tc == test_tc
    assert new_tc.name == "test"

    new_tc = RTSTimeComponent.from_time_component(test_tc)

    assert new_tc == test_tc
    assert new_tc.name == "base"

    new_tc = RTSTimeComponent.from_time_component(test_tc, "test")

    assert new_tc == test_tc
    assert new_tc.name == "test"


def test_to_timestamp():
    new_tc = RTSTimeComponent(134566, "base")
    assert new_tc.to_timestamp() == "base:134566"

    new_tc = RTSTimeComponent(1458777, "test")
    assert new_tc.to_timestamp() == "test:1458777"

    new_tc = RTSTimeComponent(1458777, "test_tc")
    assert new_tc.to_timestamp() == "test_tc:1458777"


def test_format():
    format_str = "[b.RO]:[b.OC]:[b.HE]:[b.TA]:[b.DE]:[b.BE]/[b.RH]:[b.HO]:[b.MI]:[b.SE] [b.DA]-[b.YE]-[b.QU]"

    new_tc = RTSTimeComponent(134566, "b")
    assert new_tc.format(format_str) == "7:1:0:0:04:06/28:04:02:04 1-0-0"

    new_tc = RTSTimeComponent(1458777, "b")
    assert new_tc.format(format_str) == "75:3:7:4:09:17/303:15:54:42 12-0-0"

    new_tc = RTSTimeComponent(1458777, "c")
    assert (
        new_tc.format(format_str)
        == "[b.RO]:[b.OC]:[b.HE]:[b.TA]:[b.DE]:[b.BE]/[b.RH]:[b.HO]:[b.MI]:[b.SE] [b.DA]-[b.YE]-[b.QU]"
    )
