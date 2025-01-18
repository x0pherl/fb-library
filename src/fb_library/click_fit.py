"""
click_fit.py allows for the creation of a preciscely fitting
snap fit connector that is easier to assemble and slower to
wear out than a simple half sphere.
"""

from build123d import (
    Axis,
    BuildPart,
    Part,
    Plane,
    BuildSketch,
    Circle,
    chamfer,
    extrude,
    loft,
)

from ocp_vscode import show, Camera


def divot(
    radius: float = 0.5, positive: bool = True, extend_base=False
) -> Part:
    """
    Create a divot that can be used to create a snap fit connector.
    ----------
    Arguments:
        - radius: float
            The radius of the divot.
        - positive: bool
            when True, reduces the size and shaping of the divot
            for the extruded part. when False, deepens and widens the socket.
        - extend_base: bool
            when True, extends the base of the divot to allow for a clean
            connection when attaching without precise placement.
    """
    tolerance = 0 if not positive else radius * 0.05
    ratio = 0.5 if positive else 0.55
    with BuildPart() as divot_part:
        with BuildSketch():
            Circle(radius - tolerance)
        with BuildSketch(Plane.XY.offset(radius * ratio)) as sketch:
            Circle(radius * ratio)
        loft()
        chamfer(
            divot_part.part.faces().sort_by(Axis.Z)[-1].edges(), radius * 0.1
        )
        if extend_base:
            extrude(divot_part.part.faces().sort_by(Axis.Z)[0], radius)
    return divot_part.part


if __name__ == "__main__":
    show(
        divot(10, extend_base=True),
        divot(10, positive=False),
        reset_camera=Camera.KEEP,
    )
