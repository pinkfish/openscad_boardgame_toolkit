# pysolidfive

A small libfive-based (F-Rep / signed-distance-function) shape library for [PythonSCAD](https://github.com/pythonscad/pythonscad).

## Install

```sh
pip install .                      # from this directory
pip install -e .                   # editable install, for local development
pip install "git+https://github.com/pinkfish/openscad_boardgame_toolkit.git#subdirectory=pysolidfive"
```

Note: `import pysolidfive` itself works with any Python, but the library's shape functions call
`libfive`/`pythonscad` (`frep()`) at runtime, which only exist inside PythonSCAD's embedded
Python interpreter -- neither is a real PyPI dependency, so they aren't installed automatically.
Run code that actually builds shapes inside PythonSCAD (or against `tests/mock_libfive.py`'s
numeric stand-in, as this project's own test suite does).

## Usage

```python
import pysolidfive

shape = pysolidfive.cuboid([20, 20, 20], rounding=4)
shape.show()
```

## Design

- Self-contained: no dependency on `bosl2` (and therefore no transitive `numpy` dependency).
  Everything it needs -- direction-vector constants, the `edges=` selector mini-language,
  anchor-offset math -- is vendored locally (`_constants.py`, `_edges.py`).
- Every shape function returns a `PyShape`: a lazy wrapper around a symbolic SDF that composes
  (translate/rotate/round/chamfer/boolean ops) without touching the real meshing engine until
  `.mesh()` is actually needed.

See the module docstring in `__init__.py` for the full design rationale and algorithm notes.

## Documentation

The built docs live in [`wiki/`](wiki/index.html) -- checked in, so they're browsable straight
from the repo. They're generated with Sphinx (autodoc + napoleon), pulling directly from the
docstrings in `__init__.py`:

```sh
pip install -e ".[docs]"
make -C docs html      # rebuilds wiki/ -- commit it along with the docstring change
open wiki/index.html
```

Any docstring with an `Examples:` section containing a `.. pythonscad-example::` block gets its
example code actually rendered with the real PythonSCAD binary and embedded as an image right
next to the code -- see `docs/_ext/pythonscad_example.py`. Set `PYTHONSCAD_BIN` to point at a
real PythonSCAD install to get the rendered images; without it, the build still succeeds, just
showing source code with no image (and a build warning per skipped example). Unchanged examples
reuse their cached image (`docs/_generated/`) without needing the binary at all.

## License

Apache-2.0
