import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class IntersectLineLineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLineLineNode"
    bl_label = "Intersect Line Line"
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Line 1 Start", "line1Start")
        self.inputs.new("an_VectorSocket", "Line 1 End", "line1End")
        self.inputs.new("an_VectorSocket", "Line 2 Start", "line2Start")
        self.inputs.new("an_VectorSocket", "Line 2 End", "line2End")
        
        self.outputs.new("an_VectorSocket", "Intersection 1", "int1")
        self.outputs.new("an_VectorSocket", "Intersection 2", "int2")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid")
        
    def getExecutionCode(self):
        yield "int = mathutils.geometry.intersect_line_line(line1Start, line1End, line2Start, line2End)"
        
        yield "if int is None: int1, int2, isValid = " + "mathutils.Vector((0, 0, 0)), " * 2 + "False"
        yield "else: (int1, int2), isValid = int, True"
        
    def getUsedModules(self):
        return ["mathutils"]