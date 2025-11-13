# Project Migration

fb_lbrary is currently deprecated, and has been replaced with [b3dkit](https://github.com/x0pherl/b3dkit)


The Fender-Bender library began as a way to externalize and isolate some common [build123d](https://github.com/gumyr/build123d) utilities, functions, & methods from the [Fender-Bender](https://github.com/x0pherl/fender-bender) project.

It grew to include many capabilities not required by that project and outgrew its name as well.

As it's expanded beyond its original purpose, I've wanted to update it to have a more "build123d-native" feel. For example, in fb-library you would always have to add a Part with the add function even within a BuildPart context. Example:

Also, fb-library followed pep-8 method naming conventions while Build123d uses CamelCase method names. This creates friction when using fb-library.

So we've now archived this library, and unfortunately this means anyone currently using fb-library on an active project that wants to continue to get updates and new functionality will need to refactor their code around the new b3dkit standards.

This was a tough choice to make, but it was not going to get easier over time.