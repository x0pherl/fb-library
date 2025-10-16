from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Face,
    Iterable,
    Location,
    Part,
    add,
    extrude,
    fillet,
)
from math import atan, degrees
from ocp_vscode import show, Camera


def anti_chamfer(
    part: Part,
    faces: Face | Iterable[Face],
    length: float,
    length2: float | None = None,
) -> Part:
    """create an anti-chamfer (extending outwards like a foot or flat crown molding) on the specified faces of a part
    ----------
    Arguments:
        - part: Part
            The part to apply the anti-chamfer to
        - faces: Face | Iterable[Face]
            The face or faces to apply the anti-chamfer to
        - length: float
            The depth of the anti-chamfer (how far to offset inward)
        - length2: float | None
            The width of the taper at the bottom. If None, defaults to length
    Returns:
        - Part: A new part with the anti-chamfer applied"""
    if length2 is None:
        length2 = length
    if length == 0 or length2 == 0:
        return part
    if isinstance(faces, Face):
        faces = [faces]

    with BuildPart() as antichamfer:
        add(part)
        for f in faces:
            extrude(
                f.offset(-length),
                amount=length,
                taper=-degrees(atan(length2 / length)),
            )
    return antichamfer.part


if __name__ == "__main__":
    with BuildPart(Location((33, 11, 0))) as bkt:
        Box(
            60,
            10,
            20,
            rotation=(0, 0, 45),
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        fillet(bkt.edges().filter_by(Axis.Z), 3)
    bkt = anti_chamfer(bkt, bkt.faces().filter_by(Axis.Z), 2, 1)
    show(bkt, reset_camera=Camera.KEEP)
