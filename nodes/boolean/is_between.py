import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

compare_types = [   "A <  value <  B",
                    "A <= value <= B",
                    "A <= value <  B",
                    "A <  value <= B",
                    
                    "A >  value >  B",
                    "A >= value >= B",
                    "A >= value >  B",
                    "A >  value >= B"]
compare_types_items = [(t, t, "") for t in compare_types]

class IsBetweenNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IsBetweenNode"
    bl_label = "Is Between"
    
    def assignedTypeChanged(self, context):
        self.inputIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    inputIdName = StringProperty()

    compareType = EnumProperty(name = "Compare Type", 
        items = compare_types_items, update = executionCodeChanged)
    negate = BoolProperty(name = "Negate", 
        default = False, update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"
        self.outputs.new("an_BooleanSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "compareType", text = "")
        layout.prop(self, "negate")

    def getExecutionCode(self):
        
        type = self.compareType.lower()
        neg = "not " if self.negate else ""
        
        return "try: result = " + neg + type +"\nexcept: result = False" 

    def edit(self):
        dataType = self.getWantedDataType()
        self.assingType(dataType)

    def getWantedDataType(self):
        inputV = self.inputs[0].dataOrigin
        inputA = self.inputs[1].dataOrigin
        inputB = self.inputs[2].dataOrigin

        if inputV is not None: return inputV.dataType
        if inputA is not None: return inputA.dataType
        if inputB is not None: return inputB.dataType
        return self.inputs[0].dataType

    def assingType(self, dataType):
        if self.assignedType == dataType: return
        self.assignedType = dataType

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.inputs.new(self.inputIdName, "Value", "value")
        self.inputs.new(self.inputIdName, "A", "a")
        self.inputs.new(self.inputIdName, "B", "b")