from enum import Enum, auto
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
    FilletPolyline,
    GridLocations,
    Line,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Polyline,
    add,
    extrude,
    fillet,
    loft,
    make_face,
)

from build123d.objects_part import Cylinder, Sphere

# it's a bad habit, but I keep some simple test code under __main__
# to make creating test object easy -- this adds ".fb_library" to the path
if __name__ == "__main__":
    import sys, os

    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


from fb_library.point import (
    Point,
    midpoint,
    shifted_midpoint,
)

from fb_library.click_fit import divot

class DovetailPart(Enum):
    TAIL = auto()
    SOCKET = auto()


class DovetailStyle(Enum):
    TRADITIONAL = auto()
    SNUGTAIL = auto()


def snugtail_subpart_outline(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    tolerance=0.025,
    length_ratio=.8,
    depth_ratio=.15,
    taper_distance=0,
    scarf_offset=0,
    straighten_dovetail=False,
) -> Line:
    """
    given a part and a start and end point on the XY plane, returns an outline to build an intersection Part to generate the subpart
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
    """
    tail_angle_offset = 25

    direction_multiplier = 1 if section == DovetailPart.TAIL else -1
    base_angle = start.angle_to(end)
    opposite_angle = 180 if base_angle == 0 else -base_angle
    dovetail_tolerance = -(abs(tolerance / 2)) * direction_multiplier
    adjusted_start_point = start.related_point(base_angle - 90, scarf_offset)
    adjusted_end_point = end.related_point(base_angle - 90, scarf_offset)
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

    cut_length = start.distance_to(end)
    tail_depth = cut_length * depth_ratio
    tail_length = cut_length * length_ratio

    cut_start = toleranced_start_point.related_point(
        base_angle - 90, tail_length/2 + dovetail_tolerance/2
    )

    cut_end = toleranced_end_point.related_point(
        base_angle - 90, tail_length/2 + dovetail_tolerance/2
    )

    fin_join = cut_start.related_point(
        base_angle, tail_depth + dovetail_tolerance
    ).related_point(
        base_angle - 90, tail_depth + dovetail_tolerance
    )
    fin_depart = cut_end.related_point(
        base_angle - 180, tail_depth + dovetail_tolerance
    ).related_point(
        base_angle - 90, tail_depth + dovetail_tolerance
    )

    start_fin = cut_start.related_point(
        base_angle, tail_depth + dovetail_tolerance
    ).related_point(base_angle + 90, dovetail_tolerance*1.5)
    end_fin = cut_end.related_point(
        base_angle - 180, tail_depth + dovetail_tolerance
    ).related_point(base_angle + 90, dovetail_tolerance*1.5)

    start_snugtail = start_fin.related_point(base_angle + 90, cut_length*(1-depth_ratio*2))
    end_snugtail = end_fin.related_point(base_angle + 90, cut_length*(1-depth_ratio*2))

    fin_connect = start_fin.related_point(base_angle + 90, cut_length*(1-depth_ratio)-dovetail_tolerance)
    
    fin_disconnect = end_fin.related_point(base_angle + 90, cut_length*(1-depth_ratio)-dovetail_tolerance)

    start_tail_line = fin_connect.related_point(base_angle, abs(dovetail_tolerance)
            * (4 if section == DovetailPart.TAIL else 6) - dovetail_tolerance*2)
    
    end_tail_line = fin_disconnect.related_point(opposite_angle, abs(dovetail_tolerance)
            * (4 if section == DovetailPart.TAIL else 6) - dovetail_tolerance*2)

    with BuildLine() as tail_line:
        Polyline(
            *[cut_start,
            cut_start.related_point(base_angle + 180, max_dimension),
            cut_start.related_point(
                base_angle - 225 * direction_multiplier, max_dimension
            ),
            cut_end.related_point(
                base_angle + 45 * direction_multiplier, max_dimension
            ),
            tuple(cut_end.related_point(base_angle, max_dimension)),
            tuple(cut_end),
        ])

        FilletPolyline(
            *[cut_start, fin_join, start_fin],
            radius=abs(dovetail_tolerance)
            * (3 if section == DovetailPart.TAIL else 2),
        )
        if straighten_dovetail:
            Line(start_fin, start_snugtail)
        else:
            add(
                dovetail_split_line(
                    start=start_fin.related_point(
                        base_angle, -dovetail_tolerance
                    ),
                    end=start_snugtail.related_point(
                        base_angle, -dovetail_tolerance
                    ),
                    section=section,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[start_snugtail,
            fin_connect,
            start_tail_line],
            radius=abs(dovetail_tolerance)
            * (2 if section == DovetailPart.TAIL else 3),
        )
        if straighten_dovetail:
            Line(
                start_tail_line,
                end_tail_line,
            )
        else:
            add(
                dovetail_split_line(
                    start=start_tail_line.related_point(
                        base_angle - 90, -dovetail_tolerance
                    ),
                    end=end_tail_line.related_point(
                        base_angle - 90, -dovetail_tolerance
                    ),
                    section=section,
                    linear_offset=0,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[end_tail_line,
            fin_disconnect,
            end_snugtail],
            radius=abs(dovetail_tolerance)
            * (2 if section == DovetailPart.TAIL else 3),
        )
        if straighten_dovetail:
            Line(end_snugtail, end_fin)
        else:
            add(
                dovetail_split_line(
                    start=end_snugtail.related_point(
                        base_angle, dovetail_tolerance
                    ),
                    end=end_fin.related_point(
                        base_angle, dovetail_tolerance
                    ),
                    section=section,
                    linear_offset=0,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[end_fin, fin_depart, cut_end],
            radius=abs(dovetail_tolerance)
            * (3 if section == DovetailPart.TAIL else 2),
        )
    return tail_line.line


def dovetail_subpart_outline(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.025,
    tail_angle_offset=15,
    taper_distance=0,
    length_ratio=1 / 3,
    depth_ratio=1 / 6,
    scarf_offset=0,
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
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
    """
    direction_multiplier = 1 if section == DovetailPart.TAIL else -1
    base_angle = start.angle_to(end)
    dovetail_tolerance = -(abs(tolerance / 2)) * direction_multiplier
    adjusted_start_point = start.related_point(base_angle - 90, scarf_offset)
    adjusted_end_point = end.related_point(base_angle - 90, scarf_offset)
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
        Polyline(*[
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
            tuple(toleranced_end_point)]
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
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
    return tail_line.line


def subpart_outline(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    linear_offset=0,
    tolerance=0.025,
    tail_angle_offset=15,
    taper_distance=0,
    length_ratio=1 / 3,
    depth_ratio=1 / 6,
    scarf_offset=0,
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
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
    """
    if style == DovetailStyle.TRADITIONAL:
        return dovetail_subpart_outline(
            part=part,
            start=start,
            end=end,
            section=section,
            linear_offset=linear_offset,
            tolerance=tolerance,
            tail_angle_offset=tail_angle_offset,
            taper_distance=taper_distance,
            length_ratio=length_ratio,
            depth_ratio=depth_ratio,
            scarf_offset=scarf_offset,
            straighten_dovetail=straighten_dovetail,
        )
    else:
        return snugtail_subpart_outline(
            part=part,
            start=start,
            end=end,
            section=section,
            tolerance=tolerance,
            taper_distance=taper_distance,
            scarf_offset=scarf_offset,
            straighten_dovetail=straighten_dovetail,
        )


def traditional_subpart_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.025,
    vertical_tolerance=0.2,
    scarf_angle=0,
    taper_angle=0,
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
        - scarf_angle: the scarf angle of the dovetail
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - vertical_offset: the vertical offset of the dovetail
        - click_fit_radius: the radius of the click-fit divots
    """

    cut_angle = start.angle_to(end)

    # how much of an offset is there along the top and bottom of the subparts
    scarf_offset = (
        (subpart.bounding_box().size.Z) * tan(radians(scarf_angle)) / 2
    )

    tailtop_z = subpart.bounding_box().max.Z + (
        vertical_offset if vertical_offset < 0 else 0
    )

    adjusted_top_divot_angle = scarf_angle - taper_angle

    taper_offset = (
        subpart.bounding_box().size.Z - abs(vertical_offset)
    ) * tan(radians(adjusted_top_divot_angle))

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
        start.distance_to(end) * depth_ratio
        - scarf_offset
        + taper_offset
        - click_fit_radius / 2,
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
            scarf_offset
            - ((click_fit_radius * 2) * tan(radians(scarf_angle))),
        )
        end_side = end.related_point(
            cut_angle, -click_fit_radius * 2
        ).related_point(
            cut_angle - 90,
            -scarf_offset
            + ((click_fit_radius * 2) * tan(radians(scarf_angle))),
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
                    Axis.X,
                    (90 * (1 if vertical_offset < 0 else -1)) + scarf_angle,
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
                    (90 * (1 if vertical_offset < 0 else -1)) + scarf_angle,
                )
                .rotate(Axis.Y, cut_angle),
            )

    return divotedpart.part


def snugtail_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    tolerance: float = 0.025,
    scarf_angle: float = 0,
    depth_ratio=1 / 10,
    length_ratio=1 / 5,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
) -> Part:
    part_width = start.distance_to(end)
    tail_depth = part_width * depth_ratio
    direction_multiplier = -1 if section == DovetailPart.TAIL else 1
    inner_width = (
        part_width
        - (part_width * depth_ratio * 2)
        - (tolerance * direction_multiplier)
    )
    cut_angle = start.angle_to(end)
    with BuildPart() as divotedpart:
        add(subpart, mode=Mode.ADD)
        with BuildPart(
            Location(
                (
                    0,
                    part_width * length_ratio * 1.5 + midpoint(start, end).Y,
                    click_fit_radius * 2,
                )
            ),
            mode=Mode.SUBTRACT if section == DovetailPart.SOCKET else Mode.ADD,
        ):
            with PolarLocations(inner_width / 2, 2, start_angle=cut_angle):
                add(
                    divot(
                        radius=click_fit_radius,
                        positive=True,
                        extend_base=True,
                    ).rotate(Axis.Y, -90)
                )
    return divotedpart.part


def subpart_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    linear_offset=0,
    tolerance=0.025,
    vertical_tolerance=0.2,
    scarf_angle=0,
    taper_angle=0,
    depth_ratio=1 / 6,
    length_ratio=1 / 3,
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
        - style: create a traditional dovetal or a cut that wraps around 3 sides of the object and creates a tighter fit
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - scarf_angle: the scarf angle of the dovetail
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - vertical_offset: the vertical offset of the dovetail
        - click_fit_radius: the radius of the click-fit divots
    """
    if style == DovetailStyle.TRADITIONAL:
        return traditional_subpart_divots(
            subpart=subpart,
            start=start,
            end=end,
            section=section,
            linear_offset=linear_offset,
            tolerance=tolerance,
            vertical_tolerance=vertical_tolerance,
            scarf_angle=scarf_angle,
            taper_angle=taper_angle,
            depth_ratio=depth_ratio,
            vertical_offset=vertical_offset,
            click_fit_radius=click_fit_radius,
        )
    else:
        return snugtail_divots(
            subpart=subpart,
            start=start,
            end=end,
            section=section,
            tolerance=tolerance,
            scarf_angle=scarf_angle,
            depth_ratio=1 / 10,
            length_ratio=1 / 5,
            vertical_offset=vertical_offset,
            click_fit_radius=click_fit_radius,
        )


def dovetail_subpart(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    linear_offset=0,
    tolerance=0.025,
    vertical_tolerance=0.2,
    tail_angle_offset=15,
    taper_angle=0,
    length_ratio=1 / 3,
    depth_ratio=1 / 6,
    scarf_angle=0,
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
        - style: create a traditional dovetal or a cut that wraps around 3 sides of the object and creates a tighter fit
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_angle: setting this to a non-zero value will tilt the dovetail along the Z axis which may improve part stability
        - vertical_offset: offsets the dovetail along the Z axis by the ammount specified, which results in a straight line
            cut on one side, and provides a hard stop for fitting. A positive number results in a straight cut on the bottom
            of the part passed, a negagive number results in a straight cut on the top of the part passed
    """
    if start == end:
        raise ValueError("start and end points cannot be the same")
    if abs(vertical_offset) > part.bounding_box().size.Z:
        raise ValueError(
            "Vertical offset cannot be greater than the part's height"
        )
    if vertical_offset < 0 and taper_angle < 0:
        raise ValueError(
            "a negative taper_angle and a positive vertical_offset will result in an invalid dovetail"
        )
    if vertical_offset > 0 and taper_angle > 0:
        raise ValueError(
            "a positive taper_angle and a positive vertical_offset will result in an invalid dovetail"
        )

    vertical_tolerance_adjustment = (
        vertical_tolerance
        * (1 if section == DovetailPart.TAIL else -1)
        * (1 if vertical_offset > 0 else -1)
    )
    scarf_offset = (part.bounding_box().size.Z) * tan(radians(scarf_angle)) / 2
    vertical_scarf_offset = (
        abs(vertical_offset) - vertical_tolerance_adjustment
    ) * tan(radians(scarf_angle))

    taper_offset = (
        part.bounding_box().size.Z
        - abs(vertical_offset)
        - vertical_tolerance_adjustment
    ) * tan(radians(abs(taper_angle)))
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(part.bounding_box().min.Z)):
            with BuildLine():
                add(
                    subpart_outline(
                        part=part,
                        start=start,
                        end=end,
                        section=section,
                        style=style,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        tail_angle_offset=tail_angle_offset,
                        taper_distance=(
                            taper_offset if (taper_angle < 0) else 0
                        ),
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        scarf_offset=-scarf_offset,
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
                        subpart_outline(
                            part=part,
                            start=start,
                            end=end,
                            section=section,
                            style=style,
                            linear_offset=linear_offset,
                            tolerance=tolerance,
                            tail_angle_offset=tail_angle_offset,
                            taper_distance=0,
                            length_ratio=length_ratio,
                            depth_ratio=depth_ratio,
                            scarf_offset=-scarf_offset + vertical_scarf_offset * (2 if section == DovetailPart.TAIL else .5),
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
                        subpart_outline(
                            part=part,
                            start=start,
                            end=end,
                            section=section,
                            style=style,
                            linear_offset=linear_offset,
                            tolerance=tolerance,
                            tail_angle_offset=tail_angle_offset,
                            taper_distance=(
                                taper_offset if (taper_angle < 0) else 0
                            ),
                            length_ratio=length_ratio,
                            depth_ratio=depth_ratio,
                            scarf_offset=-scarf_offset + vertical_scarf_offset * (2 if section == DovetailPart.TAIL else .5),
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
                        subpart_outline(
                            part=part,
                            start=start,
                            end=end,
                            section=section,
                            style=style,
                            linear_offset=linear_offset,
                            tolerance=tolerance,
                            tail_angle_offset=tail_angle_offset,
                            taper_distance=(
                                taper_offset if taper_angle > 0 else 0
                            ),
                            length_ratio=length_ratio,
                            depth_ratio=depth_ratio,
                            scarf_offset=scarf_offset - vertical_scarf_offset,
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
                        subpart_outline(
                            part=part,
                            start=start,
                            end=end,
                            section=section,
                            style=style,
                            linear_offset=linear_offset,
                            tolerance=tolerance,
                            tail_angle_offset=tail_angle_offset,
                            taper_distance=0,
                            length_ratio=length_ratio,
                            depth_ratio=depth_ratio,
                            scarf_offset=scarf_offset - vertical_scarf_offset,
                            straighten_dovetail=True,
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
                        style=style,
                        linear_offset=linear_offset,
                        tolerance=tolerance,
                        tail_angle_offset=tail_angle_offset,
                        taper_distance=(
                            taper_offset if taper_angle > 0 else 0
                        ),
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        scarf_offset=scarf_offset,
                        straighten_dovetail=vertical_offset < 0,
                    )
                )
            make_face()
        loft()
        add(part, mode=Mode.INTERSECT)
        if click_fit_radius != 0:
            intersect.part = subpart_divots(
                subpart=intersect.part,
                start=start,
                end=end,
                section=section,
                style=style,
                linear_offset=linear_offset,
                tolerance=tolerance,
                vertical_tolerance=vertical_tolerance,
                scarf_angle=scarf_angle,
                taper_angle=taper_angle,
                depth_ratio=depth_ratio,
                length_ratio=length_ratio,
                vertical_offset=vertical_offset,
                click_fit_radius=click_fit_radius,
            )

    return intersect.part


def dovetail_split_line(
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset=0,
    tolerance=0.025,
    tail_angle_offset=15,
    taper_distance=0,
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
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
    """
    dovetail_tolerance = (
        -(abs(tolerance / 2))
        if section == DovetailPart.TAIL
        else abs(tolerance / 2)
    )

    base_angle = start.angle_to(end)
    tail_angle_tolerance_adjustment = (dovetail_tolerance * tan(radians(tail_angle_offset)))
    base_angle = start.angle_to(end)
    length = start.distance_to(end)
    tongue_length = length * length_ratio + (dovetail_tolerance*2) 
    tongue_depth = length * depth_ratio
    tail_angle_extension = (tongue_depth - taper_distance) * tan(
        radians(tail_angle_offset)
    )
    adjusted_start_point = start.related_point(
        base_angle - 90, dovetail_tolerance
    )

    tail_end_start = adjusted_start_point.related_point(
        base_angle,
        length/2 - tongue_length/2-tail_angle_tolerance_adjustment+linear_offset,
    ).related_point(base_angle-90, tongue_depth)

    tail_end = adjusted_start_point.related_point(
        base_angle,
        length/2 + tongue_length/2+tail_angle_tolerance_adjustment+linear_offset,
    ).related_point(base_angle-90, tongue_depth)


    tail_base_start = adjusted_start_point.related_point(
        base_angle,
        length/2 - tongue_length/2 + tail_angle_extension - 
        tail_angle_tolerance_adjustment + linear_offset,
    )

    tail_base_resume = adjusted_start_point.related_point(
        base_angle,
        length/2 + tongue_length/2-tail_angle_extension+tail_angle_tolerance_adjustment+linear_offset,
    )

    adjusted_end_point = adjusted_start_point.related_point(base_angle, length)

    with BuildLine() as dovetail_outline:
        FilletPolyline(adjusted_start_point, tail_base_start, midpoint(tail_base_start, tail_end_start),
                radius=abs(dovetail_tolerance) * (2 if section == DovetailPart.TAIL else 3))
        FilletPolyline(midpoint(tail_base_start, tail_end_start), tail_end_start, midpoint(tail_end_start, tail_end),
                radius=abs(dovetail_tolerance) * (3 if section == DovetailPart.TAIL else 2))
        FilletPolyline(midpoint(tail_end_start, tail_end), tail_end, midpoint(tail_end, tail_base_resume),
                radius=abs(dovetail_tolerance) * (3 if section == DovetailPart.TAIL else 2))
        FilletPolyline(midpoint(tail_end, tail_base_resume), tail_base_resume, adjusted_end_point,
                radius=abs(dovetail_tolerance) * (2 if section == DovetailPart.TAIL else 3))

    return dovetail_outline.line

if __name__ == "__main__":
    from ocp_vscode import show, Camera

    with BuildPart(mode=Mode.PRIVATE) as test:
        Box(40, 200, 78.7, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(
                Plane.XY.offset(73.6
                ),
                mode=Mode.SUBTRACT,
            ):
                Cylinder(
                    25,
                    200,
                    rotation=(90, 0, 0),
                )

    tl = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.TAIL,
                    tolerance=.8,
                    vertical_tolerance=0.2,
                    taper_angle=2,
                    scarf_angle=20,
                    
                    vertical_offset=-14.33333,
                    click_fit_radius=.75
    ).move(Location((0, 0, 0)))
    sckt = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.SOCKET,
                    tolerance=.8,
                    vertical_tolerance=0.2,
                    taper_angle=2,
                    scarf_angle=20,
                    vertical_offset=-14.33333,
                    click_fit_radius=.75
    )
    sckt.color = (0.5, 0.5, .5)
    splines = snugtail_subpart_outline(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.SOCKET,
        taper_distance=0,
        tolerance=0.8,
        # scarf_angle=20,
        # straighten_dovetail=True,
    )
    spline = snugtail_subpart_outline(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.TAIL,
        taper_distance=0,
        tolerance=0.8,
        # scarf_angle=20,
        # straighten_dovetail=True,
    )
    splines.color = (0.5, 0.5, 0.5)
    with BuildSketch() as sks:
        add(splines)
        make_face()
    sks.color = (0.5, 0.5, 0.5)
    with BuildSketch() as sk:
        add(spline)
        make_face()
    from build123d import export_stl

    show(
        tl,
        sckt,
        sk,
        sks,
        spline,
        splines,
        reset_camera=Camera.KEEP,
    )
    # export_stl(tl, "tail.stl")
    # export_stl(sckt, "socket.stl")
