# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare legacy and current QLE defaults on the same disposable subject scene."""
from pathlib import Path
import importlib
import subprocess
import sys
import tempfile
import types
import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'quick_lighting_environment'))
qle = importlib.import_module('quick_lighting_environment')
source = subprocess.check_output(['git', '-C', str(ROOT), 'show',
    'd9b8cad:quick_lighting_environment/quick_lighting_environment/__init__.py'], text=True)
legacy = types.ModuleType('qle_legacy_render')
legacy.__file__ = qle.__file__
exec(compile(source, qle.__file__, 'exec'), legacy.__dict__)
qle.register()


def render(engine, old, output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = 128
    scene.render.resolution_y = 96
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'OPEN_EXR'
    scene.render.image_settings.color_depth = '32'
    scene.render.filepath = str(output)
    scene.cycles.samples = 16
    scene.cycles.seed = 0
    scene.cycles.use_denoising = False
    scene.cycles.device = 'CPU'
    if old:
        legacy.setup_qle_environment()
    else:
        qle.environment.add_environment(scene)
    for x, metallic, roughness in ((-0.8, 0, 0.65), (0.8, 1, 0.22)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.65, location=(x, 0, 0.68))
        obj = bpy.context.object
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        mat = bpy.data.materials.new('Subject')
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (0.35, 0.18, 0.08, 1)
        shader.inputs['Metallic'].default_value = metallic
        shader.inputs['Roughness'].default_value = roughness
        obj.data.materials.append(mat)
    data = bpy.data.cameras.new('Comparison Camera')
    cam = bpy.data.objects.new('Comparison Camera', data)
    scene.collection.objects.link(cam)
    cam.location = (4, -7, 3.6)
    cam.rotation_euler = (Vector((0, 0, 0.85)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = 48
    scene.camera = cam
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(output), check_existing=False)
    pixels = list(image.pixels)
    bpy.data.images.remove(image)
    return pixels


count = 0
with tempfile.TemporaryDirectory(prefix='qle-default-renders-') as directory:
    directory = Path(directory)
    for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
        try:
            bpy.context.scene.render.engine = engine
        except TypeError:
            continue
        a = render(engine, True, directory / 'legacy.exr')
        b = render(engine, False, directory / 'current.exr')
        differences = [abs(x-y) for index, (x,y) in enumerate(zip(a,b)) if index % 4 != 3]
        mean = sum(differences) / len(differences)
        peak = max(differences)
        print('QLE_DEFAULT_RENDER', engine, 'mean_error', mean, 'peak_error', peak, flush=True)
        assert mean < 0.005 and peak < 0.1, (engine, mean, peak)
        count += 1
assert count == 2, count
print('QLE_DEFAULT_RENDER_TESTS_OK count=2', bpy.app.version_string, flush=True)
