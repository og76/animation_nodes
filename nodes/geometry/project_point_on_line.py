import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class ProjectPointOnLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectPointOnLineNode"
    bl_label = "Project Point on Line" # Closest Point on Line ?
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Point", "point")
        self.inputs.new("an_VectorSocket", "Line Start", "lineStart")
        self.inputs.new("an_VectorSocket", "Line End", "lineEnd").value = (0, 0, 1)
        
        self.outputs.new("an_VectorSocket", "Projection", "projection")
        self.outputs.new("an_FloatSocket", "Projection Factor", "factor")
        self.outputs.new("an_BooleanSocket", "Distance to Line", "distance")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        
        yield "if lineStart == lineEnd:"
        yield "    projection, factor = lineStart, 0.0"
        if isLiked["distance"]: yield "    distance = (lineStart - point)length"
        
        yield "else:"
        yield "    projection, factor = mathutils.geometry.intersect_point_line(point, lineStart, lineEnd)"
        if isLiked["distance"]: yield "    distance = (projection - point)length"
        
    def getUsedModules(self):
        return ["mathutils"]