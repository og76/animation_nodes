import bpy
from ... base_types.node import AnimationNode

class InvertQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvertQuaternionNode"
    bl_label = "Invert Quaternion"

    def create(self):
        self.inputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
        self.outputs.new("an_QuaternionSocket", "Inverted Quaternion", "invertedQuaternion")

    def draw(self, layout):
        layout.separator()

    def getExecutionCode(self):
        return "invertedQuaternion = quaternion.inverted()"