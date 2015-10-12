import bpy
from bpy.props import *
from mathutils import Vector, Euler
from . utils.path import toIDPropertyPath as toPath
from . utils.enum_items import enumItemsFromDicts


# ID Keys
##########################

forcedIDKeyTypes = {
    "Initial Transforms" : "Transforms",
    "Initial Text" : "String" }

@enumItemsFromDicts
def getIDKeyItems(self, context):
    itemData = []
    for item in getIDKeys():
        name, type, id = item.name, item.type, item.id
        itemData.append({
            "value" : id + "|" + type,
            "name" : name,
            "description" : type})
    return itemData

def getIDKeyInfo(object, id, type = None):
    if not type: type = getIDType(id)
    typeClass = getIDTypeClass(type)
    return typeClass.read(object, id), typeClass.exists(object, id)

def hasIDKeyData(object, id, type = None):
    if not type: type = getIDType(id)
    typeClass = getIDTypeClass(type)
    return typeClass.exists(object, id)

def getIDKeyData(object, id, type = None):
    if not type: type = getIDType(id)
    typeClass = getIDTypeClass(type)
    return typeClass.read(object, id)

def setIDKeyData(object, id, type, data):
    typeClass = getIDTypeClass(type)
    typeClass.write(object, id, data)


def getIDType(id):
    return getItem(id).type

def getItem(id):
    for item in getIDKeys():
        if id == item.id: return item

def getIDTypeClass(type):
    return idTypes[type]

def getIDKeys():
    return getIDKeySettings().keys

def getIDKeySettings():
    return bpy.context.scene.animationNodes.idKeys


def createIDKey(id, type):
    if not isCreatable(id, type): return
    idKeys = getIDKeys()
    item = idKeys.add()
    item.name = id
    item.id = id
    item.type = type

def isCreatable(id, type):
    if idKeyExists(id): return False
    if not isValidCombination(id, type): return False
    return True

def idKeyExists(id):
    for item in getIDKeys():
        if item.id == id: return True
    return False

def isValidCombination(id, type):
    if "|" in id: return False
    if "|" in type: return False
    if id == "": return False
    if type not in idTypes.keys(): return False
    if id in forcedIDKeyTypes:
        if forcedIDKeyTypes[id] != type: return False
    return True


def hasProp(object, name):
    return hasattr(object, toPath(name))
def getProp(object, name, default):
    return getattr(object, toPath(name), default)
def setProp(object, name, data):
    object[name] = data
def removeProp(object, name):
    if hasProp(object, name):
        del object[name]



# ID Types
############################

# used for all custom id properties
prefix = "AN "

class TransformsIDType:
    @classmethod
    def create(cls, object, id):
        cls.write(object, id, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    @staticmethod
    def remove(object, id):
        removeProp(object, prefix + id + " Location")
        removeProp(object, prefix + id + " Rotation")
        removeProp(object, prefix + id + " Scale")

    @staticmethod
    def exists(object, id):
        return hasProp(object, prefix + id + " Location") and \
               hasProp(object, prefix + id + " Rotation") and \
               hasProp(object, prefix + id + " Scale")

    @staticmethod
    def read(object, id):
        location = getProp(object, prefix + id + " Location", (0, 0, 0))
        rotation = getProp(object, prefix + id + " Rotation", (0, 0, 0))
        scale = getProp(object, prefix + id + " Scale", (1, 1, 1))

        return Vector(location), Euler(rotation), Vector(scale)

    @staticmethod
    def write(object, id, data):
        setProp(object, prefix + id + " Location", data[0])
        setProp(object, prefix + id + " Rotation", data[1])
        setProp(object, prefix + id + " Scale", data[2])

    @staticmethod
    def draw(layout, object, id, advanced = False):
        row = layout.row()

        col = row.column(align = True)
        col.label("Location")
        col.prop(object, toPath(prefix + id + " Location"), text = "")

        col = row.column(align = True)
        col.label("Rotation")
        col.prop(object, toPath(prefix + id + " Rotation"), text = "")

        col = row.column(align = True)
        col.label("Scale")
        col.prop(object, toPath(prefix + id + " Scale"), text = "")

    @staticmethod
    def drawOperators(layout, object, id):
        props = layout.operator("an.set_current_transforms", text = "Use Current Transforms")
        props.id = id


class SimpleIDType:
    default = ""

    @classmethod
    def create(cls, object, id):
        cls.write(object, id, cls.default)

    @staticmethod
    def remove(object, id):
        removeProp(object, prefix + id)

    @staticmethod
    def exists(object, id):
        return hasProp(object, prefix + id)

    @classmethod
    def read(cls, object, id):
        value = getProp(object, prefix + id, cls.default)
        return value

    @staticmethod
    def write(object, id, data):
        setProp(object, prefix + id, data)

    @classmethod
    def draw(cls, layout, object, id, advanced = False):
        item = getItem(id)
        text = "" if advanced else item.name
        layout.prop(object, toPath(prefix + id), text = text)

    @staticmethod
    def drawOperators(layout, object, id):
        pass


class FloatIDType(SimpleIDType):
    default = 0.0

class IntegerIDType(SimpleIDType):
    default = 0

class StringIDType(SimpleIDType):
    default = ""

    @staticmethod
    def drawOperators(layout, object, id):
        props = layout.operator("an.set_current_texts", text = "Use Current Texts")
        props.id = id


idTypes = { "Transforms" : TransformsIDType,
            "Float" : FloatIDType,
            "String" : StringIDType,
            "Integer" : IntegerIDType }

idTypeItems = [
    ("Transforms", "Transforms", "Contains 3 vectors for location, rotation and scale"),
    ("Float", "Float", "A single real number"),
    ("String", "String", "A text field"),
    ("Integer", "Integer", "Number without decimals") ]



# Panels
##############################

class IDKeysManagerPanel(bpy.types.Panel):
    bl_idname = "an.id_keys_manager"
    bl_label = "ID Keys Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "AN"

    def draw(self, context):
        layout = self.layout
        self.drawExistingKeysBox(layout)
        self.drawNewKeyRow(layout)

    def drawExistingKeysBox(self, layout):
        box = layout.box()
        idKeys = getIDKeys()
        if len(idKeys) == 0:
            box.label("There is no ID Key")
            return

        col = box.column(align = True)
        for item in idKeys:
            row = col.row()
            row.prop(item, "name", text = "")
            row.label(item.type)
            hideIcon = "RESTRICT_VIEW_ON" if item.hide else "RESTRICT_VIEW_OFF"
            row.prop(item, "hide", icon = hideIcon, emboss = False, icon_only = True)
            props = row.operator("an.remove_id_key", icon = "X", emboss = False, text = "")
            props.id = item.id

    def drawNewKeyRow(self, layout):
        idKeySettings = bpy.context.scene.animationNodes.idKeys
        row = layout.row(align = True)
        row.prop(idKeySettings, "newKeyName", text = "")
        row.prop(idKeySettings, "newKeyType", text = "")
        row.operator("an.new_id_key", icon = "PLUS", text = "")


class IDKeyPanel(bpy.types.Panel):
    bl_idname = "an.id_keys"
    bl_label = "ID Keys for Active Object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "AN"

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw(self, context):
        layout = self.layout
        object = context.active_object
        settings = getIDKeySettings()

        layout.prop(settings, "showAdvanced")
        layout.separator()

        if settings.showAdvanced: self.drawKeysForObjectAdvanced(layout, object)
        else: self.drawKeysForObjectSimple(layout, object)

    def drawKeysForObjectAdvanced(self, layout, object):
        for item in getIDKeys():
            if item.hide: continue
            box = layout.box()

            keyName, keyType, keyID = item.name, item.type, item.id
            typeClass = getIDTypeClass(keyType)
            keyExists = typeClass.exists(object, keyID)

            self.drawHeader(box, object, keyName, keyType, keyID, keyExists)
            if keyExists:
                typeClass.draw(box, object, keyID, advanced = True)
            typeClass.drawOperators(box, object, keyID)

    def drawKeysForObjectSimple(self, layout, object):
        for item in getIDKeys():
            if item.hide: continue
            keyName, keyType, keyID = item.name, item.type, item.id
            typeClass = getIDTypeClass(keyType)
            keyExists = typeClass.exists(object, keyID)
            if keyExists:
                typeClass.draw(layout, object, keyID, advanced = False)
            else:
                props = layout.operator("an.create_key_on_object", icon = "NEW",  text = keyName)
                props.id = keyID
                props.type = keyType
                props.objectName = object.name

    def drawHeader(self, box, object, keyName, keyType, keyID, keyExists):
        row = box.row()

        subRow = row.row()
        subRow.alignment = "LEFT"
        subRow.label(keyName)

        subRow = row.row()
        subRow.alignment = "RIGHT"
        subRow.label(keyType)

        if keyExists:
            props = row.operator("an.remove_key_from_object", icon = "X", emboss = False, text = "")
        else:
            props = row.operator("an.create_key_on_object", icon = "NEW", emboss = False,  text = "")
        props.id = keyID
        props.type = keyType
        props.objectName = object.name



# Operators
##############################

class NewIdKey(bpy.types.Operator):
    bl_idname = "an.new_id_key"
    bl_label = "New ID Key"
    bl_description = "New Key"

    @classmethod
    def poll(cls, context):
        id, type = cls.getNewKeyData()
        return isCreatable(id, type)

    def execute(self, context):
        id, type = self.getNewKeyData()
        createIDKey(id, type)
        getIDKeySettings().newKeyName = ""
        context.area.tag_redraw()
        return {'FINISHED'}

    @classmethod
    def getNewKeyData(cls):
        idKeySettings = getIDKeySettings()
        return idKeySettings.newKeyName, idKeySettings.newKeyType


class RemoveIDKey(bpy.types.Operator):
    bl_idname = "an.remove_id_key"
    bl_label = "Remove ID Key"
    bl_description = "Remove this key"

    id = StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        idKeys = context.scene.animationNodes.idKeys
        for i, item in enumerate(idKeys.keys):
            if item.id == self.id:
                idKeys.keys.remove(i)
        context.area.tag_redraw()
        return {'FINISHED'}


class CreateKeyOnObject(bpy.types.Operator):
    bl_idname = "an.create_key_on_object"
    bl_label = "Create Key on Object"
    bl_description = "Create the key on this object"

    id = StringProperty()
    type = StringProperty()
    objectName = StringProperty()

    def execute(self, context):
        typeClass = getIDTypeClass(self.type)
        typeClass.create(bpy.data.objects.get(self.objectName), self.id)
        context.area.tag_redraw()
        return {'FINISHED'}


class RemoveKeyFromObject(bpy.types.Operator):
    bl_idname = "an.remove_key_from_object"
    bl_label = "Remove Key from Object"
    bl_description = "Remove the key from this object"

    id = StringProperty()
    type = StringProperty()
    objectName = StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        typeClass = getIDTypeClass(self.type)
        typeClass.remove(bpy.data.objects.get(self.objectName), self.id)
        context.area.tag_redraw()
        return {'FINISHED'}


class SetCurrentTransforms(bpy.types.Operator):
    bl_idname = "an.set_current_transforms"
    bl_label = "Set Current Transforms"
    bl_description = "Set current transforms on this ID Key for all selected objects"

    id = StringProperty()

    def execute(self, context):
        for object in context.selected_objects:
            TransformsIDType.write(object, self.id, (object.location, object.rotation_euler, object.scale))
        return {'FINISHED'}


class SetCurrentTexts(bpy.types.Operator):
    bl_idname = "an.set_current_texts"
    bl_label = "Set Current Texts"
    bl_description = "Set current text on this ID Key for all selected objects"

    id = StringProperty()

    def execute(self, context):
        for object in context.selected_objects:
            StringIDType.write(object, self.id, getattr(object.data, "body", ""))
        return {'FINISHED'}



# Properties
################################

class IDKeyType(bpy.types.PropertyGroup):
    name = StringProperty()
    id = StringProperty()
    type = StringProperty()
    hide = BoolProperty(default = False)

class IDKeySettings(bpy.types.PropertyGroup):
    keys = CollectionProperty(type = IDKeyType)
    newKeyName = StringProperty(default = "Initial Transforms")
    newKeyType = EnumProperty(items = idTypeItems, name = "Type", default = "Transforms")
    showAdvanced = BoolProperty(name = "Show Advanced", default = True, description = "Show more options for each ID Key")
