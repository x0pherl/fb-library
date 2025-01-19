from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from unittest.mock import patch
from pathlib import Path


from fb_library.point import Point, midpoint, shifted_midpoint


class TestPoint:
    def test_creation(self):
        x = Point(1, 2)
        assert x.X == 1
        assert x.Y == 2

    def test_list(self):
        x = Point([1, 2])
        assert x[0] == 1
        assert x[1] == 2
        with pytest.raises(IndexError):
            x[2]

    def test_midpoint(self):
        mid = midpoint(Point(0, 0), Point(2, 2))
        assert mid.X == 1
        assert mid.Y == 1

    def test_shifted_midpoint(self):
        mid = shifted_midpoint(Point(0, 0), Point(10, 10), 2)
        assert mid.X == pytest.approx(6.414213562373095)
        assert mid.Y == pytest.approx(6.414213562373095)
