from enum import Enum
from math import radians, tan
from typing import Tuple
from build123d import BuildLine, Line, Polyline, Axis, Select, Vertex, fillet
from .point import (
    Point,
    midpoint,
    shifted_midpoint,
)
from ocp_vscode import show, Camera


class DovetailPart(Enum):
    TAIL = 1
    SOCKET = 2


def dovetail_split_outline(
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    liner_offset=0,
    tolerance=0.025,
    angle_offset=15,
    scarf_distance=0,
    length_ratio=3,
    depth_ratio=6,
) -> Line:
    """
    given a start and a length, returns a dovetail split outline as a Line object
    args:
        - start: the part to split
        - length: the length of the cut (the dovetail will take approximately 1/3 of the length)
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - liner_offset: offsets the placement of the dovetail by the ammount specified
        - tolerance: the tolerance for the split
        - angle_offset: the adjustment pitch of angle of the dovetail
        - scarf_distance: an extra shrinking factor for the dovetail size
    """
    dovetail_tolerance = (
        -(abs(tolerance)) if section == DovetailPart.TAIL else abs(tolerance)
    )

    tail_center = shifted_midpoint(start, end, liner_offset)
    base_angle = start.angle_to(end)
    length = start.distance_to(end)
    tongue_length = length / length_ratio
    tongue_depth = length / depth_ratio
    offset = tongue_length * tan(radians(angle_offset))
    adjusted_start_point = start.related_point(
        base_angle - 90, dovetail_tolerance
    )
    tail_base_start = adjusted_start_point.related_point(
        base_angle,
        length / 2
        - tongue_length / 2
        - dovetail_tolerance * 1.5
        + scarf_distance,
    )
    tail_base_resume = adjusted_start_point.related_point(
        base_angle,
        length / 2
        + tongue_length / 2
        + dovetail_tolerance * 1.5
        - scarf_distance,
    )
    tail_end_start = tail_base_start.related_point(
        base_angle - 90 - angle_offset,
        tongue_depth - scarf_distance,
    )
    tail_end = tail_base_resume.related_point(
        base_angle - 90 + angle_offset,
        tongue_depth - scarf_distance,
    )
    adjusted_end_point = adjusted_start_point.related_point(base_angle, length)

    with BuildLine() as dovetail_outline:
        Polyline(
            adjusted_start_point,
            tail_base_start,
            tail_end_start,
            tail_end,
            tail_base_resume,
            adjusted_end_point,
        )
        fillet(
            dovetail_outline.vertices()
            .filter_by_position(
                Axis.X, tail_base_start.x, tail_base_start.x, (True, True)
            )
            .filter_by_position(
                Axis.Y, tail_base_start.y, tail_base_start.y, (True, True)
            )
            + dovetail_outline.vertices()
            .filter_by_position(
                Axis.X, tail_base_resume.x, tail_base_resume.x, (True, True)
            )
            .filter_by_position(
                Axis.Y, tail_base_resume.y, tail_base_resume.y, (True, True)
            ),
            abs(
                dovetail_tolerance * (2 if section == DovetailPart.TAIL else 3)
            ),
        )
        fillet(
            dovetail_outline.vertices()
            .filter_by_position(
                Axis.X, tail_end_start.x, tail_end_start.x, (True, True)
            )
            .filter_by_position(
                Axis.Y, tail_end_start.y, tail_end_start.y, (True, True)
            )
            + dovetail_outline.vertices()
            .filter_by_position(Axis.X, tail_end.x, tail_end.x, (True, True))
            .filter_by_position(Axis.Y, tail_end.y, tail_end.y, (True, True)),
            abs(
                dovetail_tolerance * (3 if section == DovetailPart.TAIL else 2)
            ),
        )
    return dovetail_outline.line


if __name__ == "__main__":
    show(
        dovetail_split_outline(
            Point(0, 0),
            Point(5, 5),
            section=DovetailPart.TAIL,
            liner_offset=0,
            scarf_distance=0,
        ),
        dovetail_split_outline(
            Point(0, 0),
            Point(5, 5),
            section=DovetailPart.SOCKET,
            liner_offset=0,
        ),
        reset_camera=Camera.KEEP,
    )
