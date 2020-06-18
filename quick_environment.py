bl_info = {
    "name": "QLE (Quick Lighting Environment)",
    "author": "Don Schnitzius",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "Scene",
    "description": "Adds Three Area Lights and Sets World Surface to Black",
    "warning": "",
    "wiki_url": "",
    "category": "Scene",
}

"""
VERSION HISTORY

1.3 – 20/06/17
    – Move QLE to New Collection
    – Sourced from https://devtalk.blender.org/t/what-are-the-python-codes-related-to-collection-actions-for-blender-2-8/4479/4
    – Refactor Delete QLE
    – Sourced from https://blender.stackexchange.com/questions/173867/selecting-a-specific-collection-by-name-and-then-deleting-it
    – Add "Clear All Lights & Empties" Button (Temp fix for missing Error Handling)

1.2 – 20/06/17
    – Add Icons to Buttons
    – Refactor Register/Unregister

1.1 – 20/03/21
    – Add Blackbody to Lights

1.0 – 20/02/24
    – Create Addon
"""

import bpy


def find_collection(context, item):
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection


def make_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    else:
        new_qle_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_qle_collection)
        return new_qle_collection


def btn_01(context):

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
    bpy.context.active_object.name = "Lights_Target"

#    ADD AREA LIGHT RIGHT
    bpy.ops.object.light_add(type='AREA', radius=10, location=(5, 1.5, 5))
    bpy.context.active_object.data.use_nodes = True
    bpy.context.active_object.name = "Area_Right"
    bpy.context.active_object.data.shape = 'RECTANGLE'
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 1
    bpy.context.active_object.data.size_y = 3
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.active_object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.active_object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.active_object.constraints["Track To"].target = bpy.data.objects["Lights_Target"]

#    ADD BLACKBODY
    light   = bpy.context.active_object.data
    nodes   = light.node_tree.nodes
    node_bb = nodes.new(type="ShaderNodeBlackbody")
    node_bb.inputs[0].default_value = 5000
    node_bb.location = -200,300
    node_ox = nodes.get('Emission')
    links   = light.node_tree.links
    link    = links.new(node_bb.outputs[0], node_ox.inputs[0])


#    ADD AREA LIGHT LEFT
    bpy.ops.object.light_add(type='AREA', radius=10, location=(-5, 1.5, 5))
    bpy.context.active_object.data.use_nodes = True
    bpy.context.active_object.name = "Area_Left"
    bpy.context.active_object.data.shape = 'RECTANGLE'
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 1
    bpy.context.active_object.data.size_y = 3
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.active_object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.active_object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.active_object.constraints["Track To"].target = bpy.data.objects["Lights_Target"]

#    ADD BLACKBODY
    light   = bpy.context.active_object.data
    nodes   = light.node_tree.nodes
    node_bb = nodes.new(type="ShaderNodeBlackbody")
    node_bb.inputs[0].default_value = 5000
    node_bb.location = -200,300
    node_ox = nodes.get('Emission')
    links   = light.node_tree.links
    link    = links.new(node_bb.outputs[0], node_ox.inputs[0])


#    ADD AREA LIGHT FILL
    bpy.ops.object.light_add(type='AREA', radius=10, location=(0, -5, 5))
    bpy.context.active_object.data.use_nodes = True
    bpy.context.active_object.name = "Area_Fill"
    bpy.context.active_object.data.shape = 'RECTANGLE'
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 6
    bpy.context.active_object.data.size_y = 4
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.active_object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.active_object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.active_object.constraints["Track To"].target = bpy.data.objects["Lights_Target"]


#    ADD BLACKBODY
    light   = bpy.context.active_object.data
    nodes   = light.node_tree.nodes
    node_bb = nodes.new(type="ShaderNodeBlackbody")
    node_bb.inputs[0].default_value = 5000
    node_bb.location = -200,300
    node_ox = nodes.get('Emission')
    links   = light.node_tree.links
    link    = links.new(node_bb.outputs[0], node_ox.inputs[0])


#    SELECT QLE OBJECTS
    light1 = bpy.data.objects["Area_Fill"]
    qle_collection = find_collection(bpy.context, light1)
    light2 = bpy.data.objects["Area_Left"]
    qle_collection = find_collection(bpy.context, light2)
    light3 = bpy.data.objects["Area_Right"]
    qle_collection = find_collection(bpy.context, light3)
    target1 = bpy.data.objects["Lights_Target"]
    qle_collection = find_collection(bpy.context, target1)


#    CREATE NEW COLLECTION
    new_qle_collection = make_collection("QLE", qle_collection)


#    MOVE TO NEW COLLECTION
    new_qle_collection.objects.link(light1)
    qle_collection.objects.unlink(light1)
    new_qle_collection.objects.link(light2)
    qle_collection.objects.unlink(light2)
    new_qle_collection.objects.link(light3)
    qle_collection.objects.unlink(light3)
    new_qle_collection.objects.link(target1)
    qle_collection.objects.unlink(target1)


class AddLights(bpy.types.Operator):
    """Add Lights"""
    bl_idname = "dms.add_lights"
    bl_label = "Add Environment"

    def execute(self, context):
        btn_01(context)
        return {'FINISHED'}


def btn_02(context):

#    CLEAR OBJECTS
    bpy.data.objects["Area_Fill"].select_set(True)
    bpy.data.objects["Area_Left"].select_set(True)
    bpy.data.objects["Area_Right"].select_set(True)
    bpy.data.objects["Lights_Target"].select_set(True)
    bpy.ops.object.delete(use_global=False)

#    CLEAR COLLECTION
    col_name = 'QLE'
    try:
        bpy.data.collections.remove(bpy.data.collections[col_name])
    except KeyError:
        print(f"The collection {col_name} doesn't exist")

#    RESET WORLD SURFACE STRENGTH
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1


class ClearLights(bpy.types.Operator):
    """Remove Lights"""
    bl_idname = "dms.clear_lights"
    bl_label = "Clear Environment"

    def execute(self, context):
        btn_02(context)
        return {'FINISHED'}


def btn_03(context):

    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_by_type(type='EMPTY')
    bpy.ops.object.delete(use_global=False)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1


class ClearAllLights(bpy.types.Operator):
    """Remove Lights"""
    bl_idname = "dms.clear_all_lights"
    bl_label = "Clear All Lights & Empties"

    def execute(self, context):
        btn_03(context)
        return {'FINISHED'}


class LayoutLightsPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Quick Lighting Environment"
    bl_idname = "SCENE_PT_quickEnvironment"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(AddLights.bl_idname, icon='ADD')

        # Big render button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(ClearLights.bl_idname, icon='REMOVE')

        # Big render button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(ClearAllLights.bl_idname, icon='PANEL_CLOSE')

        # ALTERNATE BUTTON LAYOUT
#        layout.label(text="Simple Studio Lights:")
#        row = layout.row(align=True)
#        row.operator("dms.add_lights")
#        row.operator("dms.clear_lights")


from bpy.utils import register_class, unregister_class

_classes = [
    AddLights,
    ClearLights,
    ClearAllLights,
    LayoutLightsPanel
]

def register():
    for cls in _classes:
        register_class(cls)

def unregister():
    for cls in _classes:
        unregister_class(cls)

if __name__ == "__main__":
    register()
