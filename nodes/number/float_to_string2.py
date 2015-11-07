import bpy
from ... base_types.node import AnimationNode

class FloatToString2Node(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatToStringNode2"
    bl_label = "Float to Text2"

    def create(self):
        self.inputs.new("an_FloatSocket", "Number", "number")
        socket = self.inputs.new("an_IntegerSocket", "Min Length", "minLength")
        socket.value = 10
        socket.minValue = 0
        socket = self.inputs.new("an_IntegerSocket", "Decimals", "decimals")
        socket.value = 3
        socket.minValue = 0
        self.inputs.new("an_BooleanSocket", "Insert Sign", "insertSign").value = False
        self.outputs.new("an_StringSocket", "Text", "text")

#    def execute(self, number, minLength, decimals, insertSign):
#        sign = "+" if insertSign else ""

#        formatString = "{" + ":{}0{}.{}f".format(sign, max(minLength , 0), max(decimals, 0)) + "}"
#        return formatString.format(number)
    
    def getExecutionCode(self):
        yield 'sign = "+" if insertSign else ""'

        yield 'formatString = "{" + ":{}0{}.{}f".format(sign, max(minLength , 0), max(decimals, 0)) + "}"'
        yield 'text = formatString.format(number)'
#        sign = ""
#        if number >= 0 and insertSign: sign = "+"
#        elif number < 0: sign = "-"

#        formatString = "{" + ":0>{}.{}f".format(max(minLength - len(sign), 0), max(decimals, 0)) + "}"
#        return sign + formatString.format(abs(number))
