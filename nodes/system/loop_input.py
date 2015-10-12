import re
import bpy
from bpy.props import *
from operator import attrgetter
from ... events import networkChanged
from ... utils.names import getRandomString
from ... utils.layout import splitAlignment
from ... tree_info import getNodeByIdentifier
from ... base_types.node import AnimationNode
from . subprogram_base import SubprogramBaseNode
from ... utils.nodes import newNodeAtCursor, invokeTranslation
from ... sockets.info import (toBaseIdName, toListDataType, toIdName,
                                    isBase, toListIdName, toBaseDataType)
from . subprogram_sockets import SubprogramData, subprogramInterfaceChanged

class LoopInputNode(bpy.types.Node, AnimationNode, SubprogramBaseNode):
    bl_idname = "an_LoopInputNode"
    bl_label = "Loop Input"

    def create(self):
        self.randomizeNetworkColor()
        self.subprogramName = "My Loop"
        self.outputs.new("an_IntegerSocket", "Index")
        self.outputs.new("an_IntegerSocket", "Iterations")
        self.outputs.new("an_NodeControlSocket", "New Iterator").margin = 0.15
        self.outputs.new("an_NodeControlSocket", "New Parameter").margin = 0.15
        self.width = 180

    def draw(self, layout):
        layout.separator()
        left, right = splitAlignment(layout)
        self.invokeSocketTypeChooser(left, "createGeneratorOutputNode", socketGroup = "LIST", text = "", icon = "ZOOMIN", emboss = False)
        right.label("New Generator Output")
        layout.prop(self, "subprogramName", text = "", icon = "GROUP_VERTEX")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.label("Description:")
        col.prop(self, "subprogramDescription", text = "")

        layout.separator()

        col = layout.column()
        col.label("Iterator Sockets:")
        box = col.box()
        for socket in self.getIteratorSockets():
            box.prop(socket.loop, "useAsOutput", text = "Use {} as Output".format(repr(socket.text)))
        self.invokeSocketTypeChooser(box, "newIterator", socketGroup = "LIST", text = "New Iterator", icon = "PLUS")

        layout.separator()

        col = layout.column()
        col.label("Parameter Sockets:")
        box = col.box()
        for socket in self.getParameterSockets():
            subcol = box.column(align = False)
            row = subcol.row()
            row.label(repr(socket.text))
            self.invokeFunction(row, "createReassignParameterNode", text = "Reassign", data = socket.identifier)
            row = subcol.row()
            row.prop(socket.loop, "useAsInput", text = "Input")
            row.prop(socket.loop, "useAsOutput", text = "Output")
            subrow = row.row()
            subrow.active = socket.isCopyable
            subrow.prop(socket.loop, "copyAlways", text = "Copy")
            socket.drawSocket(subcol, text = "Default", drawType = "PROPERTY_ONLY")
        self.invokeSocketTypeChooser(box, "newParameter", text = "New Parameter", icon = "PLUS")

        layout.separator()

        col = layout.column()
        col.label("List Generators:")
        box = col.box()
        for node in self.getSortedGeneratorNodes():
            box.label("{} - {}".format(repr(node.outputName), node.listDataType))
        self.invokeSocketTypeChooser(box, "createGeneratorOutputNode", socketGroup = "LIST", text = "New Generator", icon = "PLUS")

    def edit(self):
        for target in self.newIteratorSocket.dataTargets:
            if target.dataType == "Node Control": continue
            if not isBase(target.dataType): continue
            listDataType = toListDataType(target.dataType)
            socket = self.newIterator(listDataType, target.getDisplayedName())
            socket.linkWith(target)

        for target in self.newParameterSocket.dataTargets:
            if target.dataType == "Node Control": continue
            socket = self.newParameter(target.dataType, target.getDisplayedName(), target.getProperty())
            socket.linkWith(target)

        self.newIteratorSocket.removeLinks()
        self.newParameterSocket.removeLinks()

    def drawControlSocket(self, layout, socket):
        isParameterSocket = socket == self.outputs[-1]
        function, socketGroup = ("newParameter", "ALL") if isParameterSocket else ("newIterator", "LIST")

        left, right = splitAlignment(layout)
        self.invokeSocketTypeChooser(left, function, socketGroup = socketGroup, icon = "ZOOMIN", emboss = False)
        right.label(socket.name)


    def newIterator(self, listDataType, name = None):
        if name is None: name = toBaseDataType(listDataType)
        socket = self.outputs.new(toBaseIdName(listDataType), name, "iterator_" + getRandomString(5))
        socket.moveTo(self.newIteratorSocket.index)
        self.setupSocket(socket, name, moveGroup = 1)
        return socket

    def newParameter(self, dataType, name = None, defaultValue = None):
        if name is None: name = dataType
        socket = self.outputs.new(toIdName(dataType), name, "parameter_" + getRandomString(5))
        if defaultValue: socket.setProperty(defaultValue)
        socket.moveTo(self.newParameterSocket.index)
        socket.loop.copyAlways = False
        self.setupSocket(socket, name, moveGroup = 2)
        return socket

    def setupSocket(self, socket, name, moveGroup):
        socket.text = name
        socket.moveGroup = moveGroup
        socket.moveable = True
        socket.removeable = True
        socket.display.text = True
        socket.textProps.editable = True
        socket.display.textInput = True
        socket.display.removeOperator = True
        socket.loop.useAsInput = True


    def socketChanged(self):
        subprogramInterfaceChanged()

    def delete(self):
        self.outputs.clear()
        subprogramInterfaceChanged()

    def duplicate(self, sourceNode):
        self.randomizeNetworkColor()
        match = re.search("(.*) ([0-9]+)$", self.subprogramName)
        if match: self.subprogramName = match.group(1) + " " + str(int(match.group(2)) + 1)
        else: self.subprogramName += " 2"


    def getSocketData(self):
        data = SubprogramData()
        if len(self.outputs) == 0: return data

        self.insertIteratorData(data)
        self.insertGeneratorData(data)
        self.insertParameterData(data)

        return data

    def insertIteratorData(self, data):
        iteratorSockets = self.getIteratorSockets()
        if len(iteratorSockets) == 0:
            data.newInput("an_IntegerSocket", "loop_iterations", "Iterations", 0)
        else:
            for socket in iteratorSockets:
                name = socket.text + " List"
                data.newInput(toListIdName(socket.bl_idname), socket.identifier, name, [])
                if socket.loop.useAsOutput:
                    data.newOutput(toListIdName(socket.bl_idname), socket.identifier, name)

    def insertParameterData(self, data):
        for socket in self.getParameterSockets():
            if socket.loop.useAsInput:
                socketData = data.newInputFromSocket(socket)
                socketData.identifier += "_input"
            if socket.loop.useAsOutput:
                socketData = data.newOutputFromSocket(socket)
                socketData.identifier += "_output"

    def insertGeneratorData(self, data):
        for node in self.getSortedGeneratorNodes():
            data.newOutput(toIdName(node.listDataType), node.identifier, node.outputName)


    def createGeneratorOutputNode(self, dataType):
        node = newNodeAtCursor("an_LoopGeneratorOutputNode")
        node.loopInputIdentifier = self.identifier
        node.listDataType = dataType
        invokeTranslation()
        subprogramInterfaceChanged()

    def createReassignParameterNode(self, socketIdentifier):
        socket = self.outputsByIdentifier[socketIdentifier]
        node = newNodeAtCursor("an_ReassignLoopParameterNode")
        node.loopInputIdentifier = self.identifier
        node.parameterIdentifier = socketIdentifier
        invokeTranslation()
        subprogramInterfaceChanged()

    def getTemplateCode(self):
        for socket in self.getIteratorSockets():
            yield "self.newIterator({}, name = {})".format(repr(toListDataType(socket.bl_idname)), repr(socket.text))
        for socket in self.getParameterSockets():
            yield "self.newParameter({}, name = {})".format(repr(socket.dataType), repr(socket.text))


    @property
    def newIteratorSocket(self):
        return self.outputs["New Iterator"]

    @property
    def newParameterSocket(self):
        return self.outputs["New Parameter"]

    @property
    def indexSocket(self):
        return self.outputs["Index"]

    @property
    def iterationsSocket(self):
        return self.outputs["Iterations"]

    @property
    def iterateThroughLists(self):
        return len(self.getIteratorSockets()) > 0

    def getIteratorSockets(self):
        return self.outputs[2:self.newIteratorSocket.index]

    def getParameterSockets(self):
        return self.outputs[self.newIteratorSocket.index + 1:self.newParameterSocket.index]

    def getSortedGeneratorNodes(self):
        nodes = self.network.generatorOutputNodes
        nodes.sort(key = attrgetter("sortIndex"))
        for i, node in enumerate(nodes):
            node.sortIndex = i
        return nodes

    def getReassignParameterNodes(self):
        return [node for node in self.network.reassignParameterNodes if node.linkedParameterSocket]
