import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_ExtendPolygonsIndices(Node, AnimationNode):
    bl_idname = "mn_ExtendPolygonsIndices"
    bl_label = "Extend Poly Indices"
    node_category = "Mesh"
    isDetermined = True
    
#    def typeChanged(self, context):
#        self.generateInputSockets()
#        nodeTreeChanged()
    
#    selfExtend = bpy.props.BoolProperty(default = TRUE, name = "Self Extend", update = typeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Amount").number = 1
        self.inputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
#        self.generateInputSockets()
        self.outputs.new("mn_PolygonIndicesListSocket", "Extended Polygon Indices")
        allowCompiling()
        
#    def draw_buttons(self, context, layout):
#        layout.prop(self, "amount")
        
#    def generateInputSockets(self):
#        forbidCompiling()
#        self.inputs.new("mn_IntegerSocket", "Amount").number = 1
#        
#        connections = getConnectionDictionaries(self)
#        self.inputs.clear()
#        for i in range(self.amount):
#            self.inputs.new("mn_IntegerSocket", "Index " + str(i)).number = i
#        tryToSetConnectionDictionaries(self, connections)
        allowCompiling()
                
    def getInputSocketNames(self):
#        names = {}
#        for i, socket in enumerate(self.inputs):
#            names[socket.name] = "index" + str(i)
#        return names
        return {"Amount" : "amount",
                "Polygon Indices" : "polygonIndices"}
    def getOutputSocketNames(self):
        return {"Extended Polygon Indices" : "extendedPolygonIndices"}
    
    def execute(self, amount, polygonIndices):
        
        ExtendedPolygonsIndices = []
        if polygonIndices is not None:
            ExtendedPolygonsIndices.extend(polygonIndices)
            
            maxVert = max( [max(pI) for pI in polygonIndices]) + 1
            NI = []
            for i in range(amount):
                for pI in polygonIndices:
                    NI.append( [el + maxVert*(i+1) for el in pI] )
                    
            ExtendedPolygonsIndices.extend(NI)
            
        return ExtendedPolygonsIndices
#    def useInLineExecution(self):
#        return True
#    def getInLineExecutionString(self, outputUse):
#        codeLines = []
#        codeLines.append('''if %polygonIndices% is not None:
#    extendedPolygonsIndices = []
#    extendedPolygonsIndices.extend(%polygonIndices%)
#    
#    maxVert = max( [max(pI) for pI in %polygonIndices%]) + 1
#    NI = []
#    for i in range(%amount%):
#        for pI in %polygonIndices%:
#            NI.append( [el + maxVert*(i+1) for el in pI] )
#            
#    extendedPolygonsIndices.extend(NI)
#    $extendedPolygonsIndices$ = extendedPolygonsIndices
#    ''')
#        #list = ", ".join(["%index"+str(i)+"%" for i in range(self.amount)])
#        return "\n".join(codeLines)#"$extendedPolygonIndices$ = ("+ list +")"
