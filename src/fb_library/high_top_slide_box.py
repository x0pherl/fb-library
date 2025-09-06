from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    Location,
    Part,
    PolarLocations,
    Polyline,
    Mode,
    add,
    extrude,
    fillet,
    make_face,
    pack,
)
from dataclasses import field
from fb_library import diamond_cylinder, divot, Point, opposite_length, midpoint
from ocp_vscode import show, Camera


def _slide_top_rail_cut(
    part_width: float,
    part_depth: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    effective_tolerance: float = 0.05,
):
    rail_front_right = Point(
        (part_width - wall_thickness * 2 / 3 + effective_tolerance) / 2,
        (part_depth - wall_thickness) / 2,
    )
    rail_back_right = Point(
        (
            rail_front_right.x
            - (
                0
                if (rail_angle == 0)
                else opposite_length(
                    rail_angle, adjacent_length=part_depth - wall_thickness
                )
            )
        ),
        -(part_depth - wall_thickness) / 2,
    )

    with BuildPart(
        Location((0, wall_thickness / 2, 0)),
        mode=Mode.SUBTRACT,
    ) as rail_cut:
        with BuildSketch(Location((0, wall_thickness / 2))):
            with BuildLine():

                Polyline(
                    rail_front_right,
                    rail_back_right,
                    Point(-(rail_back_right.x), rail_back_right.y),
                    Point(-(rail_front_right.x), rail_front_right.y),
                    rail_front_right,
                )
            make_face()
        extrude(amount=rail_height)
        guide_radius = wall_thickness / 3 - effective_tolerance / 2
        with BuildPart(
            (
                Location(
                    (
                        rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height,
                    )
                )
            ),
            mode=Mode.ADD,
        ):
            add(
                diamond_cylinder(
                    radius=wall_thickness - effective_tolerance / 2,
                    height=part_depth - wall_thickness,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                    rotation=(90, 0, -rail_angle),
                )
            )
        with BuildPart(
            (
                Location(
                    (
                        -rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height,
                    )
                )
            ),
            mode=Mode.ADD,
        ):
            add(
                diamond_cylinder(
                    radius=wall_thickness - effective_tolerance / 2,
                    height=part_depth - wall_thickness,
                    align=(Align.MIN, Align.CENTER, Align.MIN),
                    rotation=(90, 0, rail_angle),
                )
            )

        with BuildPart(
            (
                Location(
                    (
                        rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height / 2 - effective_tolerance,
                    )
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            add(
                diamond_cylinder(
                    radius=guide_radius,
                    height=part_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    rotation=(90, 0, -rail_angle),
                )
            )
        with BuildPart(
            (
                Location(
                    (
                        -rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height / 2 - effective_tolerance,
                    )
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            add(
                diamond_cylinder(
                    radius=guide_radius,
                    height=part_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    rotation=(90, 0, rail_angle),
                )
            )
    return rail_cut.part


def _high_top_slide_box_top(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
    cut_template: bool = False,
) -> Part:
    effective_tolerance = abs(tolerance) / (-2 if cut_template else 2)
    with BuildPart() as top:
        part_width = base_part.bounding_box().size.X
        part_depth = base_part.bounding_box().size.Y
        part_height = base_part.bounding_box().size.Z
        part_max_dimension = max(part_width, part_depth, part_height)
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    -part_height
                    + top_height
                    + rail_height
                    + wall_thickness
                    - effective_tolerance * 4,
                )
            )
        ):
            add(base_part)
            with BuildPart(mode=Mode.INTERSECT):
                Box(
                    part_max_dimension,
                    part_max_dimension,
                    part_max_dimension,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        with BuildPart(
            Location((0, wall_thickness / 2, rail_height)),
            mode=Mode.SUBTRACT,
        ) as top_cut:
            Box(
                part_width - wall_thickness * 2 + effective_tolerance * 2,
                part_depth - wall_thickness,
                top_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        with BuildPart(
            Location((0, 0, 0)),
            mode=Mode.SUBTRACT,
        ) as rail_cut:
            add(
                _slide_top_rail_cut(
                    part_width=part_width,
                    part_depth=part_depth,
                    rail_height=rail_height,
                    wall_thickness=wall_thickness,
                    rail_angle=rail_angle,
                    effective_tolerance=effective_tolerance,
                )
            )
        if divot_radius > 0:
            with BuildPart(
                Location(
                    (0, (part_depth - wall_thickness) / 2, top_height + rail_height),
                    (180, 0, 0),
                ),
            ):
                with PolarLocations(radius=part_width / 3 - wall_thickness, count=2):
                    add(
                        divot(
                            radius=divot_radius,
                            positive=not cut_template,
                            extend_base=True,
                        )
                    )
            with BuildPart(
                Location(
                    (0, (-part_depth + wall_thickness) / 2, 0),
                    (180, 0, 0),
                ),
            ):
                with PolarLocations(radius=part_width / 3 - wall_thickness, count=2):
                    add(
                        divot(
                            radius=divot_radius,
                            positive=not cut_template,
                            extend_base=True,
                        )
                    )
    top.part.label = "lid"
    return top.part


def high_top_slide_box_lid(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Part:
    lid = _high_top_slide_box_top(
        base_part,
        top_height,
        rail_height,
        wall_thickness,
        rail_angle,
        divot_radius,
        thumb_radius,
        tolerance,
        cut_template=False,
    )
    lid.label = "box top"
    return lid


def high_top_slide_box_base(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Part:
    part_width = base_part.bounding_box().size.X
    part_depth = base_part.bounding_box().size.Y
    part_height = base_part.bounding_box().size.Z

    with BuildPart() as boxbottom:
        add(base_part)
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    wall_thickness,
                ),
                (0, 0, 0),
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                part_width - wall_thickness * 2,
                part_depth - wall_thickness * 2,
                part_height - wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    part_height
                    - top_height
                    - rail_height
                    - wall_thickness
                    + tolerance * 2,
                ),
                (0, 0, 0),
            ),
            mode=Mode.SUBTRACT,
        ):
            add(
                _high_top_slide_box_top(
                    base_part,
                    top_height,
                    rail_height,
                    wall_thickness,
                    rail_angle,
                    divot_radius,
                    thumb_radius,
                    tolerance,
                    cut_template=True,
                )
            )

    boxbottom.part.label = "box bottom"
    return boxbottom.part


def high_top_slide_box(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Compound:

    return Compound(
        label="slide box",
        children=pack(
            [
                high_top_slide_box_lid(
                    base_part=base_part,
                    top_height=top_height,
                    rail_height=rail_height,
                    wall_thickness=wall_thickness,
                    rail_angle=rail_angle,
                    divot_radius=divot_radius,
                    thumb_radius=thumb_radius,
                    tolerance=tolerance,
                ).rotate(Axis.X, 180),
                high_top_slide_box_base(
                    base_part=base_part,
                    top_height=top_height,
                    rail_height=rail_height,
                    wall_thickness=wall_thickness,
                    rail_angle=rail_angle,
                    divot_radius=divot_radius,
                    thumb_radius=thumb_radius,
                    tolerance=tolerance,
                ),
            ],
            padding=5,
            align_z=True,
        ),
    )


if __name__ == "__main__":
    with BuildPart() as base_box:
        Box(44, 44, 44, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)

    sb = high_top_slide_box(
        base_part=base_box.part,
        top_height=5,
        rail_height=10,
        wall_thickness=4,
        rail_angle=0.5,
        divot_radius=0.5,
        thumb_radius=0,
        tolerance=0.1,
    )
    top = (
        sb.children[0]
        .rotate(Axis.Z, 180)
        .rotate(Axis.Y, 180)
        .move(Location((44 + 5, 44, sb.children[1].bounding_box().size.Z + 4 - 0.1)))
    )
    bottom = sb.children[1]
    # show(sb, reset_camera=Camera.KEEP)
    show(top, bottom, reset_camera=Camera.KEEP)
