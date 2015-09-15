import bpy#, time, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mathutils import Vector, Matrix

    #Animation Nodes Poly Underware // ver 0.1
    #create a wireframe in centers/mids of poly
    #by o.g. 03.09.2015
    #started from dual polyhedron idea on forum 

class mn_PolyUnderware(Node, AnimationNode): 
    bl_idname = "mn_PolyUnderware"
    bl_label = "Poly Underware"
    #outputUseParameterName = "useOutput"
    
    NormalDeform = bpy.props.BoolProperty(name = "Normal Deform", default = True, description = "Deform Z using vertex normals. If off, normal is an offset, on polygon normal")
    UseCentral =  bpy.props.BoolProperty(name = "Use Central Poly", default = True, description = "Create central poly, at the stripes intersection. If off, there will be a hole")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_PolygonSocket", "Polygon")
#        self.inputs.new("mn_IntSocket", "Subdivision").integer = 1
        self.inputs.new("mn_FloatSocket", "Width Factor").number = 0.5
        self.inputs.new("mn_FloatSocket", "Smooth Factor").number = 0.0
        self.inputs.new("mn_FloatSocket", "Offset").number = 0.0
        self.outputs.new("mn_VectorListSocket", "Vertex Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygons Indices")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "NormalDeform")
        layout.prop(self, "UseCentral")
        
    def draw_buttons_ext(self, context, layout):
        layout.operator("wm.call_menu", text = "Info / Help", icon = "INFO").name = "mn.show_help_poly_underware"
        
    def getInputSocketNames(self):
        return {"Polygon" : "polygon",
                "Width Factor" : "widthFactor",
                "Smooth Factor" : "smoothFactor",
                "Offset" : "offset"}
                
    def getOutputSocketNames(self):
        return {"Vertex Locations" : "vertexLocations",
                "Polygons Indices" : "polygonsIndices"}

    def execute(self, polygon, widthFactor, smoothFactor, offset):
        
        vertexLocations = []
        polygonsIndices = []
        
            #factors relation
        wFactor = min(max(widthFactor, 0), 1)   #widthFactor clamp 
        if (1 - wFactor) == 0: 
            sFactor = min(max(smoothFactor, 0), 1) 
            lerpfac = 1-sFactor      #corner filled / full face
        else: 
            sFactor = min(max(smoothFactor, - wFactor / (1 - wFactor)), 1)
            lerpfac = wFactor + (1 - wFactor) * sFactor 
              #smoothFactor clamp on wFactor
        
        Center = polygon.center.lerp(polygon.center + polygon.normal, offset) if self.NormalDeform else polygon.center     #find center with bisectors or so, for concave poly
        polyVerts = polygon.vertices

        stripesPoly = []
        centralPoly = []
        polyIndices = []
        
        for i, polyVert in enumerate(polyVerts):
                
                #stripeVerts
            stripeVerts = []
            
            V0 = Center.lerp(polyVert.location, lerpfac)  #todo normals for edge, center and smooth normal, with interpolation, maybe -1 for the edge
                        
            i2 = (i+1) % len(polyVerts)                                             #if i < len(polyVerts) else -1
            middle = polyVert.location.lerp(polyVerts[i2].location, 0.5)
            
            V1 = middle.lerp(polyVert.location, wFactor)
            V2 = middle.lerp(polyVerts[i2].location, wFactor)                       
            
            stripeVerts = [V0, V1, V2]                                              #to do V01 V02 .. subd
            
            stripesPoly.extend(stripeVerts)     #append(v for v in stripeVerts)     #what is faster?
            
                #poli indices for stripes                                           #simple quads
            Pindex = [3 * i, 3 * i + 1, 3 * i + 2, ( (3 * i + 3) % (3*len(polyVerts)) )]   #to do subd #if (3 * i + 3) <= (3*len(polyVerts)-1) else 0
            polyIndices.append( Pindex )
                #poli indices for central 
            centralPoly.append( 3 * i )  #center will be Ngon just like the source poly, we'l see for subd
        
        if self.UseCentral:
            polyIndices.append(centralPoly)
                            
        vertexLocations = stripesPoly
        polygonsIndices = polyIndices
            
            
        return vertexLocations, polygonsIndices

#to do: take some things out of exe // move to inline exe 


class ShowHelp(bpy.types.Menu):
    bl_idname = "mn.show_help_poly_underware"
    bl_label = "Poly Underware node | Blender - Animation Nodes"
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
            
        layout.label("o.g. 09.2015", icon = "INFO")
        
    helpText ='''
Purpose:
        Creates a mesh based on centers and edge mids of a polygon, a wireframe
    going thru middle of poly. Mostly like an alternative to normal wireframe.
    It actually creates stripes, not wireframes as in edges, with possible vary
    of width or smoothness.
        
        Normally it is used in a loop to distribute this wire/network on the faces of 
    another mesh, deforming according to the shape and normals of the target polygons.
        You can alter the smooth or width per polygon. You can use other loops before 
    or after to get more variation.
    
        The width and smooth factors are related. Smooth depends on the width and
    actually goes with negative values from center of poly till (1) the corners.
    
        The stripes are made of quads, but the center polys are 3, 4 or Ngons like 
    the original poly.
    
Inputs:    
    [ Polygon ]          :  The target polygon, base for the strips
    [ Width Factor ]     :  How wide is the stripe. Factor 0-1 relative to base polygon 
    [ Smooth Factor ]    :  Smooth/round edges of stripes around verts. 
                            Factor is relative to base polygon and Width. 
                     It goes from 0-1 for noSmooth-up to cornes, 
                     but can go <0 till the center of the polygon
Outputs:
    [ Vertex Locations ] : The vertex locations of new mesh (stripes)
    [ Polygons Indices ] : Polygons Indices of new mesh (stripes)
                     use these two in the usual combine mesh to create mesh in AN ways.
                     or just use the verts or so.

'''
    noteText ='''
notes:
    I flirted with other names: 
        
        Poly's secret, sexy Poly, Poly tanga, mesh cleavage, cover your Poly ...
    And for the parameters, polygon = chick, width = thong factor, curvy, etc
    
    (it should probably be called Mid Wireframe or so)
    
    also to be found on:
        http://blenderartists.org/forum
        Addon-Animation-Nodes , page xx, post 13xx
    explanations and examples from that point on
    
    This is usually part of a mesh generator tree. Some slowness may
    be there for many polygons.
    
    The logic of the node being implemented per 1 polygon is to allow
    maximum flexibility in a nodal way. 
    This way, the vertex locations out the node can be altered 
    per polygon, per mesh, polygons can be altered before creating the stripes.
    This is somewhat different form implementing as one whole "black box".
    
    Also, the mesh is only constructed once, at the end of the tree.

To explore further:
    I will have to adapt the code to the upcoming refactor.
    That will not change the node itself, at most will bring optimization.
    
    I'm also exploring some edge continuity and more options, z offset, 
    normal smooth, subdivisions, generating or not the center polys etc.
    
    
ps: keep your panties on, Poly!

'''