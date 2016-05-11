import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... tree_info import keepNodeState
from ... events import executionCodeChanged, propertyChanged
from ... base_types.node import AnimationNode
from bmesh.ops import triangulate
from mathutils.geometry import tessellate_polygon
from bpy_extras.mesh_utils import ngon_tessellate


polyTypeItems = [
    ("VECTORS", "Vectors in order", "", "", 0),
    ("INDICES", "Simple Poly Index", "", "", 1),
    ("INDICES_LIST", "Poly Indices List", "", "", 2),
    ("MESH", "Mesh Data", "", "", 3),
    ("POLY", "Polygon", "", "", 4),
    ("POLY_LIST", "Polygon List", "", "", 5),
    ("BMESH", "Bmesh", "", "", 6)]

typesWithLoopFix = ["INDICES_LIST", "MESH"]

operationItems = [
    ("TRI", "Simple Mathutils Tri", "Speed ok. Use mathutils simple triangulate", "", 0),
    ("NGON", "Ngon Simple", "Slower 2x-3x. Use extras ngon triangulate", "", 1)  ]
operationItemsFix = operationItems + [
    ("NGON_FIX", "Ngon Fix Loops", "Slower 4x-5x. Use extras ngon. Solve some loop stuf", "", 2)]
    

class PolygonsTessellateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PolygonsTessellateNode"
    bl_label = "Triangulate Polygons"
    searchLabels = ["Tesselate Point List"]

    def polyTypeChanged(self, context):
        self.recreateSockets()
        executionCodeChanged()
        
    def operationChanged(self, context):
        executionCodeChanged()

    operation = EnumProperty(name = "Operation", default = "TRI",
                items = operationItems, update = operationChanged)
    operationFix = EnumProperty(name = "Operation Fix", default = "TRI",
                items = operationItemsFix, update = operationChanged)
                
    polyType = EnumProperty(name = "Polygon  Definition", default = "INDICES_LIST",
                items = polyTypeItems, update = polyTypeChanged)
    bmeshQuad = IntProperty(name = "Quad Method", update = propertyChanged, max = 3, min = 0)
    bmeshNgon = IntProperty(name = "Ngon Method", update = propertyChanged, max = 1, min = 0)

    errorMessage = StringProperty()

    def getActiveEnumOp(self):
        if self.polyType in typesWithLoopFix: 
            return  self.operationFix
        else: return  self.operation

    def create(self):
        self.width = 160
        self.recreateSockets()
        self.polyType = "INDICES_LIST"

    @keepNodeState
    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        type = self.polyType

        if type == "VECTORS":
            self.inputs.new("an_VectorListSocket", "Ordered Vectors", "vertexLocations")
            self.outputs.new("an_PolygonIndicesListSocket", "Triangulated Polygon Indices", "triIndices")
        elif type == "INDICES":
            self.inputs.new("an_VectorListSocket", "Vertex Locations", "vertexLocations")
            self.inputs.new("an_IntegerListSocket", "Polygon Index", "indices")
            self.outputs.new("an_PolygonIndicesListSocket", "Triangulated Polygon Indices", "triIndices")
        elif type == "INDICES_LIST":
            self.inputs.new("an_VectorListSocket", "Vertex Locations", "vertexLocations")
            self.inputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonIndices")
            self.outputs.new("an_PolygonIndicesListSocket", "Triangulated Polygon Indices", "triIndices")
            self.outputs.new("an_IntegerListSocket", "Matching Ngon Indices", "ngonIndices")
        elif type == "MESH":
            self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshData")
            self.outputs.new("an_MeshDataSocket", "Mesh Data", "triMeshData")
            self.outputs.new("an_IntegerListSocket", "Matching Ngon Indices", "ngonIndices")
        elif type == "POLY":
            self.inputs.new("an_PolygonSocket", "Polygon", "polygon")
            self.outputs.new("an_PolygonListSocket", "Triangulated Polygon", "triPolyList")
        elif type == "POLY_LIST":
            self.inputs.new("an_PolygonListSocket", "Polygon List", "polygonList")
            self.outputs.new("an_PolygonListSocket", "Triangulated Polygons", "triPolyList")
            self.outputs.new("an_IntegerListSocket", "Matching Ngon Indices", "ngonIndices")
        elif type == "BMESH":
            self.inputs.new("an_BMeshSocket", "BMesh", "bm")
            self.outputs.new("an_BMeshSocket", "BMesh", "bmOut")


    def draw(self, layout):
        layout.prop(self, "polyType", text = "")
        
        if self.polyType == "BMESH":
            layout.prop(self, "bmeshQuad")
            layout.prop(self, "bmeshNgon")
        elif self.polyType in typesWithLoopFix:
            layout.prop(self, "operationFix", expand = True)
        else: 
            layout.prop(self, "operation", expand = True)
        
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
    
        type = self.polyType
        op = self.getActiveEnumOp()#self.operation
        self.errorMessage = ""
        
        if type == "VECTORS":
            yield "triIndices = []"

            yield "lenV = len(vertexLocations)"
            yield "if lenV > 2:"
            if op == "TRI": 
                yield "    for t in self.tesselateVecs(vertexLocations):"
            elif op == "NGON":
                yield "    for t in self.tesselatePolyNgon(vertexLocations, range(lenV), False):"
#            elif op == "NGON_FIX":
#                yield "    for t in self.tesselatePolyNgon(vertexLocations, range(lenV), True):"
            yield "    " * 2 + "triIndices.append(t)"

        elif type == "INDICES":
            yield "triIndices = []"

            yield "lenV = len(vertexLocations)"
            yield "if lenV > 3:"
            yield "    vertexLocations = [vertexLocations[i] for i in indices]"
            if op == "TRI": 
                yield "    for t in self.tesselateVecs(vertexLocations):"
            elif op == "NGON":
#                yield "    for t in self.tesselatePolyNgon(vertexLocations, indices, False):"
#            elif op == "NGON_FIX":
                yield "    for t in self.tesselatePolyNgon(vertexLocations, indices, True):"
            yield "    " * 2 + "triIndices.append(t)"

        elif type == "INDICES_LIST":
            yield "triIndices, ngonIndices = [], []"

            yield "lenV = len(vertexLocations)"
            yield "if lenV > 3 and polygonIndices:"
            yield "    for p, poly in enumerate(polygonIndices):"
            yield "        if self.isValidPolyIndex(lenV, poly):"
            if op == "TRI": 
                yield "    " * 3 + "for t in self.tesselatePoly(vertexLocations, poly):"
            elif op == "NGON":
                yield "    " * 3 + "for t in self.tesselatePolyNgon(vertexLocations, poly, False):"
            elif op == "NGON_FIX":
                yield "    " * 3 + "for t in self.tesselatePolyNgon(vertexLocations, poly, True):"
            if isLinked["triIndices"]: yield "    " * 4 + "triIndices.append(t)"
            if isLinked["ngonIndices"]: yield "    " * 4 + "ngonIndices.append(p)"


        elif type == "MESH":
            yield "triMeshData = meshData"
            yield "triIndices, ngonIndices = [], []"
        
            yield "vertexLocations, polygonIndices = meshData.vertices, meshData.polygons"
            yield "lenV = len(vertexLocations)"
            yield "if lenV > 2 and polygonIndices:"
            yield "    for p, poly in enumerate(polygonIndices):"
            if op == "TRI": 
                yield "    " * 2 + "for t in self.tesselatePoly(vertexLocations, poly):"
            elif op == "NGON":
                yield "    " * 2 + "for t in self.tesselatePolyNgon(vertexLocations, poly, False):"
            elif op == "NGON_FIX":
                yield "    " * 2 + "for t in self.tesselatePolyNgon(vertexLocations, poly, True):"
            if isLinked["ngonIndices"]: 
                yield "    " * 3 + "ngonIndices.append(p)"
            if isLinked["triMeshData"]: 
                yield "    " * 3 + "triIndices.append(t)"
                yield "    triMeshData.polygons = triIndices"


        elif type == "POLY":
            yield "triPolyList = []"
            yield "if polygon is not None:"
            yield "    vertexLocations = polygon.vertexLocations"
            yield "    lenV = len(vertexLocations)"
        
            yield "    if lenV < 4: triPolyList = [polygon]"
            yield "    else:"
            if op == "TRI": 
                yield "        for t in self.tesselateVecs(vertexLocations):"
            elif op == "NGON":
                yield "        for t in self.tesselatePolyNgon(vertexLocations, range(lenV), False):"
#            elif op == "NGON_FIX":
#                yield "        for t in self.tesselatePolyNgon(vertexLocations, range(lenV), True):"
            yield "    " * 3 + "newPoly = polygon.copy()"
            yield "    " * 3 + "newPoly.vertexLocations = [vertexLocations[i] for i in t]"
            yield "    " * 3 + "triPolyList.append(newPoly)"


        elif type == "POLY_LIST":
            yield "triPolyList, ngonIndices = [], []"
            yield "if polygonList:"
            yield "    for p, polygon in enumerate(polygonList):"
            yield "        vecs = polygon.vertexLocations"
            yield "        lenV = len(vecs)"
        
            yield "        if lenV < 4: triPolyList.append(polygon)"
            yield "        else:"
            if op == "TRI": 
                yield "    " * 3 + "for t in self.tesselateVecs(vecs):"
            elif op == "NGON":
                yield "    " * 3 + "for t in self.tesselatePolyNgon(vecs, range(lenV), False):"
#            elif op == "NGON_FIX":
#                yield "    " * 3 + "for t in self.tesselatePolyNgon(vecs, range(lenV), True):"
            if isLinked["triPolyList"]: 
                yield "    " * 4 + "newPoly = polygon.copy()"
                yield "    " * 4 + "newPoly.vertexLocations = [vecs[i] for i in t]"
                yield "    " * 4 + "triPolyList.append(newPoly)"
            if isLinked["ngonIndices"]: yield "    " * 4 + "ngonIndices.append(p)"

        elif type == "BMESH":
            yield "bmOut = self.bmeshTriangulate(bm, self.bmeshQuad, self.bmeshNgon)"
            #"bm = bm"
        

    def getUsedModules(self):
        return ["mathutils"]



    # funcitons, just testing
    def isValidPolyIndex(self, lenV, poly):
        return 0 <= min(poly) and max(poly) < lenV

    def tesselateVecs(self, vecs):
        return (tuple(t) for t in tessellate_polygon( [[v for v in vecs]] ) )

    def tesselatePoly(self, vecs, poly):
        return (tuple(poly[i] for i in t) for t in tessellate_polygon( [[vecs[v] for v in poly]] ) )


    def tesselatePolyNgon(self, vecs, poly, fix):
        return (tuple(poly[i] for i in t) for t in ngon_tessellate(vecs, poly, fix_loops=fix))

    def bmeshTriangulate(self, bm, quad, ngon):
        bmOut = bm
        faces = bmOut.faces[:]
        triangulate(bmOut, faces=faces, quad_method = quad, ngon_method = ngon)
        return bmOut

