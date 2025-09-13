from build123d import (
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Sphere,
    Align,
    loft,
    fillet,
    Axis,
)
from ocp_vscode import show, Camera
from math import sqrt


def ball_mount(ball_radius: float) -> Part:
    """
    Creates a ball mount component for a ball-and-socket joint system.

    The ball mount consists of a spherical ball attached to a tapered shaft. The shaft
    is designed to be inserted into another part or component, while the ball mates
    with a corresponding ball socket to create a flexible joint that allows rotation
    in multiple axes. The shaft has a sophisticated tapered design that transitions from
    the full ball radius at the base to approximately 36% of the ball radius at the
    insertion point, providing strength while allowing for easy integration into
    mounting systems.

    args:
        - ball_radius: the radius of the spherical ball in millimeters. This determines
          the overall size of the joint system and must match the ball_radius used
          for the corresponding ball_socket.
    """
    with BuildPart() as ballmount:
        with BuildPart(Location((0, 0, ball_radius * 2.5))):
            Sphere(radius=ball_radius, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        with BuildPart() as shaft:
            with BuildSketch():
                Circle(
                    radius=ball_radius,
                    align=(Align.CENTER, Align.CENTER),
                )
            with BuildSketch(Plane.XY.offset(ball_radius * 0.5)):
                Circle(
                    radius=ball_radius / 2.75,
                    align=(Align.CENTER, Align.CENTER),
                )
            height_ratio = 0.25
            with BuildSketch(Plane.XY.offset(ball_radius * (2 + height_ratio))):
                Circle(
                    radius=ball_radius * (sqrt(1 - height_ratio**2)),
                    align=(Align.CENTER, Align.CENTER),
                )
            loft()
    return ballmount.part


def ball_socket(
    ball_radius: float, wall_thickness: float = 2, tolerance: float = 0.1
) -> Part:
    """
    Creates a ball socket component for a ball-and-socket joint system.

    The ball socket is designed to receive and hold a ball mount, creating a flexible
    joint that allows rotation in multiple axes. The socket features a hemispherical
    cavity to house the ball, a cylindrical outer shell for strength, and flexible
    cuts that allow the socket to grip the ball while still permitting smooth rotation.
    The socket includes a flange at the top with a smooth filleted edge for comfortable
    operation and four radial flex cuts that allow the socket walls to compress slightly
    for ball retention while maintaining smooth rotation.

    args:
        - ball_radius: the radius of the spherical ball that will be inserted into
          this socket, in millimeters. Must match the ball_radius of the corresponding
          ball_mount for proper fit.
        - wall_thickness: the thickness of the socket walls in millimeters. Affects
          both strength and flexibility. Thicker walls provide more strength but may
          reduce flexibility.
        - tolerance: additional clearance around the ball in millimeters. Positive
          values create looser fits, negative values create tighter fits.
    """
    with BuildPart() as socket:
        Cylinder(
            radius=ball_radius + wall_thickness,
            height=ball_radius * 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        with BuildPart(Location((0, 0, ball_radius * 2)), mode=Mode.SUBTRACT):
            Cylinder(
                radius=ball_radius + tolerance,
                height=wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
        with BuildPart(Plane.XY.offset(wall_thickness), mode=Mode.SUBTRACT) as bowl_cut:
            Sphere(
                radius=ball_radius + tolerance,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildPart(Location((0, 0, ball_radius * 2))) as flange:
            Cylinder(
                radius=ball_radius + tolerance,
                height=wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
            Cylinder(
                radius=ball_radius - wall_thickness * 0.66 + tolerance,
                height=wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )
            fillet(
                flange.faces().sort_by(Axis.Z)[-1].inner_wires().edge(),
                wall_thickness * 0.4,
            )
        with BuildPart(
            Plane.XY.offset(ball_radius * 1.5 - wall_thickness), mode=Mode.SUBTRACT
        ) as flexcuts:
            with PolarLocations(0, 4):
                Box(
                    ball_radius,
                    (ball_radius + wall_thickness) * 2,
                    ball_radius / 2 + wall_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Cylinder(
                    radius=ball_radius / 2,
                    height=(ball_radius + wall_thickness) * 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    rotation=(90, 0, 0),
                )

    socket.part.label = "Ball Socket"
    return socket.part


if __name__ == "__main__":
    show(
        ball_mount(15),
        ball_socket(15).rotate(Axis.X, 180).move(Location((0, 0, 52.5))),
        reset_camera=Camera.KEEP,
    )
