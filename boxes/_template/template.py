# SPDX-License-Identifier: Apache-2.0
"""Template for new board game insert projects.

Copy this file to boxes/your_game/your_game.py and customize.
"""

from spec_driven import (
    Project, BoxType, LabelMode, Color,
    LidBuilder, PatternBuilder, PatternType, ScoopSide,
)

project = Project(
    "MyGame",
    game_box_size=(300, 200, 80),  # Your game box outer dimensions [W, L, H]
    wall_thickness=2.0,
    floor_thickness=1.6,
    lid_thickness=2.0,
    gap_threshold=10.0,
    min_spacer_dim=15.0,
)

# ── Example: Card Box ─────────────────────────────────────────────
# cards = project.box(
#     BoxType.SLIDING,
#     "Cards",
#     size=(100, 70, 50),
#     lid=LidBuilder(
#         text="Cards",
#         label_mode=LabelMode.FRAMED,
#         text_color=Color("white"),
#         frame_color=Color("gold"),
#     ),
# )
# cards.compartment("Deck", size=(90, 65), depth=45, finger_scoop=True)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = project.export("output/")
    print(f"Exported {result.total_files} files")
