# Upstream bug reports

Write-ups of defects that live in PythonSCAD itself, not in this toolkit. They are kept here
because each one shaped a design decision in the library, and that reasoning is worth having
next to the code it explains. Neither has been filed yet.

| report | what it cost us |
|---|---|
| [`pythonscad-osuse-assert-aborts.md`](pythonscad-osuse-assert-aborts.md) | A failing `assert()` inside `.scad` code reached through `osuse()`/`osinclude()` aborts the process (SIGABRT) instead of raising, and already-flushed stderr is lost with it. This is why the toolkit has **no `osuse()` calls left** — a library that cannot contain a bad argument cannot validate by trying. Repro: `tests/repro_osuse_assert_aborts.py`. |
| [`pythonscad-library-validation-numpy.md`](pythonscad-library-validation-numpy.md) | The release build's hardened runtime rejects the installed numpy, so anything importing numpy fails to load. Worked around by re-signing with the `com.apple.security.cs.disable-library-validation` entitlement. |

Related repro kept with the tests: `tests/repro_frep_reuse_segfault.py` (reusing one
frep-meshed handle across two CSG branches segfaults the app).
