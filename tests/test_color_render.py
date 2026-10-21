# SPDX-License-Identifier: GPL-3.0-or-later
"""Small actual renders verifying that RGB blue does not tint Kelvin in either engine."""
from pathlib import Path
import sys
import tempfile

import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import quick_lighting_environment as qle
from quick_lighting_environment import backdrops, colors, environment as env, light_controls


def camera(scene):
    data = bpy.data.cameras.new('Test Camera')
    obj = bpy.data.objects.new('Test Camera', data)
    scene.collection.objects.link(obj)
    obj.location = (0, -4, 3)
    obj.rotation_euler = (-obj.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = obj


def pixel(scene, path):
    scene.render.resolution_x = 32
    scene.render.resolution_y = 32
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'OPEN_EXR'
    scene.render.filepath = str(path)
    scene.render.film_transparent = False
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 4
        scene.cycles.device = 'CPU'
        scene.cycles.use_denoising = False
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    width, height = image.size
    values = tuple(image.pixels)
    index = ((height // 2) * width + width // 2) * 4
    result = values[index:index + 3]
    bpy.data.images.remove(image)
    assert len(result) == 3 and max(result) > 0.001, result
    return result


def compare(scene, data, folder, label):
    data.qle_color_mode = 'RGB'
    data.qle_rgb = (0, 0, 1)
    rgb = pixel(scene, folder / f'{label}-rgb.exr')
    data.qle_color_mode = 'KELVIN'
    data.qle_kelvin = 5600
    kelvin = pixel(scene, folder / f'{label}-kelvin.exr')
    assert rgb[2] > max(0.001, rgb[0] * 8), (label, rgb)
    assert kelvin[0] > 0.001 and kelvin[1] > 0.001, (label, kelvin)
    assert 0.2 < kelvin[2] / kelvin[0] < 2.0, (label, kelvin)
    print('QLE_COLOR_RENDER_PASS', bpy.app.version_string, scene.render.engine, label, 'RGB', rgb, 'Kelvin', kelvin, flush=True)


qle.register()
engines = []
for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
    try:
        bpy.context.scene.render.engine = engine
    except TypeError:
        continue
    engines.append(engine)
assert len(engines) == 2, engines
with tempfile.TemporaryDirectory(prefix='qle-color-render-') as folder:
    folder = Path(folder)
    for engine in engines:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        scene.render.engine = engine
        env.add_environment(scene)
        camera(scene)
        # Empty geometry and disabled lights isolate direct World color.
        backdrops.apply(scene, 'NONE')
        for light in env.lights(scene):
            light.hide_render = True
        compare(scene, scene.world, folder, engine + '-world')
        colors.background(scene.world).inputs['Strength'].default_value = 0
        mesh = bpy.data.meshes.new('Test Surface')
        mesh.from_pydata([(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)], [], [(0, 1, 2, 3)])
        obj = bpy.data.objects.new('Test Surface', mesh)
        scene.collection.objects.link(obj)
        mat = bpy.data.materials.new('White Diffuse')
        mat.use_nodes = True
        mat.node_tree.nodes.clear()
        surface = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        surface.inputs['Color'].default_value = (1, 1, 1, 1)
        output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(surface.outputs[0], output.inputs['Surface'])
        mesh.materials.append(mat)
        env.target(scene).qle_target_position = (0, 0, 0)
        light = light_controls.add(scene)
        compare(scene, light.data, folder, engine + '-light')
qle.unregister()
print('QLE_COLOR_RENDER_TESTS_OK count=4', flush=True)
