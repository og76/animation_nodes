import bpy
from bpy.props import *
from mathutils import Vector
from math import sin, cos, radians, ceil, copysign
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.geometry_algorithms.generate2d import circleVectors, ngonEdges, ngonPolygon

class CircleMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CircleMeshNode"
    bl_label = "Circle Mesh"
    bl_width_default = 160

    staticDivision = BoolProperty(name = "Fix Div", default = False, 
        description = "Divide per 360deg circle instead of arc", 
        update = propertyChanged)
    clip360Delta = BoolProperty(name = "Clip 360", default = True,
        description = "Limit to 360deg circle and merge first/last points if complete", 
        update = propertyChanged)
    pieBow = EnumProperty(name = "Pie Bow Arc", default = "PIE", 
        items = [("PIE", "Pie", ""), ("BOW", "Bow", "") ], 
        update = propertyChanged)
        
    def deltaEndSocketName(self, context):
        socket = self.inputs["Delta Angle"]
        if self.useDeltaEnd: 
            socket.display.text = False
        else: socket.display.text = True
        propertyChanged()
    
    useDeltaEnd = BoolProperty(name = "Use Delta End Angle", default = False, 
        description = "Use Start / Delta Angle instead of Start / End angles", 
        update = deltaEndSocketName)


    def create(self):
        self.newInput("Integer", "Divisions", "divisions", value = 24, minValue = 3)
        self.newInput("Float", "X Radius", "xRadius", value = 1)
        self.newInput("Float", "Y Radius", "yRadius", value = 1)
        self.newInput("Float", "Start Angle", "startAngle", value = 30)
        socket = self.newInput("Float", "Delta Angle", "deltaAngle", value = 270)
        socket.text = "End Angle"
        self.newInput("Vector", "Center", "center", isDataModified = True)

        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "staticDivision")
        row.prop(self, "clip360Delta")
        layout.prop(self, "pieBow", expand = True)
        layout.prop(self, "useDeltaEnd")

    def execute(self, divisions, xRadius, yRadius, startAngle, deltaAngle, center):
        
        divisions = max(divisions, 3)
        if not self.useDeltaEnd: deltaAngle = deltaAngle - startAngle 

        vertices = circleVectors(center, xRadius, yRadius, startAngle, deltaAngle, divisions, 
            self.staticDivision, self.clip360Delta, self.pieBow == "PIE") if self.outputs[0].isLinked else []

        lenV = len(vertices)
        edgeIndices = ngonEdges(lenV) if self.outputs[1].isLinked else []
        polygonIndices = ngonPolygon(lenV) if self.outputs[2].isLinked else []

        return vertices, edgeIndices, polygonIndices
