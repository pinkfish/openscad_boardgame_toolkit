# Flag drawings

These are national/regional flags from **flag-icons** (https://github.com/lipis/flag-icons),
MIT licensed, taken from its `flags/4x3/` set and vendored here unmodified.

They are vendored rather than downloaded at build time on purpose: a box build must not need
the network, and a flag that silently changes upstream would change a printed part.

`flags.py` loads them with `Region.from_svg()`, which resolves each drawing's colours into
disjoint regions in SVG paint order -- so every flag comes out as one multi-colour solid
suitable for MMU, with no overlapping colour bodies.

To add a flag, drop `<iso-code>.svg` in here from the same upstream set and add an entry to
`_FLAG_CODES` in `flags.py`.
