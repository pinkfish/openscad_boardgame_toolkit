# PythonSCAD for VS Code

Compile-checks `.scad` files and PythonSCAD `.py` files by invoking the PythonSCAD
engine directly (headless CLI), and surfaces the results as inline VS Code
diagnostics — the same errors you would see in the PythonSCAD GUI console.

## Features

- **Check on save** (default on) and optional debounced **check while typing**
  for `.scad` files and `.py` files that import the `openscad` module.
- **Inline diagnostics**: OpenSCAD `ERROR:`/`WARNING:` messages and Python
  tracebacks (SyntaxError, NameError, TypeError, ...) are mapped to the correct
  line in the editor.
- **Export command**: render the current file to stl / 3mf / png / svg / etc.
  via `PythonSCAD: Export Current File...`.
- **Status bar** item showing which PythonSCAD binary is in use; click to change.
- Checks the **unsaved buffer** — a dirty editor is materialized to a hidden
  temp file next to the original so relative `include`/`use`/imports still resolve.

## Requirements

- [PythonSCAD](https://pythonscad.org) installed. On macOS the extension
  auto-detects `/Applications/PythonSCAD.app`; otherwise set
  `pythonscad.executablePath` or run `PythonSCAD: Select Executable...`.

## Security: executing Python

Checking a PythonSCAD `.py` file means **running it** (the engine passes
`--trust-python`). Untrusted code could do anything your user account can do.
By default the extension only does this when the VS Code workspace is trusted
(`pythonscad.trustPythonExecution: "workspaceTrust"`). Set it to `"never"` to
restrict checking to `.scad` files, or `"always"` at your own risk. Plain
`.scad` files are always safe to check.

## Settings

| Setting | Default | Description |
| --- | --- | --- |
| `pythonscad.executablePath` | auto-detect | Path to the PythonSCAD binary or `.app` bundle |
| `pythonscad.checkOnSave` | `true` | Check when a file is saved |
| `pythonscad.checkOnType` | `false` | Check while typing (debounced) |
| `pythonscad.checkOnTypeDelay` | `1000` | Debounce in ms for check-on-type |
| `pythonscad.checkExportFormat` | `ast` | Throwaway export format used to drive the check |
| `pythonscad.backend` | `Manifold` | Geometry backend (`Manifold` or `CGAL`) |
| `pythonscad.trustPythonExecution` | `workspaceTrust` | When `.py` execution is allowed |
| `pythonscad.pythonFileHeuristic` | `true` | Only check `.py` files that import `openscad` |
| `pythonscad.extraArgs` | `[]` | Extra CLI args (e.g. `["--hardwarnings"]`) |

## How the check works

The extension runs, e.g.:

```
PythonSCAD -o /tmp/<random>.ast --export-format ast --backend Manifold --trust-python yourfile.py
```

The `ast` export is the cheapest way to force a full parse/evaluate without a
geometry render. Output such as

```
ERROR: Parser error: syntax error in file box.scad, line 3
  File "<string>", line 12, in <module>
TypeError: Center code must be exactly 3 characters
```

is parsed into diagnostics. Note PythonSCAD evaluates `.py` sources as an
in-memory string, so traceback frames show `File "<string>"` — the line numbers
still map to your file and the extension uses them directly.

## Building / installing from source

```bash
cd pythonscad_extension
npm install
npm run compile
```

Then either:

- Open the folder in VS Code and press `F5` (Run Extension) to test, or
- Package it: `npx @vscode/vsce package` and install the resulting `.vsix`
  via *Extensions: Install from VSIX...*.
