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

    # Scale: fit game box into page with margins
    margin = 15
    draw_w = page_w - 2 * margin
    draw_h = page_h - 2 * margin - 20  # reserve 20mm for title
    scale = min(draw_w / game_box_size[0], draw_h / game_box_size[1])

    offset_x = margin + (draw_w - game_box_size[0] * scale) / 2
    offset_y = margin + 10

    # Project title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"Packing Guide: {project_name}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm  |  "
             f"Scale 1:{1/scale:.0f}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    def to_x(x_mm): return offset_x + x_mm * scale
    def to_y(y_mm): return offset_y + (game_box_size[1] - y_mm) * scale
    def to_d(mm): return mm * scale

    # Draw game box outline
    pdf.set_draw_color(100, 100, 100)
    pdf.set_line_width(0.3)
    pdf.rect(to_x(0), to_y(game_box_size[1]), to_d(game_box_size[0]), to_d(game_box_size[1]))

    # Group placements into rows by Y position
    rows: dict[float, list] = {}
    for p in packing.placements:
        y_key = round(p.position[1], 1)
        rows.setdefault(y_key, []).append(p)
    sorted_rows = sorted(rows.items())

    # Known box colors
    colors = [
        (70, 130, 180), (220, 140, 70), (60, 160, 80),
        (200, 100, 150), (100, 160, 200), (180, 180, 60),
        (160, 100, 80), (120, 140, 160),
    ]

    # Row displacement for exploded view
    accumulated_displace = 0.0
    prev_row_height = 0.0
    for row_idx, (y_pos, row_boxes) in enumerate(reversed(sorted_rows)):
        if row_idx > 0:
            accumulated_displace += to_d(prev_row_height) + 5  # 5mm gap between exploded rows

        displace_y = accumulated_displace

        for box_idx, p in enumerate(row_boxes):
            x, y, _ = p.position
            bw, bl, bh = p.size
            color = colors[box_idx % len(colors)]

            # Draw the displaced box
            pdf.set_fill_color(*color)
            pdf.set_draw_color(40, 40, 40)
            pdf.set_line_width(0.2)
            box_y = to_y(y + bl) + displace_y
            pdf.rect(to_x(x), box_y, to_d(bw), to_d(bl), style="DF")

            # Draw arrow from displaced position back to original
            if displace_y != 0:
                arrow_start_y = box_y + to_d(bl) / 2
                arrow_end_y = to_y(y + bl) + to_d(bl) / 2
                arrow_x = to_x(x) + to_d(bw) / 2

                pdf.set_draw_color(200, 50, 50)
                pdf.set_line_width(0.3)
                # Dashed line from displaced to original
                pdf.set_dash_pattern(dash=2, gap=2)
                pdf.line(arrow_x, arrow_start_y, arrow_x, arrow_end_y)
                pdf.set_dash_pattern(dash=0, gap=0)
                # Arrow head pointing back (upward on page)
                head_size = 2
                pdf.line(arrow_x, arrow_end_y, arrow_x - head_size, arrow_end_y + head_size * 1.5)
                pdf.line(arrow_x, arrow_end_y, arrow_x + head_size, arrow_end_y + head_size * 1.5)

            # Box label + dimensions
            pdf.set_font("Helvetica", "", 6)
            pdf.set_text_color(255, 255, 255)
            label_text = f"{p.label}  {bw:.0f}x{bl:.0f}x{bh:.0f}"
            text_x = to_x(x) + 1
            text_y = box_y + to_d(bl) - 3
            pdf.text(text_x, text_y, label_text)

            # Packing order number
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 8)
            pdf.text(to_x(x) + 1, box_y + 3, str(box_idx + 1))

        prev_row_height = max(p.size[1] for p in row_boxes)

    # Draw spacers
    for sp in packing.spacer_placements:
        x, y, _ = sp.position
        sw, sl, _ = sp.size
        pdf.set_fill_color(200, 200, 200)
        pdf.set_draw_color(150, 150, 150)
        pdf.set_line_width(0.15)
        pdf.rect(to_x(x), to_y(y + sl), to_d(sw), to_d(sl), style="DF")
        pdf.set_font("Helvetica", "", 5)
        pdf.set_text_color(100, 100, 100)
        pdf.text(to_x(x) + 1, to_y(y + sl) + 3, "spacer")

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
