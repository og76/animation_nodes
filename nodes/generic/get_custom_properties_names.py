import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... id_keys import filterRealIDKeys
from ... tree_info import keepNodeLinks, keepNodeState
from ... base_types.node import AnimationNode

propertyLocation = [
    ("OBJECT", "Object", "Object custom properties", "", 0),
    ("OBJECT_DATA", "Object Data", "Object Data (mesh, curve etc.) custom properties", "", 1),
    ("SCENE", "Scene", "Scene custom properties", "", 2) ]

locationLabels = {
    "OBJECT" : "Object",
    "OBJECT_DATA" : "Object Data",
    "SCENE" : "Scene" }

locationCode = {
    "OBJECT" : "object",
    "OBJECT_DATA" : "object.data",
    "SCENE" : "scene" }

locationsWithObject = ["OBJECT", "OBJECT_DATA"]

class GetCustomPropertiesNamesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetCustomPropertiesNamesNode"
    bl_label = "Get Custom Properties"

    def operationChanged(self, context):
        self.createInputs()

    path = EnumProperty(name = "Property Location", items = propertyLocation, default = "OBJECT", update = operationChanged)
    includeAnIDKeys = BoolProperty(name = "Include AN ID Keys", default = False, update = executionCodeChanged)

    def create(self):
        self.createInputs()
        self.outputs.new("an_StringListSocket", "Properties Names", "names")
        #self.outputs.new("an_GenericListSocket", "Properties Values", "values").hide = True

    def draw(self, layout):
        layout.prop(self, "path", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "includeAnIDKeys")

    def drawLabel(self):
        return locationLabels[self.path] + " Custom Properties"

    #@keepNodeLinks
    @keepNodeState
    def createInputs(self):
        self.inputs.clear()
        if self.path in locationsWithObject:
            self.newInput("Object", "Object", "object")
        if self.path == "SCENE":
            self.newInput("Scene", "Scene", "scene")

    def getExecutionCode(self):
        path = self.path
        
        if path == "OBJECT_DATA": 
            yield "if object is None or object.data is None: names = []"
        else: yield "if {} is None: names = []".format(locationCode[path])
        
        yield "else: names = self.getOnlyCustomKeys({}, self.includeAnIDKeys)".format(locationCode[path])
#        yield "else: names = [item for item in {}.keys()]".format(locationCode[path])
    
    def getOnlyCustomKeys(self, dataPath, includeAnIDKeys = False):
        # from rna_prop_ui.py
        notToEdit = ['_RNA_UI', 'animationNodes']
        rnaProperties = [prop.identifier for prop in dataPath.bl_rna.properties if prop.is_runtime] if dataPath.items() else None
        #anIDKeys = filterRealIDKeys(dataPath.keys())
        
        invalidKeys = notToEdit + rnaProperties
        
        if includeAnIDKeys: 
            return [key for key in dataPath.keys() if key not in invalidKeys]
        
        return [key for key in dataPath.keys() if key not in invalidKeys and "AN * " not in key]
        

