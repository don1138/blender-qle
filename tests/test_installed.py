# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise the built ZIP in an isolated Blender profile, or prepare a UI QA scene.

Set QLE_QA_ROOT to a disposable directory before launching Blender; the launcher
must also redirect BLENDER_USER_CONFIG/SCRIPTS/EXTENSIONS there.
"""
import importlib
import os
from pathlib import Path
import sys

import bpy

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
QA = Path(os.environ['QLE_QA_ROOT']).resolve()
assert QA != ROOT and str(QA).startswith('/private/tmp/qle-')
for key in ('BLENDER_USER_CONFIG', 'BLENDER_USER_SCRIPTS', 'BLENDER_USER_EXTENSIONS'):
    assert Path(os.environ[key]).resolve().is_relative_to(QA), key
repo_dir = QA / 'installed'
repo_dir.mkdir(exist_ok=True)
repo = bpy.context.preferences.extensions.repos.new(
    name='QLE Isolated QA', module='qle_qa', custom_directory=str(repo_dir))
result = bpy.ops.extensions.package_install_files(
    filepath=str(ROOT / 'dist/quick_lighting_environment-2.0.8.zip'),
    repo=repo.module, enable_on_install=True)
assert result == {'FINISHED'}, result
module_name = 'bl_ext.qle_qa.quick_lighting_environment'
qle = importlib.import_module(module_name)
assert Path(qle.__file__).resolve().is_relative_to(repo_dir)
assert hasattr(bpy.types, 'VIEW3D_PT_quick_lighting_environment')
assert bpy.ops.qle.add_lights() == {'FINISHED'}
scene = bpy.context.scene
assert len(qle.environment.lights(scene)) == 4
original_world_name = scene.qle_settings.original_world.name
light = qle.environment.lights(scene)[0]
identity = light['qle_id']
light.data.energy = 321
for kind in ('L_BACKDROP', 'FLAT_BACKGROUND', 'FLOOR', 'NONE', 'C_BACKDROP'):
    assert bpy.ops.qle.set_backdrop(kind=kind) == {'FINISHED'}, kind
assert bpy.ops.qle.protect_light(light_id=identity, protect=True) == {'FINISHED'}
blend = QA / 'QLE_QA.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.preferences.addon_disable(module=module_name)
assert not hasattr(bpy.types, 'VIEW3D_PT_quick_lighting_environment')
bpy.ops.preferences.addon_enable(module=module_name)
assert hasattr(bpy.types, 'VIEW3D_PT_quick_lighting_environment')
bpy.ops.wm.open_mainfile(filepath=str(blend))
scene = bpy.context.scene
light = next(obj for obj in qle.environment.lights(scene) if obj['qle_id'] == identity)
assert light.data.energy == 321 and light['qle_protected']
assert len(qle.environment.lights(scene)) == 4
assert bpy.ops.qle.clear_lights() == {'FINISHED'}
assert len(qle.environment.lights(scene)) == 1
assert scene.world.name == original_world_name
assert bpy.ops.qle.add_lights() == {'FINISHED'}
assert len(qle.environment.lights(scene)) == 4
assert bpy.ops.qle.protect_light(light_id=identity, protect=False) == {'FINISHED'}
assert bpy.ops.qle.reset_environment() == {'FINISHED'}
print('QLE_INSTALLED_TESTS_OK', bpy.app.version_string, qle.__file__, flush=True)
if not bpy.app.background:
    def prepare_ui():
        if bpy.context.screen is None:
            return 0.2
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.show_region_ui = True
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        print('QLE_UI_READY', blend, flush=True)
        return None
    bpy.app.timers.register(prepare_ui, first_interval=0.5)
