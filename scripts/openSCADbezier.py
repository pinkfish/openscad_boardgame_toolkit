#!/usr/bin/env python

# openSCADbezier.py

# Copyright (C) 2018 Australian Institute of Marine Science
#
# Contact: Gael Lafond <g.lafond@aims.gov.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This is an Inkscape extension to output paths to OpenSCAD bezier.
# The Inkscape objects must first be converted to paths (Path > Object to Path).
# Some paths may not work well -- the paths have to be polygons. As such,
# paths derived from text may meet with mixed results.

# Inspired from:
#   https://www.thingiverse.com/thing:25036

# EDIT 2018-04-02
#   Added support for InkScape layers, as suggested by Warren Baird:
#     https://www.thingiverse.com/thing:2805184/#comment-1837500

import inkex
import simplepath
import simpletransform
import cubicsuperpath
import re

class OpenSCADBezier(inkex.Effect):
	moduleList = {}

	# Constructor
	def __init__(self):
		inkex.Effect.__init__(self)

		# Dictionary of warnings issued. This to prevent from warning
		# multiple times about the same problem
		self.warnings = {}

	# Output in the saved file
	# Somehow, this is called by "e.affect()"
	def effect(self):
		docWidth = None
		if 'getDocumentWidth' in dir (self):
			docWidth = self.svg.width

		docHeight = None
		if 'getDocumentHeight' in dir (self):
			docHeight = self.svg.height

		level = 0
		if docWidth and docHeight:
			level = 1

		print(self.getHeader())
		openSCADTree = self.convertNodeTree(self.document.getroot(), level)

		if docWidth and docHeight:
			print('translate([' + str(float(docWidth) / -2) + ', ' + str(float(docHeight) / 2) + ']) {\n')

		if self.moduleList:
			for moduleName in self.moduleList:
				print(("\t"*level) + moduleName + '();')
			print()

		print(openSCADTree)

		if docWidth and docHeight:
			print('}\n')

		if self.moduleList:
			for moduleName in self.moduleList:
				print(self.moduleList[moduleName])

		print(self.getBezierLibrary())

	def getHeader(self):
		output = '/**\n'
		output += ' * This file contains a 2D vector representation of your InkScape file.\n'
		output += ' * You can set the global variable "$fn" to alter the precision of the curves.\n'
		output += ' * You should use "linear_extrude" or "rotate_extrude" to give it some volume.\n'
		output += ' */\n'
		return output

	def sanitizeString(self, string):
		return re.sub('[\W_]+', '_', string)

	def getBezierLibrary(self):
		output = '/**\n'
		output += ' * Stripped down version of "bezier_v2.scad".\n'
		output += ' * For full version, see: https://www.thingiverse.com/thing:2170645\n'
		output += ' */\n'
		output += '\n'
		output += 'function BEZ03(u) = pow((1-u), 3);\n'
		output += 'function BEZ13(u) = 3*u*(pow((1-u),2));\n'
		output += 'function BEZ23(u) = 3*(pow(u,2))*(1-u);\n'
		output += 'function BEZ33(u) = pow(u,3);\n'
		output += '\n'
		output += 'function bezier_2D_point(p0, p1, p2, p3, u) = [\n'
		output += '	BEZ03(u)*p0[0]+BEZ13(u)*p1[0]+BEZ23(u)*p2[0]+BEZ33(u)*p3[0],\n'
		output += '	BEZ03(u)*p0[1]+BEZ13(u)*p1[1]+BEZ23(u)*p2[1]+BEZ33(u)*p3[1]\n'
		output += '];\n'
		output += '\n'
		output += 'function bezier_coordinates(points, steps) = [\n'
		output += '	for (c = points)\n'
		output += '		for (step = [0:steps])\n'
		output += '			bezier_2D_point(c[0], c[1], c[2],c[3], step/steps)\n'
		output += '];\n'
		output += '\n'
		output += 'module bezier_polygon(points) {\n'
		output += '	steps = $fn <= 0 ? 30 : $fn;\n'
		output += '	polygon(bezier_coordinates(points, steps));\n'
		output += '}'
		return output

	# Recursive method that traverse an InkScape tree and print nodes as
	#   OpenSCAD Bezier objects
	def convertNodeTree(self, nodes, level=0, transform=inkex.transforms.Transform([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0]]), parent_visibility='visible', inModule=False):
		output = ''

		for node in nodes:
			# Ignore invisible nodes
			visibility = node.get('visibility', parent_visibility)
			if visibility == 'inherit':
				visibility = parent_visibility
			if visibility == 'hidden' or visibility == 'collapse':
				pass

			# First apply the current matrix transform to this node's tranform
			nodeTransform = transform * inkex.transforms.Transform(node.get("transform"))

			if node.tag == inkex.addNS('g', 'svg') or node.tag == 'g':
				groupContent = None
				if inModule:
					groupContent = self.convertNodeTree(node, level+1, nodeTransform, visibility, True)
				else:
					groupContent = self.convertNodeTree(node, 1, nodeTransform, visibility, True)

				if groupContent:
					# Output the node ID as an OpenSCAD comment
					groupId = node.get('id', 'UNDEFINED')
					if not inModule:
						# Create a new module, using the layer name if available
						moduleName = self.sanitizeString(node.get(inkex.addNS('label', 'inkscape'), groupId))
						groupContent = '// Group ID: ' + groupId + '\n' + 'module ' + moduleName + '() {\n' + groupContent + '}\n'
						self.moduleList[moduleName] = groupContent

					else:
						# This group is inside a module. We don't want to create a module in a module.
						output += ("\t"*level) + '// Group ID: ' + groupId + '\n'
						output += ("\t"*level) + 'union() {\n'
						output += groupContent
						output += ("\t"*level) + '}\n'

			elif node.tag == inkex.addNS('use', 'svg') or node.tag == 'use':

				# A <use> element refers to another SVG element via an xlink:href="#blah"
				# attribute. We will handle the element by doing an XPath search through
				# the document, looking for the element with the matching id="blah"
				# attribute. We then recursively process that element after applying
				# any necessary (x,y) translation.
				#
				# Notes:
				#  1. We ignore the height and width attributes as they do not apply to
				#     path-like elements, and
				#  2. Even if the use element has visibility="hidden", SVG still calls
				#     for processing the referenced element. The referenced element is
				#     hidden only if its visibility is "inherit" or "hidden".

				refid = node.get(inkex.addNS('href', 'xlink'))
				if not refid:
					pass

				# [1:] to ignore leading '#' in reference
				path = '//*[@id="%s"]' % refid[1:]
				refnode = node.xpath(path)
				if refnode:
					x = float(node.get('x', '0'))
					y = float(node.get('y', '0'))
					# Note: the transform has already been applied
					if (x != 0) or (y != 0):
						newNodeTransform = nodeTransform * inkex.transforms.Transform('translate(%f,%f)' % (x,y))
					else:
						newNodeTransform = nodeTransform
					visibility = node.get('visibility', visibility)

					# Output the node ID as an OpenSCAD comment
					refContent = self.convertNodeTree(refnode, level, newNodeTransform, visibility, inModule)
					if refContent:
						output += ("\t"*level) + '// Referenced element ID: ' + node.get('id', 'UNDEFINED') + '\n'
						output += refContent

			elif node.tag == inkex.addNS('path', 'svg'):

				path_data = node.get('d')
				if path_data:
					pathContent = self.getPathVertices(path_data, level, node, nodeTransform)
					if pathContent:
						# Output the node ID as an OpenSCAD comment
						output += ("\t"*level) + '// Path ID: ' + node.get('id', 'UNDEFINED') + '\n'
						output += pathContent

			elif node.tag == inkex.addNS('rect', 'svg') or node.tag == 'rect':

				# Manually transform
				#
				#   <rect x="X" y="Y" width="W" height="H"/>
				#
				# into
				#
				#   <path d="MX,Y lW,0 l0,H l-W,0 z"/>
				#
				# I.e., explicitly draw three sides of the rectangle and the
				# fourth side implicitly

				# Create a path with the outline of the rectangle
				#   by drawing points CLOCKWISE
				x = float(node.get('x'))
				y = float(node.get('y'))
				if (not x) or (not y):
					pass
				w = float(node.get('width', '0'))
				h = float(node.get('height', '0'))
				pathArray = []
				pathArray.append(['M ', [x, y]])
				pathArray.append([' l ', [0, h]])
				pathArray.append([' l ', [w, 0]])
				pathArray.append([' l ', [0, -h]])
				pathArray.append([' Z', []])

				# Output the node ID as an OpenSCAD comment
				rectContent = self.getPathVertices(str(pathArray), level, node, nodeTransform)
				if rectContent:
					output += ("\t"*level) + '// Rectangle ID: ' + node.get('id', 'UNDEFINED') + '\n'
					output += rectContent

			elif node.tag == inkex.addNS('line', 'svg') or node.tag == 'line':

				# Convert
				#
				#   <line x1="X1" y1="Y1" x2="X2" y2="Y2/>
				#
				# to
				#
				#   <path d="MX1,Y1 LX2,Y2"/>

				x1 = float(node.get('x1'))
				y1 = float(node.get('y1'))
				x2 = float(node.get('x2'))
				y2 = float(node.get('y2'))
				if (not x1) or (not y1) or (not x2) or (not y2):
					pass
				pathArray = []
				pathArray.append(['M ', [x1, y1]])
				pathArray.append([' L ', [x2, y2]])

				# Output the node ID as an OpenSCAD comment
				lineContent = self.getPathVertices(simplepath.formatPath(pathArray), level, node, nodeTransform)
				if lineContent:
					output += ("\t"*level) + '// Line ID: ' + node.get('id', 'UNDEFINED') + '\n'
					output += lineContent

			elif node.tag == inkex.addNS('polyline', 'svg') or node.tag == 'polyline':

				# Convert
				#
				#   <polyline points="x1,y1 x2,y2 x3,y3 [...]"/>
				#
				# to
				#
				#   <path d="Mx1,y1 Lx2,y2 Lx3,y3 [...]"/>
				#
				# Note: we ignore polylines with no points

				points = node.get('points', '').strip()
				if points == '':
					pass

				pointArray = points.split()
				linePath = "".join(["M " + pointArray[i] if i == 0 else " L " + pointArray[i] for i in range(0, len(pointArray))])

				# Output the node ID as an OpenSCAD comment
				output += ("\t"*level) + '// Polyline ID: ' + node.get('id', 'UNDEFINED') + '\n'
				output += self.getPathVertices(linePath, level, node, nodeTransform)

			elif node.tag == inkex.addNS('polygon', 'svg') or node.tag == 'polygon':

				# Convert
				#
				#   <polygon points="x1,y1 x2,y2 x3,y3 [...]"/>
				#
				# to
				#
				#   <path d="Mx1,y1 Lx2,y2 Lx3,y3 [...] Z"/>
				#
				# Note: we ignore polygons with no points

				points = node.get('points', '').strip()
				if points == '':
					pass

				pointArray = points.split()
				polygonPath = "".join(["M " + pointArray[i] if i == 0 else " L " + pointArray[i] for i in range(0, len(pointArray))])
				polygonPath += " Z"

				# Output the node ID as an OpenSCAD comment
				polygonContent = self.getPathVertices(polygonPath, level, node, nodeTransform)
				if polygonContent:
					output += ("\t"*level) + '// Polygon ID: ' + node.get('id', 'UNDEFINED') + '\n'
					output += polygonContent

			elif node.tag == inkex.addNS('ellipse', 'svg') or node.tag == 'ellipse':

				# Convert ellipses to a path with two 180 degree arcs.
				# In general, we convert
				#
				#   <ellipse rx="RX" ry="RY" cx="X" cy="Y"/>
				#
				# to
				#
				#   <path d="MX1,CY A RX,RY 0 1 0 X2,CY A RX,RY 0 1 0 X1,CY"/>
				#
				# where
				#
				#   X1 = CX - RX
				#   X2 = CX + RX
				#
				# Note: ellipses with a radius attribute of value 0 are ignored

				rx = float(node.get('rx', '0'))
				ry = float(node.get('ry', '0'))

				if rx == 0 or ry == 0:
					pass

				cx = float(node.get('cx', '0'))
				cy = float(node.get('cy', '0'))
				x1 = cx - rx
				x2 = cx + rx
				ellipsePath = 'M %f,%f ' % (x1, cy) + \
					'A %f,%f ' % (rx, ry) + \
					'0 1 0 %f,%f ' % (x2, cy) + \
					'A %f,%f ' % (rx, ry) + \
					'0 1 0 %f,%f' % (x1, cy)

				# Output the node ID as an OpenSCAD comment
				ellipseContent = self.getPathVertices(ellipsePath, level, node, nodeTransform)
				if ellipseContent:
					output += ("\t"*level) + '// Ellipse ID: ' + node.get('id', 'UNDEFINED') + '\n'
					output += ellipseContent

			elif node.tag == inkex.addNS('circle', 'svg') or node.tag == 'circle':

				# Convert circles to a path with two 180 degree arcs.
				# In general, we convert
				#
				#   <circle r="R" cx="X" cy="Y"/>
				#
				# to
				#
				#   <path d="MX1,CY A R,R 0 1 0 X2,CY A R,R 0 1 0 X1,CY"/>
				#
				# where
				#
				#   X1 = CX - R
				#   X2 = CX + R
				#
				# Note: circles with a radius attribute of value 0 are ignored

				r = float(node.get('r', '0'))

				if r == 0:
					pass

				cx = float(node.get('cx', '0'))
				cy = float(node.get('cy', '0'))
				x1 = cx - r
				x2 = cx + r
				circlePath = 'M %f,%f ' % (x1, cy) + \
					'A %f,%f ' % (r, r) + \
					'0 1 0 %f,%f ' % (x2, cy) + \
					'A %f,%f ' % (r, r) + \
					'0 1 0 %f,%f' % (x1, cy)

				# Output the node ID as an OpenSCAD comment
				circleContent = self.getPathVertices(circlePath, level, node, nodeTransform)
				if circleContent:
					output += ("\t"*level) + '// Circle ID: ' + node.get('id', 'UNDEFINED') + '\n'
					output += circleContent

			elif node.tag == inkex.addNS('pattern', 'svg') or node.tag == 'pattern':

				pass

			elif node.tag == inkex.addNS('metadata', 'svg') or node.tag == 'metadata':

				pass

			elif node.tag == inkex.addNS('defs', 'svg') or node.tag == 'defs':

				pass

			elif node.tag == inkex.addNS('desc', 'svg') or node.tag == 'desc':

				pass

			elif node.tag == inkex.addNS('namedview', 'sodipodi') or node.tag == 'namedview':

				pass

			elif node.tag == inkex.addNS('eggbot', 'svg') or node.tag == 'eggbot':

				pass

			elif node.tag == inkex.addNS('text', 'svg') or node.tag == 'text':

				if not self.warnings.has_key('text'):
					inkex.errormsg('Warning: unable to draw text, please convert it to a path first.')
					self.warnings['text'] = 1
				pass

			elif node.tag == inkex.addNS('title', 'svg') or node.tag == 'title':

				pass

			elif node.tag == inkex.addNS('image', 'svg') or node.tag == 'image':

				if not self.warnings.has_key('image'):
					inkex.errormsg('Warning: unable to draw bitmap images; ' +
						'please convert them to line art first. Consider using the "Trace bitmap..." ' +
						'tool of the "Path" menu. Mac users please note that some X11 settings may ' +
						'cause cut-and-paste operations to paste in bitmap copies.')
					self.warnings['image'] = 1
				pass

			elif node.tag == inkex.addNS('pattern', 'svg') or node.tag == 'pattern':

				pass

			elif node.tag == inkex.addNS('radialGradient', 'svg') or node.tag == 'radialGradient':

				# Similar to pattern
				pass

			elif node.tag == inkex.addNS('linearGradient', 'svg') or node.tag == 'linearGradient':

				# Similar in pattern
				pass

			elif node.tag == inkex.addNS('style', 'svg') or node.tag == 'style':

				# This is a reference to an external style sheet and not the value
				# of a style attribute to be inherited by child elements
				pass

			elif node.tag == inkex.addNS('cursor', 'svg') or node.tag == 'cursor':

				pass

			elif node.tag == inkex.addNS('color-profile', 'svg') or node.tag == 'color-profile':

				# Gamma curves, color temp, etc. are not relevant to single color output
				pass

			elif not isinstance(node.tag, basestring):

				# This is likely an XML processing instruction such as an XML
				# comment. lxml uses a function reference for such node tags
				# and as such the node tag is likely not a printable string.
				# Further, converting it to a printable string likely won't
				# be very useful.

				pass

			else:

				if not self.warnings.has_key(node.tag):
					inkex.errormsg('Warning: unable to draw object <%s>, please convert it to a path first.' % node.tag)
					self.warnings[node.tag] = 1
				pass

		return output


	def getPathVertices(self, path, level, node=None, transform=None):
		output = ''

		# Debugging
		#output += ("\t"*level) + '// PATH: ' + path + '\n'

		if (not path) or (len(path) == 0):
			# Nothing to do
			return output

		# parsePath() may raise an exception. This is okay
		pathArray = inkex.paths.Path.parse_string(path)

		# pathArray is a "generator". There is no way to test if a generator is empty.
		if (not pathArray):
			# Path must have been devoid of any real content
			return output

		# Get a cubic super path
		# TODO FIX - Function "cubicsuperpath.CubicSuperPath" is deprecated, but its replacement "inkex.paths.CubicSuperPath" crashes with:
		#     "ValueError: ZoneClose segments can not be changed into curves."
		#multiPolygonPoints = inkex.paths.CubicSuperPath(pathArray)
		multiPolygonPoints = cubicsuperpath.CubicSuperPath(pathArray)
		if (not multiPolygonPoints) or (len(multiPolygonPoints) == 0):
			# Probably never happens, but...
			return output

		# Debugging
		#output += ("\t"*level) + '// multiPolygonPoints: ' + str(multiPolygonPoints) + '\n'

		if transform:
			multiPolygonPoints = multiPolygonPoints.transform(transform)

		polygonTree = self.buildPolygonTree(multiPolygonPoints)

		#output += '// multiPolygonPoints: ' + str(multiPolygonPoints) + '\n'
		#output += '// polygonTree: ' + str(polygonTree) + '\n'

		output += self.getOpenSCADPolygonList(polygonTree["children"], level)
		return output


	def getOpenSCADPolygonList(self, polygonNodeList, level):
		output = ''

		for polygonNode in polygonNodeList:
			holes = []
			childPolygonNodes = []

			for polygonHole in polygonNode["children"]:
				holes.append(self.getOpenSCADPolygon(polygonHole["polygon"]))
				for childPolygonNode in polygonHole["children"]:
					childPolygonNodes.append(childPolygonNode)

			if holes:
				output += ("\t"*level) + 'difference() {\n'
				level += 1

			output += ("\t"*level) + self.getOpenSCADPolygon(polygonNode["polygon"]) + ';\n'
			for hole in holes:
				output += ("\t"*level) + hole + ';\n'

			if holes:
				level -= 1
				output += ("\t"*level) + '}\n'

			output += self.getOpenSCADPolygonList(childPolygonNodes, level)

		return output


	def getOpenSCADPolygon(self, polygon):
		openScadPolygon = []
		length = len(polygon)
		if (length < 2):
			return

		for index in range(0, length-1):
			point = polygon[index]
			nextPoint = polygon[index+1]
			openScadPolygon.append([point[1], point[2], nextPoint[0], nextPoint[1]])
		firstPoint = polygon[0]
		lastPoint = polygon[length-1]
		openScadPolygon.append([lastPoint[1], lastPoint[2], firstPoint[0], firstPoint[1]])
		return 'bezier_polygon(' + str(openScadPolygon) + ')'


	def buildPolygonTree(self, multiPolygonPoints):
		polygonTree = {
			"children": [],
			"polygon": None
		}
		for polygonPoints in multiPolygonPoints:
			if (len(polygonPoints) > 1):
				polygonNode = {
					"children": [],
					"polygon": polygonPoints
				}
				self.addPolygon(polygonTree, polygonNode)

		return polygonTree


	def addPolygon(self, branch, polygonNode):
		'''
		Recursive function
		Pseudo-code:
			addPolygon(branch, polygonNode)
				# If node is inside one already in the tree
				for node in branch.children
					if polygonNode.polygon is inside node.polygon
						addPolygon(node, polygonNode)
						return

				# If node contains nodes already in the tree
				for node in branch.children
					if node.polygon is inside polygonNode.polygon
						polygonNode.children.append(node)
						branch.children.remove(node)

				# If node is not contained by any node in the branch
				branch.children.append(polygonNode)

		branch = a "node"
		node = object containing:
			- children = array of "node"
			- polygon = array of points
			- hole = boolean
		'''

		# If node is inside one already in the tree
		for node in branch["children"]:
			if self.polyInPoly(polygonNode["polygon"], None, node["polygon"], None):
				self.addPolygon(node, polygonNode)
				return

		# If node contains nodes already in the tree
		for node in branch["children"]:
			if self.polyInPoly(node["polygon"], None, polygonNode["polygon"], None):
				polygonNode["children"].append(node)

		# Check if children is empty
		#   If it's not empty, that means we just moved some node from the branch to the node
		#   Those node needs to me removed from the branch
		if (polygonNode["children"]):
			for node in polygonNode["children"]:
				branch["children"].remove(node)

		# If node is not contained by any node in the branch
		branch["children"].append(polygonNode)



	# NOTE: The proper way to determine if a polygon is a hole is to
	#   check if it's counter-clockwise.
	#   This method is a clever way to efficiently calculate this.
	#   Unfortunately, the simplepath library do not follow the standard
	#   and draw polygons clockwise and counter-clockwise without any
	#   concerns for developers sanity!
	#
	# Solution: Don't use polyIsHole.
	#   Instead, determine if a polygon is a hole by checking if it's
	#   within another polygon
	#
	# https://nerd.mmccoo.com/2018/01/11/understanding-and-parsing-svg-paths/
	def polyIsHole(self, poly):
		# to determine if a poly is a hole or outer boundary i check for
		# clockwise or counter-clockwise.
		# As suggested here:
		# https://stackoverflow.com/a/1165943/23630
		# I take the area under the curve, and if it's positive or negative
		# I'll know bounds or hole.
		lastpt = poly[-1]
		area = 0.0
		for pt in poly:
			# the area under a line is (actually twice the area, but we just
			# want the sign
			# NOTE: The actual code found on mmccoo.com was doing a division here
			area = area + (pt[2][0]-lastpt[2][0]) * (pt[2][1]+lastpt[2][1])
			lastpt = pt
		return (area>0.0)

	def pointInBBox(self, pt, bbox):

		'''
		Determine if the point pt=[x, y] lies on or within the bounding
		box bbox=[xmin, xmax, ymin, ymax].
		'''

		# if ( x < xmin ) or ( x > xmax ) or ( y < ymin ) or ( y > ymax )
		if (pt[2][0] < bbox[0]) or (pt[2][0] > bbox[1]) or \
			(pt[2][1] < bbox[2]) or (pt[2][1] > bbox[3]):
			return False
		else:
			return True

	def bboxInBBox(self, bbox1, bbox2):

		'''
		Determine if the bounding box bbox1 lies on or within the
		bounding box bbox2. NOTE: we do not test for strict enclosure.

		Structure of the bounding boxes is

		bbox1 = [ xmin1, xmax1, ymin1, ymax1 ]
		bbox2 = [ xmin2, xmax2, ymin2, ymax2 ]
		'''

		# if ( xmin1 < xmin2 ) or ( xmax1 > xmax2 ) or ( ymin1 < ymin2 ) or ( ymax1 > ymax2 )

		if (bbox1[0] < bbox2[0]) or (bbox1[1] > bbox2[1]) or \
			(bbox1[2] < bbox2[2]) or (bbox1[3] > bbox2[3]):
			return False
		else:
			return True

	def pointInPoly(self, p, poly, bbox=None):

		'''
		Use a ray casting algorithm to see if the point p = [x, y] lies within
		the polygon poly = [[x1,y1],[x2,y2],...]. Returns True if the point
		is within poly, lies on an edge of poly, or is a vertex of poly.
		'''

		if (p is None) or (poly is None):
			return False

		# Check to see if the point lies outside the polygon's bounding box
		if not bbox is None:
			if not self.pointInBBox(p, bbox):
				return False

		# Check to see if the point is a vertex
		if p in poly:
			return True

		# Handle a boundary case associated with the point
		# lying on a horizontal edge of the polygon
		x = p[2][0]
		y = p[2][1]
		p1 = poly[0]
		p2 = poly[1]
		for i in range(len(poly)):
			if i != 0:
				p1 = poly[i-1]
				p2 = poly[i]
			if (y == p1[2][1]) and (p1[2][1] == p2[2][1]) and \
				(x > min(p1[2][0], p2[2][0])) and (x < max(p1[2][0], p2[2][0])):
				return True

		# http://www.ariel.com.au/a/python-point-int-poly.html
		n = len(poly)
		inside = False

		p1_x,p1_y = poly[0][2]
		for i in range(n + 1):
			p2_x,p2_y = poly[i % n][2]
			if y > min(p1_y, p2_y):
				if y <= max(p1_y, p2_y):
					if x <= max(p1_x, p2_x):
						if p1_y != p2_y:
							intersect = p1_x + (y - p1_y) * (p2_x - p1_x) / (p2_y - p1_y)
							if x <= intersect:
								inside = not inside
						else:
							inside = not inside
			p1_x,p1_y = p2_x,p2_y

		return inside

	def polyInPoly(self, poly1, bbox1, poly2, bbox2):

		'''
		Determine if polygon poly2 = [[x1,y1],[x2,y2],...]
		contains polygon poly1.

		The bounding box information, bbox=[xmin, xmax, ymin, ymax]
		is optional. When supplied it can be used to perform rejections.
		Note that one bounding box containing another is not sufficient
		to imply that one polygon contains another. It's necessary, but
		not sufficient.
		'''

		# See if poly1's bboundin box is NOT contained by poly2's bounding box
		# if it isn't, then poly1 cannot be contained by poly2.

		if (not bbox1 is None) and (not bbox2 is None):
			if not self.bboxInBBox(bbox1, bbox2):
				return False

		# To see if poly1 is contained by poly2, we need to ensure that each
		# vertex of poly1 lies on or within poly2

		# NOTE: We should check for every single points, but
		#   some polygon can have some points outside it's parent
		#   due to curves been removed to do this test.
		# Using set to ignore duplicate points
		pointInPolySet = set()
		pointOutsidePolySet = set()
		for p in poly1:
			if self.pointInPoly(p, poly2, bbox2):
				pointInPolySet.add(str(p))
			else:
				pointOutsidePolySet.add(str(p))

		# Looks like poly1 is contained on or in Poly2
		return len(pointInPolySet) > len(pointOutsidePolySet);

# Main function
#   What is executed by InkScape when the plugin is activated
#   using "Save as > OpenSCAD Bezier (*.scad)"
if __name__ == '__main__':

	e = OpenSCADBezier()
	e.run()
