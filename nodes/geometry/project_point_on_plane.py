import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

planeTypeItems = [  ("POINT_AND_NORMAL", "Plane: Point/Normal", ""),
                    ("MATRIX_XY", "Plane: Matrix XY", "") ]

class ProjectPointOnPlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectPointOnPlaneNode"
    bl_label = "Project Point on Plane" # Closest Point on Plane ?
    
    def planeTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
    
    planeType = EnumProperty(name = "Plane Type", default = "POINT_AND_NORMAL",
        items = planeTypeItems, update = planeTypeChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Point", "point")
        
        self.inputs.new("an_VectorSocket", "Plane Point", "planePoint")
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)
        self.inputs.new("an_MatrixSocket", "Matrix XY Plane", "matrix")
        self.updateHideStatus()
        
        self.outputs.new("an_VectorSocket", "Projection", "projection")
        self.outputs.new("an_FloatSocket", "Distance", "distance")
        
    def draw(self, layout):
        layout.prop(self, "planeType", text = "")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        yield "plane_co, plane_no = " + getPlane(self.planeType)
        yield "int = mathutils.geometry.intersect_line_plane(point, point + plane_no, plane_co, plane_no, False)"
        yield "projection = mathutils.Vector((0, 0, 0)) if int is None else int"
        if isLinked["distance"]: yield "distance = (point - projection).length * (-1 if (point - projection).dot(plane_no) < 0 else 1)"
    
    def getUsedModules(self):
        return ["mathutils"]

    def updateHideStatus(self):
        for socket in self.inputs[1:]: socket.hide = True
        
        if self.planeType == "POINT_AND_NORMAL":
            self.inputs["Plane Point"].hide = False
            self.inputs["Plane Normal"].hide = False
        if self.planeType == "MATRIX_XY":
            self.inputs["Matrix XY Plane"].hide = False

def getPlane(type):
    if type == "POINT_AND_NORMAL": 
        return "planePoint, planeNormal if planeNormal != mathutils.Vector((0, 0, 0)) else mathutils.Vector((0, 0, 1))"
    if type == "MATRIX_XY": 
        return "matrix.to_translation(), matrix.to_3x3() * mathutils.Vector((0, 0, 1))"