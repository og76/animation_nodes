import bpy, time, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
#from ... data_structures.mesh import *
#from ... mn_cache import *
from mathutils import Vector, Matrix

    #Animation Nodes Adaptive Quad, // ver 0.1
    #deforms a mesh according to deformed quad 
    #by o.g. 19.08.2015
    #on the idea of JoseConseco, based on Adaptive Duplifaces by Alessandro Zomparelli 

class mn_AdaptiveQuad(Node, AnimationNode): 
    bl_idname = "mn_AdaptiveQuad"
    bl_label = "Adaptive Quad"
    #outputUseParameterName = "useOutput"
    
    NormalDeform = bpy.props.BoolProperty(name = "Normal Deform", default = True, description = "Deform Z using vertex normals. If off, use straight Z, on polygon normal")
    UseBbox =  bpy.props.BoolProperty(name = "Use Bound Box", default = True, description = "Use min max. If off, use default 2x2 plane base as reference")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_PolygonSocket", "Polygon")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.inputs.new("mn_VectorListSocket", "Vertex Locations")
        self.inputs.new("mn_FloatSocket", "Z Factor").number = 1.0
        self.outputs.new("mn_VectorListSocket", "Deformed Vertex Locations")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "NormalDeform")
        layout.prop(self, "UseBbox")
        
    def draw_buttons_ext(self, context, layout):
        layout.operator("wm.call_menu", text = "Info / Help", icon = "INFO").name = "mn.show_help_adaptive_quad"
        
    def getInputSocketNames(self):
        return {"Polygon" : "polygon",
                "Matrix" : "matrix",
                "Vertex Locations" : "vertexLocations",
                "Z Factor" : "zFactor"}
    def getOutputSocketNames(self):
        return {"Deformed Vertex Locations" : "deformedVertexLocations"}

    def execute(self, polygon, matrix, vertexLocations, zFactor):
        
        VL = vertexLocations
        QV = polygon.vertices
        
        minX = min(v[0] for v in VL) if self.UseBbox and len(VL)>0 else -1.0
        maxX = max(v[0] for v in VL) if self.UseBbox and len(VL)>0 else 1.0
        minY = min(v[1] for v in VL) if self.UseBbox and len(VL)>0 else -1.0
        maxY = max(v[1] for v in VL) if self.UseBbox and len(VL)>0 else 1.0
        minZ = min(v[2] for v in VL) if self.UseBbox and len(VL)>0 else -1.0
        maxZ = max(v[2] for v in VL) if self.UseBbox and len(VL)>0 else 1.0
        
        #quad
        if len(QV) > 2:
            q0 = QV[0].location
            q1 = QV[1].location
            q2 = QV[2].location
            q3 = QV[-1].location  #escaping non quads, take last
            n0 = QV[0].normal
            n1 = QV[1].normal
            n2 = QV[2].normal
            n3 = QV[-1].normal  #escaping non quads, take last
            np = polygon.normal
        else:   
            #like default 2x2 plane
            q0 = Vector((-1, -1, 0))
            q1 = Vector(( 1, -1, 0))
            q2 = Vector(( 1,  1, 0))
            q3 = Vector((-1,  1, 0))
            n0 = Vector((-1, -1, 1))
            n1 = Vector(( 1, -1, 1))
            n2 = Vector(( 1,  1, 1))
            n3 = Vector((-1,  1, 1))
            np = Vector(( 0,  0, 1))

        DeformedLocations = []
        for v in VL:
            # vert as ratio
            rx = (v[0]-minX) / (maxX-minX) if maxX-minX != 0 else 1.0
            ry = (v[1]-minY) / (maxY-minY) if maxY-minY != 0 else 1.0
            rz = (v[2]-minZ) / (maxZ-minZ) if maxZ-minZ != 0 else 1.0
            #deform xy
            q01 = q0 + (q1 - q0)*rx
            q32 = q3 + (q2 - q3)*rx
            qdef= q01+ (q32-q01)*ry
            #normal verts or normal poly
            if self.NormalDeform:
                n01 = n0 + (n1 - n0)*rx
                n32 = n3 + (n2 - n3)*rx
                ndef= n01+ (n32-n01)*ry
            else:
                ndef= np
            
            DeformedLocations.append(matrix*(qdef+ndef*v[2]*zFactor))

        return DeformedLocations

#to do: take some things out of exe // move to inline exe 


class ShowHelp(bpy.types.Menu):
    bl_idname = "mn.show_help_adaptive_quad"
    bl_label = "Adaptive Quad node | Blender - Animation Nodes"
    bl_icon = "FORCE_TURBULENCE"
    
    helpText = bpy.props.StringProperty(default = "help here")
    noteText = bpy.props.StringProperty(default = "note here")
    helpLines = []
    noteLines = []
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.label('''Help, notes.''', icon = "INFO")
        row = layout.row(align = True)
        
        col = row.column(align = True)
        helpLines = self.helpText.split("\n")
        for li in helpLines:
            if li:
                col.label(text=li)
                
        col = row.column(align = True)
        noteLines = self.noteText.split("\n")
        for li in noteLines:
            if li:
                col.label(text=li)
            
        layout.label("o.g. 08.2015", icon = "INFO")
        
    helpText ='''
Purpose:
        Deform a mesh based on a deformed polygon, preferably quad. 
    On non quads, the results may be harder to control. Triangels are acceptable 
    (see on the forum how it works, a red sphere ...), but more than 4 points 
    Ngons will leave a gap in the fabric.
         Normally it is used in a loop to distribute a mesh on the faces of another, 
    deforming the instances according to the shape and normals of the target polygons.
        You can alter the mesh before or after deformation in any way. You can use 
    more than 1 mesh to distribute and may use adaptives on top of adaptives.(see forum)
    
Inputs:
    [ Polygon ] :  The target polygon, that will deform the instance
    [ Matrix  ] :  The target polygon object matrix, to get the world pos 
                  of the object. Other sources may be used (just a convenience)
    [ Vertex Locations ] :  Vertices of the mesh to be instanced and stretched 
    [ ZFactor ] :  An extra z factor. Will multiply with original z of the mesh (instance)
Outputs:
    [ Deformed Vertex Locations ] :  The vertex locations deformed positions

Options:
    [ Normal Deform ] :  z on the normals (interpolated) or straight up
            [v] On  =  deforming on Z in a "radial" way, based on the normal of vertices. 
                       Instances make a continuous contact on z.
            [.] Off =  deforming xy, but keep z straight up from the poly. 
                       No "radial" deformation, more like buildings on a sphere.
    [ Use Bound Box ] : the reference source for deformation
            [v] On  =  basis of the mesh is the bounding box (xyz min/max). This rectangle 
                       will be morphed into the target poly. Z +/- to the origin of the mesh obj
                       The mesh will be "enclosed" in the polygon area 
            [.] Off =  basis of the mesh is a 2x2 square like the B default plane (-1 to 1) 
                       with the origin 0. This square will be morphed into the target polygon. 
                       Useful when you want the mesh to go outside the polygon base.
'''
    noteText ='''
notes:
    also to be found on:
        http://blenderartists.org/forum
        Addon-Animation-Nodes , page 68, post 1350
    explanations and examples from that point on
    
    This is usually part of a heavy mesh/object generator tree. Some
    slowness is inevitable when over 1000 polygons, and 500 points of mesh.
    But that depends more on the efficiency of the system, rather than 
    this node
    
    The logic of the node being implemented per 1 polygon is to allow
    maximum flexibility in a nodal way. 
    This way, the vertex locations in or out the node can be altered 
    per polygon, per mesh, before or afer deform and in any combination.
    Using loops to iterate the mesh points or the polygons give maximum 
    freedom.
    This is somewhat different form implementing as one whole "black box".
    
    Also, the mesh is only constructed once, at the end of the tree.
    Being usually executed in a loop, and with many mesh instances, 
    any optimization becomes imortant.
    Plus, there is no concern over recalc normals or 
    
    
        
To explore further:
    I will have to adapt the code to the upcoming refactor.
    That will not change the node itself, at most will bring optimization.
    
    I'm also exploring some edge continuity and more options.
    
'''