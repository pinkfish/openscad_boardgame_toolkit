Miscellaneous: extrusions, bbox, hull & minkowski
=================================================

Pure-Python port of BOSL2's ``miscellaneous.scad`` -- the extrusions (``extrude_from_to``,
``path_extrude2d``, ``path_extrude``, ``cylindrical_extrude``), the bounding box, ``chain_hull``,
and the minkowski-based transforms (``minkowski_difference``, ``offset3d``, ``round3d``).

The two path extrusions are methods on :class:`~bosl2.paths.Path` / :class:`~bosl2.paths.Path3D`,
and -- unlike BOSL2, which extrudes its *children* -- they take the 2-D cross-section as a
**profile argument**::

    Path([[0, 0], [40, 0], [40, 40]]).path_extrude2d(s2.square([4, 8], center=True))
    Path3D([[0, 0, 0], [30, 0, 10], [30, 30, 20]]).path_extrude(s2.circle(r=4))

The *profile* can be a native 2-D shape, a :class:`~bosl2.paths.Path`, a
:class:`~bosl2.regions.Region`, a :class:`~bosl2.shapes3d.Bosl2Solid` wrapping 2-D geometry, or a
**zero-argument factory** that returns fresh geometry each call -- the "children" form. Use a
factory when the profile is a frep/SDF solid, so each placement gets its own handle (avoiding the
frep handle-reuse segfault); a plain object is meshed once and reused, which is fine for native CSG.

Coverage of BOSL2 ``miscellaneous.scad``
----------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 16 54

   * - BOSL2 module
     - Status
     - Notes
   * - ``extrude_from_to``
     - ported
     - :func:`~bosl2.miscellaneous.extrude_from_to` -- linear extrude of a profile between two 3-D
       points, with ``twist`` / ``scale`` / ``slices``.
   * - ``path_extrude2d``
     - ported
     - :meth:`~bosl2.miscellaneous.Extrudable.path_extrude2d` -- a moulding along a 2-D path, with
       revolved corner fillets, ``closed`` loops and rounded ``caps``.
   * - ``path_extrude``
     - ported
     - :meth:`~bosl2.miscellaneous.Extrudable.path_extrude` -- extrude a profile along a 2-D/3-D
       path (mitre-clipped segments). :func:`~bosl2.skin.path_sweep` is faster for a single polygon.
   * - ``cylindrical_extrude``
     - ported
     - :func:`~bosl2.miscellaneous.cylindrical_extrude` -- wrap a 2-D profile around a cylinder.
   * - ``bounding_box``
     - ported
     - :meth:`~bosl2.miscellaneous.Miscellaneous.bounding_box` -- uses the native bbox (exact and
       fast; BOSL2's projection/minkowski trick isn't needed). ``planar`` is not ported (the host
       is always a 3-D solid).
   * - ``chain_hull``
     - ported
     - :func:`~bosl2.miscellaneous.chain_hull` and the :meth:`~bosl2.miscellaneous.Miscellaneous.chain_hull`
       method.
   * - ``minkowski_difference``
     - ported
     - :func:`~bosl2.miscellaneous.minkowski_difference` and the method form.
   * - ``offset3d`` / ``round3d``
     - ported
     - :meth:`~bosl2.miscellaneous.Miscellaneous.offset3d` / :meth:`~bosl2.miscellaneous.Miscellaneous.round3d`
       -- minkowski-based; **very** slow, as in BOSL2.

Examples
--------

A moulding that follows an L-shaped path:

.. pythonscad-example::

    route = Path([[0, 0], [40, 0], [40, 40]], closed=False)
    route.path_extrude2d(s2.square([4, 8], center=True)).show()

A profile swept along a rising 3-D path:

.. pythonscad-example::

    route = Path3D([[0, 0, 0], [30, 0, 10], [30, 30, 20], [0, 30, 30]], closed=False)
    route.path_extrude(s2.circle(r=4, _fn=16)).show()

A twisting, tapering column between two points:

.. pythonscad-example::

    extrude_from_to(s2.square([8, 4], center=True), [0, 0, 0], [8, 12, 30], twist=180, scale=2).show()

API reference
-------------

.. automodule:: bosl2.miscellaneous
   :members:
   :undoc-members:
   :exclude-members: Extrudable, Miscellaneous

.. autoclass:: bosl2.miscellaneous.Extrudable
   :members:

.. autoclass:: bosl2.miscellaneous.Miscellaneous
   :members:
