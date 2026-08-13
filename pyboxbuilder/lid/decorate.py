# SPDX-License-Identifier: Apache-2.0
"""Apply a `LidBuilder` to a lid's geometry (T161 / US9).

Every box type produces a bare lid; this is where it gets its label, its
through-hole pattern and its colours. Doing it here rather than in each box type
means all thirteen types decorate identically, and a new type gets decoration
for free.

The decoratable face is derived from the lid's own bounding box — its top, inset
by the border margin — so no box type has to declare where its flat area is.

Colour handling differs by export mode, which is the whole reason this returns a
pair rather than one solid:

* **mmu** — the label stays a separate coloured object so the slicer can give it
  its own material.
* **single** — the label is engraved into the lid instead, because a raised
  label in one colour is invisible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pyboxbuilder.enums import LabelMode

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.lid.builder import LidBuilder

ENGRAVE_DEPTH_MM = 0.4
"""How deep a single-colour label is cut into the lid."""


@dataclass
class DecoratedLid:
    """A decorated lid, plus any parts that print in their own colour."""

    solid: "Bosl2Solid"
    inserts: list = field(default_factory=list)
    """Coloured positives, kept separate in mmu mode and fused in single mode."""

    skipped_label: bool = False
    """True when the label was dropped for being under the minimum text height."""


def decorate_lid(
    lid: "Bosl2Solid",
    builder: "LidBuilder | None",
    lid_thickness: float,
    mode: str = "mmu",
) -> DecoratedLid:
    """Apply a lid's label, pattern and colours to its geometry.

    Args:
        lid: The bare lid from a box type's `build_lid`.
        builder: The lid configuration; None leaves the lid untouched.
        lid_thickness: Thickness of the plate the decoration goes into.
        mode: "mmu" or "single".

    Returns:
        The decorated lid and its coloured inserts.
    """
    if lid is None or builder is None:
        return DecoratedLid(solid=lid)

    resolved = builder.resolve_for_mode(mode)
    face = _top_face(lid)
    if face is None:
        return DecoratedLid(solid=lid)

    width, length, origin_x, origin_y, top_z = face
    result = DecoratedLid(solid=lid)

    if resolved.pattern is not None:
        result.solid = _cut_pattern(
            result.solid, resolved, width, length,
            origin_x, origin_y, top_z, lid_thickness,
        )

    if resolved.text:
        _apply_label(
            result, resolved, width, length, origin_x, origin_y, top_z, mode,
        )

    return result


def _top_face(lid: "Bosl2Solid") -> tuple[float, float, float, float, float] | None:
    """(width, length, origin_x, origin_y, top_z) of the lid's upper surface."""
    try:
        (cx, cy, cz), (w, l, h) = lid.bounds()
    except Exception:
        return None
    if w <= 0 or l <= 0:
        return None
    return (float(w), float(l), float(cx - w / 2), float(cy - l / 2), float(cz + h / 2))


def _cut_pattern(
    lid: "Bosl2Solid",
    builder: "LidBuilder",
    width: float,
    length: float,
    origin_x: float,
    origin_y: float,
    top_z: float,
    lid_thickness: float,
) -> "Bosl2Solid":
    """Cut the through-hole pattern into the lid, clear of its border."""
    from pyboxbuilder.box.shell import block
    from pyboxbuilder.lid.pattern import build_pattern

    assert builder.pattern is not None
    margin = builder.border_margin_mm
    area_w = width - 2 * margin
    area_l = length - 2 * margin
    if area_w <= 0 or area_l <= 0:
        return lid

    # Overshoot above and below so the holes go all the way through — a pattern
    # that stops short of the top face leaves a skin and shows nothing.
    depth = lid_thickness + 2.0
    base = (origin_x + margin, origin_y + margin, top_z - lid_thickness - 1.0)

    holes = build_pattern(
        area_w, area_l, depth, builder.pattern.type, builder.pattern.spacing
    )
    # Each fill function anchors its own way, so place it by its bounding box
    # rather than trusting where it put itself, then trim it to the area so it
    # cannot eat into the lid's border.
    holes = _place_by_corner(holes, base)
    return lid - (holes & block([area_w, area_l, depth], at=base))


def _place_by_corner(solid: "Bosl2Solid", at) -> "Bosl2Solid":
    """Move a solid so its bounding box's minimum corner lands on `at`."""
    (cx, cy, cz), (w, l, h) = solid.bounds()
    return solid.translate([
        at[0] - (cx - w / 2), at[1] - (cy - l / 2), at[2] - (cz - h / 2),
    ])


def _apply_label(
    result: DecoratedLid,
    builder: "LidBuilder",
    width: float,
    length: float,
    origin_x: float,
    origin_y: float,
    top_z: float,
    mode: str,
) -> None:
    """Add the label to `result`, raised for mmu or engraved for single."""
    from pyboxbuilder.enums import LabelMode
    from pyboxbuilder.lid.label import build_label

    assert builder.text is not None
    # A frame is a colour feature: in one material there is nothing to
    # distinguish the backing plate from the lid, so a framed label degenerates
    # to engraved text. Asking for the frame anyway would also lift the text
    # clear of the face and engrave nothing at all.
    label_mode = builder.label_mode if mode != "single" else LabelMode.FRAMELESS

    label = build_label(
        width=width,
        length=length,
        thickness=0.0,
        text=builder.text,
        label_mode=label_mode,
        diagonal=builder.diagonal,
        min_text_height_mm=builder.min_text_height_mm,
        border_margin_mm=builder.border_margin_mm,
    )
    if label is None:
        result.skipped_label = True
        return

    def onto_face(solid):
        return solid.translate([origin_x, origin_y, top_z])

    if mode == "single":
        # One material, so a raised label would not read — sink the *text*
        # instead. Engraving the backing plate too would just cut a rectangular
        # recess and take the lettering with it.
        cut = onto_face(label.text).translate([0.0, 0.0, -ENGRAVE_DEPTH_MM])
        result.solid = result.solid - cut
        return

    text = onto_face(label.text)
    result.inserts.append(_coloured(text, builder.text_color))
    if label.backing is not None:
        result.inserts.append(_coloured(onto_face(label.backing), builder.frame_color))


def _coloured(solid, colour):
    """Tint a solid when a colour is set; pybosl2 wrappers carry their own."""
    if colour is None:
        return solid
    try:
        return solid.color(colour)
    except Exception:
        return solid
