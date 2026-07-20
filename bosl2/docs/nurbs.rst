NURBS: curves & surfaces
========================

Pure-Python port of the NURBS **evaluation** API from BOSL2's ``nurbs.scad``: evaluate a NURBS
curve, sample a NURBS surface patch, mesh a patch into a VNF, and elevate a curve's degree. All
three flavours -- ``"clamped"``, ``"open"`` and ``"closed"`` -- are supported, with weights
(rational NURBS), knot multiplicities, and explicit knot vectors.

:func:`~bosl2.nurbs.nurbs_curve` returns a :class:`~bosl2.paths.Path` (2-D control points) or
:class:`~bosl2.paths.Path3D` (3-D), so the result carries the full path/extrude/stroke API;
:func:`~bosl2.nurbs.nurbs_vnf` returns a :class:`~bosl2.vnf.VNF`. Every case is pinned
point-for-point to the real BOSL2 output in ``tests/test_bosl2_reorient.py`` -- including the
classic rational-NURBS sphere.

The first argument to any of these may be a NURBS parameter list
``[type, degree, control, knots, mult, weights]`` instead of separate arguments.

Coverage of BOSL2 ``nurbs.scad``
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - BOSL2 function
     - Status
     - Notes
   * - ``nurbs_curve``
     - ported
     - :func:`~bosl2.nurbs.nurbs_curve` -- clamped/open/closed, weights, mult, explicit knots,
       ``splinesteps`` or ``u``. Returns a Path / Path3D (a scalar ``u`` returns one point).
   * - ``nurbs_patch_points``
     - ported
     - :func:`~bosl2.nurbs.nurbs_patch_points` -- sample a surface on a grid (``splinesteps`` or
       ``u``/``v``); per-direction degree/type/mult/knots.
   * - ``nurbs_vnf``
     - ported
     - :func:`~bosl2.nurbs.nurbs_vnf` -- mesh a patch (built on ``vnf_vertex_array``), with
       ``style`` / ``reverse`` / ``caps``.
   * - ``nurbs_elevate_degree``
     - ported
     - :func:`~bosl2.nurbs.nurbs_elevate_degree` -- raise a clamped/open curve's degree (collocation
       at Greville points).
   * - ``is_nurbs_patch``
     - ported
     - :func:`~bosl2.nurbs.is_nurbs_patch`.
   * - ``nurbs_interp`` / ``nurbs_interp_surface``
     - not ported
     - the constrained least-squares *interpolation* solvers (fit a NURBS through given points with
       derivative/curvature/corner constraints) -- thousands of lines of custom linear algebra; a
       large follow-up.
   * - ``debug_nurbs`` / ``debug_nurbs_interp``
     - not ported
     - preview/annotation display modules.

Examples
--------

A cubic clamped NURBS curve, swept into a tube:

.. pythonscad-example::

    ctrl = [[0, 0, 0], [10, 20, 5], [30, -10, 10], [50, 20, 0], [60, 0, 15]]
    nurbs_curve(ctrl, 3, splinesteps=12).stroke(width=3).show()

A cubic B-spline surface patch meshed into a sheet:

.. pythonscad-example::

    patch = [
        [[-50, 50, 0], [-16, 50, 20], [16, 50, 20], [50, 50, 0]],
        [[-50, 16, 20], [-16, 16, 40], [16, 16, 40], [50, 16, 20]],
        [[-50, -16, 20], [-16, -16, 40], [16, -16, 40], [50, -16, 20]],
        [[-50, -50, 0], [-16, -50, 20], [16, -50, 20], [50, -50, 0]],
    ]
    nurbs_vnf(patch, 3, splinesteps=10).polyhedron().show()

A sphere as a rational NURBS surface (weights + repeated knots):

.. pythonscad-example::

    patch = [[[0, 0, 1]] * 7,
             [[2, 0, 1], [2, 4, 1], [-2, 4, 1], [-2, 0, 1], [-2, -4, 1], [2, -4, 1], [2, 0, 1]],
             [[2, 0, -1], [2, 4, -1], [-2, 4, -1], [-2, 0, -1], [-2, -4, -1], [2, -4, -1], [2, 0, -1]],
             [[0, 0, -1]] * 7]
    weights = [[w / 9 for w in row] for row in
               [[9, 3, 3, 9, 3, 3, 9], [3, 1, 1, 3, 1, 1, 3], [3, 1, 1, 3, 1, 1, 3], [9, 3, 3, 9, 3, 3, 9]]]
    nurbs_vnf(patch, 3, weights=weights, knots=[None, [0, 0.5, 0.5, 0.5, 1]], splinesteps=12).polyhedron().show()

API reference
-------------

.. automodule:: bosl2.nurbs
   :members:
   :undoc-members:
