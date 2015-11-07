import bpy
from ... base_types.node import AnimationNode

class NormalizeQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NormalizeQuaternionNode"
    bl_label = "Normalize Quaternion"

    def create(self):
        self.inputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
        self.outputs.new("an_QuaternionSocket", "Normalized Quaternion", "normalizedQuaternion")

    def draw(self, layout):
        layout.separator()

    def getExecutionCode(self):
        return "normalizedQuaternion = quaternion.normalized()"