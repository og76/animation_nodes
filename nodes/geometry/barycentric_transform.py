import bpy
import mathutils
from bpy.props import *
from ... utils.layout import writeText
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationTypeItems = [  ("POINT", "Transform Vector", ""),
                        ("LIST", "Transform Vector List", "") ]

class BarycentricTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BarycentricTransformNode"
    bl_label = "Barycentric Transform"
    bl_width_default = 160
    searchTags = ["Transform by Triangles", "Morph by Triangles"]
    
    def operationTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()
    
    operationType = EnumProperty(name = "Operation Type", default = "POINT",
        items = operationTypeItems, update = operationTypeChanged)
    errorMessage = StringProperty()
        
    def create(self):
        self.generateSockets()
        self.operationType = "POINT"

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        
        if self.operationType == "POINT":
            self.inputs.new("an_VectorSocket", "Point", "point")
            self.inputs.new("an_VectorListSocket", "Source Triangle Points", "t1")
            self.inputs.new("an_VectorListSocket", "Target Triangle Points", "t2")
            self.outputs.new("an_VectorSocket", "Morphed Location", "location")
        if self.operationType == "LIST":
            self.inputs.new("an_VectorListSocket", "Point List", "pointList")
            self.inputs.new("an_VectorListSocket", "Source Triangle Points", "t1")
            self.inputs.new("an_VectorListSocket", "Target Triangle Points", "t2")
            self.outputs.new("an_VectorListSocket", "Morphed Locations", "locationList")

    def draw(self, layout):
        layout.prop(self, "operationType", text = "")
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 21)
        
    def drawAdvanced(self, layout):
        layout.label('Expected:')
        layout.label('3 Different vectors for Source')
        layout.label('3 vectors for Target')
        writeText(layout, 'Only the first 3 points in each tri list will be considered', width = 21)
  
    def getExecutionCode(self):
        
        yield "self.errorMessage = self.barycentricValidTriInputs(t1, t2)"
        yield "if self.errorMessage == '': "
        if self.operationType == "POINT":
            yield "    location = self.barycentricTransform(point, t1, t2)"
            yield "else: location = point"
        elif self.operationType == "LIST":
            yield "    locationList = [self.barycentricTransform(p, t1, t2) for p in pointList]"
            yield "else: locationList = []"

#        # separate validation and function
#        yield "isValid, self.errorMessage = self.barycentricValidTriInputs(t1, t2)"

#        if self.operationType == "POINT":
#            yield "if isValid: location = self.barycentricTransform(point, t1, t2)"
#            yield "else: location = point"
#        elif self.operationType == "LIST":
#            yield "if isValid: locationList = [self.barycentricTransform(p, t1, t2) for p in pointList]"
#            yield "else: locationList = []"

#        # sepatate functions item/list
#        if self.operationType == "POINT":
#            return "location, self.errorMessage = self.barycentricTransformVector(point, t1, t2)"
#        else:
#            return "locationList, self.errorMessage = self.barycentricTransformList(pointList, t1, t2)"


    def getUsedModules(self):
        return ["mathutils"]



    def barycentricValidTriInputs(self, sourceTri, targetTri):
        valid = False
        if len(sourceTri) < 3:   
            errorMessage = 'Expected 3 vectors for Source Triangle'
        elif len(targetTri) < 3: 
            errorMessage = 'Expected 3 vectors for Target Triangle'
        elif any((  sourceTri[0]==sourceTri[1], 
                    sourceTri[1]==sourceTri[2], 
                    sourceTri[2]==sourceTri[0]) ): 
            errorMessage = 'Expected 3 Different vectors for Source'
        else:
            valid = True
            errorMessage = ''
            
        return errorMessage
    
    def barycentricTransform(self, vector, sourceTri, targetTri):
        return mathutils.geometry.barycentric_transform(      vector, 
                            sourceTri[0], sourceTri[1], sourceTri[2], 
                            targetTri[0], targetTri[1], targetTri[2])


#    def barycentricTransformVector(self, vector, sourceTri, targetTri):
#        if len(sourceTri) < 3:   
#            location = vector
#            errorMessage = 'Expected 3 vectors for Source Triangle'
#        elif len(targetTri) < 3: 
#            location = vector
#            errorMessage = 'Expected 3 vectors for Target Triangle'
#        elif any((  sourceTri[0]==sourceTri[1], 
#                    sourceTri[1]==sourceTri[2], 
#                    sourceTri[2]==sourceTri[0]) ): 
#            location = vector
#            self.errorMessage = 'Expected 3 Different vectors for Source'
#            
#        else: 
#            location = mathutils.geometry.barycentric_transform(  vector, 
#                                sourceTri[0], sourceTri[1], sourceTri[2], 
#                                targetTri[0], targetTri[1], targetTri[2])
#            errorMessage = ''
#        
#        return location, errorMessage


#    def barycentricTransformList(self, vectorList, sourceTri, targetTri):
#        if len(sourceTri) < 3:   
#            locations = []
#            errorMessage = 'Expected 3 vectors for Source Triangle'
#        elif len(targetTri) < 3: 
#            locations = []
#            errorMessage = 'Expected 3 vectors for Target Triangle'
#        elif any((  sourceTri[0]==sourceTri[1], 
#                    sourceTri[1]==sourceTri[2], 
#                    sourceTri[2]==sourceTri[0]) ): 
#            locations = []
#            self.errorMessage = 'Expected 3 Different vectors for Source'
#            
#        else: 
#            barycentric = mathutils.geometry.barycentric_transform(vector, 
#                                sourceTri[0], sourceTri[1], sourceTri[2], 
#                                targetTri[0], targetTri[1], targetTri[2])
#            locations = [barycentric for vector in vectorList]
#            errorMessage = ''
#        
#        return locations, errorMessage
    


