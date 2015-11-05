import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class IntersectLineSphereNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLineSphereNode"
    bl_label = "Intersect Line Sphere"
    
    clip = BoolProperty(description = "Only consider intersections inside the line, otherwise line is infinite", 
        default = False, update = propertyChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Line Start", "lineStart")
        self.inputs.new("an_VectorSocket", "Line End", "lineEnd").value = (0, 0, 1)
        self.inputs.new("an_VectorSocket", "Sphere Center", "center")
        self.inputs.new("an_VectorSocket", "Sphere Radius", "radius").value = 1
        
        self.outputs.new("an_VectorSocket", "Intersection 1", "intersection1")
        self.outputs.new("an_VectorSocket", "Intersection 2", "intersection2")
        
    def draw(self, layout):
        layout.prop(self, "clip")
        
    def getExecutionCode(self):
        yield "int = mathutils.geometry.intersect_line_sphere(lineStart, lineEnd, center, radius, clip)"
        yield "intersection1 = int[0] if int[0] != None else center"
        yield "intersection2 = int[1] if int[1] != None else center"
        
    def getUsedModules(self):
        return ["mathutils"]