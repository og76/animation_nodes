import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_CharactersNode(Node, AnimationNode):
    bl_idname = "mn_CharactersNode"
    bl_label = "Characters"
    
    def init(self, context):
        forbidCompiling()
        self.outputs.new("mn_StringSocket", "Lower Case")
        self.outputs.new("mn_StringSocket", "Upper Case")
        self.outputs.new("mn_StringSocket", "Digits")
        self.outputs.new("mn_StringSocket", "Special")
        self.outputs.new("mn_StringSocket", "Line Break")
        self.outputs.new("mn_StringSocket", "All")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {"Lower Case" : "lower",
                "Upper Case" : "upper",
                "Digits" : "digits",
                "Special" : "special",
                "Line Break" : "lineBreak",
                "All" : "all"}
        
    def execute(self):
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        special = "!$%&/()=?*+#'-_.:,;" + '"'
        lineBreak = "\n"
        all = lower + upper + digits + special + lineBreak
        return lower, upper, digits, special, lineBreak, all
