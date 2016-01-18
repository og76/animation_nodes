import bpy
from bpy.props import *
from operator import itemgetter
from itertools import zip_longest 
from ... events import executionCodeChanged, propertyChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("DISTANCE", "Distance to Center", "Sort by Distance to Center", "", 0),
    ("DIRECTION", "Direction Vector", "Sort by Direction Vector", "", 1),
    ("CUSTOM_FLOAT", "Custom Number List", "Sort by Custom Numbers   /Provide a list with Numbers to pair each element", "", 2),
    ("CUSTOM_STRING", "Custom Text List", "Sort by Custom Text      /Provide a list with Texts to pair each element", "", 3),
    ("NAMES", "Object Names", "Sort by Object Names", "", 4) ]
    
operationsWithFloat = ["CUSTOM_FLOAT"]
operationsWithString = ["CUSTOM_STRING", "NAMES"]

operationLabels = {item[0] : item[2][:24] for item in operationItems}
operationSocket = {item[0] : item[1] for item in operationItems}

class SortObjectsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SortObjectsNode"
    bl_label = "Sort Objects"

    def operationChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "DIRECTION", update = operationChanged)
    reversed = BoolProperty(name = "Reverse Order", default = True, update = propertyChanged)
        
    def create(self):
        self.width = 180
        self.inputs.new("an_ObjectListSocket", "Object List", "objectList")
        self.inputs.new("an_VectorSocket", "Vector", "vector").value = [0, 0, 1] #operationSocket[self.operation]
        self.inputs.new("an_FloatListSocket", "Custom Number List", "numbers")
        self.inputs.new("an_StringListSocket", "Custom Text List", "strings")
        self.updateHideStatus()
        
        self.outputs.new("an_ObjectListSocket", "Sorted Object List", "sortedList")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")
        layout.prop(self, "reversed")

    def drawLabel(self):
        return operationLabels[self.operation]

    def getExecutionCode(self):
        yield "if objectList == []: sortedList = []"
        if type == "CUSTOM_FLOAT": yield "if numbers == []: sortedList = objectList"
        if type == "CUSTOM_STRING": yield "if strings == []: sortedList = objectList"
        yield "else: sortedList = [a for (a,b) in sorted(itertools.zip_longest(objectList,{}), key = lambda e: e[1], reverse = self.reversed)]".format(getConditions(self.operation)) 
    def getUsedModules(self):
        return ["itertools"]
    
    def updateHideStatus(self):
        for socket in self.inputs[1:]: socket.hide = True
        
        if "CUSTOM" not in self.operation: self.inputs["Vector"].hide = False
        if self.operation in operationsWithFloat: self.inputs["Custom Number List"].hide = False
        if self.operation in operationsWithString: self.inputs["Custom Text List"].hide = False
        

def getConditions(type):
    if type == "DISTANCE": return "[(ob.location - vector).length for ob in objectList], fillvalue = 0"
    elif type == "DIRECTION": return "[ob.location.dot(vector) for ob in objectList], fillvalue = 0"
    elif type == "CUSTOM_FLOAT": return "numbers[:len(objectList)], fillvalue = min(numbers) if numbers else 0"
    elif type == "CUSTOM_STRING": return "strings[:len(objectList)], fillvalue = 'a'"
    elif type == "NAMES": return "[ob.name for ob in objectList], fillvalue = 'a'"