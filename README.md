# modular

A lightweight library for writing modular code

## Presentation

`modular.py` is a small library that helps you write a modular and maintainable
codebase.

The library works with class: the loaded plug-ins are "injected" in
the given class. You can specify the way of injection, either by stacking
functions, with the `modulable` decorator, by overloading the base method, with
the `overridable` decorator, and finally with the `alternative` decorator,
which runs every function until it finds one that doesn't raise an exception.

Those decorators conserve the original method's informations, such as name,
module, docstring, and annotations.
