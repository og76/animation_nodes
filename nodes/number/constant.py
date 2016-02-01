import bpy
import math
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode


operationItems = [
    ("PI", "pi number", " pi ", "", 0),
    ("E", "e number", " e ", "", 1),
    ("GOLDEN", "Golden Ratio", "Golden Ratio , a.k.a. PHI, Fibonacci series", "", 2),
    ("SILVER", "Silver Ratio", "Silver Ratio, a.k.a. A4 (paper), Dynamic Ratio" , "", 3)]

singleInputOperations = ("SINE", "COSINE", "TANGENT", "ARCSINE",
    "ARCCOSINE", "ARCTANGENT", "ABSOLUTE", "FLOOR", "CEILING", "SQRT", "INVERT", "RECIPROCAL")

operationLabels = {item[0] : item[2][:12] for item in operationItems}

searchItems = {
    "pi number" : "PI",
    "e number" : "E",
    "Golden Ratio" : "GOLDEN",
    "Silver Ratio" : "SILVER" }


class FloatConstantNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatConstantNode"
    bl_label = "Constant"

    @classmethod
    def getSearchTags(cls):
        tags = []
        for name, operation in searchItems.items():
            tags.append((name, {"operation" : repr(operation)}))
        return tags

    def operationChanged(self, context):
        #self.inputs[1].hide = self.operation in singleInputOperations
        executionCodeChanged()

    def outputIntegerChanged(self, context):
        self.recreateOutputSocket()

    operation = EnumProperty(name = "Operation", default = "PI",
        items = operationItems, update = operationChanged)

    outputInteger = BoolProperty(name = "Output Integer", default = False,
        update = outputIntegerChanged)

    def create(self):
        #self.inputs.new("an_FloatSocket", "A", "a")
        #self.inputs.new("an_FloatSocket", "B", "b").value = 1.0
        self.outputs.new("an_FloatSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def drawLabel(self):
        return operationLabels[self.operation]

    def edit(self):
        self.outputInteger = self.outputs[0].isOnlyLinkedToDataType("Integer")

    def recreateOutputSocket(self):
        idName = "an_IntegerSocket" if self.outputInteger else "an_FloatSocket"
        if self.outputs[0].bl_idname == idName: return
        self._recreateOutputSocket(idName)

    @keepNodeLinks
    def _recreateOutputSocket(self, idName):
        self.outputs.clear()
        self.outputs.new(idName, "Result", "result")

    def getExecutionCode(self):
        op = self.operation
        if op == "PI": yield "result = math.pi"
        if op == "E": yield "result = math.e"
        if op == "GOLDEN": yield "result = (1 + math.sqrt(5) ) / 2"
        if op == "SILVER": yield "result = math.sqrt(2)"

        if self.outputInteger:
            yield "result = int(result)"

    def getUsedModules(self):
        return ["math"]
