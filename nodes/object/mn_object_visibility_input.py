import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ObjectVisibilityInput(Node, AnimationNode):
    bl_idname = "mn_ObjectVisibilityInput"
    bl_label = "Object Visibility Input"
    outputUseParameterName = "useOutput"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_BooleanSocket", "Hide")
        self.outputs.new("mn_BooleanSocket", "Hide Select").hide = True
        self.outputs.new("mn_BooleanSocket", "Hide Render")
        self.outputs.new("mn_BooleanSocket", "Show Name").hide = True
        self.outputs.new("mn_BooleanSocket", "Show Axis").hide = True
        self.outputs.new("mn_BooleanSocket", "Show Xray").hide = True
        allowCompiling()

    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return {"Hide" : "hide",
                "Hide Select" : "hideSelect",
                "Hide Render" : "hideRender",
                "Show Name" : "showName",
                "Show Axis" : "showAxis",
                "Show Xray" : "showXray"}
        
    def execute(self, useOutput, object):
        hide, hideSelect, hideRender, showName, showAxis, showXray = None, None, None, None, None, None
        
        if useOutput["Hide"]: hide = object.hide
        if useOutput["Hide Select"]: hideSelect = object.hide_select
        if useOutput["Hide Render"]: hideRender = object.hide_render
        
        if useOutput["Show Name"]: showName = object.show_name
        if useOutput["Show Axis"]: showAxis = object.show_axis
        if useOutput["Show Xray"]: showXray = object.show_x_ray

        return hide, hideSelect, hideRender, showName, showAxis, showXray