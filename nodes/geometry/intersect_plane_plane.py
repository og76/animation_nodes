import bpy
from ... base_types.node import AnimationNode

class IntersectPlanePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectPlanePlaneNode"
    bl_label = "Intersect Plane Plane"

    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Plane 1 Point", "p1_co")
        self.inputs.new("an_VectorSocket", "Plane 1 Normal", "p1_no").value = (1, 0, 0)
        self.inputs.new("an_VectorSocket", "Plane 2 Point", "p2_co")
        self.inputs.new("an_VectorSocket", "Plane 2 Normal", "p2_no").value = (0, 0, 1)
        
        self.outputs.new("an_VectorSocket", "Intersection Point", "intersection")
        self.outputs.new("an_VectorSocket", "Direction Vector", "direction")
        self.outputs.new("an_FloatSocket", "Angle", "angle")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid")
          
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        intersection  = isLinked["intersection"]
        direction  = isLinked["direction"]
        angle  = isLinked["angle"]
        isValid = isLinked["isValid"]
        zero = "mathutils.Vector((0,0,0))"
        
        for i in [1, 2]:
            i = str(i)
            yield "if p{}_no =" + zero + ": p{}_no = mathutils.Vector((0, 0, 1))".format(i, i)
        
        yield "int = mathutils.geometry.intersect_plane_plane(p1_co, p1_no, p2_co, p2_no)"
        
        yield "if int != (None, None):"
        if intersection : yield "    intersection = int[0]"
        if direction : yield "    direction = int[1]"
        if isValid: yield "    isValid = True"
        yield "else: "
        if intersection : yield "    intersection =" + zero
        if direction : yield "    direction =" + zero
        if isValid: yield "    isValid = False"
    
        if angle  : yield "angle = math.pi - (p1_no.angle(p2_no, math.pi))"
        
    def getUsedModules(self):
        return ["mathutils, math"]
