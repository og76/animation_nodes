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
        self.outputs.new("an_FloatSocket", "Distance to Line", "distance")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        yield "if lineStart == lineEnd:"
        yield "    projection, factor = lineStart, 0.0"
        yield "    distance = (lineStart - point).length" #if isLiked["distance"]: 
        
        yield "else:"
        yield "    projection, factor = mathutils.geometry.intersect_point_line(point, lineStart, lineEnd)"
        yield "    distance = (projection - point).length" #if isLiked["distance"]: 
        
    def getUsedModules(self):
        return ["mathutils"]