import bpy
from bpy.props import *
from operator import itemgetter
from itertools import zip_longest 
from ... events import executionCodeChanged, propertyChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("DISTANCE", "Distance to Vector", "Sort by Distance to Vector", "", 0),
    ("DIRECTION", "Direction Vector", "Sort by Direction Vector", "", 1),
    ("CUSTOM_FLOAT", "Custom Number List", "Sort by Custom Numbers   /Provide a list with Numbers to pair each element", "", 2),
    ("CUSTOM_STRING", "Custom Text List", "Sort by Custom Text      /Provide a list with Texts to pair each element", "", 3) ]

operationsWithFloat = ["CUSTOM_FLOAT"]
operationsWithString = ["CUSTOM_STRING"]

operationLabels = {item[0] : item[2][:24] for item in operationItems}
operationSocket = {item[0] : item[1] for item in operationItems}

class SortVectorsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SortVectorsNode"
    bl_label = "Sort Vectors"

    def operationChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "DIRECTION", update = operationChanged)
    reversed = BoolProperty(name = "Reverse Order", default = True, update = propertyChanged)
    precision = IntProperty(name = "Precision Digits", default = 4, update = propertyChanged)
        
    def create(self):
        self.width = 180
        self.inputs.new("an_VectorListSocket", "Vector List", "vectorList")
        self.inputs.new("an_VectorSocket", "Vector", "vector").value = [0, 0, 1] #operationSocket[self.operation]
        self.inputs.new("an_FloatListSocket", "Custom Number List", "numbers")
        self.inputs.new("an_StringListSocket", "Custom Text List", "strings")
        self.updateHideStatus()
        
        self.outputs.new("an_VectorListSocket", "Sorted Vector List", "sortedList")
        self.outputs.new("an_IntegerListSocket", "Sorted Indices List", "sortedIndices")
        
    def draw(self, layout):
        layout.prop(self, "operation", text = "")
        layout.prop(self, "reversed")

    def drawAdvanced(self, layout):
        layout.prop(self, "precision")

    def drawLabel(self):
        return operationLabels[self.operation]

    def getExecutionCode(self):
        yield "if vectorList == []: sortedList, sortedIndices = [], []"
        if type == "CUSTOM_FLOAT": yield "if numbers == []: sortedList, sortedIndices  = vectorList, [range(len(vectorList))]"
        yield "else:"
        yield "    sortedList, sortedIndices = [], []"
        yield "    for (a,i,k) in sorted(itertools.zip_longest(vectorList,range(len(vectorList)),{}), key = lambda e: e[2], reverse = self.reversed):".format(getConditions(self.operation)) 
        yield "        sortedList.append(a)"
        yield "        sortedIndices.append(i)"
    def getUsedModules(self):
        return ["itertools"]
    
    def updateHideStatus(self):
        for socket in self.inputs[1:]: socket.hide = True
        
        if "CUSTOM" not in self.operation: self.inputs["Vector"].hide = False
        if self.operation in operationsWithFloat: self.inputs["Custom Number List"].hide = False
        if self.operation in operationsWithString: self.inputs["Custom Text List"].hide = False
        

def getConditions(type):
    if type == "DISTANCE": return "[round((v - vector).length_squared, self.precision) for v in vectorList], fillvalue = 0"
    elif type == "DIRECTION": return "[round(v.dot(vector), self.precision) for v in vectorList], fillvalue = 0"
    elif type == "CUSTOM_FLOAT": return "numbers[:len(vectorList)], fillvalue = min(numbers) if numbers else 0"
    elif type == "CUSTOM_STRING": return "strings, fillvalue = 'a'"