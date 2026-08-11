import sys
sys.path[:0] = [
    "/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit/.venv/lib/python3.14/site-packages",
    "/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit/examples",
    "/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit"
]
try:
    from earth_animal_kingdom import AnimalBoxLid
    AnimalBoxLid().show()
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
