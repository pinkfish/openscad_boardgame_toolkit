# SPDX-License-Identifier: Apache-2.0
"""Tests for applying a LidBuilder to lid geometry (T161 / US9)."""

from __future__ import annotations

import os
import tempfile
import unittest

from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.enums import BoxType, LabelMode, PatternType
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.lid.decorate import decorate_lid
from pyboxbuilder.lid.label import build_label, text_height_for

SPEC = {
    "width": 100.0, "length": 70.0, "height": 30.0,
    "wall_thickness": 2.0, "floor_thickness": 2.0, "lid_thickness": 2.0,
}


def bare_lid():
    return BOX_IMPL_REGISTRY[BoxType.SLIDING]().build_lid(SPEC)


def volume(solid) -> float:
    """Mesh volume of a solid, via a round trip through the 3MF exporter."""
    import re
    import zipfile

    from openscad import export  # type: ignore[import-not-found]

    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as handle:
        path = handle.name
    try:
        export(solid.shape, path)
        model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    finally:
        os.unlink(path)

    verts = [
        (float(x), float(y), float(z))
        for x, y, z in re.findall(
            r'<vertex x="([-0-9.e+]+)" y="([-0-9.e+]+)" z="([-0-9.e+]+)"', model
        )
    ]
    total = 0.0
    for a, b, c in re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', model):
        p, q, r = verts[int(a)], verts[int(b)], verts[int(c)]
        total += (
            p[0] * (q[1] * r[2] - r[1] * q[2])
            - p[1] * (q[0] * r[2] - r[0] * q[2])
            + p[2] * (q[0] * r[1] - r[0] * q[1])
        ) / 6.0
    return abs(total)


class LabelSizingTests(unittest.TestCase):
    def test_text_fills_the_lid_minus_its_margin(self) -> None:
        """SC-014 — a label on a 100x70 lid is set well above the 4mm floor."""
        height = text_height_for(100.0, 70.0, "Cards", border_margin_mm=5.0)
        self.assertGreaterEqual(height, 4.0)
        self.assertLessEqual(height, 60.0 * 0.9)

    def test_a_long_string_is_set_smaller(self) -> None:
        short = text_height_for(100.0, 70.0, "Cat")
        long = text_height_for(100.0, 70.0, "Animal Cards Box")
        self.assertGreater(short, long)

    def test_an_illegible_label_is_skipped(self) -> None:
        """SC-015 — a single letter on a 30x20 lid produces no geometry."""
        self.assertIsNone(build_label(30.0, 20.0, 2.0, "A" * 20))

    def test_no_text_produces_no_label(self) -> None:
        self.assertIsNone(build_label(100.0, 70.0, 2.0, ""))

    def test_frameless_is_text_alone(self) -> None:
        label = build_label(100.0, 70.0, 2.0, "Cards", label_mode=LabelMode.FRAMELESS)
        assert label is not None
        self.assertIsNone(label.backing)

    def test_framed_adds_a_backing_that_hugs_the_text(self) -> None:
        """A plate the size of the whole label area would cover the pattern."""
        label = build_label(100.0, 70.0, 2.0, "Cards", label_mode=LabelMode.FRAMED)
        assert label is not None
        self.assertIsNotNone(label.backing)

        (_, _, _), (text_w, text_l, _) = label.text.bounds()
        (_, _, _), (back_w, back_l, _) = label.backing.bounds()
        self.assertGreaterEqual(back_w, text_w)
        self.assertGreaterEqual(back_l, text_l)
        # "Cards" fills the width exactly, so only the length shows the hug.
        self.assertLessEqual(back_w, 90.0, "backing must stay inside the margin")
        self.assertLess(back_l, 60.0, "backing should not fill the label area")

    def test_the_text_never_runs_past_the_margin(self) -> None:
        """Sizing is measured, not guessed — the guess put 102mm of text on a
        100mm lid."""
        for text in ("Cards", "A", "Animal Cards", "Wood"):
            label = build_label(100.0, 70.0, 2.0, text, label_mode=LabelMode.FRAMELESS)
            assert label is not None, text
            (cx, cy, _), (w, l, _) = label.text.bounds()
            self.assertLessEqual(round(w, 3), 90.0, f"{text} is too wide")
            self.assertLessEqual(round(l, 3), 60.0, f"{text} is too tall")
            self.assertAlmostEqual(cx, 50.0, places=3, msg=f"{text} off-centre")
            self.assertAlmostEqual(cy, 35.0, places=3, msg=f"{text} off-centre")


class DecorationTests(unittest.TestCase):
    def test_no_builder_leaves_the_lid_alone(self) -> None:
        lid = bare_lid()
        self.assertAlmostEqual(
            volume(decorate_lid(lid, None, 2.0).solid), volume(lid), places=3
        )

    def test_mmu_keeps_the_label_as_a_separate_insert(self) -> None:
        """The lid itself is untouched so the slicer can give the text its own
        material (T068a)."""
        lid = bare_lid()
        decorated = decorate_lid(
            lid, LidBuilder(text="Animals", label_mode=LabelMode.FRAMELESS), 2.0, "mmu"
        )
        self.assertEqual(len(decorated.inserts), 1)
        self.assertAlmostEqual(volume(decorated.solid), volume(lid), places=3)
        self.assertGreater(volume(decorated.inserts[0]), 0.0)

    def test_framed_mmu_yields_text_and_backing_separately(self) -> None:
        decorated = decorate_lid(
            bare_lid(),
            LidBuilder(text="Animals", label_mode=LabelMode.FRAMED),
            2.0, "mmu",
        )
        self.assertEqual(len(decorated.inserts), 2)

    def test_single_engraves_the_label_into_the_lid(self) -> None:
        """One material, so the text is sunk rather than raised."""
        lid = bare_lid()
        decorated = decorate_lid(
            lid, LidBuilder(text="Animals", label_mode=LabelMode.FRAMELESS),
            2.0, "single",
        )
        self.assertEqual(decorated.inserts, [])
        self.assertLess(volume(decorated.solid), volume(lid))

    def test_single_engraves_the_text_not_the_backing(self) -> None:
        """Sinking the backing plate too would cut a rectangle and lose the
        lettering with it."""
        framed = decorate_lid(
            bare_lid(), LidBuilder(text="Hi", label_mode=LabelMode.FRAMED),
            2.0, "single",
        )
        frameless = decorate_lid(
            bare_lid(), LidBuilder(text="Hi", label_mode=LabelMode.FRAMELESS),
            2.0, "single",
        )
        self.assertAlmostEqual(volume(framed.solid), volume(frameless.solid), places=3)

    def test_a_skipped_label_is_reported(self) -> None:
        decorated = decorate_lid(
            bare_lid(), LidBuilder(text="A" * 60), 2.0, "mmu"
        )
        self.assertTrue(decorated.skipped_label)
        self.assertEqual(decorated.inserts, [])

    def test_a_pattern_cuts_all_the_way_through(self) -> None:
        """A pattern that stops short of the top face leaves a skin and shows
        nothing — the lid must actually lose volume."""
        lid = bare_lid()
        decorated = decorate_lid(
            lid,
            LidBuilder(pattern=PatternBuilder(type=PatternType.HEX, spacing=9.0)),
            2.0, "mmu",
        )
        self.assertLess(volume(decorated.solid), volume(lid) * 0.95)

    def test_a_pattern_stays_clear_of_the_lid_border(self) -> None:
        lid = bare_lid()
        decorated = decorate_lid(
            lid,
            LidBuilder(
                pattern=PatternBuilder(type=PatternType.HEX, spacing=9.0),
                border_margin_mm=8.0,
            ),
            2.0, "mmu",
        )
        (bare_c, bare_s) = lid.bounds()
        (deco_c, deco_s) = decorated.solid.bounds()
        # Cutting holes inside the border must not change the lid's outline.
        for got, want in zip(deco_s, bare_s):
            self.assertAlmostEqual(got, want, places=3)

    def test_pattern_and_label_coexist(self) -> None:
        lid = bare_lid()
        decorated = decorate_lid(
            lid,
            LidBuilder(
                text="Animals",
                label_mode=LabelMode.FRAMED,
                pattern=PatternBuilder(type=PatternType.HEX, spacing=9.0),
            ),
            2.0, "mmu",
        )
        self.assertEqual(len(decorated.inserts), 2)
        self.assertLess(volume(decorated.solid), volume(lid) * 0.95)


class ExportIntegrationTests(unittest.TestCase):
    def test_a_decorated_lid_differs_between_the_two_modes(self) -> None:
        """The mmu lid keeps its face; the single lid has the label sunk in."""
        import zipfile
        from pathlib import Path

        from pyboxbuilder.project import Project

        project = Project("Deco", game_box_size=(200, 150, 60), clearance_slack=0.0)
        project.box(
            BoxType.SLIDING, "Cards", size=(100, 70, 40), expandable=False,
            position=(0.0, 0.0, 0.0),
            lid=LidBuilder(text="Cards", label_mode=LabelMode.FRAMED),
        )
        with tempfile.TemporaryDirectory() as tmp:
            project.export(tmp)
            root = Path(tmp) / "Deco"
            mmu = zipfile.ZipFile(root / "mmu" / "Cards_lid.3mf").read(
                "3D/3dmodel.model"
            )
            single = zipfile.ZipFile(root / "single" / "Cards_lid_single.3mf").read(
                "3D/3dmodel.model"
            )
        self.assertNotEqual(
            mmu.count(b"<vertex "), single.count(b"<vertex "),
            "a decorated lid should not be identical in both colour modes",
        )


if __name__ == "__main__":
    unittest.main()
