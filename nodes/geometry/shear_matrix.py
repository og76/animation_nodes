import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

planeItems = [("XY", "XY", ""), ("XZ", "XZ", ""), ("YZ", "YZ", "")]
#other = {"XY" : "(0, 0, 1)", "XZ" : "(0, 1, 0)", "YZ" : "(1, 0, 0)"}
#other = {"XY": (0, 0, 1), "XZ": (0, 1, 0), "YZ": (1, 0, 0)}
other = {"XY": "z(0, 0, 1)", "XZ": "y(0, 1, 0)", "YZ": "x(1, 0, 0)"}

class ShearMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShearMatrixNode"
    bl_label = "Shear Matrix"

    plane = EnumProperty(items = planeItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_VectorSocket", "Shear", "shear").value = [1, 1, 1]
        self.outputs.new("an_MatrixSocket", "Matrix", "matrix")

    def draw(self, layout):
        layout.prop(self, "plane", expand = True)

    def getExecutionCode(self):

        yield ("sca = mathutils.Matrix.Scale(shear.{}, 4, {})"#format(other[self.plane][0], other[self.plane][1]) )
                .format([co.lower() for co in ('XYZ') if co not in self.plane][0], other[self.plane][1:]) )
        yield ("mat = mathutils.Matrix.Shear('{}', 4, (shear.{}, shear.{}))"
                .format(self.plane, self.plane[0].lower(), self.plane[1].lower()) )
        yield "matrix = sca * mat"

#    def getExecutionCode(self):
#        return ("matrix = mathutils.Matrix.Shear('{}', 4, (shear.{}, shear.{}))"
#                .format(self.plane, self.plane[0].lower(), self.plane[1].lower()) )

    def getUsedModules(self):
        return ["mathutils"]