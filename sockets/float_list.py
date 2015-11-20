import bpy
from .. base_types.socket import AnimationNodeSocket

class FloatListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FloatListSocket"
    bl_label = "Float List Socket"
    dataType = "Float List"
    allowedInputTypes = ["Float List", "Integer List"]
    drawColor = (0.4, 0.4, 0.7, 0.5)
    storable = True
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
