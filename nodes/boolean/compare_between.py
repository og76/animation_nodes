import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

# double menu variant
typesGreat = ["< ", "<="]
typesSmall = ["> ", ">="]
typesA = [(t, "A " + t, "") for t in typesGreat + typesSmall]
typesB = [(t, t + " B", "") for t in typesGreat + typesSmall]

# classic variant
compare_types = [   "A <  value <  B",
                    "A <= value <= B",
                    "A <= value <  B",
                    "A <  value <= B",
                    
                    "A >  value >  B",
                    "A >= value >= B",
                    "A >= value >  B",
                    "A >  value >= B"]
compare_types_items = [(t, t, "") for t in compare_types]

class CompareBetweenNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CompareBetweenNode"
    bl_label = "Compare Between"
    bl_defaultwidth = 160
    
    def assignedTypeChanged(self, context):
        self.inputIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    inputIdName = StringProperty()


    def TypeAChanged(self, context):
        A, B = self.TypeA, self.TypeB
        if A in typesGreat:
            if B in typesSmall: self.TypeB = typesGreat[0]#typesB[A]
        if A in typesSmall:
            if B in typesGreat: self.TypeB = typesSmall[0]#typesB[A]
        executionCodeChanged()
        
    def TypeBChanged(self, context):
        A, B = self.TypeA, self.TypeB
        if B in typesGreat:
            if A in typesSmall: self.TypeA = typesGreat[0]#typesA[B]
        if B in typesSmall:
            if A in typesGreat: self.TypeA = typesSmall[0]#typesA[B]
        executionCodeChanged()

    compareType = EnumProperty(name = "Compare Type", 
        items = compare_types_items, update = executionCodeChanged)
        
    TypeA = EnumProperty(name = "Compare to A", default = "< ",
        items = typesA, update = TypeAChanged)
    TypeB = EnumProperty(name = "Compare to B", default = "< ",
        items = typesB, update = TypeBChanged)
    formulaAB = StringProperty(default = "haha")
    
    negate = BoolProperty(name = "Negate", 
        default = False, update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"
        self.outputs.new("an_BooleanSocket", "Result", "result")

    def draw(self, layout):
#        layout.prop(self, "compareType", text = "")
        row = layout.row(align = True)
        row.prop(self, "TypeA", text = "")
        row.prop(self, "TypeB", text = "")
        layout.prop(self, "negate")
        
        A, B = self.TypeA, self.TypeB
        type = "A " + A + " value " + B + " B"
        neg = "not " if self.negate else ""
        layout.label(neg + type, icon = "INFO")

    def getExecutionCode(self):
        
        #type = self.compareType.lower()
        #type = self.compareTypeAB.lower()
        A, B = self.TypeA, self.TypeB
        type = "a " + A + " value " + B + " b"
        neg = "not " if self.negate else ""
        
        return "try: result = " + neg + type +"\nexcept: result = False" 
        
#        return "try: result = " +self.compareTypeAB +"\nexcept: result = False" 

#        if type == "A = B":	return "result = a == b"
#        if type == "A != B": return "result = a != b"
#        if type == "A < B":	return "try: result = a < value < b \nexcept: result = False"
#        if type == "A <= B": return "try: result = a < value <= b \nexcept: result = False"
#        if type == "A > B":	return "try: result = a > b \nexcept: result = False"
#        if type == "A >= B": return "try: result = a >= b \nexcept: result = False"
#        if type == "A is B": return "result = a is b"
#        return "result = False"

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

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.inputs.new(self.inputIdName, "Value", "value")
        self.inputs.new(self.inputIdName, "A", "a")
        self.inputs.new(self.inputIdName, "B", "b")