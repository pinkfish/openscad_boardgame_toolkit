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

    # Projection settings (Cabinet Oblique)
    import math
    angle_rad = math.radians(30)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    alpha = 0.45  # shortening factor for depth Y

    def project(x, y, z):
        # Cabinet Oblique: X maps right/up-right, Y (depth) maps up-right, Z maps straight up
        px = x + y * cos_a * alpha
        py = -z - y * sin_a * alpha
        return px, py

    # Headroom for exploded stacking (Z-displacement of upper boxes by 70mm)
    max_z_exploded = game_box_size[2] + 70.0

    # Bounding box of projected coordinates (including headroom) to scale to page
    corners = [
        (0, 0, 0),
        (game_box_size[0], 0, 0),
        (0, game_box_size[1], 0),
        (game_box_size[0], game_box_size[1], 0),
        (0, 0, game_box_size[2]),
        (game_box_size[0], 0, game_box_size[2]),
        (0, game_box_size[1], game_box_size[2]),
        (game_box_size[0], game_box_size[1], game_box_size[2]),
        (0, 0, max_z_exploded),
        (game_box_size[0], 0, max_z_exploded),
        (0, game_box_size[1], max_z_exploded),
        (game_box_size[0], game_box_size[1], max_z_exploded),
    ]
    projected = [project(x, y, z) for x, y, z in corners]
    min_px = min(p[0] for p in projected)
    max_px = max(p[0] for p in projected)
    min_py = min(p[1] for p in projected)
    max_py = max(p[1] for p in projected)

    proj_w = max_px - min_px
    proj_h = max_py - min_py

    margin = 15
    avail_w = page_w - 2 * margin
    avail_h = page_h - 2 * margin - 20

    scale = min(avail_w / proj_w, avail_h / proj_h)

    # Offsets to center the projection on the A4 page
    offset_x = margin + (avail_w - proj_w * scale) / 2 - min_px * scale
    offset_y = margin + 15 - min_py * scale

    # Project title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"Packing Guide: {project_name}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm  |  3D Exploded Assembly",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    def to_pdf(x, y, z):
        px, py = project(x, y, z)
        return offset_x + px * scale, offset_y + py * scale

    # Draw Game Box Outline (Z=0 bottom face, vertical corners, Z=H top face)
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(0.2)
    # Bottom face
    p_base = [to_pdf(0, 0, 0), to_pdf(game_box_size[0], 0, 0),
              to_pdf(game_box_size[0], game_box_size[1], 0), to_pdf(0, game_box_size[1], 0)]
    pdf.polygon(p_base, style="D")
    # Corners
    for cx, cy in [(0, 0), (game_box_size[0], 0), (game_box_size[0], game_box_size[1]), (0, game_box_size[1])]:
        pdf.line(*to_pdf(cx, cy, 0), *to_pdf(cx, cy, game_box_size[2]))
    # Top face
    p_top = [to_pdf(0, 0, game_box_size[2]), to_pdf(game_box_size[0], 0, game_box_size[2]),
             to_pdf(game_box_size[0], game_box_size[1], game_box_size[2]), to_pdf(0, game_box_size[1], game_box_size[2])]
    pdf.polygon(p_top, style="D")

    # Known box colors
    colors = [
        (70, 130, 180), (220, 140, 70), (60, 160, 80),
        (200, 100, 150), (100, 160, 200), (180, 180, 60),
        (160, 100, 80), (120, 140, 160),
    ]

    def draw_box_3d(x, y, z, bw, bl, bh, color, label=None, index_str=None):
        # Front face
        p_front = [to_pdf(x, y, z), to_pdf(x + bw, y, z),
                   to_pdf(x + bw, y, z + bh), to_pdf(x, y, z + bh)]
        # Right face
        p_right = [to_pdf(x + bw, y, z), to_pdf(x + bw, y + bl, z),
                   to_pdf(x + bw, y + bl, z + bh), to_pdf(x + bw, y, z + bh)]
        # Top face
        p_top = [to_pdf(x, y, z + bh), to_pdf(x + bw, y, z + bh),
                 to_pdf(x + bw, y + bl, z + bh), to_pdf(x, y + bl, z + bh)]

        # Face colors for 3D shading
        c_top = color
        c_front = tuple(max(0, int(c * 0.85)) for c in color)
        c_right = tuple(max(0, int(c * 0.70)) for c in color)

        # Top Face
        pdf.set_fill_color(*c_top)
        pdf.set_draw_color(40, 40, 40)
        pdf.set_line_width(0.15)
        pdf.polygon(p_top, style="DF")

        # Front Face
        pdf.set_fill_color(*c_front)
        pdf.polygon(p_front, style="DF")

        # Right Face
        pdf.set_fill_color(*c_right)
        pdf.polygon(p_right, style="DF")

        # Text labels
        if label:
            lbl = label[:16] + ".." if len(label) > 16 else label
            pdf.set_font("Helvetica", "B", 7.5)
            tw = pdf.get_string_width(lbl)
            th = 4.0
            
            cx, cy = to_pdf(x + bw / 2, y + bl / 2, z + bh)
            
            # Determine if label is covered by stacked/upper boxes
            is_covered = False
            z_top = z + bh
            for other in packing.placements:
                if other.label == label:
                    continue
                ox, oy, oz = other.position
                ow, ol, oh = other.size
                if oz >= z_top - 0.5 and (ox < x + bw - 1.0 and ox + ow > x + 1.0) and (oy < y + bl - 1.0 and oy + ol > y + 1.0):
                    is_covered = True
                    break
                    
            if is_covered:
                # Shift label to the side to avoid stack occlusion
                shift_dir = -1 if (x + bw/2) < game_box_size[0] / 2 else 1
                cx_shifted = cx + shift_dir * 25
                cy_shifted = cy - 5
                
                # Draw leader line
                pdf.set_draw_color(200, 50, 50)
                pdf.set_line_width(0.2)
                pdf.set_dash_pattern(dash=1, gap=1)
                pdf.line(cx, cy, cx_shifted, cy_shifted)
                pdf.set_dash_pattern(dash=0, gap=0)
                
                # Draw text badge at shifted position
                pdf.set_fill_color(255, 255, 255)
                pdf.set_draw_color(40, 40, 40)
                pdf.set_line_width(0.15)
                pdf.rect(cx_shifted - tw/2 - 1.5, cy_shifted - th/2 - 1, tw + 3, th + 2, style="DF")
                
                pdf.set_text_color(0, 0, 0)
                pdf.text(cx_shifted - tw/2, cy_shifted + th/2 - 1.0, lbl)
            else:
                # Draw text badge at centered position
                pdf.set_fill_color(255, 255, 255)
                pdf.set_draw_color(40, 40, 40)
                pdf.set_line_width(0.15)
                pdf.rect(cx - tw/2 - 1.5, cy - th/2 - 1, tw + 3, th + 2, style="DF")
                
                pdf.set_text_color(0, 0, 0)
                pdf.text(cx - tw/2, cy + th/2 - 1.0, lbl)
                
            # If present, draw index number on the badge
            if index_str:
                pdf.set_fill_color(200, 50, 50)
                pdf.set_draw_color(40, 40, 40)
                pdf.rect((cx_shifted if is_covered else cx) - tw/2 - 5.5, (cy_shifted if is_covered else cy) - th/2 - 1, 4.5, th + 2, style="DF")
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 7)
                pdf.text((cx_shifted if is_covered else cx) - tw/2 - 4.5, (cy_shifted if is_covered else cy) + th/2 - 1.0, index_str)

    # Draw Spacers
    for sp in packing.spacer_placements:
        x, y, z = sp.position
        sw, sl, sh = sp.size
        draw_box_3d(x, y, z, sw, sl, sh, (220, 220, 220), "spacer")

    # Draw Placements (ordered by height Z so bottom ones draw first, preventing overlap bugs)
    sorted_placements = sorted(enumerate(packing.placements), key=lambda x: x[1].position[2])

    for box_idx, p in sorted_placements:
        x, y, z = p.position
        bw, bl, bh = p.size
        color = colors[box_idx % len(colors)]

        # Exploded stacking: pull upper boxes (Z > 0) upwards
        z_drawn = z
        if z > 0:
            z_drawn = z + 70.0  # Explode upward by 70mm

            # Draw target placement footprint outline on the lower level
            p_slot = [to_pdf(x, y, z), to_pdf(x + bw, y, z),
                      to_pdf(x + bw, y + bl, z), to_pdf(x, y + bl, z)]
            pdf.set_draw_color(200, 50, 50)
            pdf.set_line_width(0.15)
            pdf.polygon(p_slot, style="D")

            # Draw dashed vertical trace line
            cx_slot, cy_slot = to_pdf(x + bw / 2, y + bl / 2, z)
            cx_float, cy_float = to_pdf(x + bw / 2, y + bl / 2, z_drawn)
            pdf.set_draw_color(200, 50, 50)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=2, gap=2)
            pdf.line(cx_slot, cy_slot, cx_float, cy_float)
            pdf.set_dash_pattern(dash=0, gap=0)

        # Draw the 3D shaded box
        draw_box_3d(x, y, z_drawn, bw, bl, bh, color, p.label, str(box_idx + 1))

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
