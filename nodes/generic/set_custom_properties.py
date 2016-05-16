import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
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

class SetCustomPropertiesNamesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetCustomPropertiesNamesNode"
    bl_label = "Set Custom Properties"
    bl_width_default = 160

    def operationChanged(self, context):
        self.createInputs()

    path = EnumProperty(name = "Property Location", items = propertyLocation, default = "OBJECT", update = operationChanged)
    includeAnIDKeys = BoolProperty(name = "Include AN ID Keys", default = False, update = executionCodeChanged)

    def create(self):
        self.createInputs()

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
        self.outputs.clear()
        if self.path in locationsWithObject:
            self.newInput("Object", "Object", "object")
            self.newOutput("Object", "Object", "object")
        if self.path == "SCENE":
            self.newInput("Scene", "Scene", "scene")
            self.newOutput("Scene", "Scene", "scene")
            
        self.newInput("String", "Property", "property")
        self.newInput("Generic", "Value", "value")
        self.newInput("Boolean", "On/Off", "on").value = False
        self.newInput("Boolean", "Add (off = Remove)", "add")

    def getExecutionCode(self):
        path = self.path
        location = locationCode[path]
        
        if path == "OBJECT_DATA":
            testPath = "object"
            testData = True
        else:
            testPath = location
            testData = False

        yield "if self.validConditions(on, property, value, {}, {}, self.includeAnIDKeys):".format(testPath, testData)
        yield "    if add: {}[property] = value".format(location)
        yield "    else: "
        yield "        if property in {}: del {}[property]".format(location, location)


    def validConditions(self, on, propName, propValue, testPath, testData, includeAnIDKeys):
        if not on: return False
        if propName is '': return False
        if propValue is None: return False

        if testPath is None: return False
        if testData:
            if testPath.data is None: return False
        
        path = testPath.data if testData else testPath
        if not self.isValidProperty(path, propName, includeAnIDKeys): return False
        return True

    def isValidProperty(self, dataPath, property, includeAnIDKeys = False):
        
        invalidNames = ['_RNA_UI', 'animationNodes']
        rnaProperties = [prop.identifier for prop in dataPath.bl_rna.properties if prop.is_runtime] if dataPath.items() else None
        
        if includeAnIDKeys: 
            return property not in invalidNames + rnaProperties
        return property not in invalidNames + rnaProperties and "AN * " not in property 
