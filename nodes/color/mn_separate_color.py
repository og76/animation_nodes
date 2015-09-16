import bpy, random, colorsys
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

targetTypeItems = [
    ("RGB", "RGB", "Red, Green, Blue"),            #"Red, Green, Blue"
    ("HSV", "HSV", "Hue, Saturation, Value"),      #Hue, Saturation, Value"
    ("HSL", "HSL", "Hue, Saturation, Lightness"),  #"Hue, Lightness, Saturation"
    ("YIQ", "YIQ", "Luma, Chrominance")]           #"Luma, Chrominance"

class mn_SeparateColor(Node, AnimationNode):
    bl_idname = "mn_SeparateColor"
    bl_label = "Separate Color"
    #isDetermined = True
    
    def targetTypeChanged(self, context):
        self.updateHideStatus()
        nodePropertyChanged(self, context)
    
    targetType = bpy.props.EnumProperty(items = targetTypeItems, default = "RGB", name = "Target Type", update = targetTypeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ColorSocket", "Color")
        
        self.outputs.new("mn_FloatSocket", "Red")
        self.outputs.new("mn_FloatSocket", "Green")
        self.outputs.new("mn_FloatSocket", "Blue")
        
        self.outputs.new("mn_FloatSocket", "Hue")
        self.outputs.new("mn_FloatSocket", "Saturation")
        self.outputs.new("mn_FloatSocket", "Value")
        #same H, S
        self.outputs.new("mn_FloatSocket", "Lightness")
        
        self.outputs.new("mn_FloatSocket", "Y Luma")
        self.outputs.new("mn_FloatSocket", "I In phase")
        self.outputs.new("mn_FloatSocket", "Q Quadrature")

        self.outputs.new("mn_FloatSocket", "Alpha")#.number = 1
        self.updateHideStatus()
        allowCompiling()

    def draw_buttons(self, context, layout):
        layout.prop(self, "targetType")

    def getInputSocketNames(self):
        return {"Color" : "color"}
    def getOutputSocketNames(self):
        return {"Red" : "red",
                "Green" : "green",
                "Blue" : "blue",
                "Hue" : "hue",
                "Saturation" : "saturation",
                "Value" : "value",
                "Lightness" : "lightness",
                "Y Luma" : "y",
                "I In phase" : "i",
                "Q Quadrature" : "q",
                "Alpha" : "alpha"}

    def execute(self, color):
        r, g, b, h, s, v, l, y, i, q = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 
        if self.targetType == "RGB":    r, g, b = color[0], color[1], color[2]
        elif self.targetType == "HSV":  h, s, v = colorsys.rgb_to_hsv(color[0], color[1], color[2])
        elif self.targetType == "HSL":  h, l, s = colorsys.rgb_to_hls(color[0], color[1], color[2]) #attention to the HLS order!
        elif self.targetType == "YIQ":  y, i, q = colorsys.rgb_to_yiq(color[0], color[1], color[2])
        alpha = color[3]
            
        return r, g, b, h, s, v, l, y, i, q, alpha
        
    def updateHideStatus(self):
        self.outputs["Red"].hide = True
        self.outputs["Green"].hide = True
        self.outputs["Blue"].hide = True
        
        self.outputs["Hue"].hide = True
        self.outputs["Saturation"].hide = True
        self.outputs["Value"].hide = True
        
        self.outputs["Lightness"].hide = True
        
        self.outputs["Y Luma"].hide = True
        self.outputs["I In phase"].hide = True
        self.outputs["Q Quadrature"].hide = True
        
        if self.targetType == "RGB":
            self.outputs["Red"].hide = False
            self.outputs["Green"].hide = False
            self.outputs["Blue"].hide = False
        elif self.targetType == "HSV":
            self.outputs["Hue"].hide = False
            self.outputs["Saturation"].hide = False
            self.outputs["Value"].hide = False
        elif self.targetType == "HSL":
            self.outputs["Hue"].hide = False
            self.outputs["Saturation"].hide = False
            self.outputs["Lightness"].hide = False
        elif self.targetType == "YIQ":
            self.outputs["Y Luma"].hide = False
            self.outputs["I In phase"].hide = False
            self.outputs["Q Quadrature"].hide = False