import sys
sys.path.insert(0, '/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit')
from cap_box import MakeBoxWithCapLid
shape = MakeBoxWithCapLid([80, 60, 20])
shape.show()
