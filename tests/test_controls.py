# SPDX-License-Identifier: GPL-3.0-or-later
"""Background Blender control tests; temporary factory scenes only."""
from math import radians
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_foundation as foundation
from quick_lighting_environment import backdrops, colors, environment as env, light_controls, panels, position, temperatures
from quick_lighting_environment.state import IDENTITY, PROTECTED, ROLE


class LayoutProbe:
    """Exercise every Python drawing branch without pretending to render UI."""
    def __init__(self, calls=None, opened=True, full_width=True):
        self.calls = calls if calls is not None else []
        self.opened = opened
        self.full_width = full_width

    def row(self, **kwargs):
        return LayoutProbe(self.calls, self.opened, full_width=False)

    column = row
    box = row

    def panel(self, name, **kwargs):
        assert self.full_width, 'Blender panels cannot be nested inside boxes or columns'
        self.calls.append(('panel', name))
        return self.row(), LayoutProbe(self.calls, self.opened) if self.opened else None

    def prop(self, owner, name, **kwargs):
        value = getattr(owner, name)  # Validate actual registered RNA paths/getters.
        self.calls.append(('prop', name))

    def prop_enum(self, owner, name, value, **kwargs):
        enum_items = getattr(owner.bl_rna.properties[name], 'enum_items', ())
        assert value in {item.identifier for item in enum_items}
        self.calls.append(('prop_enum', name, value))

    def operator(self, name, **kwargs):
        group, identifier = name.split('.')
        getattr(getattr(bpy.ops, group), identifier).get_rna_type()
        self.calls.append(('operator', name))
        return SimpleNamespace()

    def operator_menu_enum(self, name, field, **kwargs):
        return self.operator(name, **kwargs)

    def label(self, **kwargs):
        self.calls.append(('label', kwargs.get('text', '')))

    def menu(self, name, **kwargs):
        self.calls.append(('menu', name))

    def context_pointer_set(self, name, owner):
        pass

    def separator(self):
        pass


class PanelProbe:
    draw = panels.LightingPanel.draw
    draw_backdrop = panels.LightingPanel.draw_backdrop
    draw_world = panels.LightingPanel.draw_world

    def __init__(self, opened):
        self.layout = LayoutProbe(opened=opened)


class ControlsTests(unittest.TestCase):
    setUp = foundation.FoundationTests.setUp
    add = foundation.FoundationTests.add
    by_slot = foundation.FoundationTests.by_slot

    def update(self):
        self.scene.view_layers[0].update()

    def assertPoint(self, actual, expected):
        self.assertLess((Vector(actual) - Vector(expected)).length, 0.0001, (tuple(actual), tuple(expected)))

    def test_default_orbit_matches_world_and_distance_only_changes_radius(self):
        self.add()
        light = self.by_slot()
        before = position.orbit(light)
        self.assertAlmostEqual(before[0], radians(-45), places=5)
        light.qle_distance = 2
        self.update()
        after = position.orbit(light)
        self.assertAlmostEqual(after[0], before[0], places=5)
        self.assertAlmostEqual(after[1], before[1], places=5)
        self.assertAlmostEqual(after[2], 2, places=5)
        light.qle_around = radians(90)
        self.update()
        self.assertAlmostEqual(light.qle_around, radians(90), places=5)
        self.assertAlmostEqual(light.qle_distance, 2, places=5)
        light.qle_elevation = radians(15)
        self.update()
        self.assertAlmostEqual(light.qle_elevation, radians(15), places=5)

    def test_manual_moves_are_live_and_subsequent_distance_does_not_snap(self):
        self.add()
        light = self.by_slot()
        light.location += Vector((2, 1, 3))
        self.update()
        before = position.world_position(light)
        center = position.world_position(env.target(self.scene))
        around, elevation, distance = position.orbit(light)
        light.qle_distance = distance * 2
        self.update()
        self.assertPoint(position.world_position(light), center + (before - center) * 2)
        self.assertAlmostEqual(light.qle_around, around, places=5)
        self.assertAlmostEqual(light.qle_elevation, elevation, places=5)

    def test_native_global_grab_moves_actual_light(self):
        self.add()
        light = self.by_slot()
        for obj in self.scene.objects:
            obj.select_set(False)
        light.select_set(True)
        bpy.context.view_layer.objects.active = light
        before = position.world_position(light)
        result = bpy.ops.transform.translate(value=(1, 2, 3), orient_type='GLOBAL')
        self.assertEqual(result, {'FINISHED'})
        self.update()
        self.assertPoint(position.world_position(light), before + Vector((1, 2, 3)))
        self.assertAlmostEqual(light.qle_distance, (position.world_position(light) - position.world_position(env.target(self.scene))).length, places=5)

    def test_follow_and_aim_are_independent_and_toggling_preserves_position(self):
        self.add()
        light = self.by_slot()
        target = env.target(self.scene)
        before = position.world_position(light)
        target.location += Vector((2, 3, 4))
        self.update()
        self.assertPoint(position.world_position(light), before + Vector((2, 3, 4)))
        light.qle_follow_target = False
        self.update()
        fixed = position.world_position(light)
        target.location += Vector((1, 2, 3))
        self.update()
        self.assertPoint(position.world_position(light), fixed)
        direction = light.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        desired = (position.world_position(target) - fixed).normalized()
        self.assertPoint(direction, desired)
        light.qle_follow_target = True
        self.update()
        self.assertPoint(position.world_position(light), fixed)
        target.location.x += 2
        self.update()
        self.assertPoint(position.world_position(light), fixed + Vector((2, 0, 0)))

    def test_manual_aim_preserves_direction_and_can_rotate_without_moving(self):
        self.add()
        light = self.by_slot()
        before = light.matrix_world.to_quaternion()
        light.qle_aim_mode = 'MANUAL'
        self.update()
        self.assertLess(before.rotation_difference(light.matrix_world.to_quaternion()).angle, 0.0001)
        location = position.world_position(light)
        light.rotation_euler = (0.2, 0.3, 0.4)
        self.update()
        self.assertPoint(position.world_position(light), location)
        rotation = light.matrix_world.to_quaternion()
        env.target(self.scene).location.x += 3
        self.update()
        self.assertLess(rotation.rotation_difference(light.matrix_world.to_quaternion()).angle, 0.0001)
        light.qle_aim_mode = 'TARGET'
        self.update()
        direction = light.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        self.assertPoint(direction, (position.world_position(env.target(self.scene)) - position.world_position(light)).normalized())

    def test_pole_and_coincident_positions_have_finite_controls(self):
        self.add()
        light = self.by_slot()
        center = position.world_position(env.target(self.scene))
        position.set_world_position(light, center + Vector((0, 0, 2)))
        self.update()
        self.assertAlmostEqual(light.qle_elevation, radians(90), places=5)
        light.qle_around = radians(65)
        light.qle_elevation = radians(30)
        self.update()
        self.assertAlmostEqual(light.qle_around, radians(65), places=5)
        position.set_world_position(light, center)
        self.update()
        self.assertTrue(all(abs(v) < 1000 for v in position.orbit(light)))

    def test_object_follow_auto_snaps_allows_offset_and_ignores_rotation_scale(self):
        self.add()
        target = env.target(self.scene)
        source = bpy.data.objects.new('Subject', None)
        self.scene.collection.objects.link(source)
        source.location = (3, 4, 5)
        self.update()
        target.qle_follow_mode = 'OBJECT'
        target.qle_follow_object = source
        self.update()
        self.assertPoint(position.world_position(target), (3, 4, 5))
        target.qle_target_position = (3, 4, 6)
        source.location = (6, 7, 8)
        source.rotation_euler = (1, 2, 3)
        source.scale = (2, 3, 4)
        self.update()
        self.assertPoint(position.world_position(target), (6, 7, 9))
        self.assertPoint(target.matrix_world.to_scale(), (1, 1, 1))
        self.assertPoint(target.matrix_world.to_euler(), (0, 0, 0))
        before = position.world_position(target)
        target.qle_follow_mode = 'FREE'
        source.location = (30, 40, 50)
        self.update()
        self.assertPoint(position.world_position(target), before)

    def test_switching_follow_object_snaps_to_new_origin(self):
        self.add()
        target = env.target(self.scene)
        target.qle_follow_mode = 'OBJECT'
        for location in ((1, 2, 3), (4, 5, 6)):
            obj = bpy.data.objects.new('Subject', None)
            self.scene.collection.objects.link(obj)
            obj.location = location
            self.update()
            target.qle_follow_object = obj
            self.update()
            self.assertPoint(position.world_position(target), location)

    def test_deleting_follow_object_preserves_last_target_and_light_position(self):
        self.add()
        target = env.target(self.scene)
        obj = bpy.data.objects.new('Subject', None)
        self.scene.collection.objects.link(obj)
        target.qle_follow_mode = 'OBJECT'
        target.qle_follow_object = obj
        obj.location = (5, 6, 7)
        self.update()
        before_target = position.world_position(target)
        light = self.by_slot()
        before_light = position.world_position(light)
        bpy.data.objects.remove(obj, do_unlink=True)
        self.update()
        self.update()
        self.assertEqual(target.qle_follow_mode, 'FREE')
        self.assertPoint(position.world_position(target), before_target)
        self.assertPoint(position.world_position(light), before_light)

    def test_target_picker_rejects_managed_objects_and_other_scenes(self):
        self.add()
        target = env.target(self.scene)
        self.assertFalse(position.target_object_allowed(target, self.by_slot()))
        other = bpy.data.objects.new('Outside scene', None)
        self.assertFalse(position.target_object_allowed(target, other))

    def test_object_mode_can_be_chosen_after_removing_its_old_source_while_free(self):
        self.add()
        target = env.target(self.scene)
        obj = bpy.data.objects.new('Subject', None)
        self.scene.collection.objects.link(obj)
        target.qle_follow_mode = 'OBJECT'
        target.qle_follow_object = obj
        target.qle_follow_mode = 'FREE'
        bpy.data.objects.remove(obj, do_unlink=True)
        target.qle_follow_mode = 'OBJECT'
        self.update()
        self.assertEqual(target.qle_follow_mode, 'OBJECT')
        self.assertIsNone(target.qle_follow_object)

    def test_add_reset_delete_light_defaults_and_cleanup(self):
        self.add()
        target = env.target(self.scene)
        target.location = (1, 2, 3)
        self.update()
        light = light_controls.add(self.scene)
        identity = light[IDENTITY]
        self.assertEqual(len(env.lights(self.scene)), 5)
        self.assertEqual(light.data.energy, 100)
        self.assertEqual(light.data.shape, 'RECTANGLE')
        self.assertEqual(light.data.qle_color_mode, 'RGB')
        self.assertAlmostEqual(light.qle_distance, 3, places=5)
        self.assertAlmostEqual(light.qle_elevation, radians(45), places=5)
        self.assertAlmostEqual(light.qle_around, 0, places=5)
        light.name = 'User name'
        env.set_protected(self.scene, light, True)
        light.qle_distance = 8
        light.data.energy = 999
        light.data.qle_color_mode = 'KELVIN'
        light.qle_aim_mode = 'MANUAL'
        light_controls.reset(self.scene, light)
        self.assertEqual(light.name, 'User name')
        self.assertTrue(light.get(PROTECTED))
        self.assertEqual(light.data.energy, 100)
        self.assertEqual(light.qle_aim_mode, 'TARGET')
        self.assertEqual(light.data.qle_color_mode, 'RGB')
        self.assertAlmostEqual(light.qle_distance, 3, places=5)
        light_controls.delete(self.scene, light)
        self.assertFalse(any(obj.get('qle_dependency_for') == identity for obj in env.objects_for(self.scene)))
        self.assertEqual(len(env.lights(self.scene)), 4)

    def test_reset_original_light_restores_world_position_without_moving_target(self):
        self.add()
        target = env.target(self.scene)
        target.location = (2, 3, 4)
        self.update()
        light = self.by_slot()
        light.qle_distance = 1
        light_controls.reset(self.scene, light)
        self.update()
        self.assertPoint(position.world_position(light), (-5, -5, 5))
        self.assertPoint(position.world_position(target), (2, 3, 4))

    def test_light_color_modes_keep_separate_values_and_no_tint(self):
        self.add()
        data = self.by_slot().data
        data.qle_rgb = (0, 0, 1)
        data.qle_color_mode = 'KELVIN'
        self.assertPoint(data.color, (1, 1, 1))
        self.assertAlmostEqual(data.qle_kelvin, 3800)
        data.qle_kelvin = 3200
        data.qle_color_mode = 'RGB'
        self.assertPoint(data.color, (0, 0, 1))
        data.qle_color_mode = 'KELVIN'
        self.assertPoint(data.color, (1, 1, 1))
        self.assertEqual(data.temperature, 3200)

    def test_classic_and_added_lights_preload_their_kelvin_defaults(self):
        self.add()
        expected = {
            'Area_Right': 20000,
            'Area_Left': 3800,
            'Area_Fill': 5454,
            'Area_Back': 5454,
        }
        for slot, kelvin in expected.items():
            light = self.by_slot(slot)
            self.assertEqual(light.data.qle_color_mode, 'RGB')
            self.assertEqual(light.data.qle_kelvin, kelvin)
        added = light_controls.add(self.scene)
        self.assertEqual(added.data.qle_color_mode, 'RGB')
        self.assertEqual(added.data.qle_kelvin, 6500)

    def test_existing_lights_gain_classic_kelvin_without_overwriting_saved_choice(self):
        self.add()
        untouched = self.by_slot('Area_Right')
        del untouched.data['_qle_kelvin']
        untouched.data.temperature = 5454
        position.initialize_light(self.scene, untouched)
        self.assertEqual(untouched.data.qle_kelvin, 20000)
        saved = self.by_slot('Area_Left')
        saved.data.qle_kelvin = 3200
        position.initialize_light(self.scene, saved)
        self.assertEqual(saved.data.qle_kelvin, 3200)

    def test_world_color_modes_keep_separate_values_and_strength(self):
        self.add()
        world = self.scene.world
        self.assertEqual(world.qle_color_mode, 'KELVIN')
        world.qle_color_mode = 'RGB'
        world.qle_rgb = (0, 0, 1)
        world.qle_color_mode = 'KELVIN'
        self.assertEqual(colors.blackbody(world).inputs['Temperature'].default_value, 5454)
        self.assertPoint(colors.background(world).inputs['Color'].default_value[:3], (1, 1, 1))
        world.qle_kelvin = 3200
        world.qle_color_mode = 'RGB'
        self.assertPoint(world.qle_rgb, (0, 0, 1))
        world.qle_color_mode = 'KELVIN'
        self.assertEqual(world.qle_kelvin, 3200)
        self.assertEqual(colors.background(world).inputs['Strength'].default_value, 0.25)

    def test_temperature_presets_apply_to_light_and_world(self):
        self.add()
        light = self.by_slot()
        self.assertEqual(len(temperatures.PRESETS), 19)
        for name, (kelvin, _label, _description) in temperatures.PRESETS.items():
            self.assertEqual(bpy.ops.qle.set_temperature(light_id=light[IDENTITY], preset=name), {'FINISHED'})
            self.assertEqual(light.data.temperature, kelvin)
            self.assertPoint(light.data.color, (1, 1, 1))
        self.assertEqual(bpy.ops.qle.set_temperature(preset='DAYLIGHT'), {'FINISHED'})
        self.assertEqual(self.scene.world.qle_kelvin, 5600)

    def test_backdrop_switches_preserve_surface_and_visibility_including_none(self):
        self.add()
        backdrops.set_color(self.scene, (0.1, 0.2, 0.3, 1))
        backdrops.set_roughness(self.scene, 0.35)
        mat = backdrops.material(self.scene)
        self.assertEqual(backdrops.surface_node(mat).type, 'BSDF_PRINCIPLED')
        for kind in ('L_BACKDROP', 'FLAT_BACKGROUND', 'FLOOR', 'NONE', 'C_BACKDROP'):
            backdrops.apply(self.scene, kind)
            self.assertEqual(self.scene.qle_settings.backdrop_type, kind)
            self.assertEqual(backdrops.material(self.scene), mat)
            self.assertAlmostEqual(backdrops.roughness(self.scene), 0.35, places=5)
            self.assertPoint(backdrops.color(self.scene)[:3], (0.1, 0.2, 0.3))
            count = len(backdrops.objects(self.scene))
            self.assertEqual(count, 0 if kind == 'NONE' else 1)
            env.add_environment(self.scene)
            self.assertEqual(len(backdrops.objects(self.scene)), count)
        obj = backdrops.objects(self.scene)[0]
        obj.hide_viewport = True
        obj.hide_render = True
        backdrops.apply(self.scene, 'FLOOR')
        self.assertTrue(backdrops.objects(self.scene)[0].hide_render)
        self.assertTrue(backdrops.objects(self.scene)[0].hide_viewport)

    def test_legacy_diffuse_default_is_untouched_until_finish_edit_and_reset_restores_it(self):
        self.add()
        self.assertEqual(backdrops.surface_node(backdrops.material(self.scene)).type, 'BSDF_DIFFUSE')
        original_color = backdrops.color(self.scene)
        backdrops.set_color(self.scene, (0.5, 0.2, 0.1, 1))
        self.assertEqual(backdrops.surface_node(backdrops.material(self.scene)).type, 'BSDF_DIFFUSE')
        bpy.ops.qle.set_finish(finish='REFLECTIVE')
        self.assertEqual(backdrops.surface_node(backdrops.material(self.scene)).type, 'BSDF_PRINCIPLED')
        self.assertAlmostEqual(backdrops.roughness(self.scene), 0.10, places=5)
        env.reset_environment(self.scene)
        self.assertEqual(backdrops.surface_node(backdrops.material(self.scene)).type, 'BSDF_DIFFUSE')
        self.assertPoint(backdrops.color(self.scene)[:3], original_color[:3])
        self.assertAlmostEqual(backdrops.roughness(self.scene), 1.0, places=5)

    def test_missing_option_asset_preserves_existing_backdrop(self):
        self.add()
        obj = backdrops.objects(self.scene)[0]
        with patch.object(backdrops, 'prepare', side_effect=env.QLEError('Missing test asset')):
            with self.assertRaises(env.QLEError):
                backdrops.apply(self.scene, 'L_BACKDROP')
        self.assertEqual(backdrops.objects(self.scene), [obj])
        self.assertEqual(self.scene.qle_settings.backdrop_type, 'C_BACKDROP')

    def test_clear_then_add_starts_with_default_c_backdrop(self):
        self.add()
        backdrops.apply(self.scene, 'NONE')
        env.clear_environment(self.scene)
        env.add_environment(self.scene)
        self.assertEqual(self.scene.qle_settings.backdrop_type, 'C_BACKDROP')
        self.assertEqual(len(backdrops.objects(self.scene)), 1)
        self.assertEqual(backdrops.surface_node(backdrops.material(self.scene)).type, 'BSDF_DIFFUSE')

    def test_protection_preserves_follow_reference_and_object_follow_through_reset_clear(self):
        self.add()
        target = env.target(self.scene)
        subject = bpy.data.objects.new('Subject', None)
        self.scene.collection.objects.link(subject)
        target.qle_follow_mode = 'OBJECT'
        target.qle_follow_object = subject
        light = self.by_slot()
        env.set_protected(self.scene, light, True)
        subject.location = (3, 4, 5)
        self.update()
        before = position.world_position(light)
        env.reset_environment(self.scene)
        self.update()
        self.assertPoint(position.world_position(light), before)
        env.clear_environment(self.scene)
        subject.location.x += 2
        self.update()
        self.assertPoint(position.world_position(light), before + Vector((2, 0, 0)))
        self.assertIsNotNone(position.reference_for(self.scene, light))
        env.add_environment(self.scene)
        self.assertEqual(len(env.lights(self.scene)), 4)

    def test_color_follow_and_none_surface_survive_save_reopen(self):
        self.add()
        light = self.by_slot()
        light_id = light[IDENTITY]
        light.data.qle_rgb = (0, 0, 1)
        light.data.qle_color_mode = 'KELVIN'
        light.data.qle_kelvin = 3200
        light.qle_follow_target = False
        self.scene.world.qle_color_mode = 'RGB'
        self.scene.world.qle_rgb = (0.2, 0.3, 0.4)
        backdrops.set_color(self.scene, (0.1, 0.2, 0.3, 1))
        backdrops.apply(self.scene, 'NONE')
        with tempfile.TemporaryDirectory(prefix='qle-controls-') as folder:
            path = str(Path(folder) / 'controls.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
            scene = bpy.context.scene
            light = next(obj for obj in env.lights(scene) if obj[IDENTITY] == light_id)
            self.assertFalse(light.qle_follow_target)
            self.assertEqual(light.data.qle_kelvin, 3200)
            light.data.qle_color_mode = 'RGB'
            self.assertPoint(light.data.qle_rgb, (0, 0, 1))
            self.assertPoint(scene.world.qle_rgb, (0.2, 0.3, 0.4))
            self.assertEqual(scene.qle_settings.backdrop_type, 'NONE')
            backdrops.apply(scene, 'FLOOR')
            self.assertPoint(backdrops.color(scene)[:3], (0.1, 0.2, 0.3))

    def test_add_repairs_missing_protected_target_without_duplicate_or_move(self):
        self.add()
        light = self.by_slot()
        env.set_protected(self.scene, light, True)
        self.update()
        before = position.world_position(light)
        private = env.private_target(self.scene, light)
        bpy.data.objects.remove(private, do_unlink=True)
        self.update()
        env.add_environment(self.scene)
        self.update()
        self.assertEqual(len(env.lights(self.scene)), 4)
        self.assertIsNotNone(env.private_target(self.scene, light))
        self.assertPoint(position.world_position(light), before)

    def test_enable_and_delete_operators(self):
        self.add()
        light = self.by_slot()
        self.assertEqual(bpy.ops.qle.enable_light(light_id=light[IDENTITY], enabled=False), {'FINISHED'})
        self.assertTrue(light.hide_viewport)
        self.assertTrue(light.hide_render)
        bpy.ops.qle.enable_light(light_id=light[IDENTITY], enabled=True)
        self.assertFalse(light.hide_viewport)
        bpy.ops.qle.delete_light(light_id=light[IDENTITY])
        self.assertEqual(len(env.lights(self.scene)), 3)
        self.assertEqual(len(env.objects_for(self.scene, 'position_reference')), 3)

    def test_registration_cleanup_and_panel_contract(self):
        self.assertEqual(panels.LightingPanel.bl_space_type, 'VIEW_3D')
        self.assertEqual(panels.LightingPanel.bl_region_type, 'UI')
        self.assertEqual(panels.LightingPanel.bl_category, 'Quick Tools')
        self.assertFalse(hasattr(bpy.types, 'SCENE_PT_quickEnvironment'))
        self.assertIn(position.synchronize, bpy.app.handlers.depsgraph_update_post)
        foundation.qle.unregister()
        self.assertNotIn(position.synchronize, bpy.app.handlers.depsgraph_update_post)
        self.assertNotIn(position.synchronize, bpy.app.handlers.frame_change_post)
        self.assertFalse(hasattr(bpy.types.Object, 'qle_distance'))
        self.assertFalse(hasattr(bpy.types.Light, 'qle_color_mode'))
        foundation.qle.register()
        self.assertEqual(list(bpy.app.handlers.depsgraph_update_post).count(position.synchronize), 1)

    def test_draw_paths_are_read_only_and_all_control_properties_exist(self):
        # Draw unopened, fully opened, RGB, Kelvin, Manual, None-stage,
        # protected-only, and empty states using real registered RNA objects.
        self.add()
        light = self.by_slot()
        for mode in ('RGB', 'KELVIN'):
            light.data.qle_color_mode = mode
            self.scene.world.qle_color_mode = mode
            light.qle_aim_mode = 'MANUAL'
            before = [(obj[IDENTITY], tuple(obj.location), len(obj.constraints)) for obj in env.objects_for(self.scene)]
            for opened in (False, True):
                probe = PanelProbe(opened)
                probe.draw(bpy.context)
                actions = [name for kind, name in probe.layout.calls if kind == 'operator'][:3]
                self.assertEqual(actions, ['qle.add_lights', 'qle.reset_environment', 'qle.clear_lights'])
            after = [(obj[IDENTITY], tuple(obj.location), len(obj.constraints)) for obj in env.objects_for(self.scene)]
            self.assertEqual(before, after)
            menu = SimpleNamespace(layout=LayoutProbe())
            panels.TemperatureMenu.draw(menu, SimpleNamespace(qle_color_owner=light))
            self.assertEqual(sum(kind == 'operator' for kind, _ in menu.layout.calls), 19)
        backdrops.apply(self.scene, 'NONE')
        PanelProbe(True).draw(bpy.context)
        env.set_protected(self.scene, light, True)
        env.clear_environment(self.scene)
        PanelProbe(True).draw(bpy.context)
        light_controls.delete(self.scene, light)
        PanelProbe(True).draw(bpy.context)

    def test_panel_blocks_controls_for_objects_shared_with_another_scene(self):
        self.add()
        light = self.by_slot()
        other = bpy.data.scenes.new('Other scene')
        other.collection.objects.link(light)
        probe = PanelProbe(True)
        probe.draw(bpy.context)
        self.assertFalse(any(kind == 'prop' for kind, _ in probe.layout.calls))
        self.assertTrue(any(kind == 'label' and 'shared' in text for kind, text in probe.layout.calls))

    def test_native_location_animation_still_evaluates_with_follow(self):
        self.add()
        light = self.by_slot()
        light.location = (-5, -5, 5)
        light.keyframe_insert('location', frame=1)
        light.location = (-3, -4, 6)
        light.keyframe_insert('location', frame=10)
        self.scene.frame_set(1)
        self.update()
        self.assertPoint(position.world_position(light), (-5, -5, 5))
        self.scene.frame_set(10)
        self.update()
        self.assertPoint(position.world_position(light), (-3, -4, 6))


if __name__ == '__main__':
    print('QLE_CONTROLS_BLENDER_VERSION=' + bpy.app.version_string, flush=True)
    foundation.qle.register()
    engines = []
    for name in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
        try:
            bpy.context.scene.render.engine = name
        except TypeError:
            continue
        engines.append(name)
    successful = True
    count = 0
    for foundation.TEST_ENGINE in engines:
        print('QLE_CONTROLS_ENGINE=' + foundation.TEST_ENGINE, flush=True)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ControlsTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        successful = successful and result.wasSuccessful()
        count += result.testsRun
    foundation.qle.unregister()
    if not successful:
        raise SystemExit(1)
    print(f'QLE_CONTROLS_TESTS_OK count={count}', flush=True)
