import bpy
from bpy.props import *
from math import tan, radians
from mathutils import Vector
from .... base_types.node import AnimationNode
from .... algorithms.mesh_generation.indices_utils import gridQuadPolygonIndices, gridQuadEdgeIndices
from .... algorithms.mesh_generation.basic_shapes import gridVertices
from .... events import executionCodeChanged

class TriGridMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TriGridMeshNode"
    bl_label = "Tri Grid Mesh"

    useDegree = BoolProperty(name = "Use Degree", default = True, update = executionCodeChanged)
    centerGrid = BoolProperty(name = "Center", default = True, update = executionCodeChanged)
    flip = BoolProperty(name = "Flip", default = False, update = executionCodeChanged)
    boundCenter = BoolProperty(name = "Bound Box Center", default = False, update = executionCodeChanged)

    def create(self):
        self.width = 160
        divisionsSockets = [
            self.inputs.new("an_IntegerSocket", "X Divisions", "xDivisions"),
            self.inputs.new("an_IntegerSocket", "Y Divisions", "yDivisions") ]
        for socket in divisionsSockets:
            socket.value = 5
            socket.minValue = 2
        self.inputs.new("an_FloatSocket", "Distance", "distance").value = 1
        self.inputs.new("an_FloatSocket", "Angle", "angle").value = 60
        self.inputs.new("an_FloatSocket", "Shift", "shift").value = 0
        self.inputs.new("an_VectorSocket", "Offset", "offset").isDataModified = True
        
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "centerGrid")
        row.prop(self, "flip")
        layout.prop(self, "useDegree")

    def drawAdvanced(self, layout):
        if self.centerGrid: layout.prop(self, "boundCenter")

    def execute(self, xDivisions, yDivisions, distance, angle, shift, offset):
        
        ang = tan(radians(angle)) / 2 if self.useDegree else tan(angle) / 2
        b = distance / 4 if self.boundCenter else 0
        
        offset = offset.copy()
        if self.flip:
            xDiv, yDiv = (max(yDivisions, 2), max(xDivisions, 2))
            offset.y -= (xDiv - 1) * distance / 2 + b if self.centerGrid else 0
            offset.x -= (yDiv - 1) * distance * ang / 2 if self.centerGrid else 0
        else:
            xDiv, yDiv = (max(xDivisions, 2), max(yDivisions, 2))
            offset.x -= (xDiv - 1) * distance / 2 + b if self.centerGrid else 0
            offset.y -= (yDiv - 1) * distance * ang / 2 if self.centerGrid else 0
        
        vertices = triGridVertices(xDiv, yDiv, distance, ang, shift, offset, self.flip) if self.outputs[0].isLinked else []
        edgeIndices = triGridEdgeIndices(xDiv, yDiv) if self.outputs[1].isLinked else []
        polygonIndices = triGridPolygonIndices(xDiv, yDiv) if self.outputs[2].isLinked else []

        return vertices, edgeIndices, polygonIndices

def triGridVertices(xDiv, yDiv, distance, angle, shift, offset, flip):
    fac = min(max(distance * shift, -1), 1)
    vectorList = []
    for y in range(yDiv):
        for x in range(xDiv):
            if flip:
                vectorList.append(Vector(( y * distance * angle + offset.x, x * distance + y % 2 * distance / 2 + offset.y, 0 )) )
            else:
                vectorList.append(Vector(( x * distance + y % 2 * (distance + fac) / 2 + offset.x, y * distance * angle + offset.y, 0 )) )
    return vectorList

def triGridEdgeIndices(xDiv, yDiv):
    edgeIndicesList = []
    for y in range(yDiv):
        for x in range(xDiv):
            if x < xDiv-1: edgeIndicesList.append((y * xDiv + x, y * xDiv + x + 1))
            if y < yDiv-1: edgeIndicesList.append((y * xDiv + x, (y + 1) * xDiv + x))
            if x < xDiv-1 and y < yDiv-1: 
                if y % 2 == 0: edgeIndicesList.append(((y + 1) * xDiv + x, y * xDiv + x + 1))
                else: edgeIndicesList.append((y * xDiv + x, y * (y + 1) * xDiv + x +1))
    return edgeIndicesList

def triGridPolygonIndices(xDiv, yDiv):
    polygonIndicesList = []
    for y in range(yDiv-1):
        for x in range(xDiv-1):
            if y % 2 == 0:
                polygonIndicesList.append((y * xDiv + x, y * xDiv + x + 1, (y + 1) * xDiv + x))
                polygonIndicesList.append((y * xDiv + x + 1, (y + 1) * xDiv + x + 1, (y + 1) * xDiv + x))
            else:
                polygonIndicesList.append((y * xDiv + x, (y + 1) * xDiv + x + 1, (y + 1) * xDiv + x))
                polygonIndicesList.append((y * xDiv + x, y * xDiv + x + 1, (y + 1) * xDiv + x +1))
    return polygonIndicesList