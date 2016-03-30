import bpy
from ... base_types.node import AnimationNode

class IntersectLinePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLinePlaneNode"
    bl_label = "Intersect Line Plane"

    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Line Start", "lineStart")
        self.inputs.new("an_VectorSocket", "Line End", "lineEnd").value = (0, 0, 1)

        self.inputs.new("an_VectorSocket", "Plane Point", "planePoint")
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)

        self.outputs.new("an_VectorSocket", "Intersection", "intersection")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        intersection = isLinked["intersection"]
        isValid = isLinked["isValid"]
        
        yield "if planeNormal.length_squared == 0: planeNormal = mathutils.Vector((0, 0, 1))"
        yield "int = mathutils.geometry.intersect_line_plane(lineStart, lineEnd, planePoint, planeNormal, False)"

        yield "if int is None:"
        if intersection : yield "    intersection = mathutils.Vector((0, 0, 0))"
        if isValid: yield "    isValid = False"
        yield "else:"
        if intersection : yield "    intersection = int"
        if isValid: yield "    isValid = True"

    def getUsedModules(self):
        return ["mathutils"]
