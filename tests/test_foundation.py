# SPDX-License-Identifier: GPL-3.0-or-later
"""Run with Blender --background --factory-startup --python-exit-code 1 --python this_file.

Uses disposable factory scenes only. Never opens a user project. A successful
process must both exit zero and emit QLE_FOUNDATION_TESTS_OK.
"""

from pathlib import Path
import importlib
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import bpy

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TEST_ENGINE = None
sys.path.insert(0, str(ROOT / 'quick_lighting_environment'))
qle = importlib.import_module('quick_lighting_environment')
from quick_lighting_environment import environment as env
from quick_lighting_environment.state import AIM_CONSTRAINT, IDENTITY, OWNER, PROTECTED, ROLE, SLOT


def close_vector(actual, expected, places=5):
    return all(round(a - b, places) == 0 for a, b in zip(actual, expected))


class FoundationTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        self.scene.render.engine = TEST_ENGINE
        self.original = bpy.data.worlds.new('Original World')
        self.original.use_nodes = True
        self.original.node_tree.nodes.get('Background').inputs['Strength'].default_value = 0.43
        self.scene.world = self.original

    def add(self):
        return env.add_environment(self.scene)

    def by_slot(self, slot='Area_Left'):
        return next(light for light in env.lights(self.scene) if light.get(SLOT) == slot)

    def legacy(self):
        source = subprocess.check_output(
            ['git', '-C', str(ROOT), 'show', 'd9b8cad:quick_lighting_environment/quick_lighting_environment/__init__.py'],
            text=True,
        )
        module = types.ModuleType('qle_legacy_fixture')
        module.__file__ = str(ROOT / 'quick_lighting_environment/quick_lighting_environment/__init__.py')
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        module.setup_qle_environment()
        return module

    def extra_light(self):
        data = bpy.data.lights.new('Extra', 'AREA')
        light = bpy.data.objects.new('Extra', data)
        env.collection_for(self.scene, 'environment').objects.link(light)
        env.mark(light, self.scene, 'light')
        env.mark(data, self.scene, 'light_data')
        light[SLOT] = ''
        light[PROTECTED] = False
        env.ensure_aim(self.scene, light, env.target(self.scene), reset=True)
        return light

    def test_add_defaults_and_idempotence(self):
        self.assertEqual(self.add(), [])
        self.assertEqual(len(env.lights(self.scene)), 4)
        self.assertEqual(len(env.objects_for(self.scene, 'backdrop')), 1)
        self.assertTrue(close_vector(env.target(self.scene).location, (0, 0, 1)))
        for slot, definition in qle.LIGHT_SETTINGS.items():
            light = self.by_slot(slot)
            self.assertTrue(close_vector(light.location, definition['loc']))
            self.assertTrue(close_vector(light.data.color, definition['color']))
            self.assertEqual(light.data.energy, definition['energy'])
            self.assertEqual(light.data.shape, definition['shape'])
            self.assertFalse(light.data.use_temperature)
        self.scene.view_layers[0].update()
        identities = {obj[IDENTITY] for obj in env.objects_for(self.scene)}
        world = self.scene.world
        self.add()
        self.assertEqual(identities, {obj[IDENTITY] for obj in env.objects_for(self.scene)})
        self.assertEqual(self.scene.world, world)
        self.assertEqual(self.scene.qle_settings.original_world, self.original)
        nodes = world.node_tree.nodes
        self.assertAlmostEqual(next(n for n in nodes if n.type == 'BACKGROUND').inputs['Strength'].default_value, 0.25)
        self.assertAlmostEqual(next(n for n in nodes if n.type == 'BLACKBODY').inputs['Temperature'].default_value, 5454)

    def test_add_preserves_edits_names_extras_constraints_and_engine(self):
        self.add()
        light = self.by_slot()
        light.name = 'My Orange Light'
        light.data.energy = 237
        light.location = (7, -2, 6)
        light.hide_render = True
        extra = self.extra_light()
        constraint = light.constraints.new('LIMIT_LOCATION')
        constraint.name = 'User constraint'
        backdrop = env.objects_for(self.scene, 'backdrop')[0]
        backdrop.location.z = 2
        self.add()
        self.assertEqual(light.name, 'My Orange Light')
        self.assertEqual(light.data.energy, 237)
        self.assertTrue(close_vector(light.location, (7, -2, 6)))
        self.assertTrue(light.hide_render)
        self.assertIn(extra, env.lights(self.scene))
        self.assertEqual(light.constraints.get('User constraint'), constraint)
        self.assertEqual(backdrop.location.z, 2)
        self.assertEqual(self.scene.render.engine, TEST_ENGINE)

    def test_add_repairs_only_missing_parts(self):
        self.add()
        other = self.by_slot('Area_Right')
        other.data.energy = 321
        bpy.data.objects.remove(self.by_slot(), do_unlink=True)
        bpy.data.objects.remove(env.target(self.scene), do_unlink=True)
        bpy.data.objects.remove(env.objects_for(self.scene, 'backdrop')[0], do_unlink=True)
        self.add()
        self.assertEqual(len(env.lights(self.scene)), 4)
        self.assertEqual(other.data.energy, 321)
        for light in env.lights(self.scene):
            self.assertEqual(env.aim_constraint(self.scene, light).target, env.target(self.scene))

    def test_unrelated_name_collisions_and_orphans_survive(self):
        collection = bpy.data.collections.new('QLE')
        self.scene.collection.children.link(collection)
        unrelated = bpy.data.objects.new('Area_Left', None)
        collection.objects.link(unrelated)
        backdrop = bpy.data.objects.new('Backdrop', bpy.data.meshes.new('User mesh'))
        self.scene.collection.objects.link(backdrop)
        user_world = bpy.data.worlds.new('QLE World')
        orphan = bpy.data.materials.new('Unrelated orphan material')
        self.add()
        self.assertFalse(env.owned(unrelated, self.scene))
        self.assertNotEqual(self.by_slot().name, 'Area_Left')
        self.assertNotEqual(self.scene.world, user_world)
        env.clear_environment(self.scene)
        self.assertIsNotNone(bpy.data.objects.get(unrelated.name))
        self.assertIsNotNone(bpy.data.objects.get(backdrop.name))
        self.assertIsNotNone(bpy.data.collections.get('QLE'))
        self.assertIsNotNone(bpy.data.materials.get(orphan.name))
        self.assertIsNotNone(bpy.data.worlds.get(user_world.name))
        self.assertEqual(self.scene.world, self.original)

    def test_clear_preserves_unowned_inside_managed_collection(self):
        self.add()
        collection = env.collection_for(self.scene, 'environment')
        unrelated = bpy.data.objects.new('User inside QLE', None)
        collection.objects.link(unrelated)
        env.clear_environment(self.scene)
        self.assertEqual(list(collection.objects), [unrelated])
        self.assertEqual(len(env.lights(self.scene)), 0)

    def test_reset_defaults_and_original_world_reference(self):
        self.add()
        extra = self.extra_light()
        extra_id = extra[IDENTITY]
        self.by_slot().data.energy = 999
        self.by_slot().location = (10, 20, 30)
        env.target(self.scene).location = (2, 3, 4)
        self.scene.qle_settings.backdrop_type = 'NONE'
        self.scene.world.node_tree.nodes.clear()
        env.reset_environment(self.scene)
        self.assertEqual(len(env.lights(self.scene)), 4)
        self.assertFalse(any(obj[IDENTITY] == extra_id for obj in env.lights(self.scene)))
        self.assertEqual(self.by_slot().data.energy, 100)
        self.assertTrue(close_vector(self.by_slot().location, (-5, -5, 5)))
        self.assertTrue(close_vector(env.target(self.scene).location, (0, 0, 1)))
        self.assertEqual(self.scene.qle_settings.backdrop_type, 'C_BACKDROP')
        self.assertEqual(self.scene.qle_settings.original_world, self.original)
        env.clear_environment(self.scene)
        self.assertEqual(self.scene.world, self.original)

    def test_protected_original_survives_clear_add_reset_without_duplicate(self):
        self.add()
        light = self.by_slot()
        light.name = 'My protected orange'
        light.data.energy = 333
        light.location = (2, -3, 4)
        self.scene.view_layers[0].update()
        pose = light.matrix_world.copy()
        env.set_protected(self.scene, light, True)
        private = env.aim_constraint(self.scene, light).target
        self.assertEqual(private.get(ROLE), 'private_target')
        original_data = light.data
        env.clear_environment(self.scene)
        self.scene.view_layers[0].update()
        self.assertEqual(env.lights(self.scene), [light])
        self.assertEqual(light.data, original_data)
        self.assertTrue(close_vector(light.matrix_world.translation, pose.translation))
        self.assertTrue(all(close_vector(a, b) for a, b in zip(light.matrix_world, pose)))
        self.add()
        self.assertEqual(len(env.lights(self.scene)), 4)
        self.assertEqual(self.by_slot(), light)
        env.target(self.scene).location = (9, 9, 9)
        env.reset_environment(self.scene)
        self.assertEqual(self.by_slot(), light)
        self.assertEqual(light.data.energy, 333)
        self.assertEqual(light.name, 'My protected orange')
        self.assertEqual(env.aim_constraint(self.scene, light).target, private)

    def test_protected_extra_survives_and_unprotect_then_clear_removes_it(self):
        self.add()
        extra = self.extra_light()
        identity = extra[IDENTITY]
        env.set_protected(self.scene, extra, True)
        env.clear_environment(self.scene)
        env.set_protected(self.scene, extra, False)
        self.assertEqual(env.objects_for(self.scene, 'private_target'), [])
        env.clear_environment(self.scene)
        self.assertFalse(any(obj.get(IDENTITY) == identity for obj in self.scene.objects))

    def test_protection_does_not_remove_user_collection_memberships(self):
        self.add()
        light = self.by_slot()
        user_collection = bpy.data.collections.new('User grouping')
        self.scene.collection.children.link(user_collection)
        user_collection.objects.link(light)
        env.set_protected(self.scene, light, True)
        self.assertIn(light.name, user_collection.objects)
        env.set_protected(self.scene, light, False)
        self.assertIn(light.name, user_collection.objects)

    def test_protected_light_detaches_from_deletable_parent_without_moving(self):
        self.add()
        light = self.by_slot()
        light.parent = env.target(self.scene)
        self.scene.view_layers[0].update()
        before = light.matrix_world.copy()
        env.set_protected(self.scene, light, True)
        self.assertIsNone(light.parent)
        env.clear_environment(self.scene)
        self.scene.view_layers[0].update()
        self.assertTrue(all(close_vector(a, b) for a, b in zip(light.matrix_world, before)))

    def test_original_world_none_is_restored_exactly(self):
        self.scene.world = None
        self.add()
        env.reset_environment(self.scene)
        env.clear_environment(self.scene)
        self.assertIsNone(self.scene.world)

    def test_original_world_missing_uses_reported_fallback(self):
        self.add()
        bpy.data.worlds.remove(self.original, do_unlink=True)
        warnings = env.clear_environment(self.scene)
        self.assertTrue(warnings)
        self.assertIsNotNone(self.scene.world)
        self.assertEqual(self.scene.world.name, 'QLE Restored World')

    def test_clear_without_setup_is_noop(self):
        self.assertEqual(env.clear_environment(self.scene), [])
        self.assertEqual(self.scene.world, self.original)
        self.assertEqual(list(self.scene.collection.children), [])

    def test_clear_restores_world_even_after_root_deleted(self):
        self.add()
        bpy.data.collections.remove(env.collection_for(self.scene, 'environment'))
        env.clear_environment(self.scene)
        self.assertEqual(self.scene.world, self.original)

    def test_none_backdrop_stays_none_on_add(self):
        self.add()
        env.remove_objects(self.scene, env.objects_for(self.scene, 'backdrop'))
        self.scene.qle_settings.backdrop_type = 'NONE'
        self.add()
        self.assertEqual(env.objects_for(self.scene, 'backdrop'), [])

    def test_missing_asset_cancels_before_setup_or_reset_changes(self):
        with patch.object(env, 'backdrop_path', return_value=Path('/nonexistent/qle.blend')):
            with self.assertRaises(env.QLEError):
                self.add()
        self.assertEqual(self.scene.qle_settings.environment_id, '')
        self.assertEqual(self.scene.world, self.original)
        self.add()
        light = self.by_slot()
        light.data.energy = 789
        with patch.object(env, 'backdrop_path', return_value=Path('/nonexistent/qle.blend')):
            with self.assertRaises(env.QLEError):
                env.reset_environment(self.scene)
        self.assertEqual(self.by_slot(), light)
        self.assertEqual(light.data.energy, 789)

    def test_wrong_asset_type_cancels_before_setup_or_reset_changes(self):
        with tempfile.TemporaryDirectory(prefix='qle-invalid-asset-') as folder:
            path = Path(folder) / 'invalid.blend'
            invalid = bpy.data.objects.new('Backdrop', None)
            bpy.data.libraries.write(str(path), {invalid})
            bpy.data.objects.remove(invalid)
            with patch.object(env, 'backdrop_path', return_value=path):
                with self.assertRaises(env.QLEError):
                    self.add()
            self.assertEqual(self.scene.qle_settings.environment_id, '')
            self.assertEqual(self.scene.world, self.original)
            self.assertEqual(len(env.lights(self.scene)), 0)
            self.add()
            light = self.by_slot()
            backdrop = env.objects_for(self.scene, 'backdrop')[0]
            with patch.object(env, 'backdrop_path', return_value=path):
                with self.assertRaises(env.QLEError):
                    env.reset_environment(self.scene)
            self.assertEqual(self.by_slot(), light)
            self.assertEqual(env.objects_for(self.scene, 'backdrop'), [backdrop])

    def test_legacy_adoption_preserves_pose_data_and_constraints(self):
        self.legacy()
        light = bpy.data.objects['Area_Left']
        light.data.energy = 444
        light.location = (2, -7, 6)
        user_constraint = light.constraints.new('LIMIT_ROTATION')
        user_constraint.name = 'User rotation limit'
        backdrop = bpy.data.objects['Backdrop']
        backdrop.location.z = 3
        legacy_color = tuple(light.data.color)
        legacy_world = self.scene.world
        warnings = self.add()
        self.assertTrue(warnings)
        self.assertEqual(self.by_slot(), light)
        self.assertEqual(light.data.energy, 444)
        self.assertTrue(close_vector(light.location, (2, -7, 6)))
        self.assertTrue(close_vector(light.data.color, legacy_color))
        self.assertEqual(backdrop.location.z, 3)
        self.assertIsNotNone(light.constraints.get('User rotation limit'))
        self.assertEqual(len([c for c in light.constraints if c.type == 'TRACK_TO']), 1)
        self.assertNotEqual(self.scene.world, legacy_world)
        self.assertEqual(len(self.scene.world.node_tree.nodes), len(legacy_world.node_tree.nodes))
        self.assertTrue(env.clear_environment(self.scene))
        self.assertEqual(self.scene.world.name, 'QLE Restored World')

    def test_legacy_renamed_light_recovers_slot_from_unique_legacy_data(self):
        self.legacy()
        light = bpy.data.objects['Area_Left']
        light.name = 'Renamed before QLE 2'
        self.add()
        self.assertTrue(env.owned(light, self.scene, 'light'))
        self.assertEqual(light.get(SLOT), 'Area_Left')
        self.assertEqual(len(env.lights(self.scene)), 4)

    def test_legacy_unidentifiable_renamed_light_is_kept_without_guessing_slot(self):
        self.legacy()
        light = bpy.data.objects['Area_Left']
        light.name = 'Renamed object'
        light.data.name = 'Renamed light data'
        self.add()
        self.assertTrue(env.owned(light, self.scene, 'light'))
        self.assertEqual(light.get(SLOT), '')
        self.assertEqual(len(env.lights(self.scene)), 5)

    def test_collection_name_and_light_names_alone_do_not_confer_ownership(self):
        collection = bpy.data.collections.new('QLE')
        self.scene.collection.children.link(collection)
        user_lights = []
        for name in ('Area_Left', 'Area_Right'):
            light = bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA'))
            collection.objects.link(light)
            user_lights.append(light)
        self.add()
        self.assertNotIn(OWNER, collection)
        self.assertTrue(all(not env.owned(obj, self.scene) for obj in user_lights))

    def test_legacy_with_deleted_target_is_repaired_without_resetting_lights(self):
        self.legacy()
        light = bpy.data.objects['Area_Left']
        light.data.energy = 444
        bpy.data.objects.remove(bpy.data.objects['Lights_Target'], do_unlink=True)
        self.add()
        self.assertEqual(self.by_slot(), light)
        self.assertEqual(light.data.energy, 444)
        self.assertEqual(len(env.lights(self.scene)), 4)
        self.assertEqual(env.aim_constraint(self.scene, light).target, env.target(self.scene))

    def test_two_independent_scenes_restore_their_own_worlds(self):
        self.add()
        second = bpy.data.scenes.new('Second Scene')
        second_world = bpy.data.worlds.new('Second Original')
        second.world = second_world
        env.add_environment(second)
        self.assertNotEqual(self.scene.qle_settings.environment_id, second.qle_settings.environment_id)
        first_managed = self.scene.world
        env.clear_environment(second)
        self.assertEqual(second.world, second_world)
        self.assertEqual(self.scene.world, first_managed)
        env.clear_environment(self.scene)
        self.assertEqual(self.scene.world, self.original)

    def test_shared_legacy_collection_is_rejected_without_mutation(self):
        self.legacy()
        collection = bpy.data.collections['QLE']
        second = bpy.data.scenes.new('Shared Scene')
        second.collection.children.link(collection)
        with self.assertRaises(env.QLEError):
            self.add()
        self.assertNotIn(OWNER, collection)
        self.assertEqual(self.scene.qle_settings.environment_id, '')

    def test_shared_managed_object_is_rejected(self):
        self.add()
        light = self.by_slot()
        second = bpy.data.scenes.new('Other Scene')
        second.collection.objects.link(light)
        with self.assertRaises(env.QLEError):
            env.reset_environment(self.scene)
        self.assertEqual(len(env.lights(self.scene)), 4)

    def test_save_reopen_preserves_ownership_original_world_and_protection(self):
        self.add()
        light = self.by_slot()
        identity = light[IDENTITY]
        original_name = self.original.name
        env.set_protected(self.scene, light, True)
        with tempfile.TemporaryDirectory(prefix='qle-foundation-') as folder:
            path = str(Path(folder) / 'foundation.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
            scene = bpy.context.scene
            restored = next(obj for obj in env.lights(scene) if obj[IDENTITY] == identity)
            self.assertTrue(restored.get(PROTECTED))
            self.assertEqual(scene.qle_settings.original_world.name, original_name)
            self.assertEqual(env.aim_constraint(scene, restored).target.get(ROLE), 'private_target')
            env.clear_environment(scene)
            self.assertEqual(scene.world.name, original_name)
            self.assertEqual(env.lights(scene), [restored])

    def test_unregister_reregister_retains_saved_scene_state(self):
        self.add()
        identity = self.scene.qle_settings.environment_id
        qle.unregister()
        self.assertFalse(hasattr(bpy.types.Scene, 'qle_settings'))
        qle.register()
        self.assertEqual(self.scene.qle_settings.environment_id, identity)
        env.clear_environment(self.scene)
        self.assertEqual(self.scene.world, self.original)


if __name__ == '__main__':
    print(f'QLE_FOUNDATION_BLENDER_VERSION={bpy.app.version_string}', flush=True)
    qle.register()
    engines = []
    for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
        try:
            bpy.context.scene.render.engine = engine
        except TypeError:
            continue
        engines.append(engine)
    assert len(engines) == 2, f'Expected EEVEE and Cycles; found {engines}'
    count = 0
    successful = True
    for TEST_ENGINE in engines:
        print(f'QLE_FOUNDATION_ENGINE={TEST_ENGINE}', flush=True)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(FoundationTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        count += result.testsRun
        successful = successful and result.wasSuccessful()
    qle.unregister()
    if not successful:
        raise SystemExit(1)
    print(f'QLE_FOUNDATION_TESTS_OK count={count}', flush=True)
