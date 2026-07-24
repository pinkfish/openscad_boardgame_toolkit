2-D shapes
==========

Pure-Python port of the 2-D shape generators from BOSL2's ``shapes2d.scad`` (plus ``arc()``).
Each returns native 2-D geometry (via ``polygon()``), ready to ``linear_extrude`` or offset.

Coverage of BOSL2 ``shapes2d.scad``
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 15 45

   * - BOSL2 shape
     - Status
     - Notes
   * - ``square`` / ``rect``
     - ported
     - plus ``rect_path`` for the point-list form
   * - ``circle`` / ``ellipse``
     - ported
     -
   * - ``regular_ngon`` / ``pentagon`` / ``hexagon`` / ``octagon``
     - ported
     -
   * - ``right_triangle`` / ``trapezoid``
     - ported
     -
   * - ``star``, ``teardrop2d``, ``egg``, ``glued_circles``, ``supershape``, ``reuleaux_polygon``
     - ported
     -
   * - ``squircle``
     - ported
     - :func:`~bosl2.shapes2d.squircle` — the default ``"fg"`` (Fong-Garcia) style; the
       ``"superellipse"`` / ``"bezier"`` styles are not ported
   * - ``jittered_poly``, ``round2d``, ``shell2d``
     - ported
     - ``round2d`` / ``shell2d`` are rounding / shelling operators
   * - ``arc``
     - ported
     - lives here but is documented on the :doc:`drawing` page (returns a
       :class:`~bosl2.paths.Path`)
   * - ``text``
     - ported
     - :func:`~bosl2.shapes2d.text`
   * - ``keyhole``
     - ported
     - :func:`~bosl2.shapes2d.keyhole`
   * - ``ring``
     - ported
     - :func:`~bosl2.shapes2d.ring` — the full-annulus form (``r1``/``r2`` or ``r`` + ``ring_width``);
       the arc / 3-point / corner / width+thickness forms are not ported

API reference
-------------

.. automodule:: bosl2.shapes2d
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: arc
