import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class BarycentricTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BarycentricTransformNode"
    bl_label = "Barycentric Transform"

    errorMessage = StringProperty()
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Point", "point")
        self.inputs.new("an_VectorListSocket", "Tri 1 Point List", "t1")
        self.inputs.new("an_VectorListSocket", "Tri 2 Point List", "t2")
        self.outputs.new("an_VectorSocket", "Morphed Location", "location")
        
    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)
        
    def drawAdvanced(self, layout):
        layout.label('Expected:')
        layout.label('3 Different vectors for Tri1')
        layout.label('3 vectors for Tri2')
        
    def getExecutionCode(self):
        yield "if len(points1) < 3: location, self.errorMessage = point, 'Expected 3 vectors for Tri 1'"
        yield "elif len(points2) < 3: location, self.errorMessage = point, 'Expected 3 vectors for Tri 2'"
        yield "elif any((t1[0]==t1[1], t1[1]==t1[2], t1[2]==t1[0])): location, self.errorMessage = point, 'Expected 3 Different vectors for Tri 1'"
        
        yield "else: location, self.errorMessage = mathutils.geometry.barycentric_transform(point, t1[0], t1[1], t1[2], t2[0], t2[1], t2[2]), ''"


#        yield "loc = mathutils.geometry.barycentric_transform(point, t1[0], t1[1], t1[2], t2[0], t2[1], t2[2])"
#        yield "if loc != (-1.#IND,-1.#IND,-1.#IND): location, self.errorMessage = loc, ''"
#        yield "else: location, self.errorMessage = point, 'Wrong Tris: See Advanced Panel'"
        
    def getUsedModules(self):
        return ["mathutils"]