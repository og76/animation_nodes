import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

planeTypeItems = [  ("POINT_AND_NORMAL", "Plane: Point/Normal", ""),
                    ("MATRIX_XY", "Plane: Matrix XY", "") ]

class IntersectSplinePlaneNode(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_IntersectSplinePlaneNode"
    bl_label = "Intersect Spline Plane"
    
    def planeTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
    
    planeType = EnumProperty(name = "Plane Type", default = "POINT_AND_NORMAL",
        items = planeTypeItems, update = planeTypeChanged)
    #amount = IntProperty(name = "Amount of Samples", default = 24, 
    #                        update = executionCodeChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_SplineSocket", "Spline", "spline").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_IntegerSocket", "Amount", "amount").value = 24
        
        self.inputs.new("an_VectorSocket", "Plane Point", "planePoint")
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)
        self.inputs.new("an_MatrixSocket", "Matrix XY Plane", "matrix")
        self.updateHideStatus()
        
        self.outputs.new("an_VectorListSocket", "Intersections Vector List", "intersections")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid")
        
    def draw(self, layout):
        layout.prop(self, "parameterType", text = "")
        layout.prop(self, "planeType", text = "")
        
    def drawAdvanced(self, layout):
        #layout.prop(self, "amount", text = "Samples amount")
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")
        
    def getExecutionCode(self):
        
        yield "intersections, isValid = [], False"
        
        lines = []
        yield "spline.update()"
        yield "if spline.isEvaluable:"
        yield "    positions = " + getParameterType(self.parameterType)
        yield "    planeCo, planeNo = " + getPlane(self.planeType)
        yield "    for i, pos in enumerate(positions):"
        yield " "*8 + "if i != 0:"        # this goes for non cyclic splines only ?
        yield " "*12 + "pos0 = positions[i-1]"
        yield " "*12 + "dot0, dot1 = (pos0-planeCo).dot(planeNo), (pos-planeCo).dot(planeNo)"
        yield " "*12 + "if dot1 == 0: intersections.append(pos)"
        yield " "*12 + "if (dot0 > 0 and dot1 < 0) or (dot0 < 0 and dot1 > 0):"
        yield " "*12 + "    intersections.append(mathutils.geometry.intersect_line_plane(pos0, pos, planeCo, planeNo))"
        yield "    if len(intersections) > 0: isValid = True"
        
    def getUsedModules(self):
        return ["mathutils"]

    def updateHideStatus(self):
        for socket in self.inputs[2:]: socket.hide = True
        
        if self.planeType == "POINT_AND_NORMAL":
            self.inputs["Plane Point"].hide = False
            self.inputs["Plane Normal"].hide = False
        if self.planeType == "MATRIX_XY":
            self.inputs["Matrix XY Plane"].hide = False


def getParameterType(type):
    if type == "UNIFORM":
        return "spline.getUniformSamples(amount, 0, 1, self.resolution)"
    elif type == "RESOLUTION":
        return "spline.getSamples(amount, 0, 1)"

def getPlane(type):
    if type == "POINT_AND_NORMAL":
        return "planePoint, planeNormal"
    if type == "MATRIX_XY":
        return "matrix.to_translation(), matrix.to_3x3() * mathutils.Vector((0, 0, 1))"