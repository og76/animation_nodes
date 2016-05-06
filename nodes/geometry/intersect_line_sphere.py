import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class IntersectLineSphereNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLineSphereNode"
    bl_label = "Intersect Line Sphere"
    
    clip = BoolProperty(description = "Only consider intersections inside the line, otherwise line is infinite", 
        default = False, update = propertyChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Line Start", "lineStart")
        self.inputs.new("an_VectorSocket", "Line End", "lineEnd").value = (0, 0, 1)
        self.inputs.new("an_VectorSocket", "Sphere Center", "center")
        self.inputs.new("an_FloatSocket", "Sphere Radius", "radius").value = 1
        
        self.outputs.new("an_VectorSocket", "Intersection 1", "intersection1")
        self.outputs.new("an_VectorSocket", "Intersection 2", "intersection2")
        self.outputs.new("an_BooleanSocket", "Is Valid 1", "isValid1").hide = True
        self.outputs.new("an_BooleanSocket", "Is Valid 2", "isValid2").hide = True
        
    def draw(self, layout):
        layout.prop(self, "clip")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        intersection1  = isLinked["intersection1"]
        intersection2  = isLinked["intersection2"]
        isValid1 = isLinked["isValid1"]
        isValid2 = isLinked["isValid2"]
        
        yield "if lineStart == lineEnd:"
        if intersection1 : yield "    intersection1 = center"
        if intersection2 : yield "    intersection2 = center"
        if isValid1: yield "    isValid1 = False"
        if isValid2: yield "    isValid2 = False"
        yield "else:"
        yield "    int1, int2 = mathutils.geometry.intersect_line_sphere(lineStart, lineEnd, center, radius, self.clip)"
        yield "    if int1 != None:"
        if intersection1 : yield "        intersection1 = int1"
        if isValid1: yield "        isValid1 = True"
        yield "    else:"
        if intersection1 : yield "        intersection1 = center"
        if isValid1: yield "        isValid1 = False"
        yield "    if int2 != None:"
        if intersection2 : yield "        intersection2 = int2"
        if isValid2: yield "        isValid2 = True"
        yield "    else:"
        if intersection2 : yield "        intersection2 = center"
        if isValid2: yield "        isValid2 = False"

#        yield "    intersection1, isValid1 = (int1, True) if int1 != None else (center, False)"
#        yield "    intersection2, isValid2 = (int2, True) if int2 != None else (center, False)"
        
    def getUsedModules(self):
        return ["mathutils"]