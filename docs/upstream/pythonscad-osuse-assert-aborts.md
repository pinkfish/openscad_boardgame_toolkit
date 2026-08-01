# A failing `assert()` in `.scad` code loaded via `osuse()`/`osinclude()` aborts the process

**Version:** v1.1.2 (also v1.0.0) · macOS 15 (Darwin 24.6.0), x86_64 · embedded Python 3.14.6

## Summary

When a `.scad` function reached through `osuse()` or `osinclude()` hits a failing `assert()`,
the assertion surfaces as an **uncaught C++ exception** and terminates the whole process with
SIGABRT (exit −6):

```
libc++abi: terminating due to uncaught exception of type AssertionFailedException: Assertion Failed
```

Python never sees it. `try: ... except Exception:` does not contain it, and no code after the
call runs. I would expect a catchable Python exception instead.

## Reproduction

No library needed — the entire `.scad` side is one line.

`boom.scad`:
```scad
function boom(n) = assert(n >= 3, "n must be >= 3") n;
```

`repro.py`:
```python
from pythonscad import cube, osuse

m = osuse("boom.scad")
print(m.boom(5))        # -> 5.0, fine

try:
    m.boom(2)           # assert fails
except Exception as exc:
    print("caught:", exc)   # never reached — the process is already gone

cube(1).show()
```

```sh
PythonSCAD --trust-python --enable python-engine -o out.png --render=true repro.py
echo $?     # 134 (SIGABRT)
```

## What is and is not affected

| case | result |
|---|---|
| `m.boom(5)` — valid argument, same handle | ok, exit 0 |
| `m.no_such_function()` — a **Python**-level error via the same handle | raises `AttributeError`, exit 0 |
| degenerate **native** calls (see below) | all build or raise a clean `TypeError` |
| `m.boom(2)` via `osuse()` | **SIGABRT** |
| `m.boom(2)` via `osinclude()` | **SIGABRT** |

So this is not "bad input crashes the app" in general. The native API is robust — I tried 16
deliberately degenerate calls, none of which crash: `polygon([])`, `polygon([[0,0]])`,
`polygon(pts, paths=[[0,1,9]])` (out-of-range index), `cube([0,0,0])`, `circle(r=-1)`,
`square([0,0])`, `linear_extrude(height=0)`, `square([10,10]).offset(r=-50)` (annihilates the
shape), `scale([0,0,0])`, `resize([0,0,0])`, `fill()` on a 3-D solid, `projection()` on a 2-D
one, `polyhedron` with a bad face index, `minkowski(cube(1), polygon([]))`, `text('')`.

It is specifically the `.scad` assert path, and it is not specific to `osuse()` —
`osinclude()` does it too.

## Secondary problem: diagnostic output is lost

Anything written to stderr **and flushed** before the aborting call never reaches the parent
process:

```python
import sys
sys.stderr.write("about to call boom(2)\n")
sys.stderr.flush()
m.boom(2)                      # abort — the line above is never seen
```

A crashed run therefore looks like it produced no output at all, so you cannot print your way
to the offending call. Writing to a *file* survives, which is the only workaround I found.
This turns a one-line bug into a bisect.

## Why it matters in practice

Any library that calls into `.scad` code cannot validate by trying: one bad argument deep in a
helper kills the whole job with no diagnosis and no chance to recover. In my case a
tessellation library passed a degenerate outline to BOSL2's `difference()`, which asserts
"one of the inputs is not a region" — two shape types became unbuildable and no amount of
Python error handling could contain it. I had to remove the `osuse()` calls entirely.

## Suggested fix

Catch `AssertionFailedException` (and siblings) at the FFI boundary and raise it as a Python
exception carrying the assertion message and the `.scad` file/line, the way a Python-level
failure through the same handle is already handled correctly.

## Attached

A self-contained, dual-mode repro script that drives all six cases as subprocesses and prints
a pass/crash table (`tests/repro_osuse_assert_aborts.py`).
