import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. algorithms.interpolation import getInterpolationPreset

categoryItems = [
    ("LINEAR", "Linear", "", "IPO_LINEAR", 0),
    ("SINUSOIDAL", "Sinusoidal", "", "IPO_SINE", 1),
    ("QUADRATIC", "Quadratic", "", "IPO_QUAD", 2),
    ("CUBIC", "Cubic", "", "IPO_CUBIC", 3),
    ("QUARTIC", "Quartic", "", "IPO_QUART", 4),
    ("QUINTIC", "Quintic", "", "IPO_QUINT", 5),
    ("EXPONENTIAL", "Exponential", "", "IPO_EXPO", 6),
    ("CIRCULAR", "Circular", "", "IPO_CIRC", 7),
    ("BACK", "Back", "", "IPO_BACK", 8),
    ("BOUNCE", "Bounce", "", "IPO_BOUNCE", 9),
    ("ELASTIC", "Elastic", "", "IPO_ELASTIC", 10)]

class InterpolationSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_InterpolationSocket"
    bl_label = "Interpolation Socket"
    dataType = "Interpolation"
    allowedInputTypes = ["Interpolation"]
    drawColor = (0.7, 0.4, 0.3, 1)
    hashable = True
    storable = True

    category = EnumProperty(name = "Interpolation Category", default = "LINEAR",
                            items = categoryItems, update = propertyChanged)

    easeIn = BoolProperty(name = "Ease In", default = False, update = propertyChanged)
    easeOut = BoolProperty(name = "Ease Out", default = True, update = propertyChanged)

    def drawProperty(self, layout, text):
        col = layout.column(align = True)
        if text != "": col.label(text)
        row = col.row(align = True)
        row.prop(self, "category", text = "")
        if self.category != "LINEAR":
            row.prop(self, "easeIn", text = "", icon = "IPO_EASE_IN")
            row.prop(self, "easeOut", text = "", icon = "IPO_EASE_OUT")

    def getValue(self):
        return getInterpolationPreset(self.category, self.easeIn, self.easeOut)

    def getProperty(self):
        return self.category, self.easeIn, self.easeOut

    def setProperty(self, data):
        self.category, self.easeIn, self.easeOut = data
