import bpy, random, colorsys
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

sourceTypeItems = [
    ("RGB", "RGB", "Red, Green, Blue"),            #"Red, Green, Blue"
    ("HSV", "HSV", "Hue, Saturation, Value"),      #Hue, Saturation, Value"
    ("HLS", "HLS", "Hue, Lightness, Saturation"),  #"Hue, Lightness, Saturation"
    ("YIQ", "YIQ", "Luma, Chrominance")]           #"Luma, Chrominance"

class mn_ConvertColor(Node, AnimationNode):
    bl_idname = "mn_ConvertColor"
    bl_label = "Convert Color"
    isDetermined = True
    
    def sourceTypeChanged(self, context):
        self.updateHideStatus()
        nodePropertyChanged(self, context)
    
    sourceType = bpy.props.EnumProperty(items = sourceTypeItems, default = "RGB", name = "Source Type", update = sourceTypeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Red")
        self.inputs.new("mn_FloatSocket", "Green")
        self.inputs.new("mn_FloatSocket", "Blue")
        self.inputs.new("mn_FloatSocket", "Hue")
        self.inputs.new("mn_FloatSocket", "Saturation")
        self.inputs.new("mn_FloatSocket", "Value")
        #same H, S
        self.inputs.new("mn_FloatSocket", "Luminance")
        self.inputs.new("mn_FloatSocket", "Y Luma")
        self.inputs.new("mn_FloatSocket", "I In phase")
        self.inputs.new("mn_FloatSocket", "Q Quadrature")

        self.inputs.new("mn_FloatSocket", "Alpha").number = 1
        self.updateHideStatus()
        self.outputs.new("mn_ColorSocket", "Color")
        allowCompiling()

    def draw_buttons(self, context, layout):
        layout.prop(self, "sourceType")

    def getInputSocketNames(self):
        return {"Red" : "red",
                "Green" : "green",
                "Blue" : "blue",
                "Hue" : "hue",
                "Saturation" : "saturation",
                "Value" : "value",
                "Luminance" : "luminance",
                "Y Luma" : "y",
                "I In phase" : "i",
                "Q Quadrature" : "q",
                "Alpha" : "alpha"}
    def getOutputSocketNames(self):
        return {"Color" : "color"}

    def execute(self, red, green, blue, hue, saturation, value, luminance, y, i, q, alpha):
        if self.sourceType == "RGB":    C= [red, green, blue]
        elif self.sourceType == "HSV":  C= colorsys.hsv_to_rgb(hue, saturation, value)
        elif self.sourceType == "HLS":  C= colorsys.hls_to_rgb(hue, luminance, saturation)
        elif self.sourceType == "YIQ":  C= colorsys.yiq_to_rgb(y, i, q)
            
        return [C[0], C[1], C[2], alpha]
        
    def updateHideStatus(self):
        self.inputs["Red"].hide = True
        self.inputs["Green"].hide = True
        self.inputs["Blue"].hide = True
        
        self.inputs["Hue"].hide = True
        self.inputs["Saturation"].hide = True
        self.inputs["Value"].hide = True
        
        self.inputs["Luminance"].hide = True
        
        self.inputs["Y Luma"].hide = True
        self.inputs["I In phase"].hide = True
        self.inputs["Q Quadrature"].hide = True
        
        if self.sourceType == "RGB":
            self.inputs["Red"].hide = False
            self.inputs["Green"].hide = False
            self.inputs["Blue"].hide = False
        elif self.sourceType == "HSV":
            self.inputs["Hue"].hide = False
            self.inputs["Saturation"].hide = False
            self.inputs["Value"].hide = False
        elif self.sourceType == "HLS":
            self.inputs["Hue"].hide = False
            self.inputs["Luminance"].hide = False
            self.inputs["Saturation"].hide = False
        elif self.sourceType == "YIQ":
            self.inputs["Y Luma"].hide = False
            self.inputs["I In phase"].hide = False
            self.inputs["Q Quadrature"].hide = False