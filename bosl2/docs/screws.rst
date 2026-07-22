Screws: metric screws, nuts & screw holes
=========================================

Pure-Python port of the core of BOSL2's ``screws.scad``, built on top of the
:class:`~bosl2.threading.Threading` thread generator. The :class:`~bosl2.screws.Screws` class turns a
metric screw name into ready-to-print geometry::

    Screws.screw("M6", 20, head="socket", drive="hex")   # M6 x 20 socket cap screw, hex recess
    Screws.nut("M6")                                      # matching M6 hex nut
    Screws.screw_hole("M6", 20, head="flat")             # countersunk clearance hole to subtract

A screw is specified by name -- ``"M6"`` (coarse pitch looked up from the ISO table), ``"M8x1"`` (an
explicit fine pitch), a bare number, or a ``{"diameter": ..., "pitch": ...}`` dict. Screws are built
*head-up*: the shaft occupies ``z in [-length, 0]`` (tip at the bottom) and the head sits above
``z = 0``, so a screw drops straight into a mating :meth:`~bosl2.screws.Screws.screw_hole` cut with
its mouth at ``z = 0``.

The dimension tables (ISO coarse/fine pitches, and the socket-cap, hex, button, pan, countersunk,
setscrew and nut head sizes) are transcribed verbatim from ``screws.scad`` and checked in
``tests/test_screws.py``; the assembled geometry is verified watertight with the right head, shaft
and thread in ``tests/test_stl_render.py``.

Coverage of BOSL2 ``screws.scad``
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - BOSL2 feature
     - Status
     - Notes
   * - ``screw_info``
     - ported
     - metric ISO sizes; returns a plain dict of resolved dimensions.
   * - ``screw``
     - ported
     - threaded/plain/partly-threaded shaft, plus socket / hex / button / pan / flat / setscrew heads.
   * - ``nut``
     - ported
     - hex or square nut with a matching threaded hole; ``"normal"`` / ``"thin"`` / ``"thick"`` thickness.
   * - ``screw_hole``
     - ported
     - clearance hole (close/normal/loose fit), flat-head countersink, counterbore, or tapped hole.
   * - hex / slot drive recess
     - ported
     - the two most common recesses; cut into the head (or the shaft top for a setscrew).
   * - phillips / torx drive recesses
     - not ported
     - a follow-up; the recess dimensions are tabulated but the mask shapes are not built.
   * - UTS / imperial specs, shoulder screws, named anchors, per-tolerance thread classes
     - not ported
     - a follow-up; this port covers the metric fastener geometry the toolkit needs.

Examples
--------

An M8 socket cap screw with a hex drive recess:

.. pythonscad-example::

    Screws.screw("M8", 24, head="socket", drive="hex", _fa=6, _fs=1).show()

A countersunk (flat-head) screw:

.. pythonscad-example::

    Screws.screw("M6", 20, head="flat", _fa=6, _fs=1).show()

A screw threaded into its matching hex nut (shown side by side):

.. pythonscad-example::

    screw = Screws.screw("M6", 18, head="button", drive="hex", _fa=6, _fs=1)
    nut = Screws.nut("M6", slop=0.1, _fa=6, _fs=1).right(18)
    (screw | nut).show()

API reference
-------------

.. autoclass:: bosl2.screws.Screws
   :members:
