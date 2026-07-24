Drawing: path generators & renderers
=====================================

Pure-Python port of BOSL2's ``drawing.scad``. It splits into path *generators* that return points
-- :func:`~bosl2.drawing.arc`, :func:`~bosl2.drawing.catenary`, :func:`~bosl2.drawing.turtle`
(2-D :class:`~bosl2.paths.Path`) and :func:`~bosl2.drawing.helix` (3-D
:class:`~bosl2.paths.Path3D`) -- and path *renderers* that turn points into geometry,
:func:`~bosl2.drawing.stroke` (a solid line) and :func:`~bosl2.drawing.dashed_stroke` (a list of
dash sub-paths).

The generators return **all** the computed points, so they compose with every ``Path`` operation
and feed straight into ``path_sweep`` / ``linear_extrude`` / ``stroke``. ``stroke`` and
``dashed_stroke`` are also methods on :class:`~bosl2.paths.Path` and
:class:`~bosl2.regions.Region`, so a built outline can be drawn directly::

    arc(r=30, angle=200).stroke(width=3)
    turtle(["move", 40, "arcleft", 8, "move", 40, "arcleft", 8]).stroke(width=2, closed=True)
    Region.with_holes(outline, hole).stroke(width=1)

Every generator is pinned point-for-point to the real BOSL2 output in
``tests/test_bosl2_reorient.py``.

Coverage of BOSL2 ``drawing.scad``
----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - BOSL2 function
     - Status
     - Notes
   * - ``arc``
     - ported
     - :func:`~bosl2.drawing.arc` returns a :class:`~bosl2.paths.Path`; all 2-D forms
       (radius/angle, ``angle=[start, end]``, ``width``/``thickness``, two-point with
       ``long``/``cw``/``ccw``, three-point, ``corner=``, and ``wedge=``). 3-D arcs are not ported.
   * - ``catenary``
     - ported
     - :func:`~bosl2.drawing.catenary` -- by ``droop=`` or endpoint ``angle=``.
   * - ``helix``
     - ported
     - :func:`~bosl2.drawing.helix` -- returns a :class:`~bosl2.paths.Path3D` (conical/flat spirals
       included).
   * - ``turtle``
     - ported
     - :func:`~bosl2.drawing.turtle` -- the full command set, including ``repeat`` and the
       ``arcleft``/``arcright``/``arcleftto``/``arcrightto`` arcs.
   * - ``stroke``
     - ported
     - :func:`~bosl2.drawing.stroke` -- 2-D (segment rects + joints & endcaps) and 3-D (cylinder
       tube + spherical joints + revolved endcaps). **Every** BOSL2 endcap/joint style is generated
       directly: ``round``, ``square``, ``butt``, ``dot``, ``block``, ``diamond``, ``chisel``,
       ``line``, ``x``, ``cross``, ``arrow``, ``arrow2``, ``arrow3``, ``tail``, ``tail2`` (arrow
       caps trim the line back). Per-vertex ``width`` lists and the ``*_angle``/``*_color`` knobs
       are not ported.
   * - ``dashed_stroke``
     - ported
     - :func:`~bosl2.drawing.dashed_stroke` -- the function form: a list of "on" dash
       :class:`~bosl2.paths.Path` s (stroke or extrude them to draw).
   * - ``turtle3d``
     - not ported
     - the 3-D turtle (separate ``turtle3d.scad`` machinery) -- port on request.
   * - ``debug_polygon`` / ``debug_region``
     - not ported
     - annotated debugging modules (vertex/edge labels); no geometry payload.

API reference
-------------

.. autofunction:: bosl2.shapes2d.arc

.. automodule:: bosl2.drawing
   :members: catenary, helix, turtle, stroke, dashed_stroke
   :undoc-members:
