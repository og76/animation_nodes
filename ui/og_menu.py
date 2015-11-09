import bpy
from bpy.props import *
from .. tree_info import getSubprogramNetworks
from .. utils.nodes import getAnimationNodeTrees

class OGMenu(bpy.types.Menu):
    bl_idname = "an_og_menu"
    bl_label = "OG Menu"

    def draw(self, context):

        layout = self.layout
        
        layout.label("GEOMETRY")
        insertNode(layout, "an_AdaptiveQuad", "Adaptive Quad")
        insertNode(layout, "an_PolyUnderwearNode", "Poly Underwear")
        layout.separator()
        insertNode(layout, "an_ProjectPointOnLineNode", "Project Point on Line")
        insertNode(layout, "an_ProjectPointOnPlaneNode", "Project Point on Plane")
        insertNode(layout, "an_PointListNormalNode", "Point List Normal")
        insertNode(layout, "an_BarycentricTransformNode", "Barycentric Transform")
        layout.separator()
        insertNode(layout, "an_IntersectLineLineNode", "Intersect Line Line")
        insertNode(layout, "an_IntersectLinePlaneNode", "Intersect Line Plane")
        insertNode(layout, "an_IntersectPolylinePlaneNode", "Intersect Polyline Plane")
        insertNode(layout, "an_IntersectSplinePlaneNode", "Intersect Spline Plane ??")
        insertNode(layout, "an_IntersectLineSphereNode", "Intersect Line Sphere")
        insertNode(layout, "an_IntersectPlanePlaneNode", "Intersect Plane Plane")
        layout.separator()
        layout.label("VEC/ROT/MAT")
        insertNode(layout, "an_VectorAngleNode", "Vector Angle")
        insertNode(layout, "an_VectorAngle2DNode", "Vector 2D Angle")
        layout.separator()
        insertNode(layout, "an_ShearMatrixNode", "Shear Matrix")
        insertNode(layout, "an_RoundDataNode", "Round Vector", {"dataType" : repr("Vector")})
        insertNode(layout, "an_RoundDataNode", "Round Euler", {"dataType" : repr("Euler")})
        insertNode(layout, "an_RoundDataNode", "Round Quaternion", {"dataType" : repr("Quaternion")})
        layout.separator()
        insertNode(layout, "an_EulerMathNode", "Euler Math")
        insertNode(layout, "an_QuaternionrMathNode", "Quaternion Math")
        insertNode(layout, "an_QuaternionListCombineNode", "Combine Quaternion Rotations")
        insertNode(layout, "an_NormalizeQuaternionNode", "Normalize Quaternion")
        insertNode(layout, "an_InvertQuaternionNode", "Invert Quaternion")
        layout.separator()
        layout.label("EXTRA/WIP")
        insertNode(layout, "an_CompositorNodesOutputNode", "Compositor Nodes Output")
        insertNode(layout, "an_FloatFormatNode", "Float Format OG")
        insertNode(layout, "an_FloatToStringNode2", "Float to Text2")
        layout.separator()
        insertNode(layout, "an_NLAstripsFromObjectNode", "NLA Strips from Object")
        insertNode(layout, "an_NLAStripInfoNode", "NLA Strip Info")
        insertNode(layout, "an_ShiftNLAStripNode", "Shift NLA Strip")
        layout.label("+ nla strip/list soket info")
        layout.separator()
        layout.label("hmm ...")


class OGFavs(bpy.types.Menu):
    bl_idname = "an_og_favs"
    bl_label = "OG Favs"
    
    def draw(self, context):

        layout = self.layout

        layout.label("FAVORITES")
        insertNode(layout, "an_FloatMathNode", "Math")
        insertNode(layout, "an_TimeInfoNode", "Time Info")
        insertNode(layout, "an_GetListElementNode", "Get Element")
        layout.separator()
        insertNode(layout, "an_ObjectTransformsInputNode", "Transforms Input")
        insertNode(layout, "an_ObjectTransformsOutputNode", "Transforms Output")
        insertNode(layout, "an_ObjectInstancerNode", "Instancer")
        layout.separator()
#        insertNode(layout, "an_VectorMathNode", "Vector Math")
#        insertNode(layout, "an_VectorFromValueNode", "Vector From Value")
#        insertNode(layout, "an_TransformVectorNode", "Transform Vector")
#        insertNode(layout, "an_TransformVectorListNode", "Transform Vector List")
#        layout.separator()
#        insertNode(layout, "an_DirectionToRotationNode", "Direction to Rotation")
#        insertNode(layout, "an_ConvertRotationsNode", "Euler to Matrix", {"conversionType" : repr("EULER_TO_MATRIX")})
#        layout.separator()
#        insertNode(layout, "an_ComposeMatrixNode", "Compose")
#        insertNode(layout, "an_MatrixCombineNode", "Combine")
#        layout.separator()
#        insertNode(layout, "an_ObjectMeshDataNode", "Object Mesh Data")
#        insertNode(layout, "an_VertexInfoNode", "Vertex Info")
#        insertNode(layout, "an_PolygonInfoNode", "Polygon Info")
#        layout.separator()
#        insertNode(layout, "an_FloatRangeListNode", "Integer Range", {"dataType" : repr("Integer")
#        insertNode(layout, "an_CombineMeshDataNode", "Combine")
#        insertNode(layout, "an_JoinMeshDataList", "Join Mesh Data List")
#        insertNode(layout, "an_SetBMeshOnObjectNode", "  BMesh")
#        layout.separator()
#        insertNode(layout, "an_GetSplineSamplesNode", "Get Samples")
#        insertNode(layout, "an_SetSplinesOnObjectNode", "Set on Object")
#        layout.separator()
        layout.label("   More to come ...")
        

class OGSubs(bpy.types.Menu):
    bl_idname = "an_og_subs_menu"
    bl_label = "OG Subprograms"

    def draw(self, context):

        layout = self.layout
        #row = layout.row(align = True)
        
        #col = row.column(align = True)
        layout.label("SUBPROGRAMS")

        subprograms = getSubprogramNetworks()
        if len(subprograms) == 0:
            layout.label("   There are no subprograms yet")
        else:
            for network in getSubprogramNetworks():
                insertNode(layout, "an_InvokeSubprogramNode", "-  " + network.name, {"subprogramIdentifier" : repr(network.identifier)})
        
        layout.separator()
        layout.label("New:")
        insertNode(layout, "an_GroupInputNode", "   Group")
        insertNode(layout, "an_LoopInputNode", "   Loop")
        insertNode(layout, "an_ScriptNode", "   Script")
        layout.separator()
        insertNode(layout, "an_ExpressionNode", "Expression")
        insertNode(layout, "an_DebugLoopNode", "Debug Loop")
        

class OGMenuInHeader(bpy.types.Header):
    bl_idname = "an_og_menu_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        if context.space_data.tree_type != "an_AnimationNodeTree": return
        layout = self.layout
        layout.separator()
        layout.menu("an_og_menu", text = "OG menu")
        
class OGFavsInHeader(bpy.types.Header):
    bl_idname = "an_og_favs_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        if context.space_data.tree_type != "an_AnimationNodeTree": return
        layout = self.layout
        layout.separator()
        layout.menu("an_og_favs", text = "OG Favs")
        
class OGsubsMenuInHeader(bpy.types.Header):
    bl_idname = "an_og_subs_menu_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        if context.space_data.tree_type != "an_AnimationNodeTree": return
        layout = self.layout
        layout.separator()
        layout.menu("an_og_subs_menu", text = "OG Subprograms")

def insertNode(layout, type, text, settings = {}, icon = "NONE"):
    operator = layout.operator("node.add_node", text = text, icon = icon)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator
