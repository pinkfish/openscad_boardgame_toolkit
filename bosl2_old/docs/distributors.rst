Distributors: copiers & reflected copies
========================================

Pure-Python port of BOSL2's ``distributors.scad`` -- the "copiers" that duplicate a shape into a
line, grid, ring, arc, sphere, or path pattern, plus the reflected-copy helpers. Each copier is a
module-level function returning a list of 4x4 transformation matrices (BOSL2's function form), and
a matching **method** on every geometry object via the :class:`~bosl2.distributors.Distributable`
mixin.

What a copier returns depends on the object it is called on:

* :class:`~bosl2.shapes3d.Bosl2Solid` -- the **union** of the transformed geometry copies (a new
  solid), matching BOSL2's module form::

      cuboid([10, 10, 10]).grid_copies(n=[3, 3], spacing=30)   # 9 cubes, unioned
      cuboid([6, 6, 6]).zrot_copies(n=6, r=30)                 # a ring of 6 cubes
      part.right(20).xflip_copy()                              # part + its mirror image

* :class:`~bosl2.paths.Path` / :class:`~bosl2.paths.Path3D` -- a plain ``list`` of the transformed
  path copies (BOSL2's function form). A 2-D ``Path`` only supports the in-plane copiers; one that
  would lift it out of the XY plane (``zcopies``, ``xrot_copies``, ``sphere_copies``, ...) raises,
  directing you to ``Path3D``.

Every copier's matrices are pinned to the real BOSL2 output in ``tests/test_bosl2_reorient.py``.

Coverage of BOSL2 ``distributors.scad``
---------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - BOSL2 function
     - Status
     - Notes
   * - ``move_copies``
     - ported
     - :func:`~bosl2.distributors.move_copies` -- a copy at each given offset.
   * - ``xcopies`` / ``ycopies`` / ``zcopies``
     - ported
     - spacing/``n``/``l``/``sp`` and the explicit-position-list form.
   * - ``line_copies``
     - ported
     - :func:`~bosl2.distributors.line_copies` -- along a line by spacing, length, or ``p1``/``p2``.
   * - ``grid_copies``
     - ported
     - square and staggered (hex) grids, ``size``/``n``/``spacing``, ``axes=``, and an ``inside=``
       polygon mask (``grid2d`` is the deprecated alias, not ported).
   * - ``rot_copies``
     - ported
     - rotated copies about any axis, with ``cp``/``sa``/``delta``/``subrot``.
   * - ``xrot_copies`` / ``yrot_copies`` / ``zrot_copies``
     - ported
     - rings about the X/Y/Z axes (``r``/``d``, ``sa``, ``subrot``).
   * - ``arc_copies``
     - ported
     - along a circular or elliptical arc in the XY plane (``arc_of`` alias not ported).
   * - ``sphere_copies``
     - ported
     - golden-spiral spread over a sphere/ellipsoid (``ovoid_spread`` alias not ported).
   * - ``path_copies``
     - ported
     - :func:`~bosl2.distributors.path_copies` -- along a 2-D/3-D path, oriented to it
       (``path_spread`` alias not ported).
   * - ``mirror_copy`` / ``xflip_copy`` / ``yflip_copy`` / ``zflip_copy``
     - ported
     - the original plus one reflected copy.
   * - ``distribute`` / ``xdistribute`` / ``ydistribute`` / ``zdistribute``
     - ported
     - :func:`~bosl2.distributors.distribute` -- lay a **list of distinct** solids out so they
       don't overlap (sizes taken from each child's bounding box if not given).
   * - ``$pos`` / ``$idx`` / ``$ang`` / ``$row`` / ``$col`` side-effect variables
     - not ported
     - OpenSCAD special variables for per-copy customization have no Python equivalent; build the
       variants yourself and use ``move_copies`` with explicit matrices.

Examples
--------

A grid of rounded pillars, unioned into one solid:

.. pythonscad-example::

    s3.cyl(h=12, r=4, rounding=1).grid_copies(n=[4, 3], spacing=14).show()

A ring of wedges facing the centre:

.. pythonscad-example::

    s3.prismoid([6, 10], [2, 10], h=12).zrot_copies(n=8, r=24).show()

Copies of a 2-D outline along an arc, extruded together:

.. pythonscad-example::

    tile = Path([[-3, -3], [3, -3], [3, 3], [-3, 3]])
    reduce(lambda a, b: a | b, (c.polygon() for c in tile.arc_copies(n=10, r=30, ea=180))) \
        .linear_extrude(height=3).show()

API reference
-------------

.. automodule:: bosl2.distributors
   :members:
   :undoc-members:
   :exclude-members: Distributable

.. autoclass:: bosl2.distributors.Distributable
   :members:
