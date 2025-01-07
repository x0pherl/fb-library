from build123d import (
    Axis,
    BuildPart,
    Part,
    Plane,
    BuildSketch,
    Circle,
    chamfer,
    fillet,
    loft,
)

from ocp_vscode import show, Camera


def divot(radius, positive=True) -> Part:
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
    return divot_part.part


if __name__ == "__main__":
    show(divot(10), divot(10, positive=False), reset_camera=Camera.KEEP)
