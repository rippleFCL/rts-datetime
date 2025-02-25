import pytest
from rtsdatetime.units import GeneratedRSTUnit


@pytest.fixture
def generated_unit_data():
    return [
        (4, 1, 0),
        (4, 2, 0),
        (45, 6, 0),
        (456, 60, 0),
        (-4, 1, 0),
        (-4, 2, 0),
        (-45, 6, 0),
        (-456, 60, 0),
    ]


@pytest.fixture
def generated_unit_data_with_wrap():
    return [
        (4, 1, 1),
        (4, 2, 1),
        (45, 6, 2),
        (456, 60, 1),
        (-5, 1, 2),
        (-6, 2, 2),
        (-45, 6, 2),
        (-456, 60, 1),
    ]


def test_init(generated_unit_data, generated_unit_data_with_wrap):
    for timestamp, length, wrap in generated_unit_data + generated_unit_data_with_wrap:
        unit = GeneratedRSTUnit(timestamp, length, wrap)
        assert unit.timestamp == timestamp
        assert unit.length == length
        assert unit.wrap == wrap

def test_wrap(generated_unit_data_with_wrap):
    results = [
        0,
        0,
        1,
        0,
        1,
        0,
        1,
        -1
    ]
    assert len(results) == len(generated_unit_data_with_wrap)
    for (timestamp, length, wrap), result in zip(generated_unit_data_with_wrap, results):
        unit = GeneratedRSTUnit(timestamp, length, wrap)
        assert unit.absolute_unit == result

def test_generated_unit_wrap():
    unit = GeneratedRSTUnit(0, 1, 4)
    assert unit.absolute_unit == 0
    unit = GeneratedRSTUnit(3, 1, 4)
    assert unit.absolute_unit == 3
    unit = GeneratedRSTUnit(4, 1, 4)
    assert unit.absolute_unit == 0
    unit = GeneratedRSTUnit(5, 1, 4)
    assert unit.absolute_unit == 1



def test_generated_unit_str():
    unit = GeneratedRSTUnit(0, 1, 4)
    assert str(unit) == "0"
    unit = GeneratedRSTUnit(3, 1, 4)
    assert str(unit) == "3"
    unit = GeneratedRSTUnit(-1, 1, 4)
    assert str(unit) == "0"


def test_generated_unit_repr():
    unit = GeneratedRSTUnit(0, 1, 4)
    assert repr(unit) == "GeneratedRSTUnit(0, 1, 4)"
