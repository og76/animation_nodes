import bpy
from bpy.props import *
from .. sockets.info import getBaseDataTypes
from .. tree_info import getSubprogramNetworks
from .. utils.nodes import getAnimationNodeTrees

class OGSub(bpy.types.Menu):
    bl_idname = "an_og_sub"
    bl_label = "OG Sub"

    def draw(self, context):
        layout = self.layout

        # subprograms
        insertNode(layout, "an_InvokeSubprogramNode", "Invoke Subprogram")
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

class OGMenu(bpy.types.Menu):
    bl_idname = "an_og_menu"
    bl_label = "OG Menu"

    def draw(self, context):
        layout = self.layout
        # favs
        layout.separator()
        insertNode(layout, "an_DebugNode", "Debug")
        insertNode(layout, "an_TimeInfoNode", "Time Info")
        insertNode(layout, "an_GetListElementNode", "Get Element")
        layout.separator()
#        layout.label("#### math")
        insertNode(layout, "an_FloatMathNode", "Math")
        insertNode(layout, "an_VectorMathNode", "Vector Math")
        insertNode(layout, "an_DirectionToRotationNode", "Direction to Rotation")
        insertNode(layout, "an_RotationToDirectionNode", "Rotation to Direction")
        
        layout.separator()
#        layout.label("#### object")
        insertNode(layout, "an_ObjectTransformsInputNode", "Transforms Input")
        insertNode(layout, "an_ObjectTransformsOutputNode", "Transforms Output")
        layout.separator()
#        layout.label("#### mesh")
        insertNode(layout, "an_ObjectMeshDataNode", "Object Mesh Data")
        insertNode(layout, "an_PolygonInfoNode", "Polygon Info")
        insertNode(layout, "an_MeshObjectOutputNode", "Mesh Object Output")
        layout.separator()
#        layout.label("#### spline")
        insertNode(layout, "an_SplineFromPointsNode", "Spline from Points")
        insertNode(layout, "an_CurveObjectOutputNode", "Spline Object Output")


class OGMenuInHeader(bpy.types.Header):
    bl_idname = "an_og_menu_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        if context.space_data.tree_type != "an_AnimationNodeTree": return
    
        layout = self.layout
        layout.separator()
        layout.menu("an_og_sub", text = "OG Sub")
        layout.menu("an_og_menu", text = "OG Menu")

def insertNode(layout, type, text, settings = {}, icon = "NONE"):
    operator = layout.operator("node.add_node", text = text, icon = icon)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator