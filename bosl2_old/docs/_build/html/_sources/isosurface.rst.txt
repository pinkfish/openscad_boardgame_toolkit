Isosurface: marching cubes & metaballs
======================================

Pure-Python port of the 3-D core of BOSL2's ``isosurface.scad``:
:func:`~bosl2.isosurface.isosurface` meshes the level set of a scalar field over a voxel grid
(marching cubes) into a :class:`~bosl2.vnf.VNF`; the ``mb_*`` functions are metaball field
primitives; and :func:`~bosl2.isosurface.metaballs` sums transformed primitives and meshes the
result into a blobby surface::

    isosurface(field_fn, isovalue=1, bounding_box=60, voxel_size=2)
    metaballs([(pos1, mb_sphere(12)), (pos2, mb_sphere(12))], bounding_box=box, voxel_size=2)

A field primitive returns a value that grows toward infinity at its center and falls off with
distance; the surface is drawn where the summed field reaches *isovalue* (default 1). Because the
fields add, overlapping metaballs bulge together into a smooth blob. The ``mb_*`` formulas are
pinned point-for-point to real BOSL2 in ``tests/test_bosl2_reorient.py``; the meshes are watertight
and verified geometrically.

The mesher uses the standard Paul Bourke marching-cubes triangle table, so its triangulation isn't
vertex-identical to BOSL2's, but the surface it encloses is the same; face winding is fixed to
outward via the VNF's signed volume.

Coverage of BOSL2 ``isosurface.scad``
-------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - BOSL2 function
     - Status
     - Notes
   * - ``isosurface``
     - ported
     - :func:`~bosl2.isosurface.isosurface` -- marching cubes over a field callable or a
       precomputed 3-D array; ``voxel_size``/``voxel_count``, ``closed``, ``reverse``, range
       isovalues ``[lo, hi]`` (collapsed to a one-sided threshold).
   * - ``metaballs``
     - ported
     - :func:`~bosl2.isosurface.metaballs` -- a list of ``(transform, metaball)`` pairs (or the
       BOSL2 flat form).
   * - ``mb_sphere`` / ``mb_cuboid`` / ``mb_torus`` / ``mb_capsule`` / ``mb_disk`` / ``mb_octahedron`` / ``mb_connector``
     - ported
     - the 3-D metaball field primitives, with ``cutoff`` / ``influence`` / ``negative``.
   * - ``mb_cyl``
     - not ported
     - the revolved-profile (cone/rounded) field -- a follow-up.
   * - ``contour`` / ``metaballs2d`` / ``mb_circle`` / ``mb_rect`` / ``mb_trapezoid`` / ``mb_stadium`` / ``mb_ring`` / ``mb_connector2d``
     - not ported
     - the 2-D analogues (marching squares) -- a follow-up.
   * - ``debug`` views, anchor/spin/orient
     - not ported
     - preview/attachment machinery.

Examples
--------

Two spheres merging into a peanut:

.. pythonscad-example::

    spec = [([-14, 0, 0], mb_sphere(12)), ([14, 0, 0], mb_sphere(12))]
    metaballs(spec, bounding_box=[[-40, -20, -20], [40, 20, 20]], voxel_size=2).polyhedron().show()

A ring metaball plus a connecting bar:

.. pythonscad-example::

    spec = [([0, 0, 0], mb_torus(14, 4)), ([-14, 0, 0], mb_connector([-14, 0, 0], [14, 0, 0], 4))]
    metaballs(spec, bounding_box=[[-22, -22, -10], [22, 22, 10]], voxel_size=2).polyhedron().show()

The level set of a custom field function:

.. pythonscad-example::

    def field(p):
        import numpy as np
        d = np.sqrt(p[:, 0]**2 + p[:, 1]**2 + p[:, 2]**2)
        return 18 / d + 3 * np.sin(p[:, 0] / 3) * np.cos(p[:, 1] / 3)
    isosurface(field, 1, bounding_box=70, voxel_size=2.5).polyhedron().show()

API reference
-------------

.. automodule:: bosl2.isosurface
   :members:
   :undoc-members:
   :exclude-members: Metaball

.. autoclass:: bosl2.isosurface.Metaball
   :members:
