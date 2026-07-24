Threading: screw threads, rods & nuts
=====================================

Pure-Python port of the core of BOSL2's ``threading.scad``. The :class:`~bosl2.threading.Threading`
class builds screw threads by generating the whole rod (core + helical thread) as one manifold
polyhedron -- an angular sweep of the thread profile stacked over every turn -- so the result is
always watertight. (Sweeping the thread and CSG-unioning a coaxial core instead is what Manifold
cannot triangulate cleanly, so this port builds the polyhedron directly, as BOSL2 does.)

Every method is a class method returning a :class:`~bosl2.shapes3d.Bosl2Solid`::

    Threading.threaded_rod(12, 24, 1.75)                 # ISO M12 x 1.75
    Threading.acme_threaded_rod(20, 30, 4)               # 29-degree ACME
    Threading.threaded_nut(18, 12, 10, 1.75, slop=0.1)   # matching hex nut

A *rod* is a threaded cylinder; a *nut* is a hex/square block with a matching threaded hole (cut by
a thread "tap", with *slop* radial clearance). *pitch* is the axial distance between threads,
*starts* the number of thread starts, and *left_handed* flips the helix. The thread *profiles* are
ported verbatim from BOSL2 (checked in ``tests/test_threading.py``), and the geometry is verified
watertight with the correct major/minor diameter and length.

Coverage of BOSL2 ``threading.scad``
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 16 44

   * - BOSL2 function
     - Status
     - Notes
   * - ``generic_threaded_rod`` / ``generic_threaded_nut``
     - ported
     - the profile-driven core every other builder uses.
   * - ``threaded_rod`` / ``threaded_nut``
     - ported
     - ISO (metric) / UTS 60-degree triangular threads.
   * - ``trapezoidal_threaded_rod`` / ``trapezoidal_threaded_nut``
     - ported
     - symmetric trapezoidal (metric trapezoidal by default; ``thread_angle`` / ``thread_depth``).
   * - ``acme_threaded_rod`` / ``acme_threaded_nut``
     - ported
     - 29-degree ACME threads.
   * - ``square_threaded_rod`` / ``square_threaded_nut``
     - ported
     - square-profile threads.
   * - ``buttress_threaded_rod`` / ``buttress_threaded_nut``
     - ported
     - asymmetric buttress threads.
   * - ``thread_helix``
     - ported
     - a single helical thread ridge, to add onto your own cylinder.
   * - blunt-start / lead-in tapers, ``teardrop``, bevels
     - not ported
     - the BOSL2 end-refinements; this port cuts the ends flush. A follow-up.
   * - ``ball_screw_rod`` / ``npt_threaded_rod`` / ``bspp_threaded_rod``
     - not ported
     - specialised thread forms; a follow-up.

Examples
--------

An ISO M16 x 2 rod:

.. pythonscad-example::

    Threading.threaded_rod(16, 30, 2, _fa=4, _fs=1).show()

An ACME lead screw:

.. pythonscad-example::

    Threading.acme_threaded_rod(24, 36, 5, _fa=4, _fs=1).show()

A rod threaded into its matching hex nut (shown side by side):

.. pythonscad-example::

    rod = Threading.threaded_rod(12, 30, 1.75, _fa=6, _fs=1)
    nut = Threading.threaded_nut(18, 12, 10, 1.75, slop=0.1, _fa=6, _fs=1).right(22)
    (rod | nut).show()

API reference
-------------

.. autoclass:: bosl2.threading.Threading
   :members:
