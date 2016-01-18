import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

conversionTypeItems = [
    ("DEGREE_TO_RADIAN", "Degree to Radian", ""),
    ("RADIAN_TO_DEGREE", "Radian to Degree", ""),
    ("DEGREE_TO_SLOPE", "Degree to Slope", ""),
    ("SLOPE_TO_DEGREE", "Slope to Degree", ""),
    ("RADIAN_TO_SLOPE", "Radian to Slope", ""),
    ("SLOPE_TO_RADIAN", "Slope to Radian", "")
    ]

class ConvertAngleNode2(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertAngleNode2"
    bl_label = "Convert Angle 2"

    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _ in conversionTypeItems]

    def settingChanged(self, context):
        inSocket = self.inputs["Angle"]
        outSocket = self.outputs["Angle"]
        if self.conversionType == "DEGREE_TO_RADIAN":
            inSocket.text = "Degree"
            outSocket.text = "Radian"
        elif self.conversionType == "RADIAN_TO_DEGREE":
            inSocket.text = "Radian"
            outSocket.text = "Degree"
            
        elif self.conversionType == "DEGREE_TO_SLOPE":
            inSocket.text = "Degree"
            outSocket.text = "Slope (%)"
        elif self.conversionType == "SLOPE_TO_DEGREE":
            inSocket.text = "Slope (%)"
            outSocket.text = "Degree"
        elif self.conversionType == "RADIAN_TO_SLOPE":
            inSocket.text = "Radian"
            outSocket.text = "Slope (%)"
        elif self.conversionType == "SLOPE_TO_RADIAN":
            inSocket.text = "Slope (%)"
            outSocket.text = "Radian"
        executionCodeChanged()

    conversionType = EnumProperty(name = "Conversion Type", items = conversionTypeItems, update = settingChanged)

    def create(self):
        socket1 = self.inputs.new("an_FloatSocket", "Angle", "inAngle")
        socket2 = self.outputs.new("an_FloatSocket", "Angle", "outAngle")
        for socket in [socket1, socket2]:
            socket.display.text = True
        self.conversionType = "DEGREE_TO_RADIAN"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")

    def getExecutionCode(self):
        if self.conversionType == "DEGREE_TO_RADIAN": return "outAngle = inAngle / 180 * math.pi"
        if self.conversionType == "RADIAN_TO_DEGREE": return "outAngle = inAngle * 180 / math.pi"

        if self.conversionType == "DEGREE_TO_SLOPE": return "outAngle = 100 * math.sin(inAngle / 180 * math.pi) / math.cos(inAngle / 180 * math.pi)"
        if self.conversionType == "SLOPE_TO_DEGREE": return "outAngle = math.atan(inAngle / 100) * 180 / math.pi"

        if self.conversionType == "RADIAN_TO_SLOPE": return "outAngle = 100 * math.sin(inAngle) / math.cos(inAngle)"
        if self.conversionType == "SLOPE_TO_RADIAN": return "outAngle = math.atan(inAngle / 100)"

    def getUsedModules(self):
        return ["math"]
