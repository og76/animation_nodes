import bpy
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... base_types.node import AnimationNode

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
upAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DirectionToRotationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DirectionToRotationNode"
    bl_label = "Direction to Rotation"

    trackAxis = EnumProperty(items = trackAxisItems, update = propertyChanged, default = "Z")
    upAxis = EnumProperty(items = upAxisItems, update = propertyChanged, default = "X")

    def create(self):
        self.inputs.new("an_VectorSocket", "Direction", "direction")
        self.outputs.new("an_EulerSocket", "Euler", "euler")
        self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion").hide = True
        self.width += 20

    def draw(self, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "upAxis", expand = True)

        if self.trackAxis == self.upAxis:
            layout.label("Must be different", icon = "ERROR")

    def execute(self, direction):
        if self.trackAxis == self.upAxis: return Vector((0, 0, 0))
        quaternion = direction.to_track_quat(self.trackAxis, self.upAxis)
        return quaternion.to_euler(), quaternion
