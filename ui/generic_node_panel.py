import bpy
from bpy.props import *



def draw(self, context):
    node = bpy.context.active_node
    if not getattr(node, "isAnimationNode", False): return

    layout = self.layout
    
    #developerExtra = BoolProperty(name = "Developer Extra", default = False)
    
    col = layout.column(align = True)
    col.label("Identifier: " + node.identifier)
    col.separator()
    
    row = layout.row(align = True)
    col = row.column(align = True)
    col.prop(node, "location", text = "X", index = 0)
    col.prop(node, "location", text = "Y", index = 1)

    row = layout.row(align = True)
    row.prop(node, "width", text = "Width")
    row.separator()
    row.prop(self, "developerExtra", text = "xxx", icon = "SCRIPTWIN")


    row = layout.row(align = True)

    size = max(len(node.inputs), len(node.outputs), 1)

    if len(node.inputs) > 0:
        col = row.column()
        subrow = col.row(align = True)
        subrow.label("Inputs")
        subrow.operator("an.move_input", text = "", icon = "TRIA_UP").moveUp = True
        subrow.operator("an.move_input", text = "", icon = "TRIA_DOWN").moveUp = False
        col.template_list("an_SocketUiList", "", node, "inputs", node, "activeInputIndex", rows = size, maxrows = size)

    if len(node.outputs) > 0:
        col = row.column()
        subrow = col.row(align = True)
        subrow.label("Outputs")
        subrow.operator("an.move_output", text = "", icon = "TRIA_UP").moveUp = True
        subrow.operator("an.move_output", text = "", icon = "TRIA_DOWN").moveUp = False
        col.template_list("an_SocketUiList", "", node, "outputs", node, "activeOutputIndex", rows = size, maxrows = size)

    col = layout.column(align = True)
    col.label("Toogle Operation Visibility:")
    row = col.row(align = True)
    node.invokeFunction(row, "toogleTextInputVisibility", text = "Name")
    node.invokeFunction(row, "toogleMoveOperatorsVisibility", text = "Move")
    node.invokeFunction(row, "toogleRemoveOperatorVisibility", text = "Remove")
    node.invokeFunction(row, "disableSocketEditingInNode", icon = "FULLSCREEN")




class SocketUiList(bpy.types.UIList):
    bl_idname = "an_SocketUiList"

    def draw_item(self, context, layout, node, socket, icon, activeData, activePropname):
        row = layout.row()

        if socket.textProps.editable:
            row.prop(socket, "text", emboss = False, text = "")
        else: row.label(socket.getDisplayedName())

        col = row.column()
        col.scale_x = 0.5
        if socket.removeable:
            socket.invokeFunction(col, "remove", icon = "X", emboss = False)

        col = row.column()
        col.scale_x = 0.5
        icon = "RESTRICT_VIEW_ON" if socket.hide else "RESTRICT_VIEW_OFF"
        col.prop(socket, "hide", text = "", icon_only = True, icon = icon, emboss = False)


class MoveInputSocket(bpy.types.Operator):
    bl_idname = "an.move_input"
    bl_label = "Move Input"

    moveUp = BoolProperty()

    @classmethod
    def poll(cls, context):
        socket = getActiveSocket(isOutput = False)
        return getattr(socket, "moveable", False)

    def execute(self, context):
        return moveSocket(isOutput = False, moveUp = self.moveUp)

class MoveOutputSocket(bpy.types.Operator):
    bl_idname = "an.move_output"
    bl_label = "Move Output"

    moveUp = BoolProperty()

    @classmethod
    def poll(cls, context):
        socket = getActiveSocket(isOutput = True)
        return getattr(socket, "moveable", False)

    def execute(self, context):
        return moveSocket(isOutput = True, moveUp = self.moveUp)


def moveSocket(isOutput, moveUp):
    socket = getActiveSocket(isOutput)
    socket.moveInGroup(moveUp)

    node = socket.node
    if isOutput: node.activeOutputIndex = list(node.outputs).index(socket)
    else: node.activeInputIndex = list(node.inputs).index(socket)
    return {"FINISHED"}

def getActiveSocket(isOutput):
    node = bpy.context.active_node
    if node is None: return
    if isOutput: return node.activeOutputSocket
    else: return node.activeInputSocket



# Register
##################################

def register():
    bpy.types.NODE_PT_active_node_generic.append(draw)

def unregister():
    bpy.types.NODE_PT_active_node_generic.remove(draw)
