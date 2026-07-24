Colour: colorspace conversion & colour operators
================================================

Pure-Python port of BOSL2's ``color.scad`` -- the HSL/HSV -> RGB conversions, the
:func:`~bosl2.color.rainbow` helper, and the colour operators added onto
:class:`~bosl2.shapes3d.Bosl2Solid` via the :class:`~bosl2.color.Colorable` mixin. Each operator
resolves to the native PythonSCAD calls: ``color()``, ``highlight()`` (the ``#`` modifier) and
``background()`` (the ``%`` / ghost modifier)::

    cuboid([20, 20, 10]).color("red")
    cuboid([20, 20, 10]).hsv(210, 0.8, 0.9)          # colour from an HSV hue
    cuboid([20, 20, 10]).color([0.2, 0.5, 0.9, 0.4]) # RGBA
    part.highlight()                                  # # debug modifier
    part.ghost()                                      # % transparent, non-interacting

``hsl()`` / ``hsv()`` are pinned to the real BOSL2 output in ``tests/test_bosl2_reorient.py``.

Because the toolkit builds native geometry rather than a BOSL2 ``$color`` attachment tree,
:meth:`~bosl2.color.Colorable.recolor` and :meth:`~bosl2.color.Colorable.color_this` both apply the
colour directly -- an object's already-coloured children keep their colour (OpenSCAD ``color()``
semantics), and there is no ``$color`` scheme to revert to, so a ``"default"`` colour is a no-op.

Coverage of BOSL2 ``color.scad``
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 18 52

   * - BOSL2 function
     - Status
     - Notes
   * - ``hsl`` / ``hsv``
     - ported
     - :func:`~bosl2.color.hsl` / :func:`~bosl2.color.hsv` -- the function form (RGB or RGBA) and
       the module form as the :meth:`~bosl2.color.Colorable.hsl` / :meth:`~bosl2.color.Colorable.hsv`
       object methods.
   * - ``recolor`` / ``color_this``
     - ported
     - object methods; both apply the colour natively (no ``$color`` attachment tree in this
       backend, so they are equivalent).
   * - ``rainbow``
     - ported
     - :func:`~bosl2.color.rainbow` colours a list of objects; :func:`~bosl2.color.rainbow_colors`
       returns the RGB list for a given count.
   * - ``highlight`` / ``highlight_this``
     - ported
     - :meth:`~bosl2.color.Colorable.highlight` -- the ``#`` modifier (native ``highlight()``); the
       single-level ``highlight_this`` collapses to the same call.
   * - ``ghost`` / ``ghost_this``
     - ported
     - :meth:`~bosl2.color.Colorable.ghost` -- the ``%`` modifier (native ``background()``).
   * - ``color_overlaps``
     - not ported
     - a debug module that intersects every pair of children; niche -- build it explicitly with the
       CSG operators if needed.

Examples
--------

A stack of blocks, each a different hue from HSV:

.. pythonscad-example::

    blocks = [s3.cuboid([20, 20, 4]).up(i * 5).hsv(i * 40, 0.8, 0.95) for i in range(5)]
    reduce(lambda a, b: a | b, blocks).show()

Rainbow-colouring a list of parts to tell them apart:

.. pythonscad-example::

    parts = [s3.cyl(h=20, r=4).right(i * 12) for i in range(6)]
    reduce(lambda a, b: a | b, rainbow(parts)).show()

API reference
-------------

.. automodule:: bosl2.color
   :members:
   :undoc-members:
   :exclude-members: Colorable

.. autoclass:: bosl2.color.Colorable
   :members:
