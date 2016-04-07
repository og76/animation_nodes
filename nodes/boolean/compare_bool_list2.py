import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

compareTypeItems = [
    ("ANY", "Any", ""), 
    ("ALL", "All", ""),
    ("NOT_ANY", "not Any", ""), 
    ("NOT_ALL", "not All", "")]
    
compareTypeItems = [("ANY", "Any", ""), ("ALL", "All", "")]
    
compareFormula = { t[0] : t[1].lower() for t in compareTypeItems }

class CompareBoolList2Node(bpy.types.Node, AnimationNode):
    bl_idname = "an_CompareBoolList2Node"
    bl_label = "Compare Bool List 2"

    compareType = EnumProperty(name = "Compare Type", default = "ANY",
        items = compareTypeItems, update = executionCodeChanged)
    negate = BoolProperty(name = "not ", 
        default = False, update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"
        self.inputs.new("an_BooleanListSocket", "Boolean List", "list")
        self.outputs.new("an_BooleanSocket", "Result", "result")

    def draw(self, layout):
#        layout.prop(self, "compareType", text = "")
        row = layout.row(align = True)
        row.prop(self, "negate", toggle = True)
        row.separator()
        row.prop(self, "compareType", expand = True)

    def getExecutionCode(self):
        return ("try: result = {}{}(list)\nexcept: result = False"
            .format("not " if self.negate else "", compareFormula[self.compareType]) )
#        return ("try: result = {}(list)\nexcept: result = False"
#                        .format(compareFormula[self.compareType]) )