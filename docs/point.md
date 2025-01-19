# Point

## Overview

The `Point` module provides a set of functions and methods to work with 2D points. It includes operations such as calculating angles, distances, and finding related points.

## Point

The `Point` class Represents a point in 2D space. Instantiating a point is as simple as:
```
from fb_library import Point
Point(1,3)
```
or it can be instantiated with a list:
```
from fb_library import Point
Point([1,3])
```
Once you've defined a point, you can access the x or y values through a variety of means:
```
x = Point(1,3)
x.x # returns the x coordinate (1)
x.Y # returns the y coordinate (3)
x[1] # returns the y coordinate (3)
```

### Methods

#### angle_to
- `angle_to(self, point: Point) -> float`
  - Identifies the angle to a second point from the current point.
    ```
    Point(0,0).angle_to(Point(1,1)) # returns 45.0
    ```

#### distance_to
- `distance_to(point: Point) -> float`
  - Identifies the distance to a second point from the current point.
    ```
    Point(0,10).distance_to(Point(10,10)) # returns 10.0
    ```

#### related_point
- `related_point(angle: float, distance: float) -> Point`
  - Identifies a second point at a specified angle and distance from the current point.
    ```
     Point(0,0).related_point(45, math.sqrt(2))
     # returns Point(x=1.0000000000000002, y=1.0000000000000002)
    ```

### Utility Functions

- `midpoint(point1: Point, point2: Point) -> Point`
  - Finds the midpoint between two points.
    ```
    from point import midpoint
    midpoint(Point(0,0), Point(10,10))
    # returns Point(x=5.0, y=5.0)
    ```

- `shifted_midpoint(point1: Point, point2: Point, shift: float) -> Point`
  - Finds the midpoint between two points, shifted by `shift` towards the second point.
  This can be useful when you need to make something slightly off center between two arbitrary points, or when adding points at regular midpoints of a line
    ```
    from point import shifted_midpoint
    shifted_midpoint(Point(0,0), Point(3,3), 1)
    # rturns Point(x=2.2071067811865475, y=2.2071067811865475)
    ```
