# Ball Socket

# Ball Socket Joint System Documentation

## Overview

The ball socket joint system is designed for creating flexible connections between 3D printed parts that require multi-axis rotation. This system consists of two complementary components: a ball mount and a ball socket. The ball mount features a spherical ball attached to a tapered shaft, while the ball socket provides a hemispherical cavity with flexible walls that grip the ball while allowing smooth rotation.

This joint system is particularly useful for creating articulated mechanisms, adjustable brackets, camera mounts, robotic joints, or any application where you need a connection that can rotate freely in multiple directions while maintaining a secure hold.

The `ball_mount` and `ball_socket` functions create precision-matched components with built-in tolerances and flex features optimized for 3D printing.

## Functions

### ball_mount

Creates a ball mount component for a ball-and-socket joint system.

## Arguments

- `ball_radius` (float): The radius of the spherical ball in millimeters. This determines the overall size of the joint system and must match the ball_radius used for the corresponding ball_socket.

## Returns

- `Part`: A ball mount part consisting of a sphere positioned above a tapered shaft. The ball is centered at a height of 2.5 times the ball radius above the base, and the shaft tapers from the full ball radius at the base to approximately 36% of the ball radius at the insertion point.

### ball_socket

Creates a ball socket component for a ball-and-socket joint system.

## Arguments

- `ball_radius` (float): The radius of the spherical ball that will be inserted into this socket, in millimeters. Must match the ball_radius of the corresponding ball_mount for proper fit.
- `wall_thickness` (float, default=2): The thickness of the socket walls in millimeters. Affects both strength and flexibility. Thicker walls provide more strength but may reduce flexibility. Recommended range: 1.5-3mm.
- `tolerance` (float, default=0.1): Additional clearance around the ball in millimeters. Positive values create looser fits, negative values create tighter fits. Typical range: 0.05-0.2mm.

## Returns

- `Part`: A ball socket part with label "Ball Socket". The socket has a cylindrical outer shell with height of 2 * ball_radius and radius of ball_radius + wall_thickness. Features include a hemispherical cavity, a flange at the top with filleted edges, and four radial flex cuts for ball retention.

## Design Features

### Tapered Shaft Design
The ball mount's shaft uses a sophisticated lofted design that provides optimal strength while maintaining a compact profile. The shaft transitions smoothly from the full ball radius at the base to approximately 36% of the ball radius at the narrowest point, then expands again to connect with the sphere.

### Flexible Socket Walls
The ball socket incorporates four radial flex cuts positioned at 90-degree intervals. These cuts allow the socket walls to compress slightly when the ball is inserted, providing secure retention while still permitting smooth rotation.

### Precision Tolerances
The system uses carefully calculated tolerances to ensure proper fit. The default tolerance of 0.1mm works well for most 3D printers, but can be adjusted based on printer precision and material characteristics.

### Filleted Flange
The socket features a flange at the top with smooth filleted edges for comfortable manual operation and professional appearance.

## Example

```python
from fb_library.ball_socket import ball_mount, ball_socket

# Create a basic ball joint system with 15mm radius
mount = ball_mount(15.0)
socket = ball_socket(15.0)

# Create a tighter-fitting joint with thicker walls
precision_mount = ball_mount(12.0)
precision_socket = ball_socket(
    ball_radius=12.0,
    wall_thickness=2.5,
    tolerance=0.05
)

# Create a looser joint for easy assembly
loose_mount = ball_mount(10.0)
loose_socket = ball_socket(
    ball_radius=10.0,
    wall_thickness=2.0,
    tolerance=0.15
)

# For heavy-duty applications
heavy_duty_mount = ball_mount(20.0)
heavy_duty_socket = ball_socket(
    ball_radius=20.0,
    wall_thickness=4.0,
    tolerance=0.1
)
```

## Print Settings and Assembly

### Recommended Print Orientation
- **Ball Mount**: Print with the shaft pointing up and the ball at the top. No supports needed.
- **Ball Socket**: Print with the opening facing up. The hemispherical cavity and flex cuts will print cleanly without supports.

### Layer Height
- 0.2mm layer height works well for most applications
- 0.15mm for higher precision joints
- 0.3mm acceptable for larger joints or draft prints

### Material Considerations
- **PLA**: Good for prototypes and light-duty applications
- **PETG**: Better flexibility for the socket's flex cuts
- **ABS**: Good strength and temperature resistance
- **TPU**: Can be used for the socket to create very flexible joints

### Assembly Tips
1. Test fit the components before final assembly
2. The ball should slide into the socket with slight resistance
3. Light sanding may be needed on the ball surface for optimal fit
4. A small amount of dry lubricant can improve long-term operation

## Design Guidelines

### Choosing Ball Radius
- **5-10mm**: Small mechanisms, lightweight applications
- **10-15mm**: General purpose joints, medium loads
- **15-25mm**: Heavy-duty applications, high torque loads
- **25mm+**: Industrial applications, very high loads

### Wall Thickness Selection
- **1.5-2mm**: Lightweight applications, maximum flexibility
- **2-3mm**: General purpose (recommended)
- **3-4mm**: Heavy-duty applications, maximum strength
- **4mm+**: Industrial applications or very large joints

### Tolerance Adjustment
- **0.05-0.08mm**: Precision applications, tight fit
- **0.1mm**: Standard fit (default)
- **0.15-0.2mm**: Looser fit for rough printing or materials that swell
- **0.2mm+**: Very loose fit for easy assembly or poor printer calibration

## Troubleshooting

### Ball Won't Insert
- Increase tolerance parameter
- Check for printing artifacts on the ball surface
- Verify socket flex cuts printed completely
- Light sanding of the ball surface

### Ball Too Loose
- Decrease tolerance parameter
- Check printer calibration
- Consider scaling the ball mount up by 0.1-0.2%
- Use a different material with less shrinkage

### Socket Walls Crack
- Increase wall thickness
- Use more flexible material (PETG instead of PLA)
- Check that flex cuts are properly sized
- Reduce tolerance to decrease insertion force

### Poor Rotation
- Increase tolerance slightly
- Sand the ball surface smooth
- Apply dry lubricant
- Check for layer adhesion issues on the ball

### Joint Comes Apart
- Decrease tolerance for tighter fit
- Increase wall thickness for better flex cut grip
- Check that ball is fully seated in socket
- Consider adding a retention feature to your design
