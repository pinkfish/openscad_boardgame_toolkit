Sweeps (skin)
=============

Pure-Python port of the surface generators from BOSL2's ``skin.scad`` — every one builds a
:class:`~bosl2.vnf.VNF` you render with ``.polyhedron()``.

Coverage of BOSL2 ``skin.scad``
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - BOSL2 function
     - Status
     - Notes
   * - ``sweep(shape, transforms)``
     - ported
     - :func:`~bosl2.skin.sweep`
   * - ``path_sweep(shape, path)``
     - ported
     - :func:`~bosl2.skin.path_sweep` — methods ``incremental`` / ``manual`` / ``natural``, twist,
       scale (scalar / ``[x, y]`` / per-point / ``Nx2``), open & closed paths, flat caps, user
       tangents, and the ``transforms=True`` mode
   * - ``skin(profiles, slices)``
     - ported
     - :func:`~bosl2.skin.skin` — ``direct`` and ``reindex`` methods
   * - ``linear_sweep(region, h)``
     - ported
     - :func:`~bosl2.skin.linear_sweep` — single outline, with twist / scale / shift / caps
   * - ``rotate_sweep(shape, angle)``
     - ported
     - :func:`~bosl2.skin.rotate_sweep`
   * - ``spiral_sweep(poly, h, r)``
     - ported
     - :func:`~bosl2.skin.spiral_sweep` — without the lead-in taper options
   * - ``path_sweep2d(shape, path)``
     - ported
     - :func:`~bosl2.skin.path_sweep2d` — 2-D shape along a 2-D path (mitre offset; local creases
       handled up to the path's tightest radius)
   * - ``rot_resample(rotlist, n)``
     - ported
     - :func:`~bosl2.skin.rot_resample` — resample a transform list along its screw motion, with
       ``rot_decode`` / ``rot_inverse`` in :mod:`bosl2.transforms`
   * - ``subdivide_and_slice`` / ``slice_profiles``
     - ported
     - :func:`~bosl2.skin.subdivide_and_slice`, :func:`~bosl2.skin.slice_profiles`
   * - ``skin()`` ``distance`` / ``tangent`` methods
     - not ported
     - use ``direct`` / ``reindex`` (they need the dynamic-programming vertex matcher)
   * - ``sweep_attach()``, anchors
     - not ported
     - need the BOSL2 attachment/anchor system
   * - textures (``texture()``, ``tex_*``)
     - not ported
     - the whole texturing engine
   * - rounded / chamfered "fancy" caps
     - not ported
     - use flat caps, or a native end treatment
   * - region shapes with holes
     - not ported
     - use a native ``linear_extrude`` / CSG for holed extrusions
   * - ``rot_resample()`` / ``associate_vertices()`` helpers
     - not ported
     - only needed by the un-ported matching methods

API reference
-------------

.. automodule:: bosl2.skin
   :members:
   :undoc-members:
   :show-inheritance:
