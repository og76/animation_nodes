import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class BarycentricTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BarycentricTransformNode"
    bl_label = "Barycentric Transform"
    
    searchTags = ["Transform by Triangles", "Morph by Triangles"]
    errorMessage = StringProperty()
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Point", "point")
        self.inputs.new("an_VectorListSocket", "Source Triangle Points", "t1")
        self.inputs.new("an_VectorListSocket", "Target Triangle Points", "t2")
        self.outputs.new("an_VectorSocket", "Morphed Location", "location")
        
    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 21)
        
    def drawAdvanced(self, layout):
        layout.label('Expected:')
        layout.label('3 Different vectors for Source')
        layout.label('3 vectors for Target')
        
    def getExecutionCode(self):
        yield "if len(t1) < 3:   location, self.errorMessage = point, 'Expected 3 vectors for Source Triangle'"
        yield "elif len(t2) < 3: location, self.errorMessage = point, 'Expected 3 vectors for Target Triangle'"
        yield "elif any((t1[0]==t1[1], t1[1]==t1[2], t1[2]==t1[0])): "
        yield "    location, self.errorMessage = point, 'Expected 3 Different vectors for Source'"
        
        yield "else: location, self.errorMessage = mathutils.geometry.barycentric_transform(point, t1[0], t1[1], t1[2], t2[0], t2[1], t2[2]), ''"
        
    def getUsedModules(self):
        return ["mathutils"]