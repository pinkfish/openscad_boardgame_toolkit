# SPDX-License-Identifier: Apache-2.0
"""Emberleaf fidelity tests — the port must match `examples/emberleaf.scad`.

The numbers asserted here are read off the original OpenSCAD file, not off the
port, so these fail if the port drifts away from the insert it is a copy of.
"""

from __future__ import annotations

import runpy
import unittest
from pathlib import Path

from pyboxbuilder.compartments.element import elements_bounding_box, elements_overlap
from pyboxbuilder.enums import BoxType, ElementShape

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE = REPO_ROOT / "boxes" / "emberleaf" / "emberleaf.py"


def load_example() -> dict:
    """Run the example module and hand back its namespace."""
    return runpy.run_path(str(EXAMPLE))


class DimensionTests(unittest.TestCase):
    """Every derived dimension matches the formula in emberleaf.scad."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()

    def test_game_box(self) -> None:
        self.assertEqual(self.mod["project"].game_box_size, (287.0, 287.0, 79.0))
        self.assertEqual(self.mod["project"].board_thickness, 26.5)

    def test_player_box(self) -> None:
        self.assertEqual(self.mod["PLAYER_BOX_WIDTH"], 98.0)
        self.assertEqual(self.mod["PLAYER_BOX_LENGTH"], 142.5)
        self.assertEqual(self.mod["PLAYER_BOX_HEIGHT"], 13.125)

    def test_material_box(self) -> None:
        self.assertEqual(self.mod["MATERIAL_BOX_WIDTH"], 98.0)
        self.assertEqual(self.mod["MATERIAL_BOX_LENGTH"], 71.25)
        self.assertEqual(self.mod["MATERIAL_BOX_HEIGHT"], 13.125)

    def test_card_box(self) -> None:
        self.assertEqual(self.mod["CARD_BOX_WIDTH"], 98.0)
        self.assertEqual(self.mod["CARD_BOX_LENGTH"], 73.0)
        self.assertEqual(self.mod["CARD_BOX_HEIGHT"], 52.5)

    def test_player_card_box(self) -> None:
        self.assertEqual(self.mod["PLAYER_CARD_BOX_WIDTH"], 90.0)
        self.assertEqual(self.mod["PLAYER_CARD_BOX_LENGTH"], 98.0)
        self.assertEqual(self.mod["PLAYER_CARD_BOX_HEIGHT"], 10.5)

    def test_common_box(self) -> None:
        self.assertEqual(self.mod["COMMON_BOX_WIDTH"], 90.0)
        self.assertEqual(self.mod["COMMON_BOX_LENGTH"], 188.0)
        self.assertEqual(self.mod["COMMON_BOX_HEIGHT"], 25.0)

    def test_spacers(self) -> None:
        self.assertEqual(self.mod["SPACER_FRONT_HEIGHT"], 26.5)
        self.assertEqual(self.mod["SPACER_SIDE_LENGTH"], 67.0)


class LayoutTests(unittest.TestCase):
    """Every box is present, at the position BoxLayout() puts it at."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_box_inventory(self) -> None:
        """5 player + 4 material + 3 card + 5 player-card + common. No spacers —
        the original's three are found by the packer, not declared."""
        self.assertEqual(len(self.boxes), 18)
        for colour in ("Black", "Red", "Yellow", "Blue", "Grey"):
            self.assertIn(f"PlayerBox{colour}", self.boxes)
            self.assertIn(f"CardBoxPlayer{colour}", self.boxes)
        for material in ("Food", "Stone", "Honey", "Wood"):
            self.assertIn(f"MaterialBox{material}", self.boxes)
        for card in ("Favor", "Hero", "Solo"):
            self.assertIn(f"CardBox{card}", self.boxes)
        self.assertIn("CommonBox", self.boxes)
        self.assertEqual([b for b in self.boxes if "Spacer" in b], [])

    def test_box_types_match_the_original_modules(self) -> None:
        self.assertEqual(self.boxes["PlayerBoxBlack"].box_type, BoxType.CAP)
        self.assertEqual(self.boxes["MaterialBoxFood"].box_type, BoxType.CAP)
        self.assertEqual(self.boxes["CommonBox"].box_type, BoxType.CAP)
        self.assertEqual(self.boxes["CardBoxFavor"].box_type, BoxType.SLIDING)
        self.assertEqual(self.boxes["CardBoxPlayerRed"].box_type, BoxType.SLIDING)

    def test_every_box_is_manually_positioned(self) -> None:
        for label, builder in self.boxes.items():
            self.assertIsNotNone(builder.position, f"{label} has no position")
            self.assertFalse(builder.expandable, f"{label} is expandable")

    def test_player_boxes_stack_in_two_columns(self) -> None:
        pbl, pbh = self.mod["PLAYER_BOX_LENGTH"], self.mod["PLAYER_BOX_HEIGHT"]
        self.assertEqual(self.boxes["PlayerBoxBlack"].position, (0.0, 0.0, 0.0))
        self.assertEqual(self.boxes["PlayerBoxRed"].position, (0.0, pbl, 0.0))
        self.assertEqual(self.boxes["PlayerBoxYellow"].position, (0.0, 0.0, pbh))
        self.assertEqual(self.boxes["PlayerBoxBlue"].position, (0.0, pbl, pbh))
        self.assertEqual(self.boxes["PlayerBoxGrey"].position, (0.0, 0.0, pbh * 2))

    def test_card_boxes_run_up_the_middle_column(self) -> None:
        pbw, cbl = self.mod["PLAYER_BOX_WIDTH"], self.mod["CARD_BOX_LENGTH"]
        self.assertEqual(self.boxes["CardBoxFavor"].position, (pbw, 0.0, 0.0))
        self.assertEqual(self.boxes["CardBoxHero"].position, (pbw, cbl, 0.0))
        self.assertEqual(self.boxes["CardBoxSolo"].position, (pbw, cbl * 2, 0.0))
        # y = cbl * 3 onwards is left empty; SpacerTests checks the packer fills it.

    def test_player_card_boxes_stack_five_high(self) -> None:
        pbw, pcbh = self.mod["PLAYER_BOX_WIDTH"], self.mod["PLAYER_CARD_BOX_HEIGHT"]
        for i, colour in enumerate(["Black", "Blue", "Yellow", "Grey", "Red"]):
            self.assertEqual(
                self.boxes[f"CardBoxPlayer{colour}"].position,
                (pbw * 2, 0.0, i * pcbh),
            )

    def test_nothing_overhangs_the_game_box(self) -> None:
        box_w, box_l, box_h = self.mod["project"].game_box_size
        for label, builder in self.boxes.items():
            x, y, z = builder.position
            w, l, h = builder.size
            self.assertLessEqual(x + w, box_w + 1e-6, f"{label} overhangs in X")
            self.assertLessEqual(y + l, box_l + 1e-6, f"{label} overhangs in Y")
            self.assertLessEqual(
                z + h, box_h - self.mod["BOARD_THICKNESS"] + 1e-6,
                f"{label} pokes into the board space",
            )

    def test_no_two_boxes_occupy_the_same_space(self) -> None:
        placed = [
            (label, b.position, b.size) for label, b in self.boxes.items()
        ]
        for i, (label_a, pos_a, size_a) in enumerate(placed):
            for label_b, pos_b, size_b in placed[i + 1:]:
                overlaps = all(
                    pos_a[axis] + 1e-6 < pos_b[axis] + size_b[axis]
                    and pos_b[axis] + 1e-6 < pos_a[axis] + size_a[axis]
                    for axis in range(3)
                )
                self.assertFalse(overlaps, f"{label_a} overlaps {label_b}")


class PlayerBoxContentsTests(unittest.TestCase):
    """The player box gives every worker type its own individual slot."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def elements(self, colour: str = "Black"):
        (compartment,) = self.boxes[f"PlayerBox{colour}"].compartments
        return compartment.elements

    def labels(self, colour: str = "Black") -> list[str]:
        return [e.label or "" for e in self.elements(colour)]

    def test_five_of_each_worker_species(self) -> None:
        labels = self.labels()
        for species in ("owl", "rabbit", "frog", "rat"):
            count = sum(1 for name in labels if name.startswith(species))
            self.assertEqual(count, 5, f"expected 5 {species} slots, got {count}")

    def test_each_worker_has_its_own_silhouette(self) -> None:
        for element in self.elements():
            if element.label and element.label.startswith(("owl", "rabbit", "frog", "rat")):
                self.assertEqual(element.shape, ElementShape.SVG)
                self.assertTrue(
                    (REPO_ROOT / element.shape_file).exists(),
                    f"missing SVG {element.shape_file}",
                )

    def test_worker_columns_do_not_run_into_each_other(self) -> None:
        """Different species occupy separate x bands, as in the original."""
        bands = {}
        for element in self.elements():
            species = (element.label or "").rsplit("_", 1)[0]
            if species not in ("owl", "rabbit", "frog", "rat"):
                continue
            x0, _, x1, _ = element.bounds()
            lo, hi = bands.get(species, (x0, x1))
            bands[species] = (min(lo, x0), max(hi, x1))

        ordered = sorted(bands.items(), key=lambda kv: kv[1][0])
        self.assertEqual([name for name, _ in ordered], ["owl", "rabbit", "frog", "rat"])
        for (name_a, (_, hi_a)), (name_b, (lo_b, _)) in zip(ordered, ordered[1:]):
            self.assertLessEqual(hi_a, lo_b, f"{name_a} column runs into {name_b}")

    def test_each_player_gets_their_own_hero(self) -> None:
        for colour in ("Black", "Red", "Yellow", "Blue", "Grey"):
            heroes = [e for e in self.elements(colour) if e.label == "hero"]
            self.assertEqual(len(heroes), 1)
            self.assertIn(colour.lower(), heroes[0].shape_file)
            self.assertTrue((REPO_ROOT / heroes[0].shape_file).exists())

    def test_grey_hero_is_the_rotated_one(self) -> None:
        """`GreyPlayerBox` is the only module that spins its hero 90 degrees."""
        rotations = {
            colour: next(e for e in self.elements(colour) if e.label == "hero").rotation
            for colour in ("Black", "Red", "Yellow", "Blue", "Grey")
        }
        self.assertEqual(rotations["Grey"], 90.0)
        self.assertEqual(set(rotations.values()) - {90.0}, {0.0})

    def test_markers_hexes_and_victory_tokens_are_all_present(self) -> None:
        labels = self.labels()
        self.assertEqual(sum(1 for name in labels if name == "marker"), 3)
        self.assertEqual(sum(1 for name in labels if name.startswith("hex_")), 2)
        self.assertEqual(sum(1 for name in labels if name.startswith("victory")), 3)
        self.assertEqual(sum(1 for name in labels if name.startswith("pull_out")), 2)

    def test_pieces_sit_at_their_own_depths(self) -> None:
        """A shallow token must not be cut to the full interior depth."""
        by_label = {e.label: e for e in self.elements()}
        interior_h = self.mod["PLAYER_INNER_H"]

        self.assertEqual(by_label["owl_0"].z_offset, 0.0)  # full-depth worker slot
        self.assertGreater(by_label["hex_left"].z_offset, by_label["hex_right"].z_offset)
        for element in self.elements():
            self.assertLess(element.z_offset, interior_h, f"{element.label} floats")
            self.assertGreaterEqual(element.z_offset, 0.0)

    def test_every_slot_stays_inside_the_interior(self) -> None:
        for colour in ("Black", "Red", "Yellow", "Blue", "Grey"):
            min_x, min_y, max_x, max_y = elements_bounding_box(self.elements(colour))
            self.assertGreaterEqual(min_x, -0.5, colour)
            self.assertGreaterEqual(min_y, -0.5, colour)
            self.assertLessEqual(max_x, self.mod["PLAYER_INNER_W"] + 0.5, colour)
            self.assertLessEqual(max_y, self.mod["PLAYER_INNER_L"] + 0.5, colour)

    def test_worker_slots_do_not_collide_with_the_hero(self) -> None:
        workers_and_hero = [
            e for e in self.elements()
            if (e.label or "").startswith(("owl", "rabbit", "frog", "rat", "hero"))
        ]
        collisions = [
            pair for pair in elements_overlap(workers_and_hero, tolerance=0.5)
            # Rabbits and rats interlock by design — the original nests them by
            # flipping every other copy.
            if not (pair[0].startswith(pair[1].rsplit("_", 1)[0]))
        ]
        self.assertEqual(collisions, [])


class CommonBoxContentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_five_hex_stacks_one_cell_left_out(self) -> None:
        """`CommonBox` lays out 2x3 hex cells and skips i==1, j==2."""
        (compartment,) = self.boxes["CommonBox"].compartments
        hexes = [e for e in compartment.elements if (e.label or "").startswith("hex_")]
        self.assertEqual(len(hexes), 5)
        self.assertNotIn("hex_1_2", [e.label for e in hexes])
        for element in hexes:
            self.assertEqual(element.shape, ElementShape.HEXAGON)
            self.assertEqual(element.rotation, 30.0)

    def test_contents_fit_the_interior(self) -> None:
        (compartment,) = self.boxes["CommonBox"].compartments
        min_x, min_y, max_x, max_y = elements_bounding_box(compartment.elements)
        self.assertGreaterEqual(min_x, 0.0)
        self.assertGreaterEqual(min_y, 0.0)
        self.assertLessEqual(max_x, self.mod["COMMON_INNER_W"])
        self.assertLessEqual(max_y, self.mod["COMMON_INNER_L"])


class SpacerTests(unittest.TestCase):
    """The original's three hand-named spacers must fall out of the packer.

    `SpacerPlayer`, `SpacerSide` and `SpacerFront` in emberleaf.scad are the
    three voids the 18 boxes leave behind. Nothing declares them here — the
    sweep finds them and the merge pass fuses the fragments (FR-014a/b).
    """

    @classmethod
    def setUpClass(cls) -> None:
        import tempfile

        import pyboxbuilder.export.layout_pdf as layout_pdf

        cls.mod = load_example()
        project = cls.mod["project"]

        captured = {}
        original = layout_pdf.should_regenerate_layout

        def spy(packing, *args, **kwargs):
            captured["packing"] = packing
            return original(packing, *args, **kwargs)

        layout_pdf.should_regenerate_layout = spy
        try:
            with tempfile.TemporaryDirectory() as tmp:
                project.export(tmp)
        finally:
            layout_pdf.should_regenerate_layout = original

        cls.spacers = sorted(
            captured["packing"].spacer_placements, key=lambda s: s.position
        )

    def test_exactly_three_spacers(self) -> None:
        """One per void — not one per grid fragment (FR-014a, SC-010a)."""
        self.assertEqual(
            len(self.spacers), 3,
            f"expected 3 spacers, got {[s.label for s in self.spacers]}",
        )

    def test_each_spacer_sits_where_the_original_puts_one(self) -> None:
        slack = self.mod["project"].clearance_slack
        # (origin, footprint) of SpacerPlayer / SpacerSide / SpacerFront, inset
        # by the clearance slack that makes the tray liftable (FR-014c).
        expected = [
            ((0.5, 143.0, 39.375), (97.0, 143.5)),
            ((98.5, 219.5, 0.0), (97.0, 67.0)),
            ((196.5, 98.5, 25.0), (90.0, 188.0)),
        ]
        for spacer, (origin, footprint) in zip(self.spacers, expected):
            for got, want in zip(spacer.position, origin):
                self.assertAlmostEqual(got, want, places=3, msg=spacer.label)
            for got, want in zip(spacer.size[:2], footprint):
                self.assertAlmostEqual(got, want, places=3, msg=spacer.label)
        self.assertGreater(slack, 0.0, "spacers need slack to be liftable")

    def test_spacers_clear_the_board_space(self) -> None:
        usable = self.mod["BOX_HEIGHT"] - self.mod["BOARD_THICKNESS"]
        for spacer in self.spacers:
            self.assertLessEqual(spacer.position[2] + spacer.size[2], usable + 1e-6)

    def test_no_spacer_is_too_thin_to_print(self) -> None:
        for spacer in self.spacers:
            self.assertGreaterEqual(min(spacer.size), 5.0, spacer.label)

    def test_no_spacer_collides_with_a_box(self) -> None:
        boxes = [(b.label, b.position, b.size) for b in self.mod["project"]._boxes]
        for spacer in self.spacers:
            for label, position, size in boxes:
                overlaps = all(
                    spacer.position[axis] + 1e-6 < position[axis] + size[axis]
                    and position[axis] + 1e-6 < spacer.position[axis] + spacer.size[axis]
                    for axis in range(3)
                )
                self.assertFalse(overlaps, f"{spacer.label} overlaps {label}")


class ExportTests(unittest.TestCase):
    def test_export_writes_a_body_per_box_and_a_lid_per_lidded_box(self) -> None:
        import tempfile

        mod = load_example()
        project = mod["project"]
        with tempfile.TemporaryDirectory() as tmp:
            result = project.export(tmp)

            root = Path(tmp) / "Emberleaf"
            self.assertTrue((root / "layout.pdf").exists())
            for builder in project._boxes:
                self.assertTrue((root / "mmu" / f"{builder.label}_body.3mf").exists())
                has_lid = builder.box_type is not BoxType.NO_LID
                self.assertEqual(
                    (root / "mmu" / f"{builder.label}_lid.3mf").exists(),
                    has_lid,
                    f"{builder.label} lid presence is wrong",
                )
            for n in (1, 2, 3):
                self.assertTrue((root / "mmu" / f"spacer_{n}_body.3mf").exists())
                self.assertFalse((root / "mmu" / f"spacer_{n}_lid.3mf").exists())
            self.assertFalse((root / "mmu" / "spacer_4_body.3mf").exists())
            self.assertEqual(len(result.skipped), 0)

    def test_re_export_rewrites_nothing(self) -> None:
        import tempfile

        mod = load_example()
        project = mod["project"]
        with tempfile.TemporaryDirectory() as tmp:
            project.export(tmp)
            project.export(tmp)  # settles the PDF hash written on the first run
            again = project.export(tmp)
            self.assertEqual(list(again.written), [])
            self.assertGreater(len(again.skipped), 0)


if __name__ == "__main__":
    unittest.main()
