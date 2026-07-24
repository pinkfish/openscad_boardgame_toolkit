Native-only mesh operations
===========================

These operations wrap PythonSCAD builtins that **BOSL2 has no counterpart for**, exposed as
first-class :class:`~bosl2.shapes3d.Bosl2Solid` methods (and one 2-D→3-D constructor) so they chain
fluently and keep their anchoring metadata, rather than leaking raw native handles. They execute
only inside the real PythonSCAD app; under the numeric test mock they degrade to identity/AABB
stand-ins, so the pure-Python fast suite still runs and the real geometry is covered by the STL
render tests.

.. list-table::
   :header-rows: 1
   :widths: 22 20 58

   * - Operation
     - Kind
     - What it does
   * - ``solid.repair()``
     - solid → solid
     - Force the mesh watertight, healing gaps and non-manifold edges.
   * - ``solid.oversample(n)``
     - solid → solid
     - Subdivide every facet *n*-fold (e.g. to smooth a subsequent bend).
   * - ``solid.pull(direction, distance)``
     - solid → solid
     - Pull the material on the ``+direction`` side apart, stretching what is between.
   * - ``solid.wrap(r, _fn=…)``
     - solid → solid
     - Wrap the solid around a cylinder of radius *r* (bends +X into the circumference).
   * - ``solid.separate()``
     - solid → list of solids
     - Split a solid of disconnected lumps into its connected components.
   * - ``solid.inside(point)``
     - solid → bool
     - Test whether a point lies inside the solid.
   * - ``s3.roof(shape2d)``
     - 2-D → solid
     - Raise a hip roof over a 2-D outline via its straight skeleton.

.. note::

   ``wrap()`` is a valid operation but meshing/exporting a wrapped solid is very slow in the
   Manifold backend, so it has no render test (only mock-level coverage). Call
   :meth:`~bosl2.shapes3d.Bosl2Solid.oversample` first if you need the bend to look smooth.

Examples
--------

A hip roof raised over a square outline (a pyramid; over any polygon it is a proper straight-skeleton
roof):

.. pythonscad-example::

    s3.roof(s2.square([30, 30], center=True)).show()

Oversampling subdivides a solid's facets without changing its shape -- useful before a bend or a
displacement:

.. pythonscad-example::

    s3.cuboid([30, 30, 12]).oversample(3).show()

Pulling a block apart stretches the material between the halves:

.. pythonscad-example::

    s3.cuboid([24, 24, 12]).pull([0, 0, 1], 8).show()

API reference
-------------

The methods live on :class:`~bosl2.shapes3d.Bosl2Solid`
(:meth:`~bosl2.shapes3d.Bosl2Solid.repair`, :meth:`~bosl2.shapes3d.Bosl2Solid.oversample`,
:meth:`~bosl2.shapes3d.Bosl2Solid.pull`, :meth:`~bosl2.shapes3d.Bosl2Solid.wrap`,
:meth:`~bosl2.shapes3d.Bosl2Solid.separate`, :meth:`~bosl2.shapes3d.Bosl2Solid.inside`); the roof
constructor is :func:`~bosl2.shapes3d.roof`.

.. autofunction:: bosl2.shapes3d.roof
