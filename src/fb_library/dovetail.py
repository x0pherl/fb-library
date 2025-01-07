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


# def split_part(
#     part: Part,
#     start: Point,
#     end: Point,
#     linear_offset=0,
#     tolerance=0.025,
#     angle_offset=15,
#     scarf_distance=0,
#     length_ratio=3,
#     depth_ratio=6,
# ) -> Compound:
#     base_angle = start.angle_to(end)
#     max_dimension = (
#         max(
#             part.bounding_box().size.X,
#             part.bounding_box().size.Y,
#             part.bounding_box().size.Z,
#         )
#         * 3
#     )

#     with BuildLine() as bottom_tail_line:
#         Polyline(
#             tuple(start),
#             tuple(start.related_point(base_angle + 225, max_dimension)),
#             tuple(end.related_point(base_angle + 135, max_dimension)),
#             tuple(end),
#         )
#         add(
#             (
#                 start=start,
#                 end=end,
#                 section=DovetailPart.TAIL,
#                 linear_offset=linear_offset,
#                 tolerance=tolerance,
#                 angle_offset=angle_offset,
#                 scarf_distance=0,
#                 length_ratio=length_ratio,
#                 depth_ratio=depth_ratio,
#             )
#         )
#     with BuildLine() as top_tail_line:
#         add(
#             dovetail_split_line(
#                 start=start,
#                 end=end,
#                 section=DovetailPart.TAIL,
#                 linear_offset=linear_offset,
#                 tolerance=tolerance,
#                 angle_offset=angle_offset,
#                 scarf_distance=scarf_distance,
#                 length_ratio=length_ratio,
#                 depth_ratio=depth_ratio,
#             )
#         )

#     part1 = Part()
#     part2 = Part()
#     return Compound(part1, part2)


def tail_part_outline(
    part: Part,
    start: Point,
    end: Point,
    linear_offset=0,
    tolerance=0.025,
    angle_offset=15,
    scarf_distance=0,
    length_ratio=3,
    depth_ratio=6,
) -> Line:
    base_angle = start.angle_to(end)
    dovetail_tolerance = -(abs(tolerance / 2))
    adjusted_start_point = start.related_point(
        base_angle - 90, dovetail_tolerance
    )
    adjusted_end_point = end.related_point(base_angle - 90, dovetail_tolerance)

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
            tuple(adjusted_start_point),
            tuple(
                adjusted_start_point.related_point(
                    base_angle + 180, max_dimension
                )
            ),
            tuple(
                adjusted_start_point.related_point(
                    base_angle - 225, max_dimension
                )
            ),
            tuple(
                adjusted_start_point.related_point(
                    base_angle + 45, max_dimension
                )
            ),
            tuple(
                adjusted_start_point.related_point(base_angle, max_dimension)
            ),
            tuple(adjusted_end_point),
        )
        add(
            dovetail_split_line(
                start=start,
                end=end,
                section=DovetailPart.TAIL,
                linear_offset=linear_offset,
                tolerance=tolerance,
                angle_offset=angle_offset,
                scarf_distance=scarf_distance,
                length_ratio=length_ratio,
                depth_ratio=depth_ratio,
            )
        )
    return bottom_tail_line.line


def socket_part_outline(
    part: Part,
    start: Point,
    end: Point,
    linear_offset=0,
    tolerance=0.025,
    angle_offset=15,
    scarf_distance=0,
    length_ratio=3,
    depth_ratio=6,
) -> Line:
    base_angle = start.angle_to(end)
    dovetail_tolerance = abs(tolerance / 2)
    adjusted_start_point = start.related_point(
        base_angle - 90, dovetail_tolerance
    )
    adjusted_end_point = end.related_point(base_angle - 90, dovetail_tolerance)

    max_dimension = (
        max(
            part.bounding_box().size.X,
            part.bounding_box().size.Y,
            part.bounding_box().size.Z,
        )
        * 3
    )

    with BuildLine() as socket_line:
        Polyline(
            tuple(adjusted_start_point),
            tuple(
                adjusted_start_point.related_point(
                    base_angle + 180, max_dimension
                )
            ),
            tuple(
                adjusted_start_point.related_point(
                    base_angle + 225, max_dimension
                )
            ),
            tuple(
                adjusted_start_point.related_point(
                    base_angle - 45, max_dimension
                )
            ),
            tuple(
                adjusted_start_point.related_point(base_angle, max_dimension)
            ),
            tuple(adjusted_end_point),
        )
        add(
            dovetail_split_line(
                start=start,
                end=end,
                section=DovetailPart.SOCKET,
                linear_offset=linear_offset,
                tolerance=tolerance,
                angle_offset=angle_offset,
                scarf_distance=scarf_distance,
                length_ratio=length_ratio,
                depth_ratio=depth_ratio,
            )
        )
    return socket_line.line


def tail_subpart(
    part: Part,
    start: Point,
    end: Point,
    linear_offset=0,
    tolerance=0.025,
    angle_offset=15,
    scarf_distance=0,
    length_ratio=3,
    depth_ratio=6,
) -> Part:
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(part.bounding_box().min.Z)):
            with BuildLine():
                add(
                    tail_part_outline(
                        part=part,
                        start=start,
                        end=end,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        angle_offset=angle_offset,
                        scarf_distance=scarf_distance,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                    )
                )
            make_face()
        with BuildSketch(Plane.XY.offset(part.bounding_box().max.Z)):
            with BuildLine():
                add(
                    tail_part_outline(
                        part=part,
                        start=start,
                        end=end,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        angle_offset=angle_offset,
                        scarf_distance=0,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                    )
                )
            make_face()
        loft()
        add(part, mode=Mode.INTERSECT)
    return intersect.part


def socket_subpart(
    part: Part,
    start: Point,
    end: Point,
    linear_offset=0,
    tolerance=0.025,
    angle_offset=15,
    scarf_distance=0,
    length_ratio=3,
    depth_ratio=6,
) -> Part:
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(part.bounding_box().min.Z)):
            with BuildLine():
                add(
                    socket_part_outline(
                        part=part,
                        start=start,
                        end=end,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        angle_offset=angle_offset,
                        scarf_distance=scarf_distance,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                    )
                )
            make_face()
        with BuildSketch(Plane.XY.offset(part.bounding_box().max.Z)):
            with BuildLine():
                add(
                    socket_part_outline(
                        part=part,
                        start=start,
                        end=end,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        angle_offset=angle_offset,
                        scarf_distance=0,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
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
        - linear_offset: offsets the placement of the dovetail by the ammount specified
        - tolerance: the tolerance for the split
        - angle_offset: the adjustment pitch of angle of the dovetail
        - scarf_distance: an extra shrinking factor for the dovetail size
    """
    dovetail_tolerance = (
        -(abs(tolerance / 2))
        if section == DovetailPart.TAIL
        else abs(tolerance / 2)
    )

    base_angle = start.angle_to(end)
    length = start.distance_to(end)
    tongue_length = length / length_ratio
    tongue_depth = length / depth_ratio
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
    # show(
    #     (
    #         Point(0, 0),
    #         Point(5, 5),
    #         section=DovetailPart.TAIL,
    #         linear_offset=0,
    #         scarf_distance=0,
    #     ),
    #     dovetail_split_line(
    #         Point(0, 0),
    #         Point(5, 5),
    #         section=DovetailPart.SOCKET,
    #         linear_offset=0,
    #     ),
    #     reset_camera=Camera.KEEP,
    # )
    with BuildPart() as test:
        Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    show(
        # test.part,
        # socket_part_outline(
        #     test.part, Point(-5, 0), Point(5, 0), scarf_distance=0.5
        # ),
        # tail_part_outline(
        #     test.part, Point(-5, 0), Point(5, 0), scarf_distance=0.5
        # ),
        tail_subpart(test.part, Point(-5, 0), Point(5, 0), scarf_distance=0.5),
        socket_subpart(
            test.part, Point(-5, 0), Point(5, 0), scarf_distance=0.5
        ),
        reset_camera=Camera.KEEP,
    )
