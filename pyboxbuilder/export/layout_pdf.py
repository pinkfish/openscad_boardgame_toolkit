# SPDX-License-Identifier: Apache-2.0
"""PDF packing guide — layered exploded breakdown with arrows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.packing.layout import BoxPacking


def generate_layout_pdf(
    packing: BoxPacking,
    output_path: Path,
    project_name: str,
    game_box_size: tuple[float, float, float],
    box_builders: list | None = None,
) -> Path | None:
    """Generate a PDF packing guide with layered step-by-step breakdown.

    Renders each layer (Base, Middle, Top) on a separate page.

    Args:
        packing: The computed packed layout.
        output_path: Path to write the PDF file (str or Path).
        project_name: Game name for the title.
        game_box_size: Outer game box dimensions (W, L, H).

    Returns:
        The output path, or None if generation failed.
    """
    output_path = Path(output_path)
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # Build a lookup map for box configurations
    box_map = {}
    if box_builders:
        box_map = {b.label: b for b in box_builders}

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
        px = x + y * cos_a * alpha
        py = -z - y * sin_a * alpha
        return px, py

    # Bounding box of projected coordinates (no headroom exploded offset since pages are separate)
    corners = [
        (0, 0, 0),
        (game_box_size[0], 0, 0),
        (0, game_box_size[1], 0),
        (game_box_size[0], game_box_size[1], 0),
        (0, 0, game_box_size[2]),
        (game_box_size[0], 0, game_box_size[2]),
        (0, game_box_size[1], game_box_size[2]),
        (game_box_size[0], game_box_size[1], game_box_size[2]),
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

    def to_pdf(x, y, z):
        px, py = project(x, y, z)
        return offset_x + px * scale, offset_y + py * scale

    # Known box colors
    colors = [
        (70, 130, 180), (220, 140, 70), (60, 160, 80),
        (200, 100, 150), (100, 160, 200), (180, 180, 60),
        (160, 100, 80), (120, 140, 160),
    ]

    def draw_box_3d(x, y, z, bw, bl, bh, color, label=None, index_str=None, visible_placements=None):
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
            
            # Determine if label is covered by other active/visible boxes on this page
            is_covered = False
            z_top = z + bh
            check_list = visible_placements or packing.placements
            for other in check_list:
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

    # Group placements dynamically by Z coordinates into 3 logical layers
    H = game_box_size[2]
    layer_defs = [
        ("Base Layer", lambda z: z < 0.1, lambda z: False),
        ("Middle Layer", lambda z: 0.1 <= z < H * 0.7, lambda z: z < 0.1),
        ("Top Layer", lambda z: z >= H * 0.7, lambda z: z < H * 0.7),
    ]

    active_pages = []
    for name, is_active, is_lower in layer_defs:
        active_p = [p for p in packing.placements if is_active(p.position[2])]
        lower_p = [p for p in packing.placements if is_lower(p.position[2])]
        active_s = [s for s in packing.spacer_placements if is_active(s.position[2])]
        lower_s = [s for s in packing.spacer_placements if is_lower(s.position[2])]
        if active_p or active_s:
            active_pages.append({
                "name": name,
                "active_placements": active_p,
                "lower_placements": lower_p,
                "active_spacers": active_s,
                "lower_spacers": lower_s,
            })

    for step_idx, page in enumerate(active_pages):
        pdf.add_page()

        # Page Header
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, f"Packing Guide: {project_name} - Step {step_idx + 1}: {page['name']}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm",
                 align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Draw Game Box Outline
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

        # 1. Draw Lower Layer Spacers (background - light gray)
        for sp in page["lower_spacers"]:
            x, y, z = sp.position
            sw, sl, sh = sp.size
            draw_box_3d(x, y, z, sw, sl, sh, (240, 240, 240))

        # 2. Draw Lower Layer Placements (background context - light gray)
        for p in page["lower_placements"]:
            x, y, z = p.position
            bw, bl, bh = p.size
            draw_box_3d(x, y, z, bw, bl, bh, (220, 220, 220))

        # 3. Draw Active Layer Spacers (full gray spacers)
        for sp in page["active_spacers"]:
            x, y, z = sp.position
            sw, sl, sh = sp.size
            draw_box_3d(x, y, z, sw, sl, sh, (200, 200, 200), "spacer")

        # 4. Draw Active Layer Placements (colored)
        # Sort placements by height Z to render bottom active ones first
        sorted_active = sorted(page["active_placements"], key=lambda p: p.position[2])
        for p in sorted_active:
            x, y, z = p.position
            bw, bl, bh = p.size
            
            # Find original index for color mapping
            orig_idx = next(i for i, orig in enumerate(packing.placements) if orig.label == p.label)
            color = colors[orig_idx % len(colors)]
            
            draw_box_3d(x, y, z, bw, bl, bh, color, p.label, str(orig_idx + 1), page["active_placements"])

        # 5. Draw 2D Blueprint inset for Box if it has compartments
        active_compartment_boxes = [p for p in page["active_placements"] if box_map.get(p.label) and box_map[p.label].compartments]
        if active_compartment_boxes:
            draw_box_blueprint(pdf, box_map[active_compartment_boxes[0].label], 230, 25, scale=0.45)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path


def draw_box_blueprint(pdf, builder, x_bp: float, y_bp: float, scale: float = 0.45) -> None:
    """Draw a detailed 2D blueprint of the box containing its compartments and shapes."""
    wt = builder.wall_thickness or 3.0
    ft = builder.floor_thickness or 1.6
    lt = builder.lid_thickness or 2.0
    
    # Outer box boundary
    pdf.set_draw_color(50, 50, 50)
    pdf.set_line_width(0.3)
    pdf.set_fill_color(248, 248, 248)
    pdf.rect(x_bp, y_bp, builder.final_size[0] * scale, builder.final_size[1] * scale, style="DF")
    
    # Interior border
    interior_w = builder.final_size[0] - 2 * wt
    interior_l = builder.final_size[1] - 2 * wt
    pdf.set_draw_color(120, 120, 120)
    pdf.set_line_width(0.15)
    pdf.rect(x_bp + wt * scale, y_bp + wt * scale, interior_w * scale, interior_l * scale, style="D")
    
    # Title
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(50, 50, 50)
    pdf.text(x_bp + 4.0 * scale, y_bp + 10.0 * scale, f"{builder.label} Layout")
    
    # Draw compartments
    from pyboxbuilder.box.interior import Interior as BoxInterior
    from pyboxbuilder.compartments.layout import layout_compartments
    
    interior = BoxInterior(
        width=interior_w,
        length=interior_l,
        height=builder.final_size[2] - lt - ft,
        origin_x=wt,
        origin_y=wt,
        origin_z=ft,
    )
    
    comp_data = []
    for cb in builder.compartments:
        resolved = cb.resolve_size(interior_w, interior_l)
        comp_data.append((
            cb.label,
            resolved[0],
            resolved[1],
            cb.depth or 10.0,
            getattr(cb, "shape_file", None),
            cb.position,
            getattr(cb, "elements", ()),
        ))
        
    no_rotate_labels = {cb.label for cb in builder.compartments if cb.no_rotate}
    comp_layout = layout_compartments(interior, comp_data, no_rotate_labels=no_rotate_labels)
    
    pdf.set_font("Helvetica", "", 5)
    for placement in comp_layout.placements:
        # Coordinates relative to the blueprint origin
        cx = x_bp + placement.position[0] * scale
        cy = y_bp + placement.position[1] * scale
        cw = placement.size[0] * scale
        ch = placement.size[1] * scale
        
        # Draw compartment border
        pdf.set_draw_color(180, 180, 180)
        pdf.rect(cx, cy, cw, ch, style="D")
        
        # Draw label
        pdf.text(cx + 1.0 * scale, cy + 4.0 * scale, placement.label)
        
        # Draw shape/SVG if present
        if placement.shape_file:
            svg_path = Path(placement.shape_file)
            if svg_path.exists():
                pdf.image(str(svg_path), cx + 1.0 * scale, cy + 5.0 * scale, w=cw - 2.0 * scale, h=ch - 6.0 * scale)

        # Draw nested elements if present
        if placement.elements:
            for elem in placement.elements:
                elem_x = cx + elem.offset[0] * scale
                elem_y = cy + elem.offset[1] * scale
                ew = (elem.size[0] if elem.size else 15.0) * scale
                eh = (elem.size[1] if elem.size else 15.0) * scale

                if not elem.shape_file:
                    # Parametric element (circle, hexagon, scoop) — outline only.
                    pdf.set_draw_color(200, 200, 200)
                    pdf.rect(elem_x, elem_y, ew, eh, style="D")
                    continue

                svg_path = Path(elem.shape_file)
                if svg_path.exists():
                    if elem.rotation != 0.0:
                        rot_cx = elem_x + ew / 2
                        rot_cy = elem_y + eh / 2
                        with pdf.rotation(elem.rotation, rot_cx, rot_cy):
                            pdf.image(str(svg_path), elem_x, elem_y, w=ew, h=eh)
                    else:
                        pdf.image(str(svg_path), elem_x, elem_y, w=ew, h=eh)


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
    if (
        pdf_path.exists()
        and hash_file.exists()
        and hash_file.read_text().strip() == current_hash
    ):
        return False

    # Record the hash now, including on the first run — otherwise the very next
    # export sees no stored hash and rebuilds an already-current PDF.
    hash_file.parent.mkdir(parents=True, exist_ok=True)
    hash_file.write_text(current_hash)
    return True
