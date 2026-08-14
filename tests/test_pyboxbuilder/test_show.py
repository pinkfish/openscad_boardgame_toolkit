# SPDX-License-Identifier: Apache-2.0
"""Tests for the interactive preview — `Project.show` and `pyboxbuilder.preview`.

Covers T239a/T239–T242: pieces stay separate, layer removal, stable per-box
colours, grey spacers, and lighter semi-transparent lids.
"""

import unittest
from dataclasses import dataclass

from pybosl2 import Color

from pyboxbuilder.enums import BoxType
from pyboxbuilder.preview import (
    LID_ALPHA,
    layer_heights,
    lid_color,
    lighten,
    remove_top_layers,
    spacer_color,
    stable_color,
    with_alpha,
)
from pyboxbuilder.project import Project


@dataclass(frozen=True)
class FakePlacement:
    """A placement stand-in — layer filtering only reads position and size."""

    label: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]


class StableColorTests(unittest.TestCase):
    def test_same_label_same_colour(self) -> None:
        """A box must not change colour between runs (md5, not salted hash())."""
        self.assertEqual(stable_color("AnimalBox1").rgba, stable_color("AnimalBox1").rgba)

    def test_different_labels_differ(self) -> None:
        labels = ["Cards", "Sprout", "Canopy", "AnimalBox1", "AnimalBox2", "Boards"]
        hues = {stable_color(name).hex for name in labels}
        self.assertEqual(len(hues), len(labels), "labels collided on one colour")

    def test_colour_is_saturated_not_grey(self) -> None:
        """A box hue must never be mistakable for the spacer grey."""
        for name in ("Cards", "Sprout", "MoneyBox"):
            r, g, b, _ = stable_color(name).rgba
            self.assertGreater(max(r, g, b) - min(r, g, b), 0.1, f"{name} is grey")


class SpacerColorTests(unittest.TestCase):
    def test_spacer_is_grey(self) -> None:
        for label in ("spacer_1", "spacer_2", "spacer_3"):
            r, g, b, _ = spacer_color(label).rgba
            self.assertAlmostEqual(r, g, places=6)
            self.assertAlmostEqual(g, b, places=6)

    def test_spacer_is_stable_and_opaque(self) -> None:
        self.assertEqual(spacer_color("spacer_1").rgba, spacer_color("spacer_1").rgba)
        self.assertEqual(spacer_color("spacer_1").alpha, 1.0)


class LidColorTests(unittest.TestCase):
    def test_lid_is_lighter_than_its_box(self) -> None:
        box = Color("darkgreen")
        lid = lid_color(box)
        for lit, base in zip(lid.rgba[:3], box.rgba[:3]):
            self.assertGreater(lit, base - 1e-9)
        self.assertGreater(sum(lid.rgba[:3]), sum(box.rgba[:3]))

    def test_lid_is_half_transparent(self) -> None:
        self.assertAlmostEqual(lid_color(Color("gold")).alpha, LID_ALPHA)

    def test_lighten_preserves_alpha(self) -> None:
        self.assertAlmostEqual(lighten(with_alpha(Color("red"), 0.25)).alpha, 0.25)

    def test_lighten_does_not_mutate_input(self) -> None:
        box = Color("navy")
        before = box.rgba
        lighten(box)
        self.assertEqual(box.rgba, before)


class LayerRemovalTests(unittest.TestCase):
    def placements(self) -> list[FakePlacement]:
        """Three layers: two boxes at z=0, one at z=10, one at z=20."""
        return [
            FakePlacement("base_a", (0, 0, 0), (50, 50, 10)),
            FakePlacement("base_b", (50, 0, 0), (50, 50, 10)),
            FakePlacement("mid", (0, 0, 10), (50, 50, 10)),
            FakePlacement("top", (0, 0, 20), (50, 50, 10)),
        ]

    def test_layer_heights(self) -> None:
        self.assertEqual(layer_heights(self.placements()), [0.0, 10.0, 20.0])

    def test_zero_keeps_everything(self) -> None:
        self.assertEqual(len(remove_top_layers(self.placements(), 0)), 4)

    def test_one_removes_only_the_top_layer(self) -> None:
        kept = {p.label for p in remove_top_layers(self.placements(), 1)}
        self.assertEqual(kept, {"base_a", "base_b", "mid"})

    def test_two_removes_the_top_two(self) -> None:
        kept = {p.label for p in remove_top_layers(self.placements(), 2)}
        self.assertEqual(kept, {"base_a", "base_b"})

    def test_all_layers_removed_leaves_nothing(self) -> None:
        self.assertEqual(remove_top_layers(self.placements(), 3), [])
        self.assertEqual(remove_top_layers(self.placements(), 99), [])

    def test_tall_box_spanning_the_cut_is_removed_whole(self) -> None:
        """A box is judged by its top surface, never sliced through."""
        tall = FakePlacement("tall", (0, 0, 0), (50, 50, 25))
        kept = {p.label for p in remove_top_layers(self.placements() + [tall], 1)}
        self.assertNotIn("tall", kept)
        self.assertIn("base_a", kept)

    def test_negative_count_rejected(self) -> None:
        with self.assertRaises(ValueError):
            remove_top_layers(self.placements(), -1)


class PreviewPieceTests(unittest.TestCase):
    """`show()` must produce one piece per part — never a single union."""

    def make_project(self) -> Project:
        p = Project("ShowTest", game_box_size=(200, 150, 60), generate_spacers=False)
        p.box(BoxType.SLIDING, "Cards", size=(100, 70, 30), position=(0, 0, 0))
        p.box(BoxType.CAP, "Tokens", size=(80, 70, 30), position=(100, 0, 0))
        return p

    def test_one_piece_per_box_not_one_union(self) -> None:
        pieces = self.make_project().preview_pieces()
        self.assertEqual([p.label for p in pieces], ["Cards", "Tokens"])
        self.assertEqual({p.kind for p in pieces}, {"body"})
        self.assertIsNot(pieces[0].solid, pieces[1].solid)

    def test_each_box_gets_its_own_colour(self) -> None:
        pieces = self.make_project().preview_pieces()
        self.assertNotEqual(pieces[0].color.hex, pieces[1].color.hex)

    def test_declared_colour_wins_over_the_generated_hue(self) -> None:
        p = Project("ShowTest", game_box_size=(200, 150, 60), generate_spacers=False)
        p.box(BoxType.SLIDING, "Cards", size=(100, 70, 30), position=(0, 0, 0),
              color=Color("darkgreen"))
        piece = p.preview_pieces()[0]
        self.assertEqual(piece.color.hex, Color("darkgreen").hex)

    def test_lids_hidden_by_default_and_lighter_when_shown(self) -> None:
        project = self.make_project()
        self.assertEqual({p.kind for p in project.preview_pieces()}, {"body"})

        pieces = project.preview_pieces(show_lids=True)
        lids = [p for p in pieces if p.kind == "lid"]
        self.assertTrue(lids, "show_lids=True produced no lid pieces")
        for lid in lids:
            body = next(p for p in pieces if p.kind == "body" and p.label == lid.label)
            self.assertAlmostEqual(lid.color.alpha, LID_ALPHA)
            self.assertGreater(sum(lid.color.rgba[:3]), sum(body.color.rgba[:3]))

    def test_remove_layers_drops_the_top_box(self) -> None:
        p = Project("ShowTest", game_box_size=(200, 150, 60), generate_spacers=False)
        p.box(BoxType.SLIDING, "Lower", size=(100, 70, 20), position=(0, 0, 0))
        p.box(BoxType.SLIDING, "Upper", size=(100, 70, 20), position=(0, 0, 20))
        self.assertEqual({x.label for x in p.preview_pieces()}, {"Lower", "Upper"})
        self.assertEqual({x.label for x in p.preview_pieces(remove_layers=1)}, {"Lower"})

    def test_negative_remove_layers_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.make_project().preview_pieces(remove_layers=-1)

    def test_spacers_are_previewed_in_grey(self) -> None:
        """The preview shows the filled layout, spacers included (T241)."""
        p = Project("ShowTest", game_box_size=(200, 150, 40), generate_spacers=True)
        p.box(BoxType.SLIDING, "Cards", size=(100, 70, 30), position=(0, 0, 0))
        spacers = [x for x in p.preview_pieces() if x.kind == "spacer"]
        self.assertTrue(spacers, "no spacer previewed for the leftover space")
        for piece in spacers:
            r, g, b, _ = piece.color.rgba
            self.assertAlmostEqual(r, g, places=6)
            self.assertAlmostEqual(g, b, places=6)

    def test_standalone_boxes_are_laid_out_side_by_side(self) -> None:
        p = Project("Standalone")
        p.box(BoxType.NO_LID, "HexA", size=(40, 40, 20))
        p.box(BoxType.NO_LID, "HexB", size=(40, 40, 20))
        pieces = p.preview_pieces()
        self.assertEqual([x.label for x in pieces], ["HexA", "HexB"])
        self.assertNotEqual(pieces[0].color.hex, pieces[1].color.hex)


if __name__ == "__main__":
    unittest.main()
