# macOS release build cannot load any third-party Python C extension (numpy, scipy, …)

**Version:** v1.1.2 macOS DMG (`PythonSCAD-v1.1.2.dmg`) · macOS 15 (Darwin 24.6.0), x86_64

## Summary

The macOS app shipped in the release DMG is code-signed **without**
`com.apple.security.cs.disable-library-validation`. macOS library validation therefore refuses
to `dlopen` any third-party Python C extension, so `import numpy` fails — and with it
essentially the whole scientific Python ecosystem that makes PythonSCAD worth using.

The development build I had been using carries that entitlement, which is the only reason it
works. Adding it to the release build fixes the problem completely.

## Reproduction

```sh
# any venv with numpy installed
/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD --trust-python --enable python-engine \
    -o out.stl -  <<'PY'
import sys
sys.path.insert(0, "/path/to/.venv/lib/python3.14/site-packages")
import numpy          # ImportError
PY
```

```
ImportError: dlopen(.../numpy/_core/_multiarray_umath.cpython-314-darwin.so, 0x0002):
  tried: '...' (code signature ... not valid for use in process:
  mapped file has no cdhash, completely unsigned? Code has to be at least ad-hoc signed.)
```

Ad-hoc signing the extension (`codesign --force -s - _multiarray_umath...so`) gets past that
check and reveals the real one:

```
  ... not valid for use in process: mapping process and mapped file (non-platform)
  have different Team IDs
```

which is library validation.

## Diagnosis

```sh
$ codesign -d --entitlements - /Applications/PythonSCAD.app        # release
   (no entitlements)

$ codesign -d --entitlements - /Applications/PythonSCAD-dev.app    # dev build
   com.apple.security.cs.allow-dyld-environment-variables
   com.apple.security.cs.allow-unsigned-executable-memory
   com.apple.security.cs.disable-library-validation
```

Not a Python version mismatch: the release embeds 3.14.6, the dev build 3.14.5, and the
extension is `cpython-314` — the same ABI. The dev build is itself only ad-hoc signed with no
Team ID, so the entitlement is doing all the work.

## Verification of the fix

Re-signing the release copy with the dev build's entitlements makes it fully functional:

```sh
codesign -d --entitlements - --xml /Applications/PythonSCAD-dev.app > ent.plist
codesign --force --deep --sign - --entitlements ent.plist --options runtime \
    /Applications/PythonSCAD-1.1.2.app
```

After that, on v1.1.2: `numpy 2.5.1` imports, a numpy-based geometry library imports, and my
project's full render test suite passes **26/26 in 30.7 s** — identical to the dev build.

## Suggested fix

Add `com.apple.security.cs.disable-library-validation` to the entitlements used when signing
the macOS release (it is compatible with notarization; many Python-hosting apps ship it).
`allow-unsigned-executable-memory` is likely wanted too if any JIT/codegen path is used.

Without it, the shipped app can only run pure-Python code, which I suspect is not the
intention for a product whose selling point is Python scripting.
