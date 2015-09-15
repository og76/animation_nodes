import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_ObjectNameFilterNode(Node, AnimationNode):
    bl_idname = "mn_ObjectNameFilterNode"
    bl_label = "Object Name Filter"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    #objectName = bpy.props.StringProperty(update = nodePropertyChanged)
    
    useAllInScene = bpy.props.BoolProperty(default = False, description = "Use All Objects In Scene instead of socket", update = checkedPropertiesChanged)
    useCaseSensitive = bpy.props.BoolProperty(default = False, description = "Use Case Sensitive", update = checkedPropertiesChanged)
    
    filterType = bpy.props.EnumProperty(items = [("STARTS WITH", "Starts With", "All Objects with names starting with"),
                                                 ("ENDS WITH", "Ends With", "All Objects with names ending with")],
                                        update = checkedPropertiesChanged, default = "STARTS WITH")
    
    def init(self, context):
        forbidCompiling()
        self.bl_width_default = 180
        self.width = 180
        self.inputs.new("mn_ObjectListSocket", "Objects").showName = False
        self.inputs.new("mn_StringSocket", "Name")
        self.outputs.new("mn_ObjectListSocket", "Objects")
        self.outputs.new("mn_StringListSocket", "Names").hide = True
        self.updateSocketVisibility()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "filterType", text = "Type", expand = True)
        row.separator()
        row.prop(self, "useCaseSensitive", text = "", icon = "FONTPREVIEW") #Case Sensitive #SYNTAX_OFF
        row = col.row(align = True)
        row.prop(self, "useAllInScene", text = "All Scene Objects", icon = "SCENE_DATA")
        
    def updateSocketVisibility(self):
        self.inputs["Objects"].hide = self.useAllInScene
        
    def getInputSocketNames(self):
        return {"Objects" : "objects",
                "Name" : "name"}
    def getOutputSocketNames(self):
        return {"Objects" : "objects",
                "Names" : "names"}
        
#    def execute(self, objects, name):
#        return objects
    
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        codeLines.append("obList = []")
        
        if self.useAllInScene: codeLines.append("obList = bpy.context.scene.objects")
        else: codeLines.append("if %objects% is not None: obList = %objects%")
        
        codeLines.append("filteredList, filteredNames = [], []")
        codeLines.append("for obj in obList:")
        if self.useCaseSensitive: 
            if self.filterType == "STARTS WITH": codeLines.append("    filtered = obj.name.startswith(str(%name%))")
            if self.filterType == "ENDS WITH": codeLines.append("    filtered = obj.name.endswith(str(%name%))")
        else: 
            if self.filterType == "STARTS WITH": codeLines.append("    filtered = obj.name.lower().startswith(str.lower(%name%))")
            if self.filterType == "ENDS WITH": codeLines.append("    filtered = obj.name.lower().endswith(str.lower(%name%))")
        
        codeLines.append("    if filtered: filteredList.append(obj), filteredNames.append(str(obj.name))")
        codeLines.append("$objects$, $names$ = filteredList, filteredNames")
        return "\n".join(codeLines)