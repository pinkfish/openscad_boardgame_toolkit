#!/usr/bin/python
# Shared, side-effect-free helpers for scripts/make_files.py: the ScadFile record, the
# write-if-changed helper, and the .py box/doc "section" scanner. Kept in its own module so it
# can be imported and unit-tested (tests/test_make_files.py) without running make_files.py's
# top-level generation.

import ast
import itertools
import os.path
import re


class ScadFile:
    def __init__(self, filename: str, module: str, basename: str):
        self.filename = filename
        self.module = module
        self.basename = basename


def write_if_changed(path: str, content: str) -> None:
    """Write `content` to `path` only when it differs, so make's timestamps stay stable and a
    regeneration doesn't needlessly force rebuilds of unchanged wrappers."""
    existing = ""
    if os.path.exists(path):
        with open(path, "r") as f:
            existing = f.read()
    if existing != content:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


DEF_RE = re.compile(r"^def +([A-Za-z0-9_]+)\s*\(")

# Matches @make_box(key=[LITERAL], ...) to extract variant parameter lists.
_PARAM_DECORATOR_RE = re.compile(
    r"@make_box\s*\(\s*((?:[A-Za-z_]\w*\s*=\s*\[[^\]]*\],?\s*)+)\s*\)"
)
_PARAM_PAIR_RE = re.compile(r"([A-Za-z_]\w*)\s*=\s*(\[[^\]]*\])")


def _expand_variants(name, decblob):
    """If decblob contains @make_box(key=LIST,...), yield variant (name, kind)."""
    m = _PARAM_DECORATOR_RE.search(decblob)
    if not m:
        return
    # Collect parameter lists: {key: [values]}
    param_spec: dict[str, list[str]] = {}
    for k, v in _PARAM_PAIR_RE.findall(m.group(1)):
        try:
            param_spec[k] = [str(x) for x in ast.literal_eval(v)]
        except (ValueError, SyntaxError):
            return  # can't parse -- skip expansion, the base name was already yielded
    if not param_spec:
        return
    for values in itertools.product(*param_spec.values()):
        suffix = "__".join(str(v).replace(" ", "_") for v in values)
        yield f"{name}__{suffix}", "make"


def scan_py_sections(lines):
    """Yield (name, kind) for each marked box/doc function in `lines` (a list of source lines).
    kind is 'make' or 'document'. A function is matched when a `@make_box`/`@document_box`
    decorator sits directly above its `def`, OR a `# `make` me`/`# `document` me` comment is on
    the def line or the line right after it (the form scripts/s2p.py emits). A function can be
    both (marked make and document).

    When a ``@make_box(key=[...])`` decorator contains parameter lists, variant names
    ``{function}__{value}`` are yielded in addition to the base function name."""
    for i, line in enumerate(lines):
        m = DEF_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        nextline = lines[i + 1] if i + 1 < len(lines) else ""
        # contiguous decorator lines directly above the def
        decs = []
        j = i - 1
        while j >= 0 and lines[j].lstrip().startswith("@"):
            decs.append(lines[j])
            j -= 1
        decblob = " ".join(decs)
        context = line + "\n" + nextline
        if ("make_box" in decblob) or ("`make` me" in context):
            yield name, "make"
            yield from _expand_variants(name, decblob)
        if ("document_box" in decblob) or ("`document` me" in context):
            yield name, "document"
