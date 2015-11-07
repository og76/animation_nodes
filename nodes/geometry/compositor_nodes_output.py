import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

allowedSocketTypes = {
    "NodeSocketVector" : "an_VectorSocket",
    "NodeSocketColor" : "an_ColorSocket",
    "NodeSocketFloatFactor" : "an_FloatSocket",
    "NodeSocketFloat" : "an_FloatSocket" }


class CompositorNodesOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CompositorNodesOutputNode"
    bl_label = "Compositor Nodes Output"

    def getPossibleSocketItems(self, context):
        sockets = self.getPossibleSockets()
        items = []
        for socket in sockets:
            if socket.bl_idname in allowedSocketTypes.keys():
                items.append((socket.identifier, socket.identifier, ""))
        return items

    def getPossibleSockets(self):
        node = self.getSelectedNode()
        identifiers = []
        if node is not None:
            for socket in node.inputs:
                if socket.bl_idname in allowedSocketTypes.keys():
                    identifiers.append(socket)
        return identifiers

    def selectedSocketChanged(self, context):
        self.socketIsChanging = True
        self.setInputSocket()
        self.socketIsChanging = False

    sceneName = StringProperty()
    nodeName = StringProperty(update = selectedSocketChanged)
    socketIdentifier = EnumProperty(items = getPossibleSocketItems, name = "Socket", update = selectedSocketChanged)
    socketIsChanging = BoolProperty()
    #compositorUseNodes = BoolProperty(default = False)

    def create(self):
        self.width = 180
        self.inputs.new("an_SceneSocket", "Scene", "scene").hide = True
        self.inputs.new("an_GenericSocket", "Data", "data")
        

    def draw(self, layout):
        layout.label('['+self.sceneName +']: Compositor Nodes: ')
        scene = bpy.data.scenes.get(self.sceneName)
        if scene is not None:
            nodeTree = scene.node_tree
            if nodeTree is None: 
                layout.label('NO Compositor Nodes this scene ', icon = 'ERROR')
            else:
                layout.prop_search(self, 'nodeName', nodeTree, 'nodes', text='', icon='NODE')
                node = scene.node_tree.nodes.get(self.nodeName)
                if node is not None:
                    layout.prop(self, "socketIdentifier", text = "")

    def execute(self, scene, data):
        if scene is not None: self.sceneName = str(scene.name)
        
        socket = self.getSelectedSocket()
        if socket is not None:
            try: socket.default_value = data
            except: pass

    def edit(self):
        socket = self.inputs.get("Data")
        if socket is not None and not self.socketIsChanging:
            if len(socket.links) > 0:
                fromType = self.inputs[1].links[0].from_socket.bl_idname
                possibleIdentifiers = self.getInputIdentifiersFromSocketType(fromType)
                if self.inputs["Data"].bl_idname != fromType and len(possibleIdentifiers) > 0:
                    self.socketIdentifier = possibleIdentifiers[0]
                    self.setInputSocket()

    def getInputIdentifiersFromSocketType(self, searchType):
        identifiers = []
        sockets = self.getPossibleSockets()
        for socket in sockets:
            if allowedSocketTypes[socket.bl_idname] == searchType:
                identifiers.append(socket.identifier)
        return identifiers

    def getSelectedNode(self):
        scene = bpy.data.scenes.get(self.sceneName)
        if scene is not None and scene.node_tree is not None:
            node = scene.node_tree.nodes.get(self.nodeName)
            return node
        return None

    def getSelectedSocket(self):
        node = self.getSelectedNode()
        if node is not None:
            socket = self.getInputSocketWithIdentifier(node, self.socketIdentifier)
            return socket
        return None

    def getInputSocketWithIdentifier(self, node, identifier):
        for socket in node.inputs:
            if socket.identifier == identifier: return socket
        return None

    def setInputSocket(self):
        socket = self.getSelectedSocket()
        self.inputs.clear()
        self.inputs.new("an_SceneSocket", "Scene", "scene")
        if socket is None:
            self.inputs.new("an_GenericSocket", "Data")
        else:
            data = socket.default_value
            self.inputs.new(allowedSocketTypes[socket.bl_idname], "Data")
            self.inputs["Data"].setProperty(data)