import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

signModeItems = [
    ("PLUS", "Sign [+/-]", "Show [+] on positive numbers", "", 0),
    ("SPACE", "Sign [  /-]", "Show [ ]space on positive, to align with -", "", 1),
    ("NONE", "Sign [/-]", "Show only [-] default float behavior", "", 2)]
    
signs = {"PLUS": "'+'", "SPACE": "' '", "NONE": "''"}
leadItems = [("lead'0'", "Lead '0'", ""), ("lead''", "Lead '_'", "")]

class FloatFormatNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatFormatNode"
    bl_label = "Float Format OG" #Float to Text, Float to String

    signMode = EnumProperty(name = "Sign Mode", default = "PLUS",
        items = signModeItems, update = executionCodeChanged)
    
    leadingType = EnumProperty(name = "Leading Type", default = "lead'0'",
        #description = "Leading Zeros or Spaces to fill the length",
        items = leadItems, update = executionCodeChanged)

    def create(self):
        self.width = 180
        self.inputs.new("an_FloatSocket", "Float", "float")
        socket = self.inputs.new("an_IntegerSocket", "Min Length", "minLength")
        socket.value = 8
        socket.minValue = 0
        socket = self.inputs.new("an_IntegerSocket", "Decimals", "decimals")
        socket.value = 3
        socket.minValue = 0
        self.inputs.new("an_BooleanSocket", "Insert Sign", "insertSign").value = True
        self.outputs.new("an_StringSocket", "Text", "text")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "signMode", text = "", icon = "ZOOMIN")
        row.prop(self, "leadingType", text = "", icon = "INLINK")

    def getExecutionCode(self):

        yield "sign = " + signs[self.signMode]
        yield "lz = " + str(self.leadingType[4:]) #"'0' if leadingZeros else ''
        #yield "lz = '0' if leadingZeros else ''"
        #yield "string = '{:' + s + lz + str(max(length, 0)) + '.' + str(max(precision, 0)) + 'f}'"
        yield "formatString = '{' + ':{}{}{}.{}f'.format(sign, lz, max(minLength - len(sign), 0), max(decimals, 0)) + '}'"
        yield "text = formatString.format(float)"