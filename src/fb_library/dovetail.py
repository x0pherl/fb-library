from enum import Enum
from math import radians, tan
from typing import Tuple
from build123d import (
    Align,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Box,
    Compound,
    Line,
    Mode,
    Part,
    Plane,
    Polyline,
    Select,
    Vertex,
    add,
    extrude,
    fillet,
    loft,
    make_face,
)
from point import (
    Point,
    midpoint,
    shifted_midpoint,
)
from ocp_vscode import show, Camera


class DovetailPart(Enum):
    TAIL = 1
    SOCKET = 2


def subpart_outline(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.05,
    tail_angle_offset=15,
    scarf_distance=0,
    length_ratio=3,
    depth_ratio=6,
    tilt_offset=0,
) -> Line:
    """
    given a part and a start and end point on the XY plane, returns an outline to build an intersection Part to generate the subpart
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - scarf_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - tilt_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
    """
    direction_multiplier = 1 if section == DovetailPart.TAIL else -1
    base_angle = start.angle_to(end)
    dovetail_tolerance = -(abs(tolerance / 2)) * direction_multiplier
    adjusted_start_point = start.related_point(base_angle - 90, tilt_offset)
    adjusted_end_point = end.related_point(base_angle - 90, tilt_offset)
    toleranced_start_point = adjusted_start_point.related_point(
        base_angle - 90, dovetail_tolerance
    )
    toleranced_end_point = adjusted_end_point.related_point(
        base_angle - 90, dovetail_tolerance
    )

    max_dimension = (
        max(
            part.bounding_box().size.X,
            part.bounding_box().size.Y,
            part.bounding_box().size.Z,
        )
        * 3
    )

    with BuildLine() as bottom_tail_line:
        Polyline(
            tuple(toleranced_start_point),
            tuple(
                toleranced_start_point.related_point(
                    base_angle + 180, max_dimension
                )
            ),
            tuple(
                toleranced_start_point.related_point(
                    base_angle - 225 * direction_multiplier, max_dimension
                )
            ),
            tuple(
                toleranced_start_point.related_point(
                    base_angle + 45 * direction_multiplier, max_dimension
                )
            ),
            tuple(
                toleranced_start_point.related_point(base_angle, max_dimension)
            ),
            tuple(toleranced_end_point),
        )
        add(
            dovetail_split_line(
                start=adjusted_start_point,
                end=adjusted_end_point,
                section=section,
                linear_offset=linear_offset,
                tolerance=tolerance,
                tail_angle_offset=tail_angle_offset,
                scarf_distance=scarf_distance,
                length_ratio=length_ratio,
                depth_ratio=depth_ratio,
            )
        )
    return bottom_tail_line.line


def subpart(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.05,
    tail_angle_offset=15,
    scarf_distance=0,
    length_ratio=1 / 3,
    depth_ratio=1 / 6,
    tilt=0,
) -> Part:
    """
    given a part and a start and end point on the XY plane, returns a Part for the appropriate split section
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - scarf_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - tilt: setting this to a non-zero value will tilt the dovetail along the Z axis which may improve part stability
    """
    tilt_offset = (part.bounding_box().size.Z * tan(radians(tilt))) / 2
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(part.bounding_box().min.Z)):
            with BuildLine():
                add(
                    subpart_outline(
                        part=part,
                        start=start,
                        end=end,
                        section=section,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        tail_angle_offset=tail_angle_offset,
                        scarf_distance=scarf_distance,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        tilt_offset=-tilt_offset,
                    )
                )
            make_face()
        with BuildSketch(Plane.XY.offset(part.bounding_box().max.Z)):
            with BuildLine():
                add(
                    subpart_outline(
                        part=part,
                        start=start,
                        end=end,
                        section=section,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        tail_angle_offset=tail_angle_offset,
                        scarf_distance=0,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        tilt_offset=tilt_offset,
                    )
                )
            make_face()
        loft()
        add(part, mode=Mode.INTERSECT)
    return intersect.part


def dovetail_split_line(
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.05,
    tail_angle_offset=15,
    scarf_distance=0,
    length_ratio=1 / 3,
    depth_ratio=1 / 6,
) -> Line:
    """
    given a start and end point, returns a dovetail split outline as a Line object
    args:
        - start: the start point for the dovetail line
        - end: the end point for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - scarf_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
    """
    dovetail_tolerance = (
        -(abs(tolerance / 2))
        if section == DovetailPart.TAIL
        else abs(tolerance / 2)
    )

    base_angle = start.angle_to(end)
    length = start.distance_to(end)
    tongue_length = length * length_ratio
    tongue_depth = length * depth_ratio
    adjusted_start_point = start.related_point(
        base_angle - 90, dovetail_tolerance
    )
    tail_base_start = adjusted_start_point.related_point(
        base_angle,
        length / 2
        - tongue_length / 2
        - dovetail_tolerance * 1.5
        + scarf_distance
        + linear_offset,
    )

    tail_base_resume = adjusted_start_point.related_point(
        base_angle,
        length / 2
        + tongue_length / 2
        + dovetail_tolerance * 1.5
        - scarf_distance
        + linear_offset,
    )
    tail_end_start = tail_base_start.related_point(
        base_angle - 90 - tail_angle_offset,
        tongue_depth - scarf_distance,
    )
    tail_end = tail_base_resume.related_point(
        base_angle - 90 + tail_angle_offset,
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
    with BuildPart() as test:
        Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    show(
        subpart(
            test.part,
            Point(-5, 0),
            Point(5, 0),
            scarf_distance=0.5,
            section=DovetailPart.TAIL,
            tilt=20,
        ),
        subpart(
            test.part,
            Point(-5, 0),
            Point(5, 0),
            scarf_distance=0.5,
            section=DovetailPart.SOCKET,
            tilt=20,
        ),
        reset_camera=Camera.KEEP,
    )
