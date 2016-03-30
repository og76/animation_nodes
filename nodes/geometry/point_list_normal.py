import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class PointListNormalNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointListNormalNode"
    bl_label = "Point List Normal"
    
    searchTags = ["Points Normal", "Calculate Normal"]    
    errorMessage = StringProperty()
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorListSocket", "Point List", "points")
        self.outputs.new("an_VectorSocket", "Normal", "normal")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid")
        
    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)
        
    def getExecutionCode(self):
        yield "if len(points) > 2: normal, self.errorMessage = mathutils.geometry.normal(points), ''"
        yield "else: normal, self.errorMessage = mathutils.Vector((0, 0, 0)), 'Expected min 3 different vectors'"

        yield "isValid = normal != mathutils.Vector((0, 0, 0))"
        
    def getUsedModules(self):
        return ["mathutils"]
