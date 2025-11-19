import pytest

from .vm import tens_complement, to_signed


@pytest.mark.parametrize("signed, expected", [
    (0, 0),
    (1, 1),
    (-1, 999),
    (-499, 501),
    (-500, 500),
    (499, 499),
])
def test_complement_base_1000(signed, expected):
    assert tens_complement(signed) == expected


@pytest.mark.parametrize("complement, expected", [
    (0, 0),
    (1, 1),
    (499, 499),
    (999, -1),
    (501, -499),
    (500, -500),
])
def test_complement_to_signed_base_1000(complement, expected):
    assert to_signed(complement) == expected


@pytest.mark.parametrize("a, b, expected", [
    (1, -1, 0),
    (-1, 1, 0),
    (499, 499, -2),
    (-500, 0, -500),
    (0, -500, -500),
    (1, -500, -499),
    (-1, -500, 499),
    (-500, -500, 0),
    (499, -499, 0),
    (499, 1, -500),
    (42, 78, 120),
    (-42, 78, 36),
    (42, -78, -36),
    (-42, -78, -120),
])
def test_add(a, b, expected):
    ...


@pytest.mark.parametrize("a, b, expected", [
    (1, -1, 2),
    (-1, 1, -2),
    (499, 499, 0),
    (-500, 0, -500),
    (0, -500, -500),
    (1, -500, -499),
    (-1, -500, 499),
    (-500, -500, 0),
    (499, -499, -2),
    (499, 1, 498),
    (42, 78, -36),
    (-42, 78, -120),
    (42, -78, 120),
    (-42, -78, 36),
])
def test_sub(a, b, expected):
    ...
