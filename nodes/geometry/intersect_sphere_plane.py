import bpy
from ... base_types.node import AnimationNode

class IntersectSpherePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectSpherePlaneNode"
    bl_label = "Intersect Sphere Plane"

    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Sphere Center", "c")
        self.inputs.new("an_FloatSocket", "Sphere Radius", "r").value = 1
        self.inputs.new("an_VectorSocket", "Plane Point", "point")
        self.inputs.new("an_VectorSocket", "Plane Normal", "normal").value = (0, 0, 1)
        
        self.outputs.new("an_VectorSocket", "Circle Center", "center")
        self.outputs.new("an_FloatSocket", "Circle Radius", "radius")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid").hide = True
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        center  = isLinked["center"]
        radius  = isLinked["radius"]
        isValid = isLinked["isValid"]
        zero = "mathutils.Vector((0,0,0))"
        
        yield "dist = mathutils.geometry.distance_point_to_plane(c, point, normal)"
    
        yield "if abs(dist) <= r and r != 0:"
        if center : yield "    center = (normal * -dist) + c"
        if radius : yield "    radius = math.sqrt((r**2) - (dist**2))"
        if isValid: yield "    isValid = True"
        yield "else:"
        if center : yield "    center =" + zero
        if radius : yield "    radius = 0"
        if isValid: yield "    isValid = False"
        
    def getUsedModules(self):
        return ["mathutils", "math"]
