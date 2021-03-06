import bpy
from bpy.props import *
from mathutils import Quaternion
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class QuaternionSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_QuaternionSocket"
    bl_label = "Quaternion Socket"
    dataType = "Quaternion"
    allowedInputTypes = ["Quaternion"]
    drawColor = (0.8, 0.6, 0.3, 1.0)
    storable = True
    hashable = False

    value = FloatVectorProperty(default = [1, 0, 0, 0], size = 4, update = propertyChanged)

    def drawProperty(self, layout, text):
        col = layout.column(align = True)
        if text != "": col.label(text)
        col.prop(self, "value", index = 0, text = "W")
        col.prop(self, "value", index = 1, text = "X")
        col.prop(self, "value", index = 2, text = "Y")
        col.prop(self, "value", index = 3, text = "Z")

    def getValue(self):
        return Quaternion(self.value)

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value[:]

    def getCopyExpression(self):
        return "value.copy()"
