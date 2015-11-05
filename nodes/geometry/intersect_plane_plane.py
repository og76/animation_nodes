import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

planeTypeItems = [  ("POINT_AND_NORMAL", "Plane: Point/ Normal", ""),
                    ("MATRIX_XY", "Plane: Matrix XY", "") ]

class IntersectPlanePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectPlanePlaneNode"
    bl_label = "Intersect Plane Plane"
    
    def planeTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
    
    planeType1 = EnumProperty(name = "Plane Type 1", default = "POINT_AND_NORMAL",
        items = planeTypeItems, update = planeTypeChanged)
    planeType2 = EnumProperty(name = "Plane Type 2", default = "POINT_AND_NORMAL",
        items = planeTypeItems, update = planeTypeChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Plane 1 Point", "planePoint1")
        self.inputs.new("an_VectorSocket", "Plane 1 Normal", "planeNormal1")
        self.inputs.new("an_MatrixSocket", "Matrix XY Plane 1", "matrix1")
        
        self.inputs.new("an_VectorSocket", "Plane 2 Point", "planePoint2")
        self.inputs.new("an_VectorSocket", "Plane 2 Normal", "planeNormal2")
        self.inputs.new("an_MatrixSocket", "Matrix XY Plane 2", "matrix2")
        self.updateHideStatus()
        
        self.outputs.new("an_VectorSocket", "Intersection Vector", "intersection")
        self.outputs.new("an_VectorSocket", "Dorection Vector", "direction")
        
    def draw(self, layout):
        layout.prop(self, "planeType1", text = "1:")
        layout.prop(self, "planeType2", text = "2:")
        
    def getExecutionCode(self):
        yield "p1_co, p1_no = " + getPlane(self.planeType1, 1)
        yield "p2_co, p2_no = " + getPlane(self.planeType2, 2)
        yield "int = mathutils.geometry.intersect_plane_plane(p1_co, p1_no, p2_co, p2_no)"
        
        yield "if int != (None, None): intersection, direction = int"
        yield "else: intersection, direction =  mathutils.Vector((0, 0, 0)),  mathutils.Vector((0, 0, 0))"
        
    def getUsedModules(self):
        return ["mathutils"]

    def updateHideStatus(self):
        for socket in self.inputs: socket.hide = True
        
        if self.planeType1 == "POINT_AND_NORMAL":
            self.inputs["Plane 1 Point"].hide = False
            self.inputs["Plane 1 Normal"].hide = False
        if self.planeType1 == "MATRIX_XY":
            self.inputs["Matrix XY Plane 1"].hide = False

        if self.planeType2 == "POINT_AND_NORMAL":
            self.inputs["Plane 2 Point"].hide = False
            self.inputs["Plane 2 Normal"].hide = False
        if self.planeType2 == "MATRIX_XY":
            self.inputs["Matrix XY Plane 2"].hide = False

def getPlanes(type, n):
    if type == "POINT_AND_NORMAL": 
        return "planePoint" + str(n) + ", planeNormal" + str(n)
    if type == "MATRIX_XY": 
        return "matrix" + str(n) + ".to_translation(), matrix" + str(n) + ".to_3x3() * mathutils.Vector((0, 0, 1))"