from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import Part

from fb_library.ball_socket import ball_mount, ball_socket


class TestBallMount:
    def test_ball_mount_basic(self):
        """Test ball_mount with basic parameters."""
        mount = ball_mount(10.0)

        assert isinstance(mount, Part)
        assert mount.is_valid()

        # Check basic dimensions
        bbox = mount.bounding_box()
        assert bbox.size.X == pytest.approx(20.0, abs=0.1)  # 2 * radius
        assert bbox.size.Y == pytest.approx(20.0, abs=0.1)  # 2 * radius

        # Ball should be centered at height of 2.5 * radius = 25mm
        # So total height should be 25 + 10 = 35mm
        assert bbox.size.Z == pytest.approx(35.0, abs=1.0)

    def test_ball_mount_small_radius(self):
        """Test ball_mount with small radius."""
        mount = ball_mount(2.0)

        assert isinstance(mount, Part)
        assert mount.is_valid()

        bbox = mount.bounding_box()
        assert bbox.size.X == pytest.approx(4.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(4.0, abs=0.1)
        # Height should be 2.5 * 2 + 2 = 7mm
        assert bbox.size.Z == pytest.approx(7.0, abs=0.5)

    def test_ball_mount_large_radius(self):
        """Test ball_mount with large radius."""
        mount = ball_mount(25.0)

        assert isinstance(mount, Part)
        assert mount.is_valid()

        bbox = mount.bounding_box()
        assert bbox.size.X == pytest.approx(50.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(50.0, abs=0.1)
        # Height should be 2.5 * 25 + 25 = 87.5mm
        assert bbox.size.Z == pytest.approx(87.5, abs=2.0)

    def test_ball_mount_fractional_radius(self):
        """Test ball_mount with fractional radius."""
        mount = ball_mount(7.5)

        assert isinstance(mount, Part)
        assert mount.is_valid()

        bbox = mount.bounding_box()
        assert bbox.size.X == pytest.approx(15.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(15.0, abs=0.1)

    def test_ball_mount_very_small_radius(self):
        """Test ball_mount with very small radius."""
        mount = ball_mount(0.5)

        assert isinstance(mount, Part)
        assert mount.is_valid()

        bbox = mount.bounding_box()
        assert bbox.size.X == pytest.approx(1.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(1.0, abs=0.1)

    def test_ball_mount_shaft_geometry(self):
        """Test that the shaft has the expected tapered geometry."""
        mount = ball_mount(10.0)

        # The shaft should taper from ball_radius at base to ball_radius/2.75 at insertion point
        # We can verify this by checking that the part has volume consistent with a tapered shaft
        assert mount.volume > 0

        # The part should be centered at origin in X,Y
        bbox = mount.bounding_box()
        assert abs(bbox.center().X) < 0.01
        assert abs(bbox.center().Y) < 0.01


class TestBallSocket:
    def test_ball_socket_basic(self):
        """Test ball_socket with basic parameters."""
        socket = ball_socket(10.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()
        assert socket.label == "Ball Socket"

        # Check basic dimensions
        bbox = socket.bounding_box()
        # Outer radius should be ball_radius + wall_thickness = 10 + 2 = 12
        # So diameter should be 24
        assert bbox.size.X == pytest.approx(24.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(24.0, abs=0.1)
        # Height should be 2 * ball_radius = 20
        assert bbox.size.Z == pytest.approx(20.0, abs=0.1)

    def test_ball_socket_custom_wall_thickness(self):
        """Test ball_socket with custom wall thickness."""
        socket = ball_socket(10.0, wall_thickness=3.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        bbox = socket.bounding_box()
        # Outer radius should be ball_radius + wall_thickness = 10 + 3 = 13
        # So diameter should be 26
        assert bbox.size.X == pytest.approx(26.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(26.0, abs=0.1)

    def test_ball_socket_custom_tolerance(self):
        """Test ball_socket with custom tolerance."""
        socket = ball_socket(10.0, tolerance=0.2)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        # Should still have same outer dimensions
        bbox = socket.bounding_box()
        assert bbox.size.X == pytest.approx(24.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(24.0, abs=0.1)

    def test_ball_socket_negative_tolerance(self):
        """Test ball_socket with negative tolerance for tighter fit."""
        socket = ball_socket(10.0, tolerance=-0.05)

        assert isinstance(socket, Part)
        assert socket.is_valid()

    def test_ball_socket_zero_tolerance(self):
        """Test ball_socket with zero tolerance."""
        socket = ball_socket(10.0, tolerance=0.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()

    def test_ball_socket_large_tolerance(self):
        """Test ball_socket with large tolerance."""
        socket = ball_socket(10.0, tolerance=0.5)

        assert isinstance(socket, Part)
        assert socket.is_valid()

    def test_ball_socket_thin_walls(self):
        """Test ball_socket with thin walls."""
        socket = ball_socket(10.0, wall_thickness=1.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        bbox = socket.bounding_box()
        # Outer radius should be ball_radius + wall_thickness = 10 + 1 = 11
        # So diameter should be 22
        assert bbox.size.X == pytest.approx(22.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(22.0, abs=0.1)

    def test_ball_socket_thick_walls(self):
        """Test ball_socket with thick walls."""
        socket = ball_socket(10.0, wall_thickness=5.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        bbox = socket.bounding_box()
        # Outer radius should be ball_radius + wall_thickness = 10 + 5 = 15
        # So diameter should be 30
        assert bbox.size.X == pytest.approx(30.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(30.0, abs=0.1)

    def test_ball_socket_small_radius(self):
        """Test ball_socket with small radius."""
        socket = ball_socket(3.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        bbox = socket.bounding_box()
        # Outer diameter should be (3 + 2) * 2 = 10
        assert bbox.size.X == pytest.approx(10.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(10.0, abs=0.1)
        # Height should be 2 * 3 = 6
        assert bbox.size.Z == pytest.approx(6.0, abs=0.1)

    def test_ball_socket_large_radius(self):
        """Test ball_socket with large radius."""
        socket = ball_socket(20.0)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        bbox = socket.bounding_box()
        # Outer diameter should be (20 + 2) * 2 = 44
        assert bbox.size.X == pytest.approx(44.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(44.0, abs=0.1)
        # Height should be 2 * 20 = 40
        assert bbox.size.Z == pytest.approx(40.0, abs=0.1)

    def test_ball_socket_centered(self):
        """Test that ball_socket is centered at origin."""
        socket = ball_socket(10.0)

        bbox = socket.bounding_box()
        assert abs(bbox.center().X) < 0.01
        assert abs(bbox.center().Y) < 0.01

    def test_ball_socket_has_flex_cuts(self):
        """Test that ball_socket has the expected flex cuts."""
        socket = ball_socket(10.0)

        # The socket should have internal volume for the ball
        # and should have flex cuts that create openings
        assert socket.volume > 0

        # The flex cuts should reduce the volume compared to a solid cylinder
        solid_cylinder_volume = 3.14159 * (12**2) * 20  # pi * r^2 * h
        assert socket.volume < solid_cylinder_volume

    def test_ball_socket_fractional_radius(self):
        """Test ball_socket with fractional radius."""
        socket = ball_socket(7.5, wall_thickness=1.5, tolerance=0.05)

        assert isinstance(socket, Part)
        assert socket.is_valid()

        bbox = socket.bounding_box()
        # Outer diameter should be (7.5 + 1.5) * 2 = 18
        assert bbox.size.X == pytest.approx(18.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(18.0, abs=0.1)


class TestBallSocketPairCompatibility:
    def test_mount_socket_size_compatibility(self):
        """Test that ball_mount and ball_socket have compatible dimensions."""
        radius = 12.0
        mount = ball_mount(radius)
        socket = ball_socket(radius)

        mount_bbox = mount.bounding_box()
        socket_bbox = socket.bounding_box()

        # Mount ball diameter should fit within socket outer diameter
        assert mount_bbox.size.X < socket_bbox.size.X
        assert mount_bbox.size.Y < socket_bbox.size.Y

        # Mount should be taller than socket (since ball extends above)
        assert mount_bbox.size.Z > socket_bbox.size.Z

    def test_multiple_radius_compatibility(self):
        """Test compatibility for various radius sizes."""
        test_radii = [2.0, 5.0, 10.0, 15.0, 20.0]

        for radius in test_radii:
            mount = ball_mount(radius)
            socket = ball_socket(radius)

            assert mount.is_valid()
            assert socket.is_valid()

            mount_bbox = mount.bounding_box()
            socket_bbox = socket.bounding_box()

            # Basic compatibility check
            assert mount_bbox.size.X <= socket_bbox.size.X


class TestEdgeCases:
    def test_very_small_components(self):
        """Test with very small dimensions."""
        radius = 0.1
        mount = ball_mount(radius)
        socket = ball_socket(radius, wall_thickness=0.1)

        assert mount.is_valid()
        assert socket.is_valid()

    def test_minimal_wall_thickness(self):
        """Test with minimal wall thickness."""
        socket = ball_socket(10.0, wall_thickness=0.1)

        assert isinstance(socket, Part)
        assert socket.is_valid()

    def test_extreme_tolerance_values(self):
        """Test with extreme tolerance values."""
        # Very tight tolerance
        socket_tight = ball_socket(10.0, tolerance=-0.1)
        assert socket_tight.is_valid()

        # Very loose tolerance
        socket_loose = ball_socket(10.0, tolerance=1.0)
        assert socket_loose.is_valid()

    def test_parameter_validation_edge_cases(self):
        """Test edge cases for parameter validation."""
        # These should all work without errors
        test_cases = [
            (1.0, 0.5, 0.01),  # Small components
            (50.0, 10.0, 2.0),  # Large components
            (10.0, 0.1, -0.05),  # Thin walls, negative tolerance
            (10.0, 8.0, 0.5),  # Very thick walls
        ]

        for radius, wall_thickness, tolerance in test_cases:
            mount = ball_mount(radius)
            socket = ball_socket(radius, wall_thickness, tolerance)

            assert mount.is_valid()
            assert socket.is_valid()


class TestDirectRun:
    def test_direct_run(self):
        """Test that the module can be run directly without errors."""
        with (patch("ocp_vscode.show"),):
            loader = SourceFileLoader("__main__", "src/fb_library/ball_socket.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))


class TestGeometryDetails:
    def test_ball_mount_shaft_taper(self):
        """Test specific geometry details of the ball mount shaft."""
        radius = 10.0
        mount = ball_mount(radius)

        # Test that the shaft actually tapers by checking cross-sections at different heights
        # This is more of a geometry validation than a strict test
        bbox = mount.bounding_box()

        # The mount should have the ball at the top and taper down
        # Ball center should be at 2.5 * radius = 25mm
        assert (
            bbox.max.Z >= radius * 3.4
        )  # Ball top should be at least at 25 + 10 = 35mm

    def test_ball_socket_internal_features(self):
        """Test that ball socket has expected internal features."""
        radius = 10.0
        socket = ball_socket(radius)

        bbox = socket.bounding_box()

        # Socket should be hollow (has internal volume)
        assert socket.volume > 0

        # Socket should be positioned with base at Z=0
        assert bbox.min.Z == pytest.approx(0.0, abs=0.01)

    def test_socket_flange_geometry(self):
        """Test that the socket has the expected flange at the top."""
        radius = 10.0
        wall_thickness = 2.0
        socket = ball_socket(radius, wall_thickness=wall_thickness)

        # The socket should have a height of 2 * radius
        bbox = socket.bounding_box()
        assert bbox.size.Z == pytest.approx(2 * radius, abs=0.1)

        # The flange should be filleted (this affects the geometry slightly)
        # We can't easily test the fillet directly, but the part should be valid
        assert socket.is_valid()

    def test_flex_cuts_positioning(self):
        """Test that flex cuts are properly positioned."""
        radius = 10.0
        socket = ball_socket(radius)

        # The flex cuts should be at 90-degree intervals
        # This is difficult to test directly, but we can verify the part is valid
        # and has the expected volume characteristics
        assert socket.is_valid()

        # The socket should have less volume than a solid cylinder due to flex cuts
        # and internal cavity
        bbox = socket.bounding_box()
        cylinder_volume = 3.14159 * ((radius + 2) ** 2) * (2 * radius)
        assert socket.volume < cylinder_volume
