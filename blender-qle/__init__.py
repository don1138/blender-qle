# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "QLE (Quick Lighting Environment)",
    "description": "Add Area Lights & Sets World Surface",
    "author": "Don Schnitzius",
    "version": (1, 6, 5),
    "blender": (2, 80, 0),
    "location": "Properties > Scene",
    "warning": "",
    "doc_url": "https://github.com/don1138/blender-qle",
    "support": "COMMUNITY",
    "category": "Lighting",
}


import os
import bpy


old_world_name = ""
# old_exposure_val = ""


def wo_register():
    global old_world_name
    old_world_name = bpy.context.scene.world.name
    # global old_exposure_val
    # old_exposure_val = bpy.context.scene.view_settings.exposure


def find_collection(context, item):
    collections = item.users_collection
    return collections[0] if len(collections) > 0 else context.scene.collection


def make_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    new_qle_collection = bpy.data.collections.new(collection_name)
    parent_collection.children.link(new_qle_collection)
    return new_qle_collection


def add_to_collection(item):
    my_coll = bpy.data.collections.get("QLE")
    qle_collection = find_collection(bpy.context, item)
    if my_coll:
        my_coll.objects.link(item)
    else:
        new_qle_collection = make_collection("QLE", qle_collection)
        new_qle_collection.objects.link(item)
    qle_collection.objects.unlink(item)


def add_light(loc, name, shape, energy, size_x, size_y):
    bpy.ops.object.light_add(type='AREA', radius=10, location=loc)
    result = bpy.context.active_object
    result.name = name
    result.data.name = name
    result.data.shape = shape
    result.data.energy = energy
    result.data.size = size_x
    result.data.size_y = size_y
    add_tracking(result)
    add_blackbody(result)
    add_to_collection(result)
    return result


def add_tracking(item):
    bpy.ops.object.constraint_add(type='TRACK_TO')
    item.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    item.constraints["Track To"].up_axis = 'UP_Y'
    item.constraints["Track To"].target = bpy.data.objects["Lights_Target"]


def add_track_to(ident, name):
    result = ident.constraints.get("Track To")
    result.target = bpy.data.objects["Lights_Target"]
    if result is None:
        add_tracking(ident)
    print(f"{name} already in collection")
    return result


def add_blackbody(item):
    item.data.use_nodes = True
    light = bpy.context.active_object.data
    nodes = light.node_tree.nodes
    lights_output = nodes.get('Light Output')
    lights_output.location = 0, 0
    node_ox = nodes.get('Emission')
    node_ox.location = -200, 0
    links = light.node_tree.links
    node_bb = nodes.new(type="ShaderNodeBlackbody")
    node_bb.inputs[0].default_value = 5454
    node_bb.location = -400, 0
    link = links.new(node_bb.outputs[0], node_ox.inputs[0])


def make_world():
    qle_world = bpy.data.worlds.new("QLE World")
    qle_world.use_nodes = True
    world_wo = qle_world.node_tree.nodes.get('World Output')
    world_wo.location = (0, 0)
    world_bg = qle_world.node_tree.nodes.get('Background')
    world_bg.inputs[1].default_value = 0.25
    world_bg.location = (-200, 0)
    world_bb = qle_world.node_tree.nodes.new('ShaderNodeBlackbody')
    world_bb.inputs[0].default_value = 5454
    world_bb.location = (-400, 0)
    qle_world.node_tree.links.new(world_bb.outputs[0], world_bg.inputs[0])


def also_make_world(self, scene):
    new_world = bpy.data.worlds.new("World")
    new_world.use_nodes = True
    world_wo = new_world.node_tree.nodes.get('World Output')
    world_wo.location = (0, 0)
    world_bg = new_world.node_tree.nodes.get('Background')
    world_bg.location = (-200, 0)
    scene.world = new_world


def clear_objects():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["Area_Back"].select_set(True)
    bpy.data.objects["Area_Fill"].select_set(True)
    bpy.data.objects["Area_Left"].select_set(True)
    bpy.data.objects["Area_Right"].select_set(True)
    bpy.data.objects["Lights_Target"].select_set(True)
    bpy.data.objects["Backdrop"].select_set(True)
    bpy.ops.object.delete(use_global=True)


def btn_01(self, context):

    scene = bpy.context.scene
    wo_register()
    # print(old_world_name, old_exposure_val)
    if qle_world := bpy.data.worlds.get("QLE World"):
        scene.world = qle_world
        qle_world.node_tree.nodes["Background"].inputs[1].default_value = 0.25
    else:
        make_world()
        scene.world = qle_world

#    ADJUST EXPOSURE
    # scene.view_settings.exposure = 0.2
    if area_target := bpy.data.objects.get("Lights_Target"):
        print("Lights_Target already in collection")
        self.report({'INFO'}, "QLE already in Scene")

    else:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
        area_target = bpy.context.active_object
        bpy.context.active_object.name = "Lights_Target"

#    ADD TO COLLECTION
        add_to_collection(area_target)

#    ADD AREA LIGHT RIGHT
    if area_right := bpy.data.objects.get("Area_Right"):
        ar_track = add_track_to(area_right, 'Area_Right')
    else:
        area_right = add_light((5, -5, 5), 'Area_Right',
                               'RECTANGLE', 100, 2, 6)
        bpy.data.lights["Area_Right"].node_tree.nodes["Blackbody"].inputs[0].default_value = 20000

#    ADD AREA LIGHT LEFT
    if area_left := bpy.data.objects.get("Area_Left"):
        al_track = add_track_to(area_left, 'Area_Left')
    else:
        area_left = add_light((-5, -5, 5), 'Area_Left', 'RECTANGLE', 100, 2, 6)
        bpy.data.lights["Area_Left"].node_tree.nodes["Blackbody"].inputs[0].default_value = 3800

#    ADD AREA LIGHT FILL
    if area_fill := bpy.data.objects.get("Area_Fill"):
        af_track = add_track_to(area_fill, 'Area_Fill')
    else:
        area_fill = add_light((0, 0, 8), 'Area_Fill', 'DISK', 800, 8, 8)

#    ADD AREA LIGHT BACK
    if area_back := bpy.data.objects.get("Area_Back"):
        ab_track = add_track_to(area_back, 'Area_Back')
    else:
        area_back = add_light((0, 5, 5), 'Area_Back', 'RECTANGLE', 100, 8, 1)

#    ADD BACKDROP OBJECT
        filepath = os.path.join(os.path.dirname(__file__), "_backdrop.blend")
        obj_name = "Backdrop"
        link = False
        with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
            data_to.objects = [
                name for name in data_from.objects if name.startswith(obj_name)]
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.collection.objects.link(obj)
                add_to_collection(obj)

        self.report({'INFO'}, "QLE added to Scene")


class AddLights(bpy.types.Operator):
    """Add Lights"""
    bl_idname = "qle.add_lights"
    bl_label = "Add Environment"

    def execute(self, context):
        btn_01(self, context)
        return {'FINISHED'}


def btn_02(self, context):

    scene = bpy.context.scene
    old_world = bpy.data.worlds.get(old_world_name)

#    CLEAR OBJECTS
    try:
        clear_objects()
        self.report({'INFO'}, "QLE removed from Scene")
    except KeyError:
        # print(f"One or more objects don't exist")
        self.report({'INFO'}, "QLE not in Scene")

#    CLEAR COLLECTION
    if qle_col := bpy.data.collections.get('QLE'):
        bpy.data.collections.remove(qle_col)

#    RESET WORLD SURFACE STRENGTH
    qle_world = bpy.data.worlds.get("QLE World")
    default_world = bpy.data.worlds.get("World")
    if qle_world:
        qle_world.node_tree.nodes["Background"].inputs[1].default_value = 1
        if old_world:
            scene.world = old_world
        elif default_world:
            scene.world = default_world
        else:
            self.also_make_world(scene)
            # scene.view_settings.exposure = old_exposure_val

#    PURGE SCENE
    bpy.ops.outliner.orphans_purge(
        do_local_ids=True, do_linked_ids=True, do_recursive=True)


class ClearLights(bpy.types.Operator):
    """Remove Lights"""
    bl_idname = "qle.clear_lights"
    bl_label = "Clear Environment"

    def execute(self, context):
        btn_02(self, context)
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

        # Add Environment button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(AddLights.bl_idname, icon='ADD')

        # Clear Environment button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(ClearLights.bl_idname, icon='REMOVE')


_classes = [
    AddLights,
    ClearLights,
    LayoutLightsPanel
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
