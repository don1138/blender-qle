bl_info = {
    "name": "QLE (Quick Lighting Environment)",
    "description": "Adds Three Area Lights and Sets World Surface to Black",
    "author": "Don Schnitzius",
    "version": (1, 5, 2),
    "blender": (2, 80, 0),
    "location": "Properties > Scene",
    "warning": "",
    "wiki_url": "https://github.com/don1138/blender-qle",
    "support": "COMMUNITY",
    "category": "Lighting",
}

"""
VERSION HISTORY

1.5.2 – 20/08/30
      – Change category to Lighting
      – Add Wiki URL
      – Rename script to "quick_lighting_environment.py"

1.5.1 – 20/08/22
      – Set light Blackbody to 5800 (More accurate Sun temperature)

1.5 – 20/07/19
    – Code cleanup
    – Arrange light nodes
    – Set light Blackbody to 6000

1.4 – 20/06/29
    – Error handling for:
        – Clicking Add Environment multple times
        – Clicking Clear Environment when there is no QLE in Scene

1.3 – 20/06/17
    – Move QLE to New Collection
    – Sourced from https://devtalk.blender.org/t/what-are-the-python-codes-related-to-collection-actions-for-blender-2-8/4479/4
    – Refactor Delete QLE
    – Sourced from https://blender.stackexchange.com/questions/173867/selecting-a-specific-collection-by-name-and-then-deleting-it
    – Add "Clear All Lights & Empties" Button (Error Handling)

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


    try:
        bpy.data.objects["Lights_Target"]
    except:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
        area_target = bpy.context.active_object
        bpy.context.active_object.name = "Lights_Target"


#    ADD AREA LIGHT RIGHT
    try:
        bpy.data.objects["Area_Right"]
    except:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(5, 1.5, 5))
        area_right = bpy.context.active_object
        area_right.name = "Area_Right"
        area_right.data.shape = 'RECTANGLE'
        area_right.data.energy = 300
        area_right.data.size = 1
        area_right.data.size_y = 3
        area_right.data.use_nodes = True
        bpy.ops.object.constraint_add(type='TRACK_TO')
        area_right.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        area_right.constraints["Track To"].up_axis = 'UP_Y'
        area_right.constraints["Track To"].target = bpy.data.objects["Lights_Target"]

#    ADD BLACKBODY
        light   = bpy.context.active_object.data
        nodes   = light.node_tree.nodes
        lights_output = nodes.get('Light Output')
        lights_output.location = 0,0
        lights_output.width = 180
        node_ox = nodes.get('Emission')
        node_ox.location = -200,0
        node_ox.width = 180
        links   = light.node_tree.links
        node_bb = nodes.new(type="ShaderNodeBlackbody")
        node_bb.inputs[0].default_value = 5800
        node_bb.location = -400,0
        node_bb.width = 180
        link    = links.new(node_bb.outputs[0], node_ox.inputs[0])


#    ADD AREA LIGHT LEFT
    try:
        bpy.data.objects["Area_Left"]
    except:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(-5, 1.5, 5))
        area_left = bpy.context.active_object
        area_left.name = "Area_Left"
        area_left.data.shape = 'RECTANGLE'
        area_left.data.energy = 300
        area_left.data.size = 1
        area_left.data.size_y = 3
        area_left.data.use_nodes = True
        bpy.ops.object.constraint_add(type='TRACK_TO')
        area_left.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        area_left.constraints["Track To"].up_axis = 'UP_Y'
        area_left.constraints["Track To"].target = bpy.data.objects["Lights_Target"]

#    ADD BLACKBODY
        light   = bpy.context.active_object.data
        nodes   = light.node_tree.nodes
        lights_output = nodes.get('Light Output')
        lights_output.location = 0,0
        lights_output.width = 180
        node_ox = nodes.get('Emission')
        node_ox.location = -200,0
        node_ox.width = 180
        links   = light.node_tree.links
        node_bb = nodes.new(type="ShaderNodeBlackbody")
        node_bb.inputs[0].default_value = 5800
        node_bb.location = -400,0
        node_bb.width = 180
        link    = links.new(node_bb.outputs[0], node_ox.inputs[0])


#    ADD AREA LIGHT FILL
    try:
        bpy.data.objects["Area_Fill"]
    except:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(0, -5, 5))
        area_fill = bpy.context.active_object
        area_fill.name = "Area_Fill"
        area_fill.data.shape = 'RECTANGLE'
        area_fill.data.energy = 300
        area_fill.data.size = 6
        area_fill.data.size_y = 4
        area_fill.data.use_nodes = True
        bpy.ops.object.constraint_add(type='TRACK_TO')
        area_fill.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        area_fill.constraints["Track To"].up_axis = 'UP_Y'
        area_fill.constraints["Track To"].target = bpy.data.objects["Lights_Target"]


#    ADD BLACKBODY
        light   = bpy.context.active_object.data
        nodes   = light.node_tree.nodes
        lights_output = nodes.get('Light Output')
        lights_output.location = 0,0
        lights_output.width = 180
        node_ox = nodes.get('Emission')
        node_ox.location = -200,0
        node_ox.width = 180
        links   = light.node_tree.links
        node_bb = nodes.new(type="ShaderNodeBlackbody")
        node_bb.inputs[0].default_value = 5800
        node_bb.location = -400,0
        node_bb.width = 180
        link    = links.new(node_bb.outputs[0], node_ox.inputs[0])


#    SELECT QLE OBJECTS
    qle_collection = find_collection(bpy.context, area_right)
    qle_collection = find_collection(bpy.context, area_left)
    qle_collection = find_collection(bpy.context, area_fill)
    qle_collection = find_collection(bpy.context, area_target)


#    CREATE NEW COLLECTION
    new_qle_collection = make_collection("QLE", qle_collection)


#    MOVE TO NEW COLLECTION
    try:
        new_qle_collection.objects.link(area_right)
        qle_collection.objects.unlink(area_right)
    except RuntimeError:
        print(f"Area_Fill already in collection")

    try:
        new_qle_collection.objects.link(area_left)
        qle_collection.objects.unlink(area_left)
    except RuntimeError:
        print(f"Area_Left already in collection")

    try:
        new_qle_collection.objects.link(area_fill)
        qle_collection.objects.unlink(area_fill)
    except RuntimeError:
        print(f"Area_Right already in collection")

    try:
        new_qle_collection.objects.link(area_target)
        qle_collection.objects.unlink(area_target)
    except RuntimeError:
        print(f"Lights_Target already in collection")

class AddLights(bpy.types.Operator):
    """Add Lights"""
    bl_idname = "dms.add_lights"
    bl_label = "Add Environment"

    def execute(self, context):
        btn_01(context)
        return {'FINISHED'}


def btn_02(context):

#    CLEAR OBJECTS
    try:
        bpy.data.objects["Area_Fill"].select_set(True)
        bpy.data.objects["Area_Left"].select_set(True)
        bpy.data.objects["Area_Right"].select_set(True)
        bpy.data.objects["Lights_Target"].select_set(True)
        bpy.ops.object.delete(use_global=False)
    except KeyError:
        print(f"One or more objects don't exist")

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


#def btn_03(context):

#    bpy.ops.object.select_by_type(type='LIGHT')
#    bpy.ops.object.delete(use_global=False)
#    bpy.ops.object.select_by_type(type='EMPTY')
#    bpy.ops.object.delete(use_global=False)
#    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1


#class ClearAllLights(bpy.types.Operator):
#    """Remove Lights"""
#    bl_idname = "dms.clear_all_lights"
#    bl_label = "Clear All Lights & Empties"

#    def execute(self, context):
#        btn_03(context)
#        return {'FINISHED'}
#

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

        # Add Environment button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(AddLights.bl_idname, icon='ADD')

        # Clear Environment button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(ClearLights.bl_idname, icon='REMOVE')

        # Big render button
#        row = layout.row()
#        row.scale_y = 1.5
#        row.operator(ClearAllLights.bl_idname, icon='PANEL_CLOSE')

        # ALTERNATE BUTTON LAYOUT
#        layout.label(text="Simple Studio Lights:")
#        row = layout.row(align=True)
#        row.operator("dms.add_lights")
#        row.operator("dms.clear_lights")


from bpy.utils import register_class, unregister_class

_classes = [
    AddLights,
    ClearLights,
#    ClearAllLights,
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