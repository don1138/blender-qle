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

import bpy
import os

bl_info = {
    "name": "QLE (Quick Lighting Environment)",
    "description": "Add Area Lights & Sets World Surface",
    "author": "Don Schnitzius",
    "version": (1, 8, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Scene",
    "warning": "",
    "doc_url": "https://github.com/don1138/blender-qle",
    "support": "COMMUNITY",
    "category": "Lighting",
}


# Global state class
class QLEState:
    """Stores global state for the QLE add-on."""
    def __init__(self):
        self.old_world_name = None

qle_state = QLEState()

LIGHT_SETTINGS = {
    "Area_Right": {
        "loc": (5, -5, 5),
        "shape": "RECTANGLE",
        "energy": 100,
        "size_x": 2,
        "size_y": 6,
        "color": (0.407237, 0.564712, 1), #3800
        "temperature": None
    },
    "Area_Left": {
        "loc": (-5, -5, 5),
        "shape": "RECTANGLE",
        "energy": 100,
        "size_x": 2,
        "size_y": 6,
        "color": (1, 0.584079, 0.337164), #20,000
        "temperature": None
    },
    "Area_Fill": {
        "loc": (0, 0, 8),
        "shape": "DISK",
        "energy": 800,
        "size_x": 8,
        "size_y": 8,
        "color": (1, 0.846874, 0.723055), #5454
        "temperature": None
    },
    "Area_Back": {
        "loc": (0, 5, 5),
        "shape": "RECTANGLE",
        "energy": 100,
        "size_x": 8,
        "size_y": 1,
        "color": (1, 0.846874, 0.723055), #5454
        "temperature": None
    },
}


def wo_register():
    """Registers the original world state before making changes."""
    scene = bpy.context.scene
    # Only record the old world name if we haven't already done so
    if qle_state.old_world_name is None and scene.world:
        qle_state.old_world_name = scene.world.name


def ensure_collection_exists(collection_name="QLE", parent_collection=None):
    """Ensure that a collection with the given name exists, and return it."""
    col = bpy.data.collections.get(collection_name)
    if col is None:
        if parent_collection is None:
            parent_collection = bpy.context.scene.collection
        col = bpy.data.collections.new(collection_name)
        parent_collection.children.link(col)
    return col


def move_to_collection(obj, collection_name="QLE"):
    """Ensure an object is exclusively placed in the specified collection."""
    for c in obj.users_collection:
        c.objects.unlink(obj)
    target_collection = ensure_collection_exists(collection_name)
    if obj.name not in target_collection.objects:
        target_collection.objects.link(obj)


def load_object_from_blend(filepath, obj_name, collection_name="QLE"):
    """Load an object from a .blend file and place it into the specified collection."""
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name == obj_name]

    loaded_objs = []
    for obj in data_to.objects:
        if obj:
            move_to_collection(obj, collection_name)
            loaded_objs.append(obj)
    return loaded_objs


def add_backdrop():
    """Adds or ensures the Backdrop object exists and is in the QLE collection."""
    # If the Backdrop object itself exists, just move it to QLE and return.
    backdrop = bpy.data.objects.get("Backdrop")
    if backdrop:
        move_to_collection(backdrop, "QLE")
        return

    # If we don't have the Backdrop object, check if its mesh data block is already in bpy.data.meshes.
    # Here we assume the mesh data name is "_backdrop_".
    backdrop_mesh = bpy.data.meshes.get("_backdrop_")
    if backdrop_mesh:
        # If the mesh data exists, we can create a new object from it without importing again.
        backdrop = bpy.data.objects.new("Backdrop", backdrop_mesh)
        bpy.context.scene.collection.objects.link(backdrop)
        move_to_collection(backdrop, "QLE")
        return

    # If the mesh isn't found, we need to load it from the external blend file.
    filepath = os.path.join(os.path.dirname(__file__), "_backdrop.blend")
    objs = load_object_from_blend(filepath, "Backdrop", "QLE")


def apply_blackbody_to_light(light, temperature):
    """Adds a Blackbody node to the light's emission if a temperature is specified."""
    light.data.use_nodes = True
    nodes = light.data.node_tree.nodes
    links = light.data.node_tree.links

    emission = nodes.get('Emission')
    # Clear existing links to the emission color to avoid duplicates
    for link in list(links):
        if link.to_node == emission and link.to_socket == emission.inputs[0]:
            links.remove(link)

    node_bb = nodes.new(type="ShaderNodeBlackbody")
    node_bb.location = (-400, 0)
    node_bb.inputs[0].default_value = temperature
    links.new(node_bb.outputs[0], emission.inputs[0])


def create_empty(name, location):
    """Creates an empty object directly."""
    empty = bpy.data.objects.new(name=name, object_data=None)
    empty.empty_display_type = 'PLAIN_AXES'
    empty.location = location
    bpy.context.scene.collection.objects.link(empty)
    return empty


def create_and_configure_light(name, settings):
    """Create or reconfigure a single light based on provided settings."""
    light = bpy.data.objects.get(name)
    if not light:
        light_data = bpy.data.lights.new(name=name, type='AREA')
        light = bpy.data.objects.new(name, light_data)
        light.location = settings["loc"]
        light_data.shape = settings["shape"]
        light_data.energy = settings["energy"]
        light_data.size = settings["size_x"]
        light_data.size_y = settings["size_y"]
        light_data.color = settings["color"]
        bpy.context.scene.collection.objects.link(light)

        if settings["temperature"]:
            apply_blackbody_to_light(light, settings["temperature"])

    move_to_collection(light, "QLE")
    return light


def setup_tracking(light, target):
    """Adds a Track To constraint to a light object to track the given target object."""
    bpy.context.view_layer.objects.active = light
    # Remove old TRACK_TO constraints if they exist
    for c in light.constraints:
        if c.type == 'TRACK_TO':
            light.constraints.remove(c)

    track = light.constraints.new(type='TRACK_TO')
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    track.target = target


def setup_environment_lights():
    """Set up all lights and their target."""
    target = bpy.data.objects.get("Lights_Target")
    if not target:
        target = create_empty("Lights_Target", (0, 0, 1))
    move_to_collection(target, "QLE")

    for name, settings in LIGHT_SETTINGS.items():
        light = create_and_configure_light(name, settings)
        setup_tracking(light, target)


def create_world(world_name, bg_strength=0.25, temperature=5454):
    """Creates a new world with a blackbody-based background."""
    world = bpy.data.worlds.new(world_name)
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    background = nodes.get('Background')
    blackbody = nodes.new('ShaderNodeBlackbody')

    blackbody.inputs[0].default_value = temperature
    background.inputs[1].default_value = bg_strength

    links.new(blackbody.outputs[0], background.inputs[0])
    return world


def delete_objects(objects_to_delete):
    """Deletes objects directly from bpy.data."""
    for obj in objects_to_delete:
        bpy.data.objects.remove(obj, do_unlink=True)


def clear_objects_safe(object_names):
    """Safely clears objects from the scene if they exist."""
    objects_to_delete = [bpy.data.objects.get(name) for name in object_names if bpy.data.objects.get(name)]
    delete_objects(objects_to_delete)


def setup_qle_environment():
    """Fully sets up the QLE environment including world, lights, and backdrop."""
    scene = bpy.context.scene
    wo_register()

    # Ensure QLE collection
    ensure_collection_exists("QLE", scene.collection)

    # Create/Assign QLE World
    qle_world = bpy.data.worlds.get("QLE World")
    if not qle_world:
        qle_world = create_world("QLE World")
    scene.world = qle_world

    # Setup lights and backdrop
    setup_environment_lights()
    add_backdrop()


def clear_qle_environment():
    """Clears the QLE environment, including removing QLE world and lights."""
    scene = bpy.context.scene

    # Clear QLE objects
    to_delete = list(LIGHT_SETTINGS.keys()) + ["Lights_Target", "Backdrop"]
    clear_objects_safe(to_delete)

    # Remove QLE collection
    qle_col = bpy.data.collections.get('QLE')
    if qle_col:
        bpy.data.collections.remove(qle_col)

    # Handle QLE world removal
    qle_world = bpy.data.worlds.get("QLE World")
    if qle_world:
        # Resetting background strength (optional)
        background_node = qle_world.node_tree.nodes.get("Background")
        if background_node:
            background_node.inputs[1].default_value = 1

        # Unlink QLE World from all scenes
        for s in bpy.data.scenes:
            if s.world == qle_world:
                # Try restoring old world or default
                old_world = bpy.data.worlds.get(qle_state.old_world_name) if qle_state.old_world_name else None
                s.world = old_world or bpy.data.worlds.get("World") or create_world("World")

        # Remove QLE World after unlinking
        bpy.data.worlds.remove(qle_world, do_unlink=True)

    # Ensure scene has a valid world
    if not scene.world:
        scene.world = bpy.data.worlds.get("World") or create_world("World")

    # Purge orphaned data
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


def btn_01(self, context):
    """Button action to set up QLE environment."""
    setup_qle_environment()

    self.report({'INFO'}, "QLE added to Scene")


def btn_02(self, context):
    """Button action to clear QLE environment."""
    clear_qle_environment()

    self.report({'INFO'}, "QLE removed from Scene")


class AddLights(bpy.types.Operator):
    """Add Lights"""
    bl_idname = "qle.add_lights"
    bl_label = "Add Environment"

    def execute(self, context):
        btn_01(self, context)
        return {'FINISHED'}


class ClearLights(bpy.types.Operator):
    """Remove Lights"""
    bl_idname = "qle.clear_lights"
    bl_label = "Clear Environment"

    def execute(self, context):
        btn_02(self, context)
        return {'FINISHED'}


class LayoutLightsPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor."""
    bl_label = "Quick Lighting Environment"
    bl_idname = "SCENE_PT_quickEnvironment"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5
        row.operator(AddLights.bl_idname, icon='ADD')
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
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
