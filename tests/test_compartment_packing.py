# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: tests/test_compartment_packing.py
#    The bin packing itself: where compartments land, when they get turned, and the plan
#    cache. Pure Python -- the packing is arithmetic, so it runs in the 1.4s inner loop and
#    needs no app.
#
# FileSummary: Unit tests for compartment packing, rotation and the plan cache.
# FileGroup: Tests

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import compartments
from base_bgtk import InnerSize
from compartments import (
    BIN_PACKING_VERSION,
    Compartment,
    PackingBin,
    Group,
    Justify,
    LayoutError,
    Shape,
    layout_cache_clear,
    layout_cache_info,
    layout_compartments,
)


def _rects(count: int, w: float, l: float, **kw) -> list[Compartment]:
    return [Compartment(shape=Shape.RECT, w=w, l=l, depth=8, **kw) for _ in range(count)]


class RotationTests(unittest.TestCase):
    """A compartment may be turned a quarter turn, but only when asked and only to fit."""

    def setUp(self):
        layout_cache_clear()

    def test_a_row_that_does_not_fit_still_does_not_without_rotate(self):
        """rotate is opt-in: turning by default would move every compartment in every
        existing box, silently changing parts people have already printed."""
        contents = layout_compartments([Group(_rects(3, 30, 10))])
        with self.assertRaises(LayoutError) as caught:
            contents(InnerSize(width=70, length=60, height=20))
        self.assertIn("WIDTH", str(caught.exception))

    def test_rotate_lets_the_same_row_fit(self):
        contents = layout_compartments([Group(_rects(3, 30, 10, rotate=True))])
        self.assertTrue(contents(InnerSize(width=70, length=60, height=20)))

    def test_only_as_many_are_turned_as_the_fit_needs(self):
        """Turning more than necessary is churn -- it changes a layout for no reason."""
        items = _rects(3, 30, 10, rotate=True)
        turns = compartments._row_turns(items, 70, 2)
        self.assertEqual(2, sum(turns), f"expected the fewest turns that fit, got {turns}")

    def test_nothing_is_turned_when_the_row_already_fits(self):
        items = _rects(2, 20, 10, rotate=True)
        self.assertEqual([False, False], compartments._row_turns(items, 100, 2))

    def test_turning_swaps_the_cell(self):
        c = Compartment(shape=Shape.RECT, w=30, l=10)
        self.assertEqual((30, 10), c.cell())
        self.assertEqual((10, 30), c.cell(True))

    def test_a_square_cell_cannot_be_changed_by_turning(self):
        """Circles and hexes pack in a square cell, so rotation is a no-op for them and the
        packer must not waste a turn on one."""
        hexa = Compartment(shape=Shape.HEX, across=20, rotate=True)
        self.assertEqual(hexa.cell(), hexa.cell(True))
        self.assertEqual([False], compartments._row_turns([hexa], 5, 2))

    def test_turning_changes_the_band_depth_too(self):
        """A turned cell is deeper as well as narrower, and the group's band has to be
        measured on the orientation the row will really use."""
        group = Group(_rects(3, 30, 10, rotate=True))
        self.assertEqual(10, compartments._group_band_length(group, 2))        # untouched
        self.assertEqual(30, compartments._group_band_length(group, 2, 70))    # turned to fit


class PlanCacheTests(unittest.TestCase):
    """The packing result is cached on a hash of its inputs plus the version."""

    def setUp(self):
        layout_cache_clear()

    def test_the_same_input_is_packed_once(self):
        contents = layout_compartments([Group(_rects(3, 30, 20))])
        inner = InnerSize(width=100, length=80, height=20)
        contents(inner)
        contents(inner)
        self.assertEqual(1, layout_cache_info()["entries"])

    def test_a_different_interior_is_a_different_plan(self):
        contents = layout_compartments([Group(_rects(3, 30, 20))])
        contents(InnerSize(width=100, length=80, height=20))
        contents(InnerSize(width=120, length=80, height=20))
        self.assertEqual(2, layout_cache_info()["entries"])

    def test_geometry_is_rebuilt_even_on_a_cache_hit(self):
        """Only the PLAN is cached. One solid handle used by two CSG branches crashes the
        renderer, so a cached layout must never hand back the same objects twice."""
        contents = layout_compartments([Group(_rects(2, 30, 20))])
        inner = InnerSize(width=100, length=80, height=20)
        first, second = contents(inner), contents(inner)
        self.assertEqual(len(first), len(second))
        for a, b in zip(first, second):
            self.assertIsNot(a, b)

    def test_the_version_is_part_of_the_key(self):
        """A bump has to make old plans UNREACHABLE, not merely detectable."""
        contents = layout_compartments([Group(_rects(2, 30, 20))])
        inner = InnerSize(width=100, length=80, height=20)
        contents(inner)
        original = compartments.BIN_PACKING_VERSION
        try:
            compartments.BIN_PACKING_VERSION = original + 1
            contents(inner)
            self.assertEqual(2, layout_cache_info()["entries"])
        finally:
            compartments.BIN_PACKING_VERSION = original

    def test_artwork_does_not_split_the_cache(self):
        """`solid`/`label_shape`/colours are geometry: they cannot move a cell, they cannot
        be hashed, and two compartments differing only in artwork must share a plan."""
        a = layout_compartments([Group([Compartment(shape=Shape.RECT, w=30, l=20, depth=8, label="A")])])
        b = layout_compartments([Group([Compartment(shape=Shape.RECT, w=30, l=20, depth=8, label="B")])])
        inner = InnerSize(width=100, length=80, height=20)
        a(inner)
        b(inner)
        self.assertEqual(1, layout_cache_info()["entries"])

    def test_gap_and_justify_are_part_of_the_key(self):
        inner = InnerSize(width=100, length=80, height=20)
        layout_compartments([Group(_rects(2, 30, 20))], min_gap=2)(inner)
        layout_compartments([Group(_rects(2, 30, 20))], min_gap=5)(inner)
        layout_compartments([Group(_rects(2, 30, 20))], justify=Justify.START)(inner)
        self.assertEqual(3, layout_cache_info()["entries"])


class PackingStrategyTests(unittest.TestCase):
    """The four bin strategies, each doing what its name says.

    A row is the bin. The distinguishing case is 60, 50, 30 into rows of 100: after 50 fails
    to join the 60, only a strategy that CLOSES the first row refuses to put the 30 back in
    it.
    """

    WIDTHS = (60, 50, 30)

    def setUp(self):
        layout_cache_clear()

    def _rows(self, strategy):
        items = [Compartment(shape=Shape.RECT, w=w, l=10, depth=5) for w in self.WIDTHS]
        layout_compartments([Group(items, packing=strategy)], min_gap=2, margin=0)(
            InnerSize(width=100, length=80, height=20)
        )
        plan = next(iter(compartments._PLAN_CACHE.values()))
        rows: dict[int, list[float]] = {}
        for placement in plan:
            rows.setdefault(placement.row, []).append(self.WIDTHS[placement.item])
        return [rows[k] for k in sorted(rows)]

    def test_next_fit_closes_the_row_behind_it(self):
        self.assertEqual([[60], [50, 30]], self._rows(PackingBin.BNF))

    def test_first_fit_goes_back_to_an_earlier_row(self):
        self.assertEqual([[60, 30], [50]], self._rows(PackingBin.BFF))

    def test_best_fit_goes_back_to_an_earlier_row(self):
        self.assertEqual([[60, 30], [50]], self._rows(PackingBin.BBF))

    def test_global_picks_what_goes_next(self):
        """GLOBAL is the only one allowed to reorder: it takes the best-fitting compartment
        left rather than the next one given. 10 then 90 into a 100 row shows it -- the
        others keep the order and need two rows for it, GLOBAL puts the 90 first."""
        items = [Compartment(shape=Shape.RECT, w=w, l=10) for w in (10, 90)]
        ordered = compartments._assign_rows(items, 100, 2, PackingBin.GLOBAL)
        self.assertEqual([[90], [10]], [[items[i].w for i, _t in r] for r in ordered])
        for keeps_order in (PackingBin.BNF, PackingBin.BFF, PackingBin.BBF):
            rows = compartments._assign_rows(items, 100, 2, keeps_order)
            self.assertEqual([[10], [90]], [[items[i].w for i, _t in r] for r in rows],
                             f"{keeps_order} must not reorder")

    def test_wrapping_is_opt_in(self):
        """Without a strategy a row is one row, and overflowing it is still an error --
        wrapping by default would re-arrange boxes people have already printed."""
        items = [Compartment(shape=Shape.RECT, w=w, l=10, depth=5) for w in self.WIDTHS]
        with self.assertRaises(LayoutError):
            layout_compartments([Group(items)], min_gap=2, margin=0)(
                InnerSize(width=100, length=80, height=20)
            )

    def test_the_band_covers_every_wrapped_row(self):
        """Wrapping makes a group taller; if the band did not grow, the next group would be
        laid straight over it."""
        items = [Compartment(shape=Shape.RECT, w=w, l=10, depth=5) for w in self.WIDTHS]
        one_row = compartments._group_band_length(Group(items), 2, 100)
        wrapped = compartments._group_band_length(Group(items, packing=PackingBin.BNF), 2, 100)
        self.assertEqual(10, one_row)
        self.assertEqual(22, wrapped)      # two 10mm rows plus the 2mm gap

    def test_strategy_is_part_of_the_cache_key(self):
        items = [Compartment(shape=Shape.RECT, w=w, l=10, depth=5) for w in self.WIDTHS]
        inner = InnerSize(width=100, length=80, height=20)
        layout_compartments([Group(items, packing=PackingBin.BNF)], min_gap=2, margin=0)(inner)
        layout_compartments([Group(items, packing=PackingBin.BFF)], min_gap=2, margin=0)(inner)
        self.assertEqual(2, layout_cache_info()["entries"])

    def test_rotation_helps_a_wrapped_row_too(self):
        """The two features compose, but they turn for different reasons.

        A plain row turns only as many compartments as the fit needs, because its job is to
        keep an existing layout put. Under a packing strategy the job is to get as much into
        each bin as possible, so a turnable compartment takes whichever way round is
        narrower -- all three here, not just the two that would have sufficed.
        """
        items = [Compartment(shape=Shape.RECT, w=60, l=10, depth=5, rotate=True) for _ in range(3)]
        rows = compartments._assign_rows(items, 100, 2, PackingBin.BFF)
        self.assertEqual(1, len(rows), f"turned they are 10 wide and all three fit one row: {rows}")
        self.assertEqual([True, True, True], [t for _i, t in rows[0]])
        # ...against the non-wrapping row, which turns the minimum.
        self.assertEqual(2, sum(compartments._row_turns(items, 100, 2)))


class PlanShapeTests(unittest.TestCase):
    """The plan is the packing, so it can be asserted directly."""

    def setUp(self):
        layout_cache_clear()

    def test_a_cached_plan_places_every_compartment(self):
        contents = layout_compartments([Group(_rects(3, 20, 20))])
        contents(InnerSize(width=100, length=80, height=20))
        (plan,) = _plans = list(compartments._PLAN_CACHE.values())
        self.assertEqual(3, len(plan))
        self.assertTrue(all(p.width == 20 and p.length == 20 for p in plan))
        # laid out along X, in order, without overlapping
        xs = [p.x for p in plan]
        self.assertEqual(sorted(xs), xs)
        for near, far in zip(plan, plan[1:]):
            self.assertGreaterEqual(far.x, near.x + near.width)


if __name__ == "__main__":
    unittest.main()
