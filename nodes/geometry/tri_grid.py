import bpy
from bpy.props import *
from mathutils import Vector
from math import tan, radians
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.geometry_algorithms.generate2d import triGridVertices, triGridEdgeIndices, triGridPolygonIndices

class TriGridMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TriGridMeshNode"
    bl_label = "Tri Grid Mesh"
    bl_width_default = 160
    
    useDegree = BoolProperty(name = "Use Degree", default = True, 
        update = propertyChanged)
    flip = BoolProperty(name = "Flip", default = False, 
        update = propertyChanged)
    centerGrid = BoolProperty(name = "Center", default = True, 
        update = propertyChanged)
    boundCenter = BoolProperty(name = "Bound Box Center", default = False, 
        update = propertyChanged)

    def create(self):
        divisionsSockets = [
            self.newInput("Integer", "X Divisions", "xDivisions"),
            self.newInput("Integer", "Y Divisions", "yDivisions") ]
        for socket in divisionsSockets:
            socket.value = 5
            socket.minValue = 2
        self.newInput("Float", "Distance", "distance").value = 1
        self.newInput("Float", "Angle", "angle").value = 60
        self.newInput("Float", "Shift", "shift").value = 0
        self.newInput("Vector", "Offset", "offset").isDataModified = True
        
        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "centerGrid")
        row.prop(self, "flip")

    def drawAdvanced(self, layout):
        layout.prop(self, "useDegree")
        if self.centerGrid: layout.prop(self, "boundCenter")

    def execute(self, xDivisions, yDivisions, distance, angle, shift, offset):
        
        xDiv, yDiv = max(xDivisions, 2), max(yDivisions, 2)
        
        if self.useDegree: angle = radians(angle)
        distY = distance * tan(angle) / 2
        
        b = distance / 4 if self.boundCenter else 0
        if self.flip:
            xDiv, yDiv = yDiv, xDiv
            oy = (xDiv - 1) * distance / 2 + b if self.centerGrid else 0
            ox = (yDiv - 1) * distY / 2 if self.centerGrid else 0
        else:
            ox = (xDiv - 1) * distance / 2 + b if self.centerGrid else 0
            oy = (yDiv - 1) * distY / 2 if self.centerGrid else 0

        offset = offset.copy()
        offset.x -= ox
        offset.y -= oy
        
        vertices = triGridVertices(offset, xDiv, yDiv, distance, distY, 
                            shift, self.flip) if self.outputs[0].isLinked else []
        edgeIndices = triGridEdgeIndices(xDiv, yDiv) if self.outputs[1].isLinked else []
        polygonIndices = triGridPolygonIndices(xDiv, yDiv) if self.outputs[2].isLinked else []

        return vertices, edgeIndices, polygonIndices
