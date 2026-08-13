# SPDX-License-Identifier: Apache-2.0
"""Earth Animal Kingdom fidelity tests.

The numbers here are read off `examples/earth_animal_kingdom.scad` and
`lib/animal_kingdom_items*.scad`, not off the port, so these fail if the port
drifts from the insert it copies.
"""

from __future__ import annotations

import runpy
import unittest
from pathlib import Path

from pyboxbuilder.enums import BoxType

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE = REPO_ROOT / "boxes" / "earth_animal_kingdom" / "earth_animal_kingdom.py"


def load_example() -> dict:
    return runpy.run_path(str(EXAMPLE))


class DimensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()

    def test_game_box(self) -> None:
        self.assertEqual(self.mod["project"].game_box_size, (288.0, 158.0, 47.0))

    def test_card_box(self) -> None:
        """card_box_width = wall*2 + card width; height = 36 cards + 2."""
        self.assertEqual(self.mod["CARD_BOX_WIDTH"], 76.0)
        self.assertEqual(self.mod["CARD_BOX_LENGTH"], 156.0)
        self.assertAlmostEqual(self.mod["CARD_BOX_HEIGHT"], 23.6)

    def test_sprout_box(self) -> None:
        self.assertEqual(self.mod["SPROUT_BOX_WIDTH"], 76.0)
        self.assertEqual(self.mod["SPROUT_BOX_LENGTH"], 158.0)
        self.assertAlmostEqual(self.mod["SPROUT_BOX_HEIGHT"], 22.4)

    def test_canopy_box(self) -> None:
        self.assertEqual(self.mod["CANOPY_BOX_WIDTH"], 38.0)
        self.assertEqual(self.mod["CANOPY_BOX_LENGTH"], 158.0)
        self.assertEqual(self.mod["CANOPY_BOX_HEIGHT"], 46.0)

    def test_animal_box(self) -> None:
        """animal_box_width = box - card box - canopy box; height = 8mm token + skins."""
        self.assertEqual(self.mod["ANIMAL_BOX_WIDTH"], 174.0)
        self.assertEqual(self.mod["ANIMAL_BOX_LENGTH"], 158.0)
        self.assertEqual(self.mod["ANIMAL_BOX_HEIGHT"], 12.5)
        self.assertEqual(self.mod["ANIMAL_WALL"], 1.5)

    def test_spacer_box(self) -> None:
        self.assertEqual(self.mod["SPACER_BOX_WIDTH"], 174.0)
        self.assertEqual(self.mod["SPACER_BOX_LENGTH"], 158.0)
        self.assertEqual(self.mod["SPACER_BOX_HEIGHT"], 21.0)

    def test_columns_fill_the_game_box_width(self) -> None:
        total = (
            self.mod["CARD_BOX_WIDTH"]
            + self.mod["ANIMAL_BOX_WIDTH"]
            + self.mod["CANOPY_BOX_WIDTH"]
        )
        self.assertEqual(total, self.mod["BOX_WIDTH"])


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_box_inventory(self) -> None:
        self.assertEqual(
            set(self.boxes),
            {"AnimalCardsBox", "SproutBox", "CanopyBox",
             "AnimalBox1", "AnimalBox2", "SpacerBox"},
        )

    def test_box_types_match_the_original_modules(self) -> None:
        self.assertEqual(self.boxes["AnimalCardsBox"].box_type, BoxType.SLIDING)
        self.assertEqual(self.boxes["SproutBox"].box_type, BoxType.FILAMENT_HINGE)
        self.assertEqual(self.boxes["CanopyBox"].box_type, BoxType.FILAMENT_HINGE)
        self.assertEqual(self.boxes["AnimalBox1"].box_type, BoxType.SLIPOVER)
        self.assertEqual(self.boxes["AnimalBox2"].box_type, BoxType.SLIPOVER)
        self.assertEqual(self.boxes["SpacerBox"].box_type, BoxType.NO_LID)

    def test_positions_match_box_layout(self) -> None:
        cbw = self.mod["CARD_BOX_WIDTH"]
        abh = self.mod["ANIMAL_BOX_HEIGHT"]
        self.assertEqual(self.boxes["AnimalCardsBox"].position, (0.0, 0.0, 0.0))
        self.assertEqual(
            self.boxes["SproutBox"].position, (0.0, 0.0, self.mod["CARD_BOX_HEIGHT"])
        )
        self.assertEqual(self.boxes["AnimalBox1"].position, (cbw, 0.0, 0.0))
        self.assertEqual(self.boxes["AnimalBox2"].position, (cbw, 0.0, abh))
        self.assertEqual(self.boxes["SpacerBox"].position, (cbw, 0.0, abh * 2))
        self.assertEqual(
            self.boxes["CanopyBox"].position,
            (cbw + self.mod["ANIMAL_BOX_WIDTH"], 0.0, 0.0),
        )

    def test_animal_boxes_use_the_thin_wall_and_a_foot(self) -> None:
        for label in ("AnimalBox1", "AnimalBox2"):
            self.assertEqual(self.boxes[label].wall_thickness, 1.5)
            self.assertEqual(self.boxes[label].foot, 4.0)

    def test_nothing_overhangs_the_game_box(self) -> None:
        box_w, box_l, box_h = self.mod["project"].game_box_size
        for label, builder in self.boxes.items():
            x, y, z = builder.position
            w, l, h = builder.size
            self.assertLessEqual(x + w, box_w + 1e-6, label)
            self.assertLessEqual(y + l, box_l + 1e-6, label)
            self.assertLessEqual(z + h, box_h + 1e-6, label)

    def test_no_two_boxes_overlap(self) -> None:
        placed = [(k, b.position, b.size) for k, b in self.boxes.items()]
        for i, (label_a, pos_a, size_a) in enumerate(placed):
            for label_b, pos_b, size_b in placed[i + 1:]:
                overlaps = all(
                    pos_a[n] + 1e-6 < pos_b[n] + size_b[n]
                    and pos_b[n] + 1e-6 < pos_a[n] + size_a[n]
                    for n in range(3)
                )
                self.assertFalse(overlaps, f"{label_a} overlaps {label_b}")


class AnimalLayoutTests(unittest.TestCase):
    """The precomputed partition from lib/animal_kingdom_items_layout.scad."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_slot_counts_match_the_two_containers(self) -> None:
        self.assertEqual(len(self.mod["ANIMAL_LAYOUT_1"]), 26)
        self.assertEqual(len(self.mod["ANIMAL_LAYOUT_2"]), 30)

    def test_every_animal_is_stored_exactly_once(self) -> None:
        """37 animals, some in multiples: 26 + 30 = 56 slots in total."""
        slots = list(self.mod["ANIMAL_LAYOUT_1"]) + list(self.mod["ANIMAL_LAYOUT_2"])
        species = {name.rsplit("_", 1)[0] if name[-1].isdigit() else name
                   for name, *_ in slots}
        self.assertEqual(len(slots), 56)
        # capybara_2 is its own species in the original, not a second capybara.
        self.assertIn("capybara", species)
        self.assertIn("capybara_2", species)
        self.assertEqual(len(species), 37)

    def test_multi_token_animals_get_one_slot_each(self) -> None:
        counts: dict[str, int] = {}
        for name, *_ in list(self.mod["ANIMAL_LAYOUT_1"]) + list(self.mod["ANIMAL_LAYOUT_2"]):
            key = name.rsplit("_", 1)[0] if name[-1].isdigit() else name
            counts[key] = counts.get(key, 0) + 1
        # num= values from lib/animal_kingdom_items.scad
        self.assertEqual(counts["turkey"], 5)
        self.assertEqual(counts["pangolin"], 5)
        self.assertEqual(counts["termite"], 5)
        self.assertEqual(counts["gopher"], 5)
        self.assertEqual(counts["capybara"], 2)
        self.assertEqual(counts["capybara_2"], 3)
        self.assertEqual(counts["elephant"], 1)

    def test_every_slot_fits_the_animal_box_interior(self) -> None:
        inner_w = self.mod["ANIMAL_INNER_W"]
        inner_l = self.mod["ANIMAL_INNER_L"]
        for layout in ("ANIMAL_LAYOUT_1", "ANIMAL_LAYOUT_2"):
            for name, x, y, w, l in self.mod[layout]:
                self.assertGreaterEqual(x, 0.0, f"{name} x")
                self.assertGreaterEqual(y, 0.0, f"{name} y")
                self.assertLessEqual(x + w, inner_w, f"{name} runs past the right wall")
                self.assertLessEqual(y + l, inner_l, f"{name} runs past the back wall")

    def test_no_two_slots_overlap(self) -> None:
        for layout in ("ANIMAL_LAYOUT_1", "ANIMAL_LAYOUT_2"):
            slots = self.mod[layout]
            for i, (name_a, ax, ay, aw, al) in enumerate(slots):
                for name_b, bx, by, bw, bl in slots[i + 1:]:
                    overlaps = (
                        ax + 1e-6 < bx + bw and bx + 1e-6 < ax + aw
                        and ay + 1e-6 < by + bl and by + 1e-6 < ay + al
                    )
                    self.assertFalse(overlaps, f"{name_a} overlaps {name_b} in {layout}")

    def test_each_animal_box_carries_its_slots_plus_the_access_pan(self) -> None:
        for label, layout in (("AnimalBox1", "ANIMAL_LAYOUT_1"),
                              ("AnimalBox2", "ANIMAL_LAYOUT_2")):
            compartments = self.boxes[label].compartments
            self.assertEqual(len(compartments), len(self.mod[layout]) + 1)
            self.assertEqual(compartments[0].label, "Access")
            self.assertEqual(compartments[0].depth, 4.0)  # token thickness / 2
            for comp in compartments[1:]:
                self.assertEqual(comp.depth, 8.5)  # token thickness + 0.5
                self.assertIsNotNone(comp.position)


class ExportTests(unittest.TestCase):
    def test_export_writes_a_body_per_box_and_a_lid_per_lidded_box(self) -> None:
        import tempfile

        mod = load_example()
        project = mod["project"]
        with tempfile.TemporaryDirectory() as tmp:
            project.export(tmp)
            root = Path(tmp) / "EarthAnimalKingdom"
            for builder in project._boxes:
                self.assertTrue((root / "mmu" / f"{builder.label}_body.3mf").exists())
                self.assertEqual(
                    (root / "mmu" / f"{builder.label}_lid.3mf").exists(),
                    builder.box_type is not BoxType.NO_LID,
                    builder.label,
                )
            # No auto spacers: the original's SpacerBox is declared, and the
            # hand-placed boxes leave nothing else over.
            self.assertFalse((root / "mmu" / "spacer_1_body.3mf").exists())


if __name__ == "__main__":
    unittest.main()
