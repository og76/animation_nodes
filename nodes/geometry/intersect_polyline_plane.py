import bpy
from bpy.props import *
from mathutils import Vector, geometry
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

#edgesTypeItems = [  ("POINTS", "Points in order", ""),
#                    ("EDGES", "Points by edges", "") ]

planeTypeItems = [  ("POINT_AND_NORMAL", "Plane: Point/Normal", ""),
                    ("MATRIX_XY", "Plane: Matrix XY", "") ]

class IntersectPolylinePlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntersectPolylinePlaneNode"
    bl_label = "Intersect Polyline Plane"
#    
#    def edgesTypeChanged(self, context):
#        self.updateHideStatus()
#        executionCodeChanged()
    
    def planeTypeChanged(self, context):
        self.updateHideStatus()
        executionCodeChanged()
    
#    edgesType = EnumProperty(name = "Plane Type", default = "POINTS",
#        items = edgesTypeItems, update = edgesTypeChanged)
    planeType = EnumProperty(name = "Plane Type", default = "POINT_AND_NORMAL",
        items = planeTypeItems, update = planeTypeChanged)
    cyclic = BoolProperty(name = "Cyclic points", description = "Consider last point to first point also", 
        default = False, update = executionCodeChanged)
        
    def create(self):
        self.width = 160
        self.inputs.new("an_VectorListSocket", "Positions", "positions")
        self.inputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edges")
        self.inputs[1].useIsUsedProperty = True
        self.inputs[1].isUsed = False
        self.inputs.new("an_VectorSocket", "Plane Point", "planePoint")
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)
        self.inputs.new("an_MatrixSocket", "Matrix XY Plane", "matrix")
        self.updateHideStatus()
        
        self.outputs.new("an_VectorListSocket", "Intersections Vector List", "intersections")
        self.outputs.new("an_BooleanSocket", "Is Valid", "isValid").hide = True
        
    def draw(self, layout):
        isLinked = self.getLinkedInputsDict()
        if not self.inputs["Edge Indices"].isUsed: layout.prop(self, "cyclic")
        layout.prop(self, "planeType", text = "")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedInputsDict()
    
        lines = []
        lines.append("intersections, isValid = [], False")
        lines.append("planeCo, planeNo = " + getPlane(self.planeType) )
        if not self.inputs["Edge Indices"].isUsed: 
            lines.append('''
if 1 < len(positions): 
    for i, pos1 in enumerate(positions):''')
            if self.cyclic: lines.append('''
        if i != 0:
            pos0 = positions[i-1]
            dot0, dot1 = (pos0-planeCo).dot(planeNo), (pos1-planeCo).dot(planeNo)
            if dot1 == 0: intersections.append(pos1)
            if (dot0 > 0 and dot1 < 0) or (dot0 < 0 and dot1 > 0):
                intersections.append(mathutils.geometry.intersect_line_plane(pos0, pos1, planeCo, planeNo))''')
            
            else: lines.append('''
        pos0 = positions[i-1]
        dot0, dot1 = (pos0-planeCo).dot(planeNo), (pos1-planeCo).dot(planeNo)
        if dot1 == 0: intersections.append(pos1)
        if (dot0 > 0 and dot1 < 0) or (dot0 < 0 and dot1 > 0):
            intersections.append(mathutils.geometry.intersect_line_plane(pos0, pos1, planeCo, planeNo))''')
            
        else: 
            lines.append('''
if max(itertools.chain([-1], *edges)) <= len(positions): 
            
    for edge in edges:
        pos0, pos1 = positions[edge[0]], positions[edge[1]]
        dot0, dot1 = (pos0-planeCo).dot(planeNo), (pos1-planeCo).dot(planeNo)
        if dot1 == 0: intersections.append(pos1)
        if (dot0 > 0 and dot1 < 0) or (dot0 < 0 and dot1 > 0):
            intersections.append(mathutils.geometry.intersect_line_plane(pos0, pos1, planeCo, planeNo))''')

        return lines
#        yield "intersections, isValid = [], False"
#        
#        yield "planeCo, planeNo = " + getPlane(self.planeType)
#        yield getLinesType(self.edgesType)
#        yield "if len(intersections) > 0: isValid = True"
        
    def getUsedModules(self):
        return ["mathutils", "itertools"]

    def updateHideStatus(self):
        for socket in self.inputs[2:]: socket.hide = True
        
        if self.planeType == "POINT_AND_NORMAL":
            self.inputs["Plane Point"].hide = False
            self.inputs["Plane Normal"].hide = False
        if self.planeType == "MATRIX_XY":
            self.inputs["Matrix XY Plane"].hide = False

#lines.append(getLinesType("EDGES"))
#def getLinesType(type):
#    if type == "POINTS":
#        lines = '''
#    for i, pos1 in enumerate(positions):
#        pos0 = positions[i-1]

#        dot0, dot1 = (pos0-planeCo).dot(planeNo), (pos1-planeCo).dot(planeNo)
#        if dot1 == 0: intersections.append(pos1)'''
#        return lines

#    elif type == "EDGES":
#        lines = '''
#    for edge in edges:
#        pos0, pos1 = positions[edge[0]], positions[edge[1]]

#        dot0, dot1 = (pos0-planeCo).dot(planeNo), (pos1-planeCo).dot(planeNo)
#        if dot1 == 0: intersections.append(pos1)
#        if (dot0 > 0 and dot1 < 0) or (dot0 < 0 and dot1 > 0):
#            intersections.append(mathutils.geometry.intersect_line_plane(pos0, pos1, planeCo, planeNo))'''
#        return lines

def getPlane(type):
    if type == "POINT_AND_NORMAL":
        return "planePoint, planeNormal"
    if type == "MATRIX_XY":
        return "matrix.to_translation(), matrix.to_3x3() * mathutils.Vector((0, 0, 1))"