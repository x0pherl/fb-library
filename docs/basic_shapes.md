# Basic Shapes

Utility functions for creating and manipulating basic 3D shapes and geometric calculations. These functions extend build123d's capabilities with shapes and operations commonly used in 3D design.

## Geometric Calculation

### apothem_to_radius

```python
def apothem_to_radius(apothem: float, side_count: int = 6) -> float
```

**Arguments**
- `apothem` (float): The apothem of the polygon
- `side_count` (float): The number of sides of the poygon.

**Returns:**
- `float`: The radius of the polygon

### circular_intersection

```python
circular_intersection(radius: float, coordinate: float) -> float
```

calculates the circumradius of a regular polygon given its apothem
    
Finds the intersection point along one axis given a coordinate on the other axis of a circle's perimeter.

**Arguments:**
- `radius` (float): The radius of the circle
- `coordinate` (float): A coordinate along one axis (must be positive and less than radius)

**Returns:**
- `float`: The intersection coordinate on the other axis

**Raises:**
- `ValueError`: If coordinate is greater than radius or negative

### distance_to_circle_edge

```python
distance_to_circle_edge(radius: float, point: tuple, angle: float) -> float
```

Calculates the distance from a given point to the edge of a circle in a specified direction.

**Arguments:**
- `radius` (float): The radius of the circle
- `point` (tuple): The starting point (x, y)
- `angle` (float): The direction angle in degrees

**Returns:**
- `float`: Distance to the circle edge

**Raises:**
- `ValueError`: If the discriminant is negative (no intersection)

### radius_to_appothem

```python
def radius_to_appothem(radius: float, side_count: int = 6) -> float
```

**Arguments:**
- `radius` (float): the radius of the polygon
- `side_count` (float): the number of sides of the polygon

**Returns:**
- `float`: The apothem of the polygon

## Part Generaction

### diamond_cylinder

```python
diamond_cylinder(
    radius: float,
    height: float,
    rotation: tuple = (0, 0, 0),
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER),
    stretch: tuple = (1, 1, 1)
) -> Part
```

Creates an extruded diamond (4-sided polygon) that behaves like a cylinder. This is a convenience wrapper for `polygonal_cylinder` with 4 sides.

**Arguments:**
- `radius` (float): The radius of the circumscribed circle
- `height` (float): The height of the extrusion
- `rotation` (tuple, default=(0, 0, 0)): Rotation angles (X, Y, Z) in degrees
- `align` (tuple, default=(Align.CENTER, Align.CENTER, Align.CENTER)): Alignment
- `stretch` (tuple, default=(1, 1, 1)): Scaling factors (X, Y, Z)

**Returns:**
- `Part`: The diamond cylinder

### diamond_torus

```python
diamond_torus(
    major_radius: float, 
    minor_radius: float, 
    stretch: tuple = (1, 1)
) -> Part
```

Creates a torus by sweeping a diamond (square rotated 45°) along a circular path.

**Arguments:**
- `major_radius` (float): The radius of the circular sweep path
- `minor_radius` (float): The radius of the diamond cross-section
- `stretch` (tuple, default=(1, 1)): Scaling factors for the diamond shape

**Returns:**
- `Part`: The diamond torus

### half_part

```python
half_part(
    base_part: Part,
    cut_alignment: tuple[Align, Align, Align] = (Align.MAX, Align.CENTER, Align.CENTER)
) -> Part
```

Cuts a part in half along the X axis, useful for creating cross-section views when debugging designs.

**Arguments:**
- `base_part` (Part): The part to cut in half
- `cut_alignment` (tuple, default=(Align.MAX, Align.CENTER, Align.CENTER)): Alignment for the cutting box

**Returns:**
- `Part`: The halved part

### heatsink_insert_cut

```python
heatsink_insert_cut(
    head_radius: float = 3,
    head_depth: float = 5,
    shaft_radius: float = 2.1,
    shaft_length: float = 20
) -> Part
```

Creates a cutout template for a heatsink and bolt assembly.

**Arguments:**
- `head_radius` (float, default=3): Radius of the heatsink head
- `head_depth` (float, default=5): Depth of the heatsink head cutout
- `shaft_radius` (float, default=2.1): Radius of the bolt shaft
- `shaft_length` (float, default=20): Length of the bolt shaft

**Returns:**
- `Part`: The heatsink cutout geometry

### nut_cut

```python
nut_cut(
    head_radius: float = 3,
    head_depth: float = 5,
    shaft_radius: float = 2.1,
    shaft_length: float = 20
) -> Part
```

Creates a cutout template for a hexagonal nut and bolt assembly.

**Arguments:**
- `head_radius` (float, default=3): Radius of the hexagonal nut
- `head_depth` (float, default=5): Depth of the nut cutout
- `shaft_radius` (float, default=2.1): Radius of the bolt shaft
- `shaft_length` (float, default=20): Length of the bolt shaft

**Returns:**
- `Part`: The nut cutout geometry

### polygonal_cylinder

```python
polygonal_cylinder(
    radius: float,
    height: float,
    sides: int = 6,
    rotation: tuple = (0, 0, 0),
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER),
    stretch: tuple = (1, 1, 1)
) -> Part
```

Creates an extruded regular polygon that behaves like a cylinder.

**Arguments:**
- `radius` (float): The radius of the circumscribed circle
- `height` (float): The height of the extrusion
- `sides` (int, default=6): Number of sides of the polygon
- `rotation` (tuple, default=(0, 0, 0)): Rotation angles (X, Y, Z) in degrees
- `align` (tuple, default=(Align.CENTER, Align.CENTER, Align.CENTER)): Alignment
- `stretch` (tuple, default=(1, 1, 1)): Scaling factors (X, Y, Z)

**Returns:**
- `Part`: The polygonal cylinder

### rounded_cylinder

```python
rounded_cylinder(
    radius: float, 
    height: float, 
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER)
) -> Part
```

Creates a cylinder with rounded (filleted) top and bottom edges.

**Arguments:**
- `radius` (float): The radius of the cylinder
- `height` (float): The height of the cylinder (must be > radius * 2)
- `align` (tuple, default=(Align.CENTER, Align.CENTER, Align.CENTER)): Alignment of the cylinder

**Returns:**
- `Part`: The rounded cylinder

**Raises:**
- `ValueError`: If height is not greater than radius * 2

### screw_cut

```python
screw_cut(
    head_radius: float = 4.5,
    head_sink: float = 1.4,
    shaft_radius: float = 2.25,
    shaft_length: float = 20,
    bottom_clearance: float = 20
) -> Part
```

Creates a cutout template for a countersunk screw with tapered head transition.

**Arguments:**
- `head_radius` (float, default=4.5): Radius of the screw head (must be > shaft_radius)
- `head_sink` (float, default=1.4): Depth of the countersunk head
- `shaft_radius` (float, default=2.25): Radius of the screw shaft
- `shaft_length` (float, default=20): Length of the screw shaft
- `bottom_clearance` (float, default=20): Additional clearance below the head

**Returns:**
- `Part`: The screw cutout geometry

**Raises:**
- `ValueError`: If head_radius is not larger than shaft_radius

### teardrop_cylinder

```python
teardrop_cylinder(
    radius: float,
    peak_distance: float,
    height: float,
    rotation: RotationLike = (0, 0, 0),
    align: Align | tuple[Align, Align, Align] = (Align.CENTER, Align.CENTER, Align.CENTER),
    mode: Mode = Mode.ADD
)
```

Creates a 3D teardrop-shaped cylinder by extruding a teardrop sketch. Particularly useful for creating holes that print well on FDM printers without supports.

**Arguments:**
- `radius` (float): The radius of the circular portion
- `peak_distance` (float): Distance from circle center to the teardrop peak
- `height` (float): Height of the extrusion
- `rotation` (tuple, default=(0, 0, 0)): Rotation angles (X, Y, Z)
- `align` (tuple, default=(Align.CENTER, Align.CENTER, Align.CENTER)): Alignment
- `mode` (Mode, default=Mode.ADD): Build mode

**Returns:**
- `Part`: The teardrop cylinder

### teardrop_sketch

```python
teardrop_sketch(
    radius: float,
    peak_distance: float,
    align: Align | tuple[Align, Align] = (Align.CENTER, Align.CENTER)
) -> Sketch
```

Creates a 2D teardrop-shaped sketch, useful for 3D printing holes that minimize overhangs.

**Arguments:**
- `radius` (float): The radius of the circular portion
- `peak_distance` (float): Distance from circle center to the teardrop peak
- `align` (tuple, default=(Align.CENTER, Align.CENTER)): Alignment of the teardrop

**Returns:**
- `Sketch`: The teardrop sketch

## Examples

```python
from fb_library.basic_shapes import (
    rounded_cylinder, 
    diamond_torus, 
    teardrop_cylinder,
    screw_cut,
    half_part
)
from build123d import BuildPart, Mode

# Create a rounded cylinder
rounded_cyl = rounded_cylinder(radius=10, height=30)

# Create a diamond torus
torus = diamond_torus(major_radius=20, minor_radius=3)

# Create a teardrop hole for 3D printing
with BuildPart() as part:
    rounded_cylinder(radius=15, height=10)
    teardrop_cylinder(
        radius=5, 
        peak_distance=6, 
        height=15, 
        mode=Mode.SUBTRACT
    )

# Create a screw cutout
screw_hole = screw_cut(
    head_radius=5,
    head_sink=2,
    shaft_radius=2.5,
    shaft_length=25
)

# Create a cross-section view
cross_section = half_part(part.part)
```

## Notes

- Many functions include 3D printing considerations (like teardrop shapes for overhangs)
- Cutout functions (heatsink_cut, nut_cut, screw_cut) are designed to be used with `Mode.SUBTRACT`
- The teardrop functions help create printable holes without supports on FDM printers
- Polygonal cylinders can be useful for creating hex bolts, nuts, or decorative elements