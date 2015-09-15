import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

options = [ ("materialIndex", "Material Index"),
            ("useBold", "Bold"),
            ("useItalic", "Italic"),
            ("useUnderline", "Underline"),
            ("useSmallCaps", "Small Caps")]

class mn_CharacterPropsOutputNode(Node, AnimationNode):
    bl_idname = "mn_CharacterPropsOutputNode"
    bl_label = "Character Props Output"
    
    def usePropertyChanged(self, context):
        self.setHideProperty()
        nodeTreeChanged()
    
    materialIndex = BoolProperty(default = True, update = usePropertyChanged)
    
    useBold = BoolProperty(default = False, update = usePropertyChanged)
    useItalic = BoolProperty(default = False, update = usePropertyChanged)
    useUnderline = BoolProperty(default = False, update = usePropertyChanged)
    useSmallCaps = BoolProperty(default = False, update = usePropertyChanged)
    
    allowNegativeIndex = BoolProperty(default = True)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Text Object").showName = False
        
        self.inputs.new("mn_IntSocket", "Start").number = 0.0
        self.inputs.new("mn_IntSocket", "End").number = -1.0
        self.inputs.new("mn_IntSocket", "Material Index").number = 0.0
        
        self.inputs.new("mn_BoolSocket", "Bold").value = False
        self.inputs.new("mn_BoolSocket", "Italic").value = False
        self.inputs.new("mn_BoolSocket", "Underline").value = False
        
        self.inputs.new("mn_FloatSocket", "Underline Position").number = 0.0
        self.inputs.new("mn_FloatSocket", "Underline Thickness").number = 0.05
        
        self.inputs.new("mn_FloatSocket", "Small Caps").value = False
        self.inputs.new("mn_FloatSocket", "Small Caps Scale").number = 0.75
        self.setHideProperty()
        
        self.outputs.new("mn_ObjectSocket", "Object")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "materialIndex", text = "", icon = "MATERIAL_DATA")  #MATSPHERE
        row.separator()
        row.prop(self, "useBold", text = "", icon = "FONT_DATA")
        row.prop(self, "useItalic", text = "", icon = "OUTLINER_DATA_FONT")
        row.prop(self, "useUnderline", text = "", icon = "FONTPREVIEW")
        row.prop(self, "useSmallCaps", text = "", icon = "FILE_FONT")   #SYNTAX_OFF

            
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "show_options")
        layout.prop(self, "allowNegativeIndex")
        
    def setHideProperty(self):
        for option in options:
            self.inputs["Material Index"].hide = not self.materialIndex
            self.inputs["Bold"].hide = not self.useBold
            self.inputs["Italic"].hide = not self.useItalic
            
            self.inputs["Underline"].hide = not self.useUnderline
            self.inputs["Underline Position"].hide = not self.useUnderline
            self.inputs["Underline Thickness"].hide = not self.useUnderline
            
            self.inputs["Small Caps"].hide = not self.useSmallCaps
            self.inputs["Small Caps Scale"].hide = not self.useSmallCaps
            
    def getInputSocketNames(self):
        return {"Text Object" : "object",
                "Start" : "start",
                "End" : "end",
                "Material Index" : "materialIndex",
                "Bold" : "bold",
                "Italic" : "italic",
                "Underline" : "underline",
                "Underline Position" : "underlinePosition",
                "Underline Thickness" : "underlineThickness",
                "Small Caps" : "smallCaps",
                "Small Caps Scale" : "smallCapsScale"}
    def getOutputSocketNames(self):
        return {"Object": "object"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        codeLines = []
        if outputUse["Object"]:
            codeLines.append("$object$ = %object%")
        codeLines.append("if %object% is not None:")
        codeLines.append("    textObject = None")
        codeLines.append("    if %object%.type == 'FONT': textObject = %object%.data")
        codeLines.append("    if textObject is not None:")
        if self.useUnderline: codeLines.append(" "*8 + "textObject.underline_position = %underlinePosition%" +
                                        "\n" + " "*8 + "textObject.underline_height = %underlineThickness%")
        if self.useSmallCaps: codeLines.append(" "*8 + "textObject.small_caps_scale = %smallCapsScale%")
        
        codeLines.append(" "*8 + "s, e = start, end")
        if not self.allowNegativeIndex: codeLines.append(" "*8 + "s, e = max(0, start), max(0, end)")
        
        codeLines.append(" "*8 + "for char in textObject.body_format[s:e]:")
        if self.materialIndex: codeLines.append(" "*12 + "char.material_index = %materialIndex%")
        if self.useBold: codeLines.append(" "*12 + "char.use_bold = %bold%")
        if self.useItalic: codeLines.append(" "*12 + "char.use_italic = %italic%")
        if self.useUnderline: codeLines.append(" "*12 + "char.use_underline = %underline%") +

        
        if self.useSmallCaps: codeLines.append(" "*12 + "char.use_small_caps = %smallCaps%")
        
        codeLines.append(" "*8 + "pass")
        
        return "\n".join(codeLines)
