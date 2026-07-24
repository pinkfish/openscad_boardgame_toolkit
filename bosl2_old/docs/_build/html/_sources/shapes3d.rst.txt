3-D shapes and Bosl2Solid
=========================

Pure-Python port of the 3-D shape generators from BOSL2's ``shapes3d.scad``. Each returns a
:class:`~bosl2.shapes3d.Bosl2Solid` wrapping native geometry, with BOSL2-style anchor/spin/orient
support and bbox-backed attachment methods.

Coverage of BOSL2 ``shapes3d.scad``
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 15 45

   * - BOSL2 shape
     - Status
     - Notes
   * - ``cube`` / ``cuboid``
     - ported
     - with chamfer / rounding / edge selection
   * - ``prismoid``
     - ported
     -
   * - ``regular_prism``
     - ported
     -
   * - ``octahedron`` / ``wedge``
     - ported
     -
   * - ``cylinder`` / ``cyl`` / ``xcyl`` / ``ycyl`` / ``zcyl``
     - ported
     -
   * - ``tube`` / ``rect_tube`` / ``pie_slice``
     - ported
     -
   * - ``sphere`` / ``spheroid``
     - ported
     -
   * - ``torus`` / ``teardrop`` / ``onion``
     - ported
     -
   * - ``text3d`` / ``path_text``
     - ported
     -
   * - ``interior_fillet``
     - ported
     -
   * - ``heightfield`` / ``cylindrical_heightfield``
     - ported
     -
   * - ``ruler``
     - ported
     -
   * - ``plot3d``
     - ported
     - :func:`~bosl2.shapes3d.plot3d` — a ``z = f(x, y)`` surface plot, with an optional solid base
   * - ``fillet``
     - ported
     - :func:`~bosl2.shapes3d.fillet` — the concave edge-fillet mask (90-degree edges only; other
       dihedral ``ang`` not ported)
   * - ``plot_revolution``
     - ported
     - :func:`~bosl2.shapes3d.plot_revolution` — a surface of revolution modulated by
       ``r = f(angle, z)`` (the ``arclength`` form is not ported)
   * - ``textured_tile``
     - ported (height-field form)
     - :func:`~bosl2.shapes3d.textured_tile` — a tiled scalar height-field texture; VNF-tile and
       named-texture forms need the BOSL2 texture engine (not ported)

Bosl2Solid & attachment
-----------------------

Every 3-D shape is a :class:`~bosl2.shapes3d.Bosl2Solid`, which carries the transform methods
(``translate``/``move``, ``rotate``/``rot``, ``right``/``left``/``back``/``forward``/``up``/``down``,
``mirror``, ``scale``, ``color``) and the BOSL2 attachment methods —
``bounds``, ``anchor_point``, ``reanchor``, ``reorient``, ``orient``, ``position``, ``attach``,
``align``, plus the edge/corner/face masking (``edge_mask``, ``edge_profile``, ``corner_profile``,
``face_profile``). All of these read the object's **native bounding box**, so a size never needs to
be threaded through the calls — e.g. ``cuboid([40,30,20]).attach(TOP, sphere(r=6))`` or
``cyl(h=20, r=5).orient(RIGHT)`` just work on the built object.

The BOSL2 attachment *framework* internals (``attachable``, ``attach_geom``, named anchors, the
``tag``/``diff``/``intersect`` tagged-CSG operations, and the ``show_anchors``/description helpers)
are not ported — the methods above cover positioning/masking directly on the object.

API reference
-------------

.. automodule:: bosl2.shapes3d
   :members:
   :undoc-members:
   :show-inheritance:
