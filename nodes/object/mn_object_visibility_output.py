import bpy
#from bpy.props import *
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_ObjectVisibilityOutput(Node, AnimationNode):
    bl_idname = "mn_ObjectVisibilityOutput"
    bl_label = "Object Visibility Output"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    useView = bpy.props.BoolProperty(name = "Use Hide", default = False, description = "Set Hide (restrict viewport visibility)", update = checkedPropertiesChanged)
    useSelect = bpy.props.BoolProperty(name = "Use Hide Select", default = False, description = "Set Hide Select (restrict viewport selection)", update = checkedPropertiesChanged)
    useRender = bpy.props.BoolProperty(name = "Use Hide", default = False, description = "Set Hide Render(restrict rendering)", update = checkedPropertiesChanged)

    useName = bpy.props.BoolProperty(name = "Use Name", default = False, description = "Set Show Name (visibility for object name)", update = checkedPropertiesChanged)
    useAxis = bpy.props.BoolProperty(name = "Use Axis", default = False, description = "Set Show Axis(visibility for object origin and axes)", update = checkedPropertiesChanged)
    useXray = bpy.props.BoolProperty(name = "Use Xray", default = False, description = "Set Show X-Ray (visibility for the object in front of others)", update = checkedPropertiesChanged)

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.inputs.new("mn_BooleanSocket", "Hide").value = False
        self.inputs.new("mn_BooleanSocket", "Hide Select").value = False
        self.inputs.new("mn_BooleanSocket", "Hide Render").value = False
        self.inputs.new("mn_BooleanSocket", "Show Name").value = False
        self.inputs.new("mn_BooleanSocket", "Show Axis").value = False
        self.inputs.new("mn_BooleanSocket", "Show Xray").value = False
        self.outputs.new("mn_ObjectSocket", "Object")
        self.updateSocketVisibility()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        rrow = layout.row()
        
        col = rrow.column()
        row = col.row(align = True)
        row.alignment = 'LEFT'
        #row.label("Visibility")
        row.prop(self, "useView", text = "", icon = "RESTRICT_VIEW_OFF")
        row.prop(self, "useSelect", text = "", icon = "RESTRICT_SELECT_OFF")
        row.prop(self, "useRender", text = "", icon = "RESTRICT_RENDER_OFF")
        
        col = rrow.column()
        row = col.row(align = True)
        row.alignment = 'RIGHT'
        #row.label("Show")
        row.prop(self, "useName", text = "", icon = "SORTALPHA")    # SYNTAX_ON / SYNTAX_OFF
        row.prop(self, "useAxis", text = "", icon = "MANIPUL")    
        row.prop(self, "useXray", text = "", icon = "ROTACTIVE")    # MOD_DECIM / META_BALL
    
    def draw_buttons_ext(self, context, layout):
        layout.operator("wm.call_menu", text = "Info / Help", icon = "INFO").name = "mn.show_help"

    def updateSocketVisibility(self):
        self.inputs["Hide"].hide = not (self.useView)
        self.inputs["Hide Select"].hide = not (self.useSelect)
        self.inputs["Hide Render"].hide = not (self.useRender)
        self.inputs["Show Name"].hide = not (self.useName)
        self.inputs["Show Axis"].hide = not (self.useAxis)
        self.inputs["Show Xray"].hide = not (self.useXray)

    def getInputSocketNames(self):
        return {"Object" : "object",
                "Hide" : "hide",
                "Hide Select" : "hideSelect",
                "Hide Render" : "hideRender",
                "Show Name" : "showName",
                "Show Axis" : "showAxis",
                "Show Xray" : "showXray"}
    def getOutputSocketNames(self):
        return {"Object" : "object"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        codeLines.append("if %object% is not None:")
        
        if self.useView: codeLines.append("    %object%.hide = %hide%")
        if self.useSelect: codeLines.append("    %object%.hide_select = %hideSelect%")
        if self.useRender: codeLines.append("    %object%.hide_render = %hideRender%")
        if self.useName: codeLines.append("    %object%.show_name = %showName%")
        if self.useAxis: codeLines.append("    %object%.show_axis = %showAxis%")
        if self.useXray: codeLines.append("    %object%.show_x_ray = %showXray%")
        
        if not (self.useView or self.useSelect or self.useRender or self.useName or self.useAxis or self.useXray): 
            codeLines = []
            
        codeLines.append("$object$ = %object%")
        return "\n".join(codeLines)





class ShowHelp(bpy.types.Menu):
    bl_idname = "mn.show_help"
    bl_label = "Object Visibility Output node | Blender - Animation Nodes"
    bl_icon = "FORCE_TURBULENCE"
    
    helpText = bpy.props.StringProperty(default = "help here")
    noteText = bpy.props.StringProperty(default = "note here")
    helpLines = []
    noteLines = []
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.label('''Help, comments, notes.''', icon = "INFO")
        row = layout.row(align = True)
        
        col = row.column(align = True)
        helpLines = self.helpText.split("\n")
        for li in helpLines:
            if li:
                col.label(text=li)
                
        col = row.column(align = True)
        noteLines = self.noteText.split("\n")
        for li in noteLines:
            if li:
                col.label(text=li)
            
        layout.label("o.g. 08.2015", icon = "INFO")
        
    helpText ='''
Purpose:
    This is a convenience node made to ease some ui procedures.
    Especially useful for objects generated by AN, when many.
    
    Allows hiding in the view or render, showing the names etc. ,
    the commands usually found in Outliner and Object properties panels
    Having as nodes is especially useful for many instanced objects, 
    or for hiding source of meshes.
    
Usage:
    Connect after the object you want to change state. Connect in loops
    for changing many at once. 
    Check the upper buttons for the parameters you want to affect.
    The props unchecked will not be affected in the object. This 
    is important for use in loops, where affecting many objects. 
    
    The top row of buttons correspond to the order of sockets:
    [hide][hide select][hide render]    [show name][show axis][show Xray]
       hide = hide in viewport
       hide select = hide from selection
       hide render = hide from rendering
       show name = shows name of the object in the viewport
       show axis = show origin and xyz tripod of the object
       show Xray = shows the object in front of others, never hidden
'''
    noteText ='''
notes:
    By default, parameters are Not checked. 
    Normally it all are Unchecked so that nothing is changed by accident.
    Also, the default values are False. This being more serious.
    
    To change these go into the [mn_object_visibility_output.py] file 
    (normally in animation nodes / nodes / object folder) and
    by the lines 14 to 20 you'll find the default states of these buttons.
    Change to True instead of False those that you consider by default
    
    You should not change the default values, near the sockets, 
    as they can lead to unwanted, blind, hiding the moment you plug 
    an object 
    
To explore further:
    there is also an Object Visibility Input brother node.
    That reads the state from objects.
    
    I think is less used, but it' there for convenience.
    Normally it is not in menu, so use search (Shift A)
'''
