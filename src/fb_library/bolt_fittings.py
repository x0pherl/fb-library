from build123d import (
    Align,
    Axis,
    BuildPart,
    Location,
    Part,
    Box,
    add,
    extrude,
)
from fb_library.antichamfer import anti_chamfer
from fb_library.basic_shapes import teardrop_cylinder


def teardrop_bolt_cut_sinkhole(
    shaft_radius: float = 1.65,
    shaft_depth: float = 2,
    head_radius: float = 3.1,
    head_depth: float = 5,
    chamfer_radius: float = 1,
    extension_distance: float = 100,
    teardrop_ratio: float = 1.1,
) -> Part:
    """create a teardrop-shaped bolt hole with countersink for vertical printing
    ----------
    Arguments:
        - shaft_radius: float
            The radius of the bolt shaft
        - shaft_depth: float
            The depth of the shaft portion
        - head_radius: float
            The radius of the bolt head countersink
        - head_depth: float
            The depth of the head countersink
        - chamfer_radius: float
            The radius of the anti-chamfer at the top
        - extension_distance: float
            How far to extend the shaft beyond the head (for through-holes)
        - teardrop_ratio: float
            The ratio to stretch the teardrop shape (1.0 = circle, 1.1 = recommended teardrop)
    Returns:
        - Part: A bolt hole part with teardrop profile for better vertical printing"""
    with BuildPart(Location((0, 0, shaft_depth))) as sinkhole:
        add(
            teardrop_cylinder(
                shaft_radius,
                shaft_radius * teardrop_ratio,
                shaft_depth,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            ),
        )
        add(
            teardrop_cylinder(
                head_radius,
                head_radius * teardrop_ratio,
                head_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ),
        )
        if extension_distance > 0:
            # extrude(sinkhole.faces().sort_by(Axis.Z)[0], amount=extension_distance)
            extrude(
                sinkhole.faces().sort_by(Axis.Z)[-1],
                amount=extension_distance,
            )
    return anti_chamfer(
        sinkhole.part,
        [
            sinkhole.part.faces().sort_by(Axis.Z)[-1],
        ],
        chamfer_radius,
    )


def bolt_cut_sinkhole(
    shaft_radius: float = 1.65,
    shaft_depth: float = 2,
    head_radius: float = 3.1,
    head_depth: float = 5,
    chamfer_radius: float = 1,
    extension_distance: float = 100,
) -> Part:
    """create a cylindrical bolt hole with countersink
    ----------
    Arguments:
        - shaft_radius: float
            The radius of the bolt shaft
        - shaft_depth: float
            The depth of the shaft portion
        - head_radius: float
            The radius of the bolt head countersink
        - head_depth: float
            The depth of the head countersink
        - chamfer_radius: float
            The radius of the anti-chamfer at the top
        - extension_distance: float
            How far to extend the shaft beyond the head (for through-holes)
    Returns:
        - Part: A cylindrical bolt hole part with countersink"""
    return teardrop_bolt_cut_sinkhole(
        shaft_radius=shaft_radius,
        shaft_depth=shaft_depth,
        head_radius=head_radius,
        head_depth=head_depth,
        chamfer_radius=chamfer_radius,
        extension_distance=extension_distance,
        teardrop_ratio=1.0,
    )


def square_nut_sinkhole(
    bolt_radius: float = 1.65,
    bolt_depth: float = 2,
    nut_height: float = 2.1,
    nut_legnth: float = 5.6,
    nut_depth: float = 100,
    bolt_extension: float = 1,
) -> Part:
    """create a bolt hole with square nut trap
    ----------
    Arguments:
        - bolt_radius: float
            The radius of the bolt shaft
        - bolt_depth: float
            The depth of the bolt hole before the nut trap
        - nut_height: float
            The height (thickness) of the square nut
        - nut_legnth: float
            The side length of the square nut
        - nut_depth: float
            How far the nut trap extends
        - bolt_extension: float
            How far to extend the bolt hole beyond the nut trap
    Returns:
        - Part: A bolt hole with square nut trap cavity"""
    with BuildPart() as sinkhole:
        add(
            teardrop_cylinder(
                bolt_radius,
                bolt_radius * 1.1,
                bolt_depth,
                rotation=(-90, 0, 0),
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ),
        )
        with BuildPart(Location((0, bolt_depth, 0))) as nut:
            Box(
                nut_legnth,
                nut_height,
                nut_legnth,
                align=(Align.CENTER, Align.MIN, Align.CENTER),
            )
            extrude(nut.part.faces().sort_by(Axis.Z)[-1], amount=nut_depth)
        if bolt_extension > 0:
            with BuildPart(Location((0, bolt_depth + nut_height, 0))) as nut:
                add(
                    teardrop_cylinder(
                        bolt_radius,
                        bolt_radius * 1.1,
                        bolt_extension,
                        rotation=(-90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    ),
                )

    return sinkhole.part
