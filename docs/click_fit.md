# Click Fit Module Documentation

## Overview

The `click_fit` module provides a divot function to create parts for snap fit connectors.

## Functions

### divot

Creates a divot that can be used to create a snap fit connector.

#### Arguments

- `radius` (float, default=0.5): The radius of the divot.
- `positive` (bool, default=True): When `True`, reduces the size and shaping of the divot for the extruded part. When `False`, deepens and widens the socket.
- `extend_base` (bool, default=False): When `True`, extends the base of the divot to allow for a clean connection when attaching without precise placement.

#### Returns

- `Part`: The created divot part.

#### Example

```python
from fb_library import divot

# Create a positive divot with a radius of 0.5
positive_divot = divot(radius=0.5, positive=True)

# Create a negative divot with a radius of 0.5 and extended base
negative_divot = divot(radius=0.5, positive=False, extend_base=True)