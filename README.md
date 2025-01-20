# fb-library Overview

The Fender-Bender library began as a way to externalize and isolate some common [build123d](https://github.com/gumyr/build123d) utilities, functions, & methods from the [Fender-Bender](https://github.com/x0pherl/fender-bender) project.

It's grown to include some capabilities not required by that project. Useful components include:
- dovetail: Splits a build123d `Part` object into two parts that can easily be slid together with very tight tolerances. Useful when building parts larger than your printer's build volume.
- click_fit: a tapered profile that allows for better printing & assembly than a simple half Sphere to allow parts to "click" or snap into place when fit together. The extruded shape and the socket are both shaped carefully to allow a mix of easy assembly and good hold.
- point: a lightweight X,Y coordinate point object with some geometric functions built into the object.
- hexwall: builds a field of hexagons with gaps in-between within a given set of bounds

# Documentation

Complete developer documentation for fb-library is maintained in the docs folder and on the [fb-library documentation](https://fb-library.readthedocs.io) site.

# Modifying the Source
The included source files rely on the build123d library. I recommend following the build123d installation instructions.

# Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# License
This project is licensed under the terms of the [MIT](https://choosealicense.com/licenses/mit/) license