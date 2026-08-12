# SPDX-License-Identifier: Apache-2.0
"""PDF packing guide — layered exploded breakdown with arrows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spec_driven.packing.layout import BoxPacking


def generate_layout_pdf(
    packing: BoxPacking,
    output_path: Path,
    project_name: str,
    game_box_size: tuple[float, float, float],
) -> Path | None:
    """Generate a PDF packing guide with layered exploded breakdown.

    Renders each row of boxes as a separate step where boxes are displaced
    upward with arrows tracing back to their original positions.

    Args:
        packing: The computed packed layout.
        output_path: Path to write the PDF file.
        project_name: Game name for the title.
        game_box_size: Outer game box dimensions (W, L, H).

    Returns:
        The output path, or None if generation failed.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    # Page dimensions
    page_w = 297  # A4 landscape
    page_h = 210

    # Scale: fit both top-down and side-view side-by-side
    margin = 12
    gap = 10
    avail_w = page_w - 2 * margin - gap
    avail_h = page_h - 2 * margin - 20  # reserve 20mm for title

    # Total width of two boxes side-by-side is 2 * game_box_size[0]
    scale = min(avail_w / (2 * game_box_size[0]), avail_h / max(game_box_size[1], game_box_size[2]))

    # Offsets
    offset_x_top = margin
    offset_x_side = margin + game_box_size[0] * scale + gap
    offset_y = margin + 15

    # Project title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"Packing Guide: {project_name}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Scaling functions
    def to_x_top(x): return offset_x_top + x * scale
    def to_y_top(y): return offset_y + (game_box_size[1] - y) * scale
    def to_x_side(x): return offset_x_side + x * scale
    def to_z_side(z): return offset_y + (game_box_size[2] - z) * scale
    def to_d(mm): return mm * scale

    # ---- Draw Views Labels ----------------------------------------------------
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.text(offset_x_top, offset_y - 2, "Top-Down View (X-Y)")
    pdf.text(offset_x_side, offset_y - 2, "Side View / Stacking (X-Z)")

    # ---- Draw Game Box Outlines -----------------------------------------------
    pdf.set_draw_color(100, 100, 100)
    pdf.set_line_width(0.3)
    # Top-Down outline
    pdf.rect(to_x_top(0), to_y_top(game_box_size[1]), to_d(game_box_size[0]), to_d(game_box_size[1]))
    # Side outline
    pdf.rect(to_x_side(0), to_z_side(game_box_size[2]), to_d(game_box_size[0]), to_d(game_box_size[2]))

    # Known box colors
    colors = [
        (70, 130, 180), (220, 140, 70), (60, 160, 80),
        (200, 100, 150), (100, 160, 200), (180, 180, 60),
        (160, 100, 80), (120, 140, 160),
    ]

    # ---- Draw Placements (Boxes) ---------------------------------------------
    for box_idx, p in enumerate(packing.placements):
        x, y, z = p.position
        bw, bl, bh = p.size
        color = colors[box_idx % len(colors)]

        # 1. Draw in Top-Down View
        pdf.set_fill_color(*color)
        pdf.set_draw_color(40, 40, 40)
        pdf.set_line_width(0.2)
        pdf.rect(to_x_top(x), to_y_top(y + bl), to_d(bw), to_d(bl), style="DF")

        # Label inside top-down view
        pdf.set_font("Helvetica", "", 5)
        pdf.set_text_color(255, 255, 255)
        label_text = f"{p.label} ({bw:.0f}x{bl:.0f}x{bh:.0f})"
        pdf.text(to_x_top(x) + 1, to_y_top(y + bl) + to_d(bl) - 2, label_text)
        
        # Packing order number
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 7)
        pdf.text(to_x_top(x) + 1, to_y_top(y + bl) + 3, str(box_idx + 1))

        # 2. Draw in Side View (X-Z Stacking)
        pdf.set_fill_color(*color)
        pdf.set_draw_color(40, 40, 40)
        pdf.rect(to_x_side(x), to_z_side(z + bh), to_d(bw), to_d(bh), style="DF")

        # Label inside side view
        pdf.set_font("Helvetica", "", 5)
        pdf.set_text_color(255, 255, 255)
        pdf.text(to_x_side(x) + 1, to_z_side(z + bh) + to_d(bh) - 2, p.label)
        
        # Packing order number
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 7)
        pdf.text(to_x_side(x) + 1, to_z_side(z + bh) + 3, str(box_idx + 1))

    # ---- Draw Spacers --------------------------------------------------------
    for sp in packing.spacer_placements:
        x, y, z = sp.position
        sw, sl, sh = sp.size

        # Top-down spacer
        pdf.set_fill_color(220, 220, 220)
        pdf.set_draw_color(150, 150, 150)
        pdf.set_line_width(0.15)
        pdf.rect(to_x_top(x), to_y_top(y + sl), to_d(sw), to_d(sl), style="DF")
        pdf.set_font("Helvetica", "", 4)
        pdf.set_text_color(120, 120, 120)
        pdf.text(to_x_top(x) + 1, to_y_top(y + sl) + 2, "spacer")

        # Side view spacer
        pdf.set_fill_color(220, 220, 220)
        pdf.rect(to_x_side(x), to_z_side(z + sh), to_d(sw), to_d(sh), style="DF")
        pdf.text(to_x_side(x) + 1, to_z_side(z + sh) + 2, "spacer")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path


def should_regenerate_layout(
    packing: BoxPacking,
    pdf_path: Path,
    library_version: str = "1.0.0",
) -> bool:
    """Check whether the PDF needs regeneration.

    Uses SHA-256 hash of packing layout + library version.
    If the PDF doesn't exist or the hash differs, regeneration is needed.

    Args:
        packing: The current packing layout.
        pdf_path: Path to the existing PDF file.
        library_version: Version string for cache invalidation.

    Returns:
        True if PDF should be regenerated, False if existing is current.
    """
    if not pdf_path.exists():
        return True

    layout_data = {
        "placements": [
            {
                "label": p.label,
                "position": list(p.position),
                "size": list(p.size),
            }
            for p in packing.placements
        ],
        "spacers": [
            {"position": list(s.position), "size": list(s.size)}
            for s in packing.spacer_placements
        ],
        "version": library_version,
    }
    current_hash = hashlib.sha256(
        json.dumps(layout_data, sort_keys=True, default=str).encode()
    ).hexdigest()

    hash_file = pdf_path.with_suffix(".sha256")
    if hash_file.exists():
        stored_hash = hash_file.read_text().strip()
        if stored_hash == current_hash:
            return False

    hash_file.write_text(current_hash)
    return True
