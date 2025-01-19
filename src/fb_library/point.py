"""
A minimal abstraction for a 2D point, allowing the x,y values to be interpreted from a tuple.
Also has some utility functions for calculating various useful properties of points.
"""

from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin, tan
from typing import Union, Tuple


@dataclass
class Point:
    """
    A 2D point with x and y coordinates.
    """

    x: float
    y: float

    @property
    def X(self):
        "the x coordinate of the point"
        return self.x

    @property
    def Y(self):
        "the y coordinate of the point"
        return self.y

    def __init__(
        self, x: Union[float, list[float, float]] = None, y: float = None
    ):
        """initialze the point with x and y coordinates passed as a tuple or idividual values"""
        if isinstance(x, list) and len(x) >= 2:
            self.x, self.y = x
        else:
            self.x = x
            self.y = y

    def __iter__(self):
        """iterate through the x and x coordinates of the point"""
        yield self.x
        yield self.y

    def __getitem__(self, index):
        """return the x or y coordinate of the point"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

    def angle_to(self, point: "Point") -> float:
        """from the point, identify the angle to a second point"""
        return degrees(atan2(point.y - self.y, point.x - self.x)) % 360

    def distance_to(self, point: "Point") -> float:
        """from the point, identify the distance to a second point"""
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def related_point(self, angle: float, distance: float) -> "Point":
        """from the point, identify a second point at a specified angle and distance"""
        angle_rad = radians(angle)
        return Point(
            self.x + distance * cos(angle_rad),
            self.y + distance * sin(angle_rad),
        )


def midpoint(point1: Point, point2: Point) -> Point:
    """find the midpoint between two points
    ----------
    Arguments:
        - point1: Point
            The first point.
        - point2: Point
            The second point."""
    midpoint = Point((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)
    return midpoint


def shifted_midpoint(point1: Point, point2: Point, shift: float) -> Point:
    """find the midpoint between two points, with an allowance to shift the
    midpoint towards point2
    ----------
    Arguments:
        - point1: Point
            The first point.
        - point2: Point
            The second point.
        - shift: float
            The distance to shift the midpoint towards point2"""
    mid_x = (point1.x + point2.x) / 2
    mid_y = (point1.y + point2.y) / 2

    direction_x = point2.x - point1.x
    direction_y = point2.y - point1.y

    # Normalize the direction vector
    length = (direction_x**2 + direction_y**2) ** 0.5
    direction_x /= length
    direction_y /= length

    # Shift the midpoint towards point2 by the specified amount
    shifted_mid_x = mid_x + direction_x * shift
    shifted_mid_y = mid_y + direction_y * shift

    return Point(shifted_mid_x, shifted_mid_y)
