import bpy
import random
from bpy.props import *
from math import pi
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class RandomEulerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomEulerNode"
    bl_label = "Random Euler"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Scale", "scale").value = pi/6
        self.outputs.new("an_EulerSocket", "Euler", "randomEuler")

    def draw(self, layout):
        layout.prop(self, "nodeSeed")

    def getExecutionCode(self):
        yield "startSeed = (seed + self.nodeSeed * 1000) % (len(random_number_cache) - 3)"
        yield ("randomEuler = mathutils.Euler(( (random_number_cache[startSeed] - 0.5) * scale, "
                                                "(random_number_cache[startSeed + 1] - 0.5) * scale, "
                                                "(random_number_cache[startSeed + 2] - 0.5) * scale))")

    def getUsedModules(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)