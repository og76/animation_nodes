import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

conversionTypeItems = [
    ("POINT_NORMAL_TO_MATRIX", "Point/Normal to Matrix", "", "NONE", 0),
    ("MATRIX_TO_POINT_NORMAL", "Matrix to Point/Normal", "", "NONE", 1)]

class ConvertPlaneTypeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertPlaneTypeNode"
    bl_label = "Convert Plane Type"

    onlySearchTags = True
    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _,_,_ in conversionTypeItems]

    def conversionTypeChanged(self, context):
        self.createSockets()
        executionCodeChanged()

    conversionType = EnumProperty(name = "Conversion Type", default = "MATRIX_TO_POINT_NORMAL",
        items = conversionTypeItems, update = conversionTypeChanged)
    useDegree = BoolProperty(name = "Use Degree", default = False, update = executionCodeChanged)

    def create(self):
        self.width = 170
        self.conversionType = "MATRIX_TO_POINT_NORMAL"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")
#        if "ANGLE" in self.conversionType: layout.prop(self, "useDegree")

    def drawLabel(self):
        for item in conversionTypeItems:
            if self.conversionType == item[0]: return item[1]

    def getExecutionCode(self):

        if self.conversionType == "POINT_NORMAL_TO_MATRIX":
            return "matrix = (mathutils.Matrix.Translation(planePoint)) * ( (planeNormal.to_track_quat('Z', 'Y')).to_matrix().to_4x4() )"
        if self.conversionType == "MATRIX_TO_POINT_NORMAL":
            return "planePoint, planeNormal = matrix.to_translation(), matrix.to_3x3() * mathutils.Vector((0, 0, 1))"

    def getUsedModules(self):
        return ["mathutils"]

    @keepNodeLinks
    def createSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        if self.conversionType == "POINT_NORMAL_TO_MATRIX":
            self.inputs.new("an_VectorSocket", "Point in Plane", "planePoint")
            self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal")
            self.outputs.new("an_MatrixSocket", "Matrix", "matrix")
        if self.conversionType == "MATRIX_TO_POINT_NORMAL":
            self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
            self.outputs.new("an_VectorSocket", "Point in Plane", "planePoint")
            self.outputs.new("an_VectorSocket", "Plane Normal", "planeNormal")

        self.inputs[0].defaultDrawType = "PREFER_PROPERTY"
