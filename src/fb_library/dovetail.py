from enum import Enum
from math import atan, atan2, degrees, radians, tan
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
    Location,
    Mode,
    Part,
    Plane,
    Polyline,
    add,
    extrude,
    fillet,
    loft,
    make_face,
)

from build123d.objects_part import Cylinder, Sphere

# from fb_library.point import (
from point import (
    Point,
    midpoint,
    shifted_midpoint,
)

from click_fit import divot

from ocp_vscode import show, Camera


class DovetailPart(Enum):
    TAIL = 1
    SOCKET = 2


def dovetail_subpart_outline(
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
    tilt_offset=0,
    straighten_dovetail=False,
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
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
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

    with BuildLine() as tail_line:
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
        if straighten_dovetail:
            Line(toleranced_start_point, toleranced_end_point)
        else:
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
    return tail_line.line


def subpart_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.05,
    tilt=0,
    scarf_distance=0,
    depth_ratio=1 / 6,
    vertical_offset=0,
    click_fit_radius=0,
):
    """
    adds/subtracts click-fit divots to subpart and returns it
    ----------
    Arguments:
        - subpart: the part to add divots to
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tilt: the tilt angle of the dovetail
        - scarf_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - vertical_offset: the vertical offset of the dovetail
        - click_fit_radius: the radius of the click-fit divots
    """

    cut_angle = start.angle_to(end)

    # how much of an offset is there along the top and bottom of the subparts
    tilt_offset = (subpart.bounding_box().size.Z) * tan(radians(tilt)) / 2

    tailtop_z = subpart.bounding_box().max.Z + (
        vertical_offset if vertical_offset < 0 else 0
    )
    # if there's a scarf, the tail is at a different angle than the rest of the subpart
    adjusted_top_divot_angle = (
        tilt
        if scarf_distance == 0
        else tilt
        + (degrees(atan((scarf_distance + abs(tolerance * 4)) / tailtop_z)))
    )

    # the required adjustement when the top of the dovetail is not the top of the part
    tailtop_offset = (
        tailtop_z
        * tan(radians(abs(adjusted_top_divot_angle)))
        * (-1 if tilt < 0 else 1)
    )

    topmode = (
        Mode.SUBTRACT
        if ((section == DovetailPart.TAIL) == (vertical_offset < 0))
        else Mode.ADD
    )
    bottommode = (
        Mode.ADD
        if ((section == DovetailPart.SOCKET) == (vertical_offset >= 0))
        else Mode.SUBTRACT
    )

    top_divot_center = shifted_midpoint(
        start, end, linear_offset
    ).related_point(
        cut_angle - 90,
        -tilt_offset
        + start.distance_to(end) * depth_ratio
        + abs(tolerance) * (0.5 if vertical_offset < 0 else -0.5)
        - scarf_distance
        + tailtop_offset
        - ((click_fit_radius * 2) * tan(radians(adjusted_top_divot_angle))),
    )
    with BuildPart() as divotedpart:
        add(subpart, mode=Mode.ADD)
        with BuildPart(
            Location(
                (
                    top_divot_center.x,
                    top_divot_center.y,
                    tailtop_z - click_fit_radius * 2,
                )
            ),
            mode=topmode,
        ):
            add(
                divot(
                    click_fit_radius,
                    positive=topmode == Mode.ADD,
                    extend_base=True,
                )
                .rotate(
                    Axis.X,
                    (90 * (-1 if vertical_offset < 0 else 1))
                    + adjusted_top_divot_angle,
                )
                .rotate(Axis.Y, cut_angle),
            )
        #####################################
        # Bottom divots
        #####################################
        start_side = start.related_point(
            cut_angle, click_fit_radius * 2
        ).related_point(
            cut_angle + 90,
            tilt_offset - ((click_fit_radius * 2) * tan(radians(tilt))),
        )
        end_side = end.related_point(
            cut_angle, -click_fit_radius * 2
        ).related_point(
            cut_angle - 90,
            -tilt_offset + ((click_fit_radius * 2) * tan(radians(tilt))),
        )
        with BuildPart(
            Location(
                (
                    start_side.x,
                    start_side.y,
                    click_fit_radius * 2,
                )
            ),
            mode=bottommode,
        ):
            add(
                divot(
                    click_fit_radius,
                    positive=bottommode == Mode.ADD,
                    extend_base=True,
                )
                .rotate(
                    Axis.X, (90 * (1 if vertical_offset < 0 else -1)) + tilt
                )
                .rotate(Axis.Y, cut_angle),
            )
        with BuildPart(
            Location((end_side.x, end_side.y, click_fit_radius * 2)),
            mode=bottommode,
        ):
            add(
                divot(click_fit_radius, positive=True, extend_base=True)
                .rotate(
                    Axis.X,
                    (90 * (1 if vertical_offset < 0 else -1)) + tilt,
                )
                .rotate(Axis.Y, cut_angle),
            )

    return divotedpart.part


def dovetail_subpart(
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
    vertical_offset=0,
    click_fit_radius=0,
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
        - vertical_offset: offsets the dovetail along the Z axis by the ammount specified, which results in a straight line
            cut on one side, and provides a hard stop for fitting. A positive number results in a straight cut on the bottom
            of the part passed, a negagive number results in a straight cut on the top of the part passed
    """
    dovetail_tolerance = 0 if vertical_offset == 0 else abs(tolerance) / 2
    vertical_tolerance_adjustment = (
        dovetail_tolerance
        * (1 if section == DovetailPart.TAIL else -1)
        * (1 if vertical_offset > 0 else -1)
    )

    if abs(vertical_offset) > part.bounding_box().size.Z:
        raise ValueError(
            "Vertical offset cannot be greater than the part's height"
        )
    if vertical_offset < 0 and scarf_distance > 0:
        raise ValueError(
            "a postive scarf_distance and a negative vertical_offset will result in an invalid dovetail"
        )
    if vertical_offset > 0 and scarf_distance < 0:
        raise ValueError(
            "a negative scarf_distance and a positive vertical_offset will result in an invalid dovetail"
        )
    tilt_offset = (part.bounding_box().size.Z) * tan(radians(tilt)) / 2
    vertical_tilt_offset = abs(vertical_offset) * tan(radians(tilt))
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(part.bounding_box().min.Z)):
            with BuildLine():
                add(
                    dovetail_subpart_outline(
                        part=part,
                        start=start,
                        end=end,
                        section=section,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        tail_angle_offset=tail_angle_offset,
                        scarf_distance=(
                            scarf_distance if vertical_offset <= 0 else 0
                        ),
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        tilt_offset=-tilt_offset,
                        straighten_dovetail=vertical_offset > 0,
                    )
                )
            make_face()
        if vertical_offset > 0:
            with BuildSketch(
                Plane.XY.offset(
                    part.bounding_box().min.Z
                    + vertical_offset
                    + vertical_tolerance_adjustment
                )
            ):
                with BuildLine():
                    add(
                        dovetail_subpart_outline(
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
                            tilt_offset=-tilt_offset + vertical_tilt_offset,
                            straighten_dovetail=True,
                        )
                    )
                make_face()
            loft()
            with BuildSketch(
                Plane.XY.offset(
                    part.bounding_box().min.Z
                    + vertical_offset
                    + vertical_tolerance_adjustment
                )
            ):
                with BuildLine():
                    add(
                        dovetail_subpart_outline(
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
                            tilt_offset=-tilt_offset + vertical_tilt_offset,
                            straighten_dovetail=False,
                        )
                    )
                make_face()
        if vertical_offset < 0:
            with BuildSketch(
                Plane.XY.offset(
                    part.bounding_box().max.Z
                    + vertical_offset
                    + vertical_tolerance_adjustment
                )
            ):
                with BuildLine():
                    add(
                        dovetail_subpart_outline(
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
                            tilt_offset=tilt_offset - vertical_tilt_offset,
                            straighten_dovetail=False,
                        )
                    )
                make_face()
            loft()
            with BuildSketch(
                Plane.XY.offset(
                    part.bounding_box().max.Z
                    + vertical_offset
                    + vertical_tolerance_adjustment
                )
            ):
                with BuildLine():
                    add(
                        dovetail_subpart_outline(
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
                            tilt_offset=tilt_offset - vertical_tilt_offset,
                            straighten_dovetail=True,
                        )
                    )
                make_face()
        with BuildSketch(Plane.XY.offset(part.bounding_box().max.Z)):
            with BuildLine():
                add(
                    dovetail_subpart_outline(
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
                        straighten_dovetail=vertical_offset < 0,
                    )
                )
            make_face()
        loft()
        add(part, mode=Mode.INTERSECT)
        if click_fit_radius != 0:
            intersect.part = subpart_divots(
                intersect.part,
                start,
                end,
                section,
                linear_offset,
                tolerance,
                tilt,
                scarf_distance,
                depth_ratio,
                vertical_offset,
                click_fit_radius,
            )

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
    -------
    arguments:
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
    # tail_end_start = tail_base_start.related_point(
    #     base_angle - 90 - tail_angle_offset,
    #     tongue_depth - scarf_distance,
    # )
    tail_angle_extension = (tongue_depth - scarf_distance) * tan(
        radians(tail_angle_offset)
    )
    tail_end_start = tail_base_start.related_point(
        base_angle - 90,
        tongue_depth - scarf_distance,
    ).related_point(base_angle, -tail_angle_extension)

    tail_end = tail_base_resume.related_point(
        base_angle - 90,
        tongue_depth - scarf_distance,
    ).related_point(base_angle, tail_angle_extension)
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
    with BuildPart(mode=Mode.PRIVATE) as test:
        Box(50, 40, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))
        show(
            dovetail_subpart(
                test.part,
                Point(-25, 0),
                Point(25, 0),
                # scarf_distance=2,
                # scarf_distance=0,
                section=DovetailPart.TAIL,
                linear_offset=10,
                tilt=20,
                vertical_offset=16.5,
                click_fit_radius=1.25,
            ),
            dovetail_subpart(
                test.part,
                Point(-25, 0),
                Point(25, 0),
                scarf_distance=2,
                # scarf_distance=0,
                section=DovetailPart.SOCKET,
                linear_offset=10,
                tilt=20,
                vertical_offset=16.5,
                click_fit_radius=1.25,
            ).move(Location((0, -40, 0))),
            # dovetail_split_line(
            #     # test.part,
            #     Point(-5, 0),
            #     Point(5, 0),
            #     scarf_distance=0.5,
            #     section=DovetailPart.SOCKET,
            #     # tilt=20,
            # ),
            # dovetail_split_line(
            #     # test.part,
            #     Point(-5, 0),
            #     Point(5, 0),
            #     scarf_distance=0.5,
            #     tail_angle_offset=0,
            #     section=DovetailPart.SOCKET,
            #     # tilt=20,
            # ),
            # dovetail_split_line(
            #     # test.part,
            #     Point(-5, 0),
            #     Point(5, 0),
            #     scarf_distance=0.5,
            #     tail_angle_offset=35,
            #     section=DovetailPart.SOCKET,
            #     # tilt=20,
            # ),
            reset_camera=Camera.KEEP,
        )
