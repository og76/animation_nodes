import bpy
from bpy.props import *
from ... sockets.info import toDataType
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... utils.enum_items import enumItemsFromDicts
from ... utils.nodes import newNodeAtCursor, invokeTranslation
from ... tree_info import getSubprogramNetworks, getNodeByIdentifier, getNetworkByIdentifier

cacheTypeItems = [
    ("DISABLED", "Disabled", ""),
    ("ONE_TIME", "One Time", "Cache the result one time and output it always."),
    ("FRAME_BASED", "Once per Frame", ""),
    ("INPUT_BASED", "Once per Input", "")]

oneTimeCache = {}
frameBasedCache = {}
inputBasedCache = {}

class InvokeSubprogramNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvokeSubprogramNode"
    bl_label = "Invoke Subprogram"

    def subprogramIdentifierChanged(self, context):
        self.updateSockets()
        executionCodeChanged()

    subprogramIdentifier = StringProperty(name = "Subprogram Identifier", default = "", update = subprogramIdentifierChanged)

    def cacheTypeChanged(self, context):
        self.clearCache()
        executionCodeChanged()

    cacheType = EnumProperty(name = "Cache Type", items = cacheTypeItems, update = cacheTypeChanged)
    isOutputStorable = BoolProperty(default = False)
    isInputHashable = BoolProperty(default = False)

    def create(self):
        self.width = 170

    @property
    def inputVariables(self):
        return { socket.identifier : "input_" + str(i) for i, socket in enumerate(self.inputs)}

    @property
    def outputVariables(self):
        return { socket.identifier : "output_" + str(i) for i, socket in enumerate(self.outputs)}

    def getExecutionCode(self):
        if self.subprogramNode is None: return ""

        parameterString = ", ".join(["input_" + str(i) for i in range(len(self.inputs))])
        invokeString = "_subprogram{}({})".format(self.subprogramIdentifier, parameterString)
        outputString = ", ".join(["output_" + str(i) for i in range(len(self.outputs))])

        if self.cacheType == "DISABLED" or not self.canCache:
            if outputString == "": return invokeString
            else: return "{} = {}".format(outputString, invokeString)
        else:
            lines = []
            lines.append("useCache, groupOutputData = self.getCachedData({})".format(parameterString))
            lines.append("if not useCache:")
            lines.append("    groupOutputData = _subprogram{}({})".format(self.subprogramIdentifier, parameterString))
            lines.append("    self.setCacheData(groupOutputData, {})".format(parameterString))
            if outputString != "": lines.append("{} = groupOutputData".format(outputString))
            return lines

    def getCachedData(self, *args):
        if self.cacheType == "ONE_TIME":
            try: return True, oneTimeCache[self.identifier]
            except: pass
        if self.cacheType == "FRAME_BASED":
            try: return True, frameBasedCache[self.identifier][str(self.nodeTree.scene.frame_current)]
            except: pass
        if self.cacheType == "INPUT_BASED":
            try: return True, inputBasedCache[self.subprogramIdentifier][self.getArgsHash(args)]
            except: pass

        return False, None

    def setCacheData(self, data, *args):
        if self.cacheType == "ONE_TIME": oneTimeCache[self.identifier] = data
        elif self.cacheType == "FRAME_BASED":
            if self.identifier not in frameBasedCache: frameBasedCache[self.identifier] = {}
            frameBasedCache[self.identifier][str(self.nodeTree.scene.frame_current)] = data
        elif self.cacheType == "INPUT_BASED":
            if self.subprogramIdentifier not in inputBasedCache: inputBasedCache[self.subprogramIdentifier] = {}
            inputBasedCache[self.subprogramIdentifier][self.getArgsHash(args)] = data

    def getArgsHash(self, *args):
        return tuple(hash(arg) for arg in args)


    def draw(self, layout):
        networks = getSubprogramNetworks()
        network = self.subprogramNetwork

        layout.separator()

        col = layout.column()
        row = col.row(align = True)
        row.scale_y = 1.6

        if len(networks) > 0:
            text, icon = (network.name, "GROUP_VERTEX") if network else ("Choose", "TRIA_RIGHT")
            props = row.operator("an.change_subprogram", text = text, icon = icon)
            props.nodeIdentifier = self.identifier

        props = row.operator("an.empty_subprogram_template", icon = "NEW", text = "New Subprogram" if len(networks) == 0 else "")
        props.targetNodeIdentifier = self.identifier

        layout.separator()

    def drawAdvanced(self, layout):
        col = layout.column()
        col.active = self.isOutputStorable
        col.prop(self, "cacheType")
        if not self.canCache:
            col = layout.column(align = True)
            layout.label("This caching method is not available:")
            if not self.isOutputStorable: layout.label("  - The output is not storable")
            if not self.isInputHashable: layout.label("  - The input is not hashable")
        self.invokeFunction(layout, "clearCache", text = "Clear Cache")


    def updateSockets(self):
        subprogram = self.subprogramNode
        if subprogram is None: self.clearSockets()
        else:
            if subprogram.network.type == "Invalid": return
            else: subprogram.getSocketData().apply(self)
        self.checkCachingPossibilities()
        self.clearCache()

    def checkCachingPossibilities(self):
        self.isInputHashable = all(socket.hashable for socket in self.inputs)
        self.isOutputStorable = all(socket.storable for socket in self.outputs)


    def clearCache(self):
        oneTimeCache.pop(self.identifier, None)
        frameBasedCache.pop(self.identifier, None)
        inputBasedCache.pop(self.subprogramIdentifier, None)


    @property
    def subprogramNode(self):
        try: return getNodeByIdentifier(self.subprogramIdentifier)
        except: return None

    @property
    def subprogramNetwork(self):
        return getNetworkByIdentifier(self.subprogramIdentifier)

    @property
    def canCache(self):
        if self.cacheType == "DISABLED": return True
        if self.cacheType in ("ONE_TIME", "FRAME_BASED") and self.isOutputStorable: return True
        if self.cacheType == "INPUT_BASED" and self.isInputHashable and self.isOutputStorable: return True
        return False


@enumItemsFromDicts
def getSubprogramItems(self, context):
    itemDict = []
    for network in getSubprogramNetworks():
        itemDict.append({
            "value" : network.identifier,
            "name" : network.name,
            "description" : network.description})
    return itemDict

class ChangeSubprogram(bpy.types.Operator):
    bl_idname = "an.change_subprogram"
    bl_label = "Change Subprogram"
    bl_description = "Change Subprogram"

    nodeIdentifier = StringProperty()
    subprogram = EnumProperty(name = "Subprogram", items = getSubprogramItems)

    @classmethod
    def poll(cls, context):
        networks = getSubprogramNetworks()
        return len(networks) > 0

    def invoke(self, context, event):
        try:
            node = getNodeByIdentifier(self.nodeIdentifier)
            self.subprogram = node.subprogramIdentifier
        except: pass # when the old subprogram identifier doesn't exist
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "subprogram", expand = self.expandSubprograms)

        network = getNetworkByIdentifier(self.subprogram)
        if network:
            layout.label("Desription: " + network.description)
            layout.separator()
            if network.type == "Group":
                socketData = network.groupInputNode.getSocketData()
            if network.type == "Loop":
                socketData = network.loopInputNode.getSocketData()
            if network.type == "Script":
                socketData = network.scriptNode.getSocketData()

            col = layout.column()
            col.label("Inputs:")
            self.drawSockets(col, socketData.inputs)

            col = layout.column()
            col.label("Outputs:")
            self.drawSockets(col, socketData.outputs)

    def drawSockets(self, layout, sockets):
        col = layout.column(align = True)
        for data in sockets:
            row = col.row()
            row.label(" "*8 + data.text)
            row.label("<  {}  >".format(toDataType(data.idName)))

    @property
    def expandSubprograms(self):
        networks = getSubprogramNetworks()
        names = "".join([network.name for network in networks])
        return len(names) < 40

    def execute(self, context):
        node = getNodeByIdentifier(self.nodeIdentifier)
        node.subprogramIdentifier = self.subprogram
        return {"FINISHED"}
