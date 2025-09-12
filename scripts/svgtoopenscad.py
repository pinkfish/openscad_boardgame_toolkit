#!/bin/python

from svgelements import *
import logging

logging.basicConfig(level=logging.DEBUG)


class OpenScadOutput():

    def __init__(self, fname):
      self.svg = SVG.parse(fname)

    def PrintElement(self, element):
        if isinstance(element, Group):
            self.PrintGroup(element)
        elif isinstance(element, Path):
            self.PrintPath(element)
        elif isinstance(element, Polygon):
            self.PrintPolygon(element)

    def PrintGroup(self, group):
        print("// group {0}".format(group.id))
        for element in group:
            if isinstance(element, Path):
               self.PrintPath(element)
            if isinstance(element, Polygon):
               self.PrintPolygon(element)
            else:
               print("unknown element {0}".format(element))
               
    def PrintPath(self, path):
        cur = None
        for s in path.segments():
            cur = self.PrintSegment(s, cur)
        print("]")

    def PrintPolygon(self, polygon):
        cur = None
        for s in polygon.segments():
            cur = self.PrintSegment(s, cur)
        print("]")
       
    def PrintSegment(self, segment, cur):
        if isinstance(segment, CubicBezier):
            if cur == None:
                print("bez = [[{0}, {1}], ".format(segment.start.x, segment.start.y));
            print("[{0}, {1}], [{2}, {3}], [{4}, {5}], ".format(segment.control1.x, segment.control1.y, segment.control2.x, segment.control2.y, segment.end.x, segment.end.y))
            return segment.end
        elif isinstance(segment, Line):
            if cur == None:
                print("line = [[{0}, {1}], ".format(segment.start.x, segment.start.y));
            else:
              if segment.start.x == cur.x and segment.start.y == cur.y:
                print("[{0}, {1}], ".format(segment.end.x, segment.end.y))
              else:
                print("[{0}, {1}], [{2}, {3}], ".format(segment.start.x, segment.start.y, segment.end.x, segment.end.y))
            return segment.end
        return cur

    def PrintAllObjects(self):
        for element in self.svg.elements():
            try:
                if element.values['visibility'] == 'hidden':
                    continue
            except (KeyError, AttributeError):
                pass
            self.PrintElement(element)

       

os = OpenScadOutput("../examples/svg/escher_lizard.svg")
os.PrintAllObjects()
