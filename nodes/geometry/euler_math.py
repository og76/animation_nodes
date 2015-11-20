import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", "A + B", "", 0),
    ("SUBTRACT", "Subtract", "A - B", "", 1),
    ("MULTIPLY", "Multiply", "A * B       Multiply element by element", "", 2),
    ("DIVIDE", "Divide", "A / B       Divide element by element", "", 3),
    ("SCALE", "Scale", "A * scale", "", 4) ]

operationsWithFloat = ["SCALE"]
operationsWithDegree = ["MULTIPLY", "DIVIDE"]

operationLabels = {item[0] : item[2][:11] for item in operationItems}

class EulerMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EulerMathNode"
    bl_label = "Euler Math"

    def operationChanged(self, context):
        self.inputs["B"].hide = self.operation in operationsWithFloat
        self.inputs["Scale"].hide = self.operation not in operationsWithFloat
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", items = operationItems, default = "ADD", update = operationChanged)
    useDegree = BoolProperty(name = "Use Degrees",
        description = "Multiply and Divide degrees. If false, operation will use radians (output is always radians)",
        default = True, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_EulerSocket", "A", "a")
        self.inputs.new("an_EulerSocket", "B", "b")
        socket = self.inputs.new("an_FloatSocket", "Scale", "scale")
        socket.hide = True
        socket.value = 1.0
        self.outputs.new("an_EulerSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")
        
    def drawAdvanced(self, layout):
        if self.operation in operationsWithDegree: layout.prop(self, "useDegree")

    def drawLabel(self):
        return operationLabels[self.operation]

    def getExecutionCode(self):
        op = self.operation
        if op == "ADD": return "result = mathutils.Euler((a[0] + b[0], a[1] + b[1], a[2] + b[2]), 'XYZ')"
        elif op == "SUBTRACT": return "result = mathutils.Euler((a[0] - b[0], a[1] - b[1], a[2] - b[2]), 'XYZ')"
    
        elif op == "MULTIPLY":
            if self.useDegree:
                return "result = mathutils.Euler((math.radians(math.degrees(A) * math.degrees(B)) for A, B in zip(a, b)), 'XYZ')"
            else: return "result = mathutils.Euler((a[0] * b[0], a[1] * b[1], a[2] * b[2]), 'XYZ')"
        elif op == "DIVIDE":
            if self.useDegree:
                return ("result = mathutils.Euler((0, 0, 0), 'XYZ')",
                                 "if b[0] != 0: result[0] = math.radians(math.degrees(a[0]) / math.degrees(b[0]))",
                                 "if b[1] != 0: result[1] = math.radians(math.degrees(a[0]) / math.degrees(b[0]))",
                                 "if b[2] != 0: result[2] = math.radians(math.degrees(a[0]) / math.degrees(b[0]))")
            else: 
                return ("result = mathutils.Euler((0, 0, 0), 'XYZ')",
                                 "if b[0] != 0: result[0] = a[0] / b[0]",
                                 "if b[1] != 0: result[1] = a[1] / b[1]",
                                 "if b[2] != 0: result[2] = a[2] / b[2]")
                                     
        elif op == "SCALE": return "result = mathutils.Euler((a[0] * scale, a[1] * scale, a[2] * scale), 'XYZ')"

    def getUsedModules(self):
        return ["math, mathutils"]