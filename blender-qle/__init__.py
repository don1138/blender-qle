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
    "name"       : "QLE (Quick Lighting Environment)",
    "description": "Add Area Lights & Sets World Surface",
    "author"     : "Don Schnitzius",
    "version"    : (1, 6, 2),
    "blender"    : (2, 80, 0),
    "location"   : "Properties > Scene",
    "warning"    : "",
    "wiki_url"   : "https://github.com/don1138/blender-qle",
    "support"    : "COMMUNITY",
    "category"   : "Lighting",
}


import bpy
import os

old_world_name = ""
# old_exposure_val = ""
def wo_register():
    global old_world_name
    old_world_name = bpy.context.scene.world.name
    # global old_exposure_val
    # old_exposure_val = bpy.context.scene.view_settings.exposure


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


def add_to_collection(item):
    my_coll = bpy.data.collections.get("QLE")
    qle_collection = find_collection(bpy.context, item)
    if my_coll:
        my_coll.objects.link(item)
    else:
        new_qle_collection = make_collection("QLE", qle_collection)
        new_qle_collection.objects.link(item)
    qle_collection.objects.unlink(item)


def add_tracking(item):
    bpy.ops.object.constraint_add(type='TRACK_TO')
    item.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    item.constraints["Track To"].up_axis = 'UP_Y'
    item.constraints["Track To"].target = bpy.data.objects["Lights_Target"]


def add_blackbody(item):
    item.data.use_nodes    = True
    light                  = bpy.context.active_object.data
    nodes                  = light.node_tree.nodes
    lights_output          = nodes.get('Light Output')
    lights_output.location = 0,    0
    lights_output.width    = 180
    node_ox                = nodes.get('Emission')
    node_ox.location       = -200, 0
    node_ox.width          = 180
    links                  = light.node_tree.links
    node_bb                = nodes.new(type="ShaderNodeBlackbody")
    node_bb.inputs[0].default_value       = 5454
    node_bb.location       = -400, 0
    node_bb.width          = 180
    link                   = links.new(node_bb.outputs[0], node_ox.inputs[0])


def btn_01(self,context):

    scene = bpy.context.scene
    wo_register()
    # print(old_world_name, old_exposure_val)
    qle_world = bpy.data.worlds.get("QLE World")

    if qle_world:
        scene.world = qle_world
        qle_world.node_tree.nodes["Background"].inputs[1].default_value = 0.25
    else:
        qle_world = bpy.data.worlds.new("QLE World")
        qle_world.use_nodes = True

        world_wo = qle_world.node_tree.nodes.get('World Output')
        world_wo.location = (0,0)
        world_bg = qle_world.node_tree.nodes.get('Background')
        world_bg.inputs[1].default_value = 0.25
        world_bg.location = (-200,0)
        world_bb = qle_world.node_tree.nodes.new('ShaderNodeBlackbody')
        world_bb.inputs[0].default_value = 5454
        world_bb.location = (-400,0)
        qle_world.node_tree.links.new(world_bb.outputs[0], world_bg.inputs[0])

        scene.world = qle_world

#    ADJUST EXPOSURE
    # scene.view_settings.exposure = 0.2

    area_target=bpy.data.objects.get("Lights_Target")
    if not area_target:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
        area_target = bpy.context.active_object
        bpy.context.active_object.name = "Lights_Target"
#    ADD TO COLLECTION
        add_to_collection(area_target)
    else:
        print(f"Lights_Target already in collection")
        self.report({'INFO'}, "QLE already in Scene")


#    ADD AREA LIGHT RIGHT
    area_right=bpy.data.objects.get("Area_Right")
    if area_right:
        ar_track = area_right.constraints.get("Track To")
        ar_track.target = bpy.data.objects["Lights_Target"]
        if ar_track is None:
            add_tracking(area_right)
        print(f"Area_Right already in collection")
    else:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(5, -5, 5))
        area_right = bpy.context.active_object
        area_right.name = "Area_Right"
        area_right.data.name = "Area_Right"
        area_right.data.shape = 'RECTANGLE'
        area_right.data.energy = 100
        area_right.data.size = 8
        area_right.data.size_y = 2
#    ADD TRACKING
        add_tracking(area_right)
#    ADD BLACKBODY
        add_blackbody(area_right)
        bpy.data.lights["Area_Right"].node_tree.nodes["Blackbody"].inputs[0].default_value = 20000
#    ADD TO COLLECTION
        add_to_collection(area_right)


#    ADD AREA LIGHT LEFT
    area_left=bpy.data.objects.get("Area_Left")
    if area_left:
        al_track = area_left.constraints.get("Track To")
        al_track.target = bpy.data.objects["Lights_Target"]
        if al_track is None:
            add_tracking(area_left)
        print(f"Area_Left already in collection")
    else:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(-5, -5, 5))
        area_left = bpy.context.active_object
        area_left.name = "Area_Left"
        area_left.data.name = "Area_Left"
        area_left.data.shape = 'RECTANGLE'
        area_left.data.energy = 100
        area_left.data.size = 8
        area_left.data.size_y = 2
#    ADD TRACKING
        add_tracking(area_left)
#    ADD BLACKBODY
        add_blackbody(area_left)
        bpy.data.lights["Area_Left"].node_tree.nodes["Blackbody"].inputs[0].default_value = 3800
#    ADD TO COLLECTION
        add_to_collection(area_left)


#    ADD AREA LIGHT FILL
    area_fill = bpy.data.objects.get("Area_Fill")
    if area_fill:
        af_track = area_fill.constraints.get("Track To")
        af_track.target = bpy.data.objects["Lights_Target"]
        if af_track is None:
            add_tracking(area_fill)
        print(f"Area_Fill already in collection")
    else:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(0, 0, 10))
        area_fill = bpy.context.active_object
        area_fill.name = "Area_Fill"
        area_fill.data.name = "Area_Fill"
        area_fill.data.shape = 'RECTANGLE'
        area_fill.data.energy = 400
        area_fill.data.size = 8
        area_fill.data.size_y = 8
#    ADD TRACKING
        add_tracking(area_fill)
#    ADD BLACKBODY
        add_blackbody(area_fill)
#    ADD TO COLLECTION
        add_to_collection(area_fill)


#    ADD AREA LIGHT BACK
    area_back = bpy.data.objects.get("Area_Back")
    if area_back:
        al_track = area_back.constraints.get("Track To")
        al_track.target = bpy.data.objects["Lights_Target"]
        if area_back is None:
            add_tracking(area_back)
        print(f"Area_Back already in collection")
    else:
        bpy.ops.object.light_add(type='AREA', radius=10, location=(0, 5, 5))
        area_back = bpy.context.active_object
        area_back.name = "Area_Back"
        area_back.data.name = "Area_Back"
        area_back.data.shape = 'RECTANGLE'
        area_back.data.energy = 100
        area_back.data.size = 8
        area_back.data.size_y = 1
        # area_back.rotation_euler[0] = 0.785398
#    ADD TRACKING
        add_tracking(area_back)
#    ADD BLACKBODY
        add_blackbody(area_back)
#    ADD TO COLLECTION
        add_to_collection(area_back)


#    ADD BACKDROP OBJECT
        filepath = os.path.join(os.path.dirname(__file__),"_backdrop.blend")
        obj_name = "Backdrop"
        link = False
        with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name.startswith(obj_name)]
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
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects["Area_Back"].select_set(True)
        bpy.data.objects["Area_Fill"].select_set(True)
        bpy.data.objects["Area_Left"].select_set(True)
        bpy.data.objects["Area_Right"].select_set(True)
        bpy.data.objects["Lights_Target"].select_set(True)
        bpy.data.objects["Backdrop"].select_set(True)
        bpy.ops.object.delete(use_global=True)
        self.report({'INFO'}, "QLE removed from Scene")

    except KeyError:
        # print(f"One or more objects don't exist")
        self.report({'INFO'}, "QLE not in Scene")


#    CLEAR COLLECTION
    qle_col = bpy.data.collections.get('QLE')
    if qle_col:
        bpy.data.collections.remove(qle_col)


#    PURGE SCENE
    bpy.ops.outliner.orphans_purge()


#    RESET WORLD SURFACE STRENGTH
    qle_world = bpy.data.worlds.get("QLE World")
    if qle_world:
        qle_world.node_tree.nodes["Background"].inputs[1].default_value = 1
        scene.world = old_world
        # scene.view_settings.exposure = old_exposure_val


class ClearLights(bpy.types.Operator):
    """Remove Lights"""
    bl_idname = "qle.clear_lights"
    bl_label = "Clear Environment"

    def execute(self, context):
        btn_02(self, context)
        return {'FINISHED'}


class LayoutLightsPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label       = "Quick Lighting Environment"
    bl_idname      = "SCENE_PT_quickEnvironment"
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = "scene"

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


from bpy.utils import register_class, unregister_class

_classes = [
    AddLights,
    ClearLights,
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
