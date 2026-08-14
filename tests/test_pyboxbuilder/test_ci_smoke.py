# SPDX-License-Identifier: Apache-2.0
"""The CI geometry pass: build every example, write nothing (FR-046a).

A CI run should not produce printable output. `export()` exists to make the
3MFs that go to a slicer, and at print precision it is minutes of tessellation
for files CI throws away. `Project.preview_pieces()` covers the same ground
that matters here — resolve the layout, pack it, build every body, lid and
spacer — without a file, a render binary, or a high facet count.

What this catches is the class of failure that only appears on real projects:
a packing that no longer fits, a box type that raises on some combination an
example uses, a compartment that overflows its interior.
"""

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BOXES = REPO_ROOT / "boxes"


def load_project(directory: Path):
    """Import an example module and hand back its `Project`.

    Args:
        directory: A directory under `boxes/` holding `<name>.py`.

    Returns:
        The module's `project`, or ``None`` if it defines none.
    """
    script = directory / f"{directory.name}.py"
    spec = importlib.util.spec_from_file_location(f"example_{directory.name}", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "project", None)


def example_directories() -> list[Path]:
    """Every example project directory, so a new one is covered on arrival."""
    return sorted(
        d for d in BOXES.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / f"{d.name}.py").exists()
    )


class ExampleBuildTests(unittest.TestCase):
    def test_there_are_examples_to_check(self) -> None:
        """A discovery bug that found nothing would make every test below pass."""
        self.assertGreaterEqual(len(example_directories()), 5)

    def test_every_example_builds_without_exporting(self) -> None:
        for directory in example_directories():
            with self.subTest(example=directory.name):
                project = load_project(directory)
                self.assertIsNotNone(project, f"{directory.name} defines no `project`")

                pieces = project.preview_pieces()
                self.assertTrue(pieces, f"{directory.name} built no geometry")
                for piece in pieces:
                    self.assertIsNotNone(
                        piece.solid, f"{directory.name}/{piece.label} built nothing"
                    )

    def test_building_writes_no_files(self) -> None:
        """The point of using the preview path in CI: no printable output."""
        before = {p for p in REPO_ROOT.rglob("*.3mf")}
        load_project(example_directories()[0]).preview_pieces()
        self.assertEqual({p for p in REPO_ROOT.rglob("*.3mf")}, before)


if __name__ == "__main__":
    unittest.main()
