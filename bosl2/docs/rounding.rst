Rounding: round_corners & smooth_path
=====================================

Pure-Python port of the path-rounding core of BOSL2's ``rounding.scad``:
:func:`~bosl2.rounding.round_corners` rounds every corner of a path, and
:func:`~bosl2.rounding.smooth_path` fits a continuous-curvature curve through a path. Both work on
2-D and 3-D paths and are methods on :class:`~bosl2.paths.Path` and :class:`~bosl2.paths.Path3D`::

    Path([[0, 0], [40, 0], [40, 30], [0, 30]]).round_corners(radius=5)
    Path([[0, 0], [40, 0], [40, 30], [0, 30]]).round_corners(method="smooth", joint=8)
    Path([[0, 0], [10, 30], [30, -10], [50, 20]], closed=False).smooth_path(relsize=0.4)

``round_corners`` supports three corner styles -- ``"circle"`` (a constant-radius arc), ``"smooth"``
(a continuous-curvature bezier, so no curvature discontinuity where the round meets the edge), and
``"chamfer"`` (a straight bevel) -- sized by exactly one of ``radius``/``r`` (circle only), ``cut``
(depth toward the corner), ``joint`` (distance back along each edge), or ``width`` (chamfer only).
``k`` (smooth only) tunes the curvature match. Both functions are pinned point-for-point to the
real BOSL2 output in ``tests/test_bosl2_reorient.py``; the circle case is bit-identical to the
toolkit's original ``round_corners``.

Coverage of BOSL2 ``rounding.scad``
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - BOSL2 function
     - Status
     - Notes
   * - ``round_corners``
     - ported
     - :func:`~bosl2.rounding.round_corners` -- all three methods, all four size measures, open/closed,
       2-D and 3-D. The roundover-overflow (scale-factor) check is included.
   * - ``smooth_path``
     - ported (``method="edges"``)
     - :func:`~bosl2.rounding.smooth_path` -- a bezier fit through the points; the
       ``method="corners"`` variant is not ported.
   * - ``path_join``
     - not ported
     - join paths end-to-end with rounded joints -- a follow-up.
   * - ``offset_stroke`` / ``offset_sweep`` (+ ``os_*``) / ``convex_offset_extrude``
     - not ported
     - variable-width strokes and rounded-edge extrusions -- a large follow-up.
   * - ``rounded_prism`` / ``join_prism`` / ``prism_connector`` / ``attach_prism`` / ``bent_cutout_mask``
     - not ported
     - the continuous-curvature 3-D prism generators (thousands of lines) -- a large follow-up.

Examples
--------

A square rounded three ways (circle, smooth, chamfer), extruded:

.. pythonscad-example::

    sq = [[0, 0], [40, 0], [40, 30], [0, 30]]
    a = round_corners(sq, method="circle", radius=6).polygon().linear_extrude(height=4)
    b = round_corners(sq, method="smooth", joint=10).polygon().linear_extrude(height=4).right(50)
    c = round_corners(sq, method="chamfer", joint=8).polygon().linear_extrude(height=4).right(100)
    (a | b | c).show()

A wiggly path smoothed into a flowing ribbon:

.. pythonscad-example::

    pts = [[0, 0], [10, 30], [30, -10], [50, 20], [70, 0]]
    smooth_path(pts, relsize=0.4).stroke(width=2).linear_extrude(height=3).show()

API reference
-------------

.. automodule:: bosl2.rounding
   :members:
   :undoc-members:
   :exclude-members: Roundable

.. autoclass:: bosl2.rounding.Roundable
   :members:
