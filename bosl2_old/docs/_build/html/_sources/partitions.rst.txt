Partitions: planar cuts & interlocking splits
=============================================

Pure-Python port of BOSL2's ``partitions.scad`` -- slice an object with a plane, or partition a
large object into two interlocking pieces for printing. The cut operators are methods on
:class:`~bosl2.shapes3d.Bosl2Solid` via the :class:`~bosl2.partitions.Partitionable` mixin; the
2-D cut-path generators return :class:`~bosl2.paths.Path` objects and the mask builders return
Bosl2Solids.

Planar half-cuts
----------------

``left_half`` / ``right_half`` / ``front_half`` / ``back_half`` / ``top_half`` / ``bottom_half``
keep one side of an axis-aligned plane, and ``half_of(v, cp)`` cuts at any plane. Each intersects
the solid with a half-space mask **auto-sized from the object's own bounding box**, so BOSL2's
``s=`` mask-size argument is optional::

    cuboid([40, 30, 20]).left_half()          # keep the -X half
    cuboid([40, 30, 20]).bottom_half(z=5)      # cut at Z=5, keep below
    sphere(r=20).half_of([0, 1, 1])            # cut on an arbitrary plane through the centre

Passing ``cut_path=`` (a 2-D :func:`~bosl2.partitions.partition_path`) makes the cut face follow an
interlocking profile instead of a flat plane; ``cut_angle`` spins that face about the normal and
``offset`` grows the mask.

Interlocking partitions
-----------------------

``.partition()`` cuts a solid into two mating pieces along a joint (jigsaw, dovetail, hammerhead,
...) and spreads them apart, returning ``[back_piece, front_piece]``::

    back, front = cuboid([60, 40, 20]).partition(spread=12, cutpath="dovetail")

:func:`~bosl2.partitions.partition_path` builds the joint profile from a list of segment
descriptors, and :func:`~bosl2.partitions.partition_mask` / :func:`~bosl2.partitions.partition_cut_mask`
give the raw masks if you want to cut manually. Every ``partition_path`` output is pinned to the
real BOSL2 in ``tests/test_bosl2_reorient.py``.

Coverage of BOSL2 ``partitions.scad``
-------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - BOSL2 function
     - Status
     - Notes
   * - ``half_of``
     - ported
     - :meth:`~bosl2.partitions.Partitionable.half_of` -- any plane; ``cut_path`` /
       ``cut_angle`` / ``offset`` supported. Auto-sizes the mask; the 2-D ``planar`` form is not
       ported (Bosl2Solid is 3-D).
   * - ``left_half`` / ``right_half`` / ``front_half`` / ``back_half`` / ``top_half`` / ``bottom_half``
     - ported
     - the six axis half-cuts, as methods.
   * - ``partition``
     - ported
     - :meth:`~bosl2.partitions.Partitionable.partition` -- returns the two interlocking pieces
       (``spread``/``cutsize``/``cutpath``/``gap``/``spin``/``slop``).
   * - ``partition_mask`` / ``partition_cut_mask``
     - ported
     - :func:`~bosl2.partitions.partition_mask` / :func:`~bosl2.partitions.partition_cut_mask`.
   * - ``partition_path``
     - ported
     - :func:`~bosl2.partitions.partition_path` -- the full segment grammar, including the
       ``xflip``/``yflip``/``addflip``/``wave``/``Nx``/``WxH``/``skew:``/``pinch:`` modifiers and
       the ``altpath`` redirect.
   * - ``show_frameref``
     - not ported
     - a preview-only frame-reference arrow (no geometry payload).

Examples
--------

A box split into two dovetail-jointed pieces, spread apart:

.. pythonscad-example::

    back, front = s3.cuboid([60, 40, 20]).partition(spread=14, cutpath="dovetail")
    (back | front).show()

A jigsaw cut face on one half of a long bar:

.. pythonscad-example::

    cut = partition_path([50, "jigsaw", 50], _fn=20)
    s3.cuboid([100, 40, 16]).back_half(cut_path=cut).show()

API reference
-------------

.. automodule:: bosl2.partitions
   :members:
   :undoc-members:
   :exclude-members: Partitionable

.. autoclass:: bosl2.partitions.Partitionable
   :members:
