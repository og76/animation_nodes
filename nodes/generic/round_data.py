import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

nodeTypes = {
    "Vector" : "Round Vector",
    "Euler" : "Round Euler",
    "Quaternion" : "Round Quaternion" }

class RoundDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RoundDataNode"
    bl_label = "Round"

    onlySearchTags = True
    searchTags = [(tag, {"dataType" : repr(type)}) for type, tag in nodeTypes.items()]

    def dataTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    dataType = StringProperty(default = "Vector", update = dataTypeChanged)
    roundDegree = BoolProperty(name = "Round Degrees",
        description = "Rounding degrees. If false round radians",
        default = False, update = executionCodeChanged)

    def create(self):
        self.generateSockets()

    def drawAdvanced(self, layout):
        if self.dataType == "Euler": layout.prop(self, "roundDegree")

    def drawLabel(self):
        return nodeTypes[self.outputs[0].dataType]

    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        idName = toIdName(self.dataType)
        self.inputs.new(idName, self.dataType, "input")
        self.inputs.new("an_IntegerSocket", "Decimals", "decimals").value = 5
        self.outputs.new(idName, "Rounded " + self.dataType, "rounded")

    def getExecutionCode(self):
#        if self.dataType == "Euler" and self.roundDegree: 
#            return "rounded = mathutils.Euler((math.radians(round(math.degrees(item), decimals)) for item in input))"
#        else: return "rounded = mathutils.{}((round(item, decimals) for item in input))".format(self.dataType)
        return "rounded = [round(item, decimals) for item in input]".format(self.dataType)
#    def getUsedModules(self):
#        return ["mathutils", "math"]