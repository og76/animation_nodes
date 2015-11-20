import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class RandomStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomStringNode"
    bl_label = "Random Text"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_IntegerSocket", "Length", "length").value = 5
        self.inputs.new("an_StringSocket", "Characters", "characters").value = "abcdefghijklmnopqrstuvwxyz"
        self.outputs.new("an_StringSocket", "Text", "text")
        self.randomizeNodeSeed()

    def draw(self, layout):
        layout.prop(self, "nodeSeed")

    def execute(self, seed, length, characters):
        random.seed(seed + 12334 * self.nodeSeed)
        return ''.join(random.choice(characters) for _ in range(length))

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
