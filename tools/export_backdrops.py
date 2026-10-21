# SPDX-License-Identifier: GPL-3.0-or-later
"""Export only the three selected QLS meshes, using Blender 4.5 for compatibility.

Developer tool; runtime never depends on the sibling QLS checkout.
"""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'blender-qls/quick_lighting_studio/assets/stages.blend'
DESTINATION = ROOT / 'quick_lighting_environment/_backdrops.blend'
NAMES = {
    'QLS Stage - L Backdrop': 'L Backdrop',
    'QLS Stage - Flat Background': 'Flat Background',
    'QLS Stage - Floor': 'Floor',
}

with bpy.data.libraries.load(str(SOURCE), link=False) as (source, destination):
    assert all(name in source.collections for name in NAMES)
    destination.collections = list(NAMES)
objects = set()
for collection, name in zip(destination.collections, NAMES.values()):
    assert len(collection.all_objects) == 1, collection.name
    obj = collection.all_objects[0]
    assert obj.type == 'MESH', obj.name
    obj.name = name
    obj.data.name = name + ' Mesh'
    obj.data.materials.clear()
    for block in (obj, obj.data):
        for key in tuple(block.keys()):
            if key.startswith('qls_'):
                del block[key]
    objects.add(obj)
bpy.data.libraries.write(str(DESTINATION), objects, fake_user=True, compress=True)
print('QLE_BACKDROP_ASSETS_EXPORTED', DESTINATION, sorted(obj.name for obj in objects), flush=True)

legacy = ROOT / 'quick_lighting_environment/_backdrop.blend'
with bpy.data.libraries.load(str(legacy), link=False) as (_source, destination):
    destination.objects = ['Backdrop']
obj = destination.objects[0]
print('QLE_LEGACY_BACKDROP', tuple(obj.location), tuple(obj.scale), obj.hide_render, obj.hide_viewport)
for material in obj.data.materials:
    print('QLE_LEGACY_MATERIAL', material.name, material.use_nodes, tuple(material.diffuse_color), material.roughness)
    if material.node_tree:
        for node in material.node_tree.nodes:
            print('QLE_LEGACY_NODE', node.type, {socket.name: tuple(socket.default_value) if socket.type in {'RGBA', 'VECTOR'} else socket.default_value for socket in node.inputs if socket.name in {'Base Color', 'Roughness', 'Metallic'}})
