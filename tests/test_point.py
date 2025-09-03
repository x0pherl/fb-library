from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from math import radians, tan
from fb_library.point import Point, midpoint, shifted_midpoint


class TestPoint:
    def test_point_creation_with_coordinates(self):
        p = Point(3.0, 4.0)
        assert p.x == 3.0
        assert p.y == 4.0

    def test_point_creation_with_list(self):
        p = Point([3.0, 4.0])
        assert p.x == 3.0
        assert p.y == 4.0

    def test_point_properties(self):
        p = Point(3.0, 4.0)
        assert p.X == 3.0
        assert p.Y == 4.0

    def test_point_iteration(self):
        p = Point(3.0, 4.0)
        coords = list(p)
        assert coords == [3.0, 4.0]

    def test_point_indexing(self):
        p = Point(3.0, 4.0)
        assert p[0] == 3.0
        assert p[1] == 4.0

        with pytest.raises(IndexError):
            _ = p[2]

    def test_angle_to(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        angle = p1.angle_to(p2)
        assert angle == pytest.approx(45.0)

    def test_distance_to(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        distance = p1.distance_to(p2)
        assert distance == pytest.approx(5.0)

    def test_related_point(self):
        p = Point(0, 0)
        related = p.related_point(45, 5)
        assert related.x == pytest.approx(3.5355339059327378)
        assert related.y == pytest.approx(3.5355339059327378)


class TestUtilityFunctions:
    def test_midpoint(self):
        p1 = Point(0, 0)
        p2 = Point(10, 10)
        mid = midpoint(p1, p2)
        assert mid.x == 5.0
        assert mid.y == 5.0

    def test_shifted_midpoint_no_shift(self):
        p1 = Point(0, 0)
        p2 = Point(10, 10)
        shifted_mid = shifted_midpoint(p1, p2, 0)
        assert shifted_mid.x == pytest.approx(5.0)
        assert shifted_mid.y == pytest.approx(5.0)

    def test_shifted_midpoint_with_shift(self):
        p1 = Point(0, 0)
        p2 = Point(10, 0)
        shifted_mid = shifted_midpoint(p1, p2, 2)
        assert shifted_mid.x == pytest.approx(7.0)  # 5 + 2
        assert shifted_mid.y == pytest.approx(0.0)

    def test_shifted_midpoint_diagonal_shift(self):
        p1 = Point(0, 0)
        p2 = Point(6, 8)  # 3-4-5 triangle scaled by 2
        shifted_mid = shifted_midpoint(p1, p2, 1)  # shift by 1 unit towards p2

        # Midpoint is at (3, 4)
        # Direction vector is (6, 8), normalized to (0.6, 0.8)
        # Shifted midpoint is (3, 4) + 1 * (0.6, 0.8) = (3.6, 4.8)
        assert shifted_mid.x == pytest.approx(3.6)
        assert shifted_mid.y == pytest.approx(4.8)
