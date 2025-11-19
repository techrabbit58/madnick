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
