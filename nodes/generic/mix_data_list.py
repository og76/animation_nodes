import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toListIdName, toListDataType

nodeTypes = {
    "Matrix" : "Mix Matrix List",
    "Vector" : "Mix Vector List",
    "Float" : "Mix Float List",
    "Color" : "Mix Color List",
    "Euler" : "Mix Euler List",
    "Quaternion" : "Mix Quaternion List" }

class MixDataListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixDataListNode"
    bl_label = "Mix Data List"

    onlySearchTags = True
    searchTags = [(tag, {"dataType" : repr(type)}) for type, tag in nodeTypes.items()]

    def dataTypeChanged(self, context):
        self.recreateSockets()

    dataType = StringProperty(update = dataTypeChanged)
    repeat = BoolProperty(name = "Repeat", default = False,
        description = "Repeat the factor for values above and below 0-1", update = executionCodeChanged)

    def create(self):
        self.dataType = "Float"

    def draw(self, layout):
        layout.prop(self, "repeat")

    def drawLabel(self):
        return nodeTypes[self.outputs[0].dataType]

    def getExecutionCode(self):
        yield "length = len(dataList)"
        yield "if length > 0:"
        yield "    f = (factor{}) * (length - 1)".format(" % 1" if self.repeat else "")
        yield "    before = dataList[max(min(math.floor(f), length - 1), 0)]"
        yield "    after = dataList[max(min(math.ceil(f), length - 1), 0)]"
        yield "    influence = interpolation(f % 1)"
        yield "    " + getMixCode(self.dataType, "before", "after", "influence", "result")
        yield "else: result = self.outputs[0].getValue()"

    def getUsedModules(self):
        return ["math"]

    @keepNodeLinks
    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        self.inputs.new("an_FloatSocket", "Factor", "factor")
        self.inputs.new(toListIdName(self.dataType), toListDataType(self.dataType), "dataList")
        self.inputs.new("an_InterpolationSocket", "Interpolation", "interpolation").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new(toIdName(self.dataType), "Result", "result")
