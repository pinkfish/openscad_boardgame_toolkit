# SPDX-License-Identifier: Apache-2.0
"""Tests for the declarative layout tree (T186)."""

from __future__ import annotations

import tempfile
import unittest

from pyboxbuilder.enums import BoxType
from pyboxbuilder.layout import (
    LayoutError,
    arrange,
    check_complete,
    columns,
    measure,
    rows,
    stack,
)
from pyboxbuilder.project import Project

SIZES = {
    "A": (10.0, 20.0, 5.0),
    "B": (10.0, 20.0, 5.0),
    "C": (30.0, 40.0, 15.0),
}


class MeasureTests(unittest.TestCase):
    def test_a_bare_label_measures_its_box(self) -> None:
        self.assertEqual(measure("A", SIZES), (10.0, 20.0, 5.0))

    def test_columns_sum_along_x(self) -> None:
        self.assertEqual(measure(columns("A", "B"), SIZES), (20.0, 20.0, 5.0))

    def test_rows_sum_along_y(self) -> None:
        self.assertEqual(measure(rows("A", "B"), SIZES), (10.0, 40.0, 5.0))

    def test_stack_sums_along_z(self) -> None:
        self.assertEqual(measure(stack("A", "B"), SIZES), (10.0, 20.0, 10.0))

    def test_the_other_axes_take_the_largest_child(self) -> None:
        self.assertEqual(measure(columns("A", "C"), SIZES), (40.0, 40.0, 15.0))

    def test_gaps_count_between_children_only(self) -> None:
        """Two children means one gap, not two."""
        self.assertEqual(measure(columns("A", "B", gap=2.0), SIZES)[0], 22.0)
        self.assertEqual(measure(columns("A", "B", "A", gap=2.0), SIZES)[0], 34.0)

    def test_an_empty_group_measures_nothing(self) -> None:
        self.assertEqual(measure(columns(), SIZES), (0.0, 0.0, 0.0))

    def test_nesting_measures_through(self) -> None:
        tree = columns(stack("A", "B"), rows("A", "B"))
        self.assertEqual(measure(tree, SIZES), (20.0, 40.0, 10.0))


class ArrangeTests(unittest.TestCase):
    def test_children_start_where_the_previous_one_ended(self) -> None:
        result = arrange(columns("A", "B"), SIZES)
        self.assertEqual(result.positions["A"], (0.0, 0.0, 0.0))
        self.assertEqual(result.positions["B"], (10.0, 0.0, 0.0))

    def test_rows_advance_along_y_and_stacks_along_z(self) -> None:
        self.assertEqual(arrange(rows("A", "B"), SIZES).positions["B"], (0.0, 20.0, 0.0))
        self.assertEqual(arrange(stack("A", "B"), SIZES).positions["B"], (0.0, 0.0, 5.0))

    def test_the_origin_shifts_everything(self) -> None:
        result = arrange(columns("A", "B"), SIZES, origin=(1.0, 2.0, 3.0))
        self.assertEqual(result.positions["A"], (1.0, 2.0, 3.0))
        self.assertEqual(result.positions["B"], (11.0, 2.0, 3.0))

    def test_a_gap_separates_adjacent_children(self) -> None:
        result = arrange(columns("A", "B", gap=1.5), SIZES)
        self.assertEqual(result.positions["B"], (11.5, 0.0, 0.0))

    def test_a_nested_group_starts_at_its_parents_cursor(self) -> None:
        """A stack ending in a pair of rows — the shape real inserts have."""
        result = arrange(stack("C", rows("A", "B")), SIZES)
        self.assertEqual(result.positions["C"], (0.0, 0.0, 0.0))
        self.assertEqual(result.positions["A"], (0.0, 0.0, 15.0))
        self.assertEqual(result.positions["B"], (0.0, 20.0, 15.0))

    def test_siblings_do_not_overlap(self) -> None:
        tree = columns(stack("A", "B"), rows("A", "B"), "C")
        sizes = {"A": (10.0, 20.0, 5.0), "B": (10.0, 20.0, 5.0), "C": (30.0, 40.0, 15.0)}
        # Distinct labels, so build a tree that uses each once.
        tree = columns(stack("A", "B"), "C")
        result = arrange(tree, sizes)
        placed = [(k, result.positions[k], sizes[k]) for k in result.positions]
        for i, (label_a, pos_a, size_a) in enumerate(placed):
            for label_b, pos_b, size_b in placed[i + 1:]:
                overlaps = all(
                    pos_a[n] + 1e-9 < pos_b[n] + size_b[n]
                    and pos_b[n] + 1e-9 < pos_a[n] + size_a[n]
                    for n in range(3)
                )
                self.assertFalse(overlaps, f"{label_a} overlaps {label_b}")

    def test_an_unknown_box_is_named_in_the_error(self) -> None:
        with self.assertRaises(LayoutError) as ctx:
            arrange(columns("A", "Nope"), SIZES)
        self.assertIn("Nope", str(ctx.exception))

    def test_placing_a_box_twice_is_rejected(self) -> None:
        with self.assertRaises(LayoutError) as ctx:
            arrange(columns("A", "A"), SIZES)
        self.assertIn("more than once", str(ctx.exception))

    def test_fits_compares_against_a_container(self) -> None:
        result = arrange(columns("A", "B"), SIZES)
        self.assertTrue(result.fits((20.0, 20.0, 5.0)))
        self.assertFalse(result.fits((19.0, 20.0, 5.0)))

    def test_check_complete_reports_boxes_the_layout_forgot(self) -> None:
        project = Project("X", game_box_size=(100, 100, 100))
        project.box(BoxType.SLIDING, "A", size=(10, 20, 5))
        project.box(BoxType.SLIDING, "B", size=(10, 20, 5))
        self.assertEqual(check_complete(columns("A"), project._boxes), ["B"])
        self.assertEqual(check_complete(columns("A", "B"), project._boxes), [])


class ProjectArrangeTests(unittest.TestCase):
    def make_project(self) -> Project:
        project = Project("Arrange", game_box_size=(100, 100, 50), clearance_slack=0.0)
        project.box(BoxType.SLIDING, "A", size=(40, 60, 20), expandable=False)
        project.box(BoxType.SLIDING, "B", size=(40, 60, 20), expandable=False)
        project.box(BoxType.SLIDING, "C", size=(30, 60, 40), expandable=False)
        return project

    def test_arrange_sets_positions_on_the_builders(self) -> None:
        project = self.make_project()
        project.arrange(columns(stack("A", "B"), "C"))
        by_label = {b.label: b for b in project._boxes}
        self.assertEqual(by_label["A"].position, (0.0, 0.0, 0.0))
        self.assertEqual(by_label["B"].position, (0.0, 0.0, 20.0))
        self.assertEqual(by_label["C"].position, (40.0, 0.0, 0.0))

    def test_an_arrangement_too_big_for_the_game_box_is_rejected(self) -> None:
        project = self.make_project()
        # 40 + 40 + 30 = 110mm across a 100mm game box.
        with self.assertRaises(LayoutError) as ctx:
            project.arrange(columns("A", "B", "C"))
        self.assertIn("does not fit", str(ctx.exception))
        self.assertIn("110.0", str(ctx.exception))

    def test_arranged_boxes_export_at_their_derived_positions(self) -> None:
        project = self.make_project()
        project.arrange(columns(stack("A", "B"), "C"))
        with tempfile.TemporaryDirectory() as tmp:
            result = project.export(tmp)
        self.assertGreater(len(result.written), 0)

    def test_the_arrangement_reports_its_extent(self) -> None:
        project = self.make_project()
        arrangement = project.arrange(columns(stack("A", "B"), "C"))
        self.assertEqual(arrangement.size, (70.0, 60.0, 40.0))


class EmberleafArrangementTests(unittest.TestCase):
    """The derived positions must equal the coordinates the original hand-types."""

    def test_emberleaf_arrangement_matches_the_original_coordinates(self) -> None:
        import runpy
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent.parent
        mod = runpy.run_path(str(root / "boxes" / "emberleaf" / "emberleaf.py"))
        boxes = {b.label: b for b in mod["project"]._boxes}

        pbw = mod["PLAYER_BOX_WIDTH"]
        pbl = mod["PLAYER_BOX_LENGTH"]
        pbh = mod["PLAYER_BOX_HEIGHT"]
        expected = {
            "PlayerBoxBlack": (0.0, 0.0, 0.0),
            "PlayerBoxRed": (0.0, pbl, 0.0),
            "PlayerBoxYellow": (0.0, 0.0, pbh),
            "PlayerBoxBlue": (0.0, pbl, pbh),
            "PlayerBoxGrey": (0.0, 0.0, pbh * 2),
            "CardBoxFavor": (pbw, 0.0, 0.0),
            "CardBoxHero": (pbw, mod["CARD_BOX_LENGTH"], 0.0),
            "CardBoxSolo": (pbw, mod["CARD_BOX_LENGTH"] * 2, 0.0),
            "CardBoxPlayerBlack": (pbw * 2, 0.0, 0.0),
            "CommonBox": (pbw * 2, mod["PLAYER_CARD_BOX_LENGTH"], 0.0),
        }
        for label, position in expected.items():
            for got, want in zip(boxes[label].position, position):
                self.assertAlmostEqual(got, want, places=6, msg=label)


if __name__ == "__main__":
    unittest.main()
