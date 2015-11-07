import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

planeTypeItems = [  ("POINT_AND_NORMAL", "Plane: Point/ Normal", ""),
                    ("MATRIX_XY", "Plane: Matrix XY", "") ]

class IntersectLinePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectLinePlaneNode"
    bl_label = "Intersect Line Plane"
    
    def planeTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
    
    planeType = EnumProperty(name = "Plane Type", default = "POINT_AND_NORMAL",
        items = planeTypeItems, update = planeTypeChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Line Start", "lineStart")
        self.inputs.new("an_VectorSocket", "Line End", "lineEnd").value = (0, 0, 1)
        
        self.inputs.new("an_VectorSocket", "Plane Point", "planePoint")
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)
        self.inputs.new("an_MatrixSocket", "Matrix XY Plane", "matrix")
        self.updateHideStatus()
        
        self.outputs.new("an_VectorSocket", "Intersection Vector", "intersection")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid")
        
    def draw(self, layout):
        layout.prop(self, "planeType", text = "")
        
    def getExecutionCode(self):
        yield "plane_co, plane_no = " + getPlane(self.planeType)
        yield "int = mathutils.geometry.intersect_line_plane(lineStart, lineEnd, plane_co, plane_no, False)"
        
        yield "if int is None: intersection, isValid = mathutils.Vector((0, 0, 0)), False"
        yield "else: intersection, isValid = int, True"
        
    def getUsedModules(self):
        return ["mathutils"]

    def updateHideStatus(self):
        for socket in self.inputs[2:]: socket.hide = True
        
        if self.planeType == "POINT_AND_NORMAL":
            self.inputs["Plane Point"].hide = False
            self.inputs["Plane Normal"].hide = False
        if self.planeType == "MATRIX_XY":
            self.inputs["Matrix XY Plane"].hide = False

def getPlane(type):
    if type == "POINT_AND_NORMAL": 
        return "planePoint, planeNormal"
    if type == "MATRIX_XY": 
        return "matrix.to_translation(), matrix.to_3x3() * mathutils.Vector((0, 0, 1))"