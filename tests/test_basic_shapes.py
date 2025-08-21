from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import Box, BuildPart, Part, Align
from fb_library.basic_shapes import (
    circular_intersection,
    diamond_torus,
    distance_to_circle_edge,
    heatsink_cut,
    half_part,
    rounded_cylinder,
    diamond_cylinder,
    polygonal_cylinder,
    # rail_block_template,
    nut_cut,
    screw_cut,
    teardrop_cylinder,
    teardrop_sketch,
    radius_to_apothem,
    apothem_to_radius,
)


class TestApothemConversions:
    def test_apothem_from_radius(self):
        assert radius_to_apothem(5) == pytest.approx(4.330127018922194)
        assert radius_to_apothem(5, 8) == pytest.approx(4.619397662556434)

    def test_radius_to_apothem(self):
        assert apothem_to_radius(5) == pytest.approx(5.773502691896257)
        assert apothem_to_radius(5, 8) == pytest.approx(5.41196100146197)


class TestTearDropSketch:
    def test_teardropsketch(self):
        sketch = teardrop_sketch(10, 12, align=(Align.MAX, Align.MIN))
        assert sketch.is_valid()
        assert sketch.bounding_box().size.X == pytest.approx(20)
        assert sketch.bounding_box().size.Y == pytest.approx(22)

    def test_teardropsketch_aligned(self):
        sketch = teardrop_sketch(10, 12, align=(Align.MIN, Align.MAX))
        assert sketch.is_valid()
        assert sketch.bounding_box().size.X == pytest.approx(20)
        assert sketch.bounding_box().size.Y == pytest.approx(22)


class TestTearDropCylinder:
    def test_teardrop_cylinder(self):
        cyl = teardrop_cylinder(
            10, 11, 10, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_align_zmax_teardrop_cylinder(self):
        cyl = teardrop_cylinder(
            10, 11, 10, align=(Align.CENTER, Align.CENTER, Align.MAX)
        )
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_align_zcenter_teardrop_cylinder(self):
        cyl = teardrop_cylinder(
            10, 11, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER)
        )
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_teardrop_cylinder(self):
        cyl = teardrop_cylinder(
            10, 11, 10, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)


class TestCircularIntersection:
    def test_circular_intersection(self) -> float:
        assert circular_intersection(10, 5) == 8.660254037844387

    def test_circular_intersection_discriminant_error(self):
        with pytest.raises(ValueError):
            circular_intersection(-25, -10) == 8.660254037844387


class TestTorus:
    def test_diamond_torus(self):
        torus = diamond_torus(major_radius=10, minor_radius=1)
        assert isinstance(torus, Part)
        assert torus.bounding_box().size.X == pytest.approx(22)
        assert torus.bounding_box().size.Y == pytest.approx(22)
        assert torus.bounding_box().size.Z == pytest.approx(2)


class TestDistanceToCircleEdge:
    def test_distance_to_circle_edge(self):
        assert distance_to_circle_edge(10, (0, 5), 45) == 5.818609561002116

    def test_distance_to_circle_edge_discriminant_error(self):
        with pytest.raises(ValueError):
            distance_to_circle_edge(10, (0, 25), 45) == 5.818609561002116


class TestRoundedCylinder:
    def test_short_cylinder_fail(self):
        with pytest.raises(ValueError):
            cyl = rounded_cylinder(2, 3)

    def test_rounded_cylinder(self):
        cyl = rounded_cylinder(5, 11)
        assert cyl.is_valid()
        assert isinstance(cyl, Part)
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(11)


class TestHalfPart:
    def test_half_part(self):
        with BuildPart() as whole_part:
            Box(10, 10, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        half = half_part(whole_part.part)
        assert half.is_valid()
        assert half.volume == pytest.approx(whole_part.part.volume / 2)


class TestPolygonalCylinder:

    def test_diamond_cylinder(self):
        cyl = diamond_cylinder(5, 10)
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_diamond_cylinder_zmax(self):
        cyl = diamond_cylinder(5, 10, align=(Align.CENTER, Align.CENTER, Align.MAX))
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_polygonal_cylinder(self):
        cyl = polygonal_cylinder(5, 10)
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_polygonal_cylinder(self):
        cyl = polygonal_cylinder(5, 10, align=(Align.CENTER, Align.CENTER, Align.MAX))
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(8.660254237844388)
        assert cyl.bounding_box().size.Z == pytest.approx(10)


class TestScrewCut:
    def test_screw_cut(self):
        screw = screw_cut(5, 1, 2, 10, 10)
        assert screw.is_valid()
        assert screw.bounding_box().size.X == pytest.approx(10)
        assert screw.bounding_box().size.Y == pytest.approx(10)
        assert screw.bounding_box().size.Z == pytest.approx(20)

    def test_nut_cut(self):
        nut = nut_cut(5, 1, 2, 10)
        assert nut.is_valid()

    def test_invalid_screw_cut(self):
        with pytest.raises(ValueError):
            screw_cut(head_radius=5, shaft_radius=6)

    def test_heatsink_cut(self):
        heatsink = heatsink_cut(10, 1, 5, 10)
        assert heatsink.is_valid()
        assert heatsink.bounding_box().size.X == pytest.approx(20)
        assert heatsink.bounding_box().size.Y == pytest.approx(20)
        assert heatsink.bounding_box().size.Z == pytest.approx(11)


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
        ):
            loader = SourceFileLoader("__main__", "src/fb_library/basic_shapes.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
