#!/usr/bin/python
"""Dependency-aware PythonSCAD box builder.

Discovers the @make_box / @document_box sections in examples/*.py (see base_bgtk / make_lib),
works out each example's transitive repo-local .py dependency set by static import analysis,
and builds each marked box's mmu + single 3mf (and each doc png) -- one box at a time -- only
when the output is missing or older than any of its .py dependencies. There is no pre-generated
makefile and no committed wrapper: ADDING a marked function to an example, or CHANGING any .py
it (transitively) imports, is picked up automatically on the next run; make_files.py never has
to be re-run for the .py flow.

Each 3mf is written via update_if_different.py (only overwrites when the geometry actually
changed enough), and the output's mtime is then refreshed so an unchanged rebuild doesn't keep
re-triggering.

Usage:
    build_boxes.py --all [--force] [--mmu-only|--single-only] [--jobs N]
    build_boxes.py <game> [<game> ...] [--box Name] [--force] ...
    build_boxes.py --list [--all|<game> ...]
    build_boxes.py --deps <game>            # print a game's .py dependency set
"""

import argparse
import ast
import concurrent.futures
import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = os.path.join(ROOT, "examples")


def _venv_site_packages():
    """The project venv's site-packages, where pybosl2 lives.

    The app's embedded Python does NOT see it on its own, so every generated wrapper has to put
    it on sys.path or `import base_bgtk` dies at `import pybosl2` and the render reports the
    unhelpful "Current top level object is empty". tests/render_app.py does the same thing.
    """
    hits = sorted(glob.glob(os.path.join(ROOT, ".venv", "lib", "*", "site-packages")))
    return hits[0] if hits else None


VENV_SITE = _venv_site_packages()
RELEASE = os.path.join(EXAMPLES, "release")
UPDATE_IF_DIFFERENT = os.path.join(HERE, "update_if_different.py")

sys.path.insert(0, HERE)
from make_lib import scan_py_sections  # noqa: E402

PYSCAD = os.environ.get("PYSCAD", "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD")
BOSL2_DIR = os.environ.get(
    "PYSCAD_BOSL2_DIR", os.path.expanduser("~/Documents/OpenSCAD/libraries-pythonscad-patched")
)

# Module names resolved against these roots (examples first, then the repo root for the toolkit).
_SEARCH_ROOTS = [EXAMPLES, ROOT]


# ---------------------------------------------------------------------------
# Static import dependency tracing (repo-local .py files only)
# ---------------------------------------------------------------------------

def _module_to_path(modname, roots):
    parts = modname.split(".")
    for base in roots:
        cand = os.path.join(base, *parts) + ".py"
        if os.path.isfile(cand):
            return cand
        pkg = os.path.join(base, *parts, "__init__.py")
        if os.path.isfile(pkg):
            return pkg
    return None


def _iter_imports(path):
    """Yield (module, level) for each import in `path`. level>0 is a relative import."""
    try:
        with open(path) as f:
            tree = ast.parse(f.read(), path)
    except (SyntaxError, OSError):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or ""), (node.level or 0)


def dependency_files(path, seen=None):
    """The transitive set of repo-local .py files `path` imports, including `path` itself.
    External modules (pythonscad, openscad, numpy, stdlib) resolve to nothing and are skipped."""
    if seen is None:
        seen = set()
    path = os.path.abspath(path)
    if path in seen or not os.path.isfile(path):
        return seen
    seen.add(path)
    pkgdir = os.path.dirname(path)
    for mod, level in _iter_imports(path):
        dep = None
        if level:
            base = pkgdir
            for _ in range(level - 1):
                base = os.path.dirname(base)
            if mod:
                dep = _module_to_path(mod, [base])
            else:
                init = os.path.join(base, "__init__.py")
                dep = init if os.path.isfile(init) else None
        else:
            dep = _module_to_path(mod, _SEARCH_ROOTS)
        if dep:
            dependency_files(dep, seen)
    return seen


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def example_games():
    games = []
    for f in sorted(os.listdir(EXAMPLES)):
        if not f.endswith(".py") or f == "__init__.py":
            continue
        base = f[:-3]
        with open(os.path.join(EXAMPLES, f)) as fh:
            lines = fh.read().splitlines()
        if any(True for _ in scan_py_sections(lines)):
            games.append(base)
    return games


def sections(game):
    """(make_boxes, doc_boxes) for a game, de-duplicated in declaration order."""
    with open(os.path.join(EXAMPLES, game + ".py")) as fh:
        lines = fh.read().splitlines()
    makes, docs = [], []
    for name, kind in scan_py_sections(lines):
        target = makes if kind == "make" else docs
        if name not in target:
            target.append(name)
    return makes, docs


# ---------------------------------------------------------------------------
# Building one target
# ---------------------------------------------------------------------------

def _is_stale(out, deps, force):
    if force or not os.path.exists(out) or os.path.getsize(out) == 0:
        return True
    omt = os.path.getmtime(out)
    return any(os.path.getmtime(d) > omt for d in deps)


def _last_error(stderr):
    lines = [l for l in stderr.splitlines() if l.strip()]
    cut = next((i for i, l in enumerate(lines) if l.startswith("Geometries in cache")), len(lines))
    return next((l for l in reversed(lines[:cut]) if l.strip()), "unknown error")[:200]


def _run_pyscad(game, box, out_tmp, mmu, doc):
    wrapper = (
        "import sys\n"
        f"sys.path[:0] = {[p for p in (VENV_SITE, EXAMPLES, ROOT) if p]!r}\n"
        f"from {game} import {box}\n"
        f"{box}().show()\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir=tempfile.gettempdir()) as f:
        f.write(wrapper)
        script = f.name
    env = dict(os.environ, MAKE_MMU=("1" if mmu else "0"), FROM_MAKE="1", BOSL2_SCAD_DIR=BOSL2_DIR)
    cmd = [PYSCAD, "--trust-python", "--enable", "python-engine", "--backend", "Manifold"]
    if doc:
        cmd += ["--viewall", "--autocenter", "--imgsize=1024,1024", "-o", out_tmp]
    else:
        cmd += ["--export-format", "3mf", "-o", out_tmp]
    cmd.append(script)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=EXAMPLES, timeout=1200)
    finally:
        os.unlink(script)
    return proc


def _run_pyscad_batch(game, jobs, mmu):
    """Build MANY boxes in ONE app process, exporting each to its own file.

    The per-box process model spends nearly all its wall time on fixed cost: ~0.9s of app
    startup plus ~1.8s importing numpy/pythonscad/shapely and the toolkit, against ~0.06s
    actually building a box. Importing once and looping turns a 28-job game from ~75s of
    overhead into a couple of seconds.

    Each box is exported with pythonscad's in-script ``export()`` rather than the process-wide
    ``-o``, which only ever writes one file. Every box is wrapped in its own try/except and
    prints a marker, so one failure is attributed to its own box instead of taking down the
    batch.

    Args:
        game: example module basename
        jobs: list of ``(box_name, out_tmp_path)`` to build
        mmu:  build the multi-material colour copies

    Returns:
        ``(results, proc)`` where *results* maps box name -> None on success or an error string.
    """
    lines = [
        "import sys, traceback",
        f"sys.path[:0] = {[p for p in (VENV_SITE, EXAMPLES, ROOT) if p]!r}",
        "from pythonscad import export, cube",
        f"import {game} as _game",
    ]
    for box, out_tmp in jobs:
        lines += [
            "try:",
            f"    _obj = _game.{box}()",
            "    export(_obj.shape if hasattr(_obj, 'shape') else _obj, " + repr(out_tmp) + ")",
            f"    print('##BOX_OK {box}')",
            "except Exception:",
            f"    print('##BOX_FAIL {box}')",
            "    traceback.print_exc()",
        ]
    # The app insists on a top-level object; this one goes to the throwaway -o target.
    lines.append("cube(1).show()")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir=tempfile.gettempdir()) as f:
        f.write("\n".join(lines) + "\n")
        script = f.name
    env = dict(os.environ, MAKE_MMU=("1" if mmu else "0"), FROM_MAKE="1", BOSL2_SCAD_DIR=BOSL2_DIR)
    throwaway = script + ".3mf"
    cmd = [PYSCAD, "--trust-python", "--enable", "python-engine", "--backend", "Manifold",
           "--export-format", "3mf", "-o", throwaway, script]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=EXAMPLES, timeout=3600)
    finally:
        for path in (script, throwaway):
            if os.path.exists(path):
                os.unlink(path)

    # The app routes the script's print() to STDERR, so markers are looked for in both.
    out = (proc.stdout or "") + (proc.stderr or "")
    results = {}
    for box, _ in jobs:
        if f"##BOX_OK {box}" in out:
            results[box] = None
        elif f"##BOX_FAIL {box}" in out:
            results[box] = "FAIL: " + _last_error(proc.stderr)
        else:
            # Never reached its marker: the process died partway (crash/timeout).
            results[box] = "FAIL: batch aborted before this box"
    return results, proc


def _finish_3mf(out_tmp, out, box, mmu):
    """Gate a freshly exported .tmp into place -- shared by the batched and per-box paths."""
    if not os.path.exists(out_tmp) or os.path.getsize(out_tmp) == 0:
        return "FAIL: no 3mf produced"
    upd = [sys.executable, UPDATE_IF_DIFFERENT, out_tmp, out]
    if not mmu:
        upd += ["--title", box]
    subprocess.run(upd, capture_output=True, text=True)
    if os.path.exists(out):
        os.utime(out, None)
    if os.path.exists(out_tmp):
        os.remove(out_tmp)
    return "built"


def build_batch(game, boxes, mmu, deps, force):
    """Build every STALE box for one game+mmu mode in a single process.

    Staleness is still decided per box, exactly as the unbatched path does it, so an unchanged
    example rebuilds nothing; only the stale ones go into the batch.

    Returns:
        A list of ``(box, status)`` pairs.
    """
    out_for = {}
    for box in boxes:
        out = os.path.join(RELEASE, game, "mmu" if mmu else "single", box + ("" if mmu else "_single") + ".3mf")
        out_for[box] = out
    stale = [b for b in boxes if _is_stale(out_for[b], deps, force)]
    results = [(b, "up-to-date") for b in boxes if b not in stale]
    if not stale:
        return results

    for box in stale:
        os.makedirs(os.path.dirname(out_for[box]), exist_ok=True)
    jobs = [(b, out_for[b] + ".tmp") for b in stale]
    built, _proc = _run_pyscad_batch(game, jobs, mmu)
    for box, out_tmp in jobs:
        err = built.get(box)
        results.append((box, err if err else _finish_3mf(out_tmp, out_for[box], box, mmu)))
    return results


def build_target(game, box, mmu, deps, force, doc=False):
    if doc:
        out = os.path.join(RELEASE, game, box + ".png")
    else:
        out = os.path.join(RELEASE, game, "mmu" if mmu else "single", box + ("" if mmu else "_single") + ".3mf")
    if not _is_stale(out, deps, force):
        return box, "up-to-date"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    out_tmp = out + ".tmp"
    proc = _run_pyscad(game, box, out_tmp if not doc else out, mmu, doc)
    if "Traceback" in proc.stderr:
        return box, "FAIL: " + _last_error(proc.stderr)
    if doc:
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return box, "built (png)"
        return box, "FAIL: no png produced"
    if not os.path.exists(out_tmp) or os.path.getsize(out_tmp) == 0:
        return box, "FAIL: " + (_last_error(proc.stderr) if proc.stderr.strip() else "no 3mf produced")
    # Gate: only overwrite the kept 3mf if the geometry changed enough.
    return box, _finish_3mf(out_tmp, out, box, mmu)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def build_game(game, which, force, jobs, only_box=None, batch=False):
    game_py = os.path.join(EXAMPLES, game + ".py")
    if not os.path.isfile(game_py):
        print(f"== {game}: no such example .py ==")
        return 0, 1
    deps = dependency_files(game_py)
    makes, docs = sections(game)
    if only_box is not None:
        makes = [b for b in makes if b == only_box]
        docs = [b for b in docs if b == only_box]
    jobset = []
    # In batch mode the 3mf work is grouped per mmu mode into ONE process each; only the doc
    # PNGs stay per-process, because those come from the app's image pipeline (-o file.png),
    # which writes exactly one image per invocation and has no in-script equivalent.
    batched_results = []
    if batch:
        for use_mmu in ((True,) if which == "mmu" else (False,) if which == "single" else (True, False)):
            batched_results += [
                (r, (r[0], use_mmu, False)) for r in build_batch(game, makes, use_mmu, deps, force)
            ]
    else:
        for box in makes:
            if which in ("all", "mmu"):
                jobset.append((box, True, False))
            if which in ("all", "single"):
                jobset.append((box, False, False))
    for box in docs:
        jobset.append((box, False, True))
    print(f"== {game} ({len(makes)} boxes, {len(docs)} docs; {len(deps)} .py deps) ==")
    ok = fail = 0

    def run(job):
        box, mmu, doc = job
        return build_target(game, box, mmu, deps, force, doc=doc), (box, mmu, doc)

    results = list(batched_results)
    if jobs > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
            results += list(ex.map(run, jobset))
    else:
        results += [run(j) for j in jobset]
    for (box, status), (_, mmu, doc) in results:
        tag = "png" if doc else ("mmu" if mmu else "single")
        good = not status.startswith("FAIL")
        ok += good
        fail += not good
        print(f"  {'OK  ' if good else 'FAIL'} {box} [{tag}]: {status}")
    return ok, fail


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("games", nargs="*", help="example basenames to build (default: use --all)")
    ap.add_argument("--all", action="store_true", help="build every example with marked sections")
    ap.add_argument("--force", action="store_true", help="rebuild even if up to date")
    ap.add_argument("--mmu-only", action="store_true")
    ap.add_argument("--single-only", action="store_true")
    ap.add_argument("--box", help="only build this one box (by name) within the given game(s)")
    ap.add_argument("--jobs", type=int, default=1, help="parallel renders per game (default 1: one by one)")
    ap.add_argument(
        "--batch",
        action="store_true",
        help="build all of a game's 3mf targets in ONE app process instead of one each. "
        "Startup+imports cost ~2.7s per process against ~0.06s of actual geometry, so this "
        "is worth roughly 10-20x on a whole game. Staleness is still per box: unchanged "
        "boxes are skipped, only the stale ones enter the batch. Doc PNGs stay per-process.",
    )
    ap.add_argument("--list", action="store_true", help="list the marked sections and exit")
    ap.add_argument("--deps", metavar="GAME", help="print a game's .py dependency set and exit")
    args = ap.parse_args()

    if args.deps:
        for d in sorted(dependency_files(os.path.join(EXAMPLES, args.deps + ".py"))):
            print(os.path.relpath(d, ROOT))
        return 0

    games = example_games() if args.all or not args.games else args.games
    if args.list:
        for g in games:
            makes, docs = sections(g)
            print(f"{g}: make={makes} doc={docs}")
        return 0

    which = "mmu" if args.mmu_only else ("single" if args.single_only else "all")
    total_ok = total_fail = 0
    for g in games:
        ok, fail = build_game(g, which, args.force, args.jobs, only_box=args.box, batch=args.batch)
        total_ok += ok
        total_fail += fail
    print(f"\n{total_ok} built/up-to-date, {total_fail} failed")
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
