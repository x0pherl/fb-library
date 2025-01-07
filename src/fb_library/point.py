from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin
from typing import Union, Tuple


@dataclass
class Point:
    x: float
    y: float

    @property
    def X(self):
        return self.x

    @property
    def Y(self):
        return self.y

    def __init__(
        self, x: Union[float, Tuple[float, float]] = None, y: float = None
    ):
        if isinstance(x, tuple):
            self.x, self.y = x
        else:
            self.x = x
            self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

    def angle_to(self, point: "Point") -> float:
        return degrees(atan2(point.y - self.y, point.x - self.x))

    def distance_to(self, point: "Point") -> float:
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def related_point(self, angle: float, distance: float) -> "Point":
        angle_rad = radians(angle)
        return Point(
            self.x + distance * cos(angle_rad),
            self.y + distance * sin(angle_rad),
        )


def midpoint(point1: Point, point2: Point) -> Point:
    midpoint = Point((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)
    return midpoint


def shifted_midpoint(point1: Point, point2: Point, shift: float) -> Point:
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
