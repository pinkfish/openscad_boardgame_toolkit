bosl2 — a pure-Python PythonSCAD port of BOSL2
==============================================

``bosl2`` is a pure-Python / numpy port of the pieces of `BOSL2 <https://github.com/BelfrySCAD/BOSL2>`_
that this toolkit uses, with **no** ``osuse()``/BOSL2 runtime dependency. Every operation hangs off
an object — :class:`~bosl2.paths.Path` for 2-D outlines, :class:`~bosl2.regions.Region` for
outlines-with-holes, :class:`~bosl2.beziers.Bezier` / :class:`~bosl2.beziers.BezierPatch` for bezier
curves and surfaces, :class:`~bosl2.vnf.VNF` for vertex-face meshes, and the
:class:`~bosl2.shapes3d.Bosl2Solid` primitives — so new code reads as fluent chains::

    Path([[0, 0], [80, 0], [80, 60], [0, 60]]).offset(r=-2).round_corners(radius=1).polygon()

Rendered examples
-----------------

Every documented function with a rendered example shows both the exact PythonSCAD code and what the
real PythonSCAD binary builds for it, via the ``pythonscad-example`` directive (in
``docs/_ext/bosl2_example.py``): an **interactive 3-D viewer** for the exported STL mesh (rotate,
pan and zoom — served by the ``stl_viewer`` extension's three.js viewer, a working drop-in for the
``sphinxstl`` ``.. stl::`` directive), plus a **download link** to the mesh. Two-dimensional or
open-surface examples that have no solid mesh fall back to a static preview image.

.. note::

   The interactive viewers fetch each ``.stl`` over HTTP, so view the built docs through a web
   server (for example ``python3 -m http.server`` from ``bosl2/wiki``) rather than opening the
   HTML files directly with a ``file://`` URL, where browsers block the local mesh fetch. You can
   also embed a viewer for any STL yourself with ``.. stl:: path/to/mesh.stl``.

A cuboid primitive:

.. pythonscad-example::

   s3.cuboid([40, 30, 20], rounding=4).show()

A bezier surface patch, meshed to a VNF and rendered as a polyhedron:

.. pythonscad-example::

   patch = [
       [[-50, -50, 0], [-16, -50, 20], [16, -50, -20], [50, -50, 0]],
       [[-50, -16, 20], [-16, -16, 20], [16, -16, -20], [50, -16, 20]],
       [[-50, 16, 20], [-16, 16, -20], [16, 16, 20], [50, 16, 20]],
       [[-50, 50, 0], [-16, 50, -20], [16, 50, 20], [50, 50, 0]],
   ]
   BezierPatch(patch).sheet([0, -6], splinesteps=16).polyhedron().show()

Sweeping a profile along a bezier curve:

.. pythonscad-example::

   circle = [[2 * math.cos(t), 2 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
   Bezier([[0, 0, 5], [0, 0, 20], [25, 12, 15], [30, 4, 6]]).sweep(circle, splinesteps=24).polyhedron().show()

API reference
-------------

.. toctree::
   :maxdepth: 2

   paths
   regions
   beziers
   vnf
   skin
   shapes3d
   shapes2d
   masking
   transforms
   geometry
   math
   vectors
   comparisons
   constants
