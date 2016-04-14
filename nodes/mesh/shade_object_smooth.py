import bpy
from ... base_types.node import AnimationNode

class ShadeObjectSmooth(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShadeObjectSmoothNode"
    bl_label = "Shade Object Smooth"

    def create(self):
        self.newInput("Object", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newInput("Boolean", "Smooth", "smooth")
        self.newOutput("Object", "Object", "object")

    def execute(self, object, smooth):
        if getattr(object, "type", "") == "MESH":
            mesh = object.data
            smoothList = [smooth] * len(mesh.polygons)
            mesh.polygons.foreach_set("use_smooth", smoothList)
            mesh.update()
        return object
