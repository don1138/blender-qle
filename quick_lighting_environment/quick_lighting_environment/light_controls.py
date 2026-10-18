# SPDX-License-Identifier: GPL-3.0-or-later
"""Add, reset, delete, and enable Area lights without adopting unrelated objects."""
from math import sqrt
import bpy
from mathutils import Vector

from . import colors, environment as env, position
from .defaults import LIGHT_SETTINGS, kelvin_for
from .state import PROTECTED, SLOT


def require_light(scene, light):
    if not env.owned(light, scene, 'light') or light.type != 'LIGHT':
        raise env.QLEError('Choose a QLE light')
    env.check_scene_isolation(scene, env.objects_for(scene))


def added_defaults(center):
    step = 3 / sqrt(2)
    return {'loc': tuple(center + Vector((0, -step, step))),
            'shape': 'RECTANGLE', 'energy': 100, 'size_x': 1, 'size_y': 1,
            'color': (1, 1, 1), 'temperature': None}


def add(scene):
    if not env.environment_exists(scene):
        raise env.QLEError('Add QLE before adding a light')
    env.check_scene_isolation(scene, env.objects_for(scene))
    target = env.target(scene)
    if target is None:
        raise env.QLEError('Click Add to restore the missing target first')
    position.update_scene(scene)
    definition = added_defaults(position.world_position(target))
    data = bpy.data.lights.new('Area Light', 'AREA')
    light = bpy.data.objects.new('Area Light', data)
    env.collection_for(scene, 'environment').objects.link(light)
    env.mark(light, scene, 'light')
    light[SLOT] = ''
    light[PROTECTED] = False
    env.configure_light(scene, light, definition)
    env.ensure_aim(scene, light, target, reset=True)
    position.initialize_light(scene, light)
    return light


def reset(scene, light):
    require_light(scene, light)
    target = position.light_target(scene, light)
    if target is None:
        raise env.QLEError('Click Add to restore the missing lighting target first')
    definition = LIGHT_SETTINGS.get(light.get(SLOT)) or added_defaults(position.world_position(target))
    position.set_follow(scene, light, False)
    env.configure_light(scene, light, definition)
    position.update_scene(scene)
    position.set_world_position(light, definition['loc'])
    colors.reset_light(light.data, definition['color'], kelvin_for(light.get(SLOT)))
    light.hide_viewport = False
    light.hide_render = False
    env.ensure_aim(scene, light, target, reset=True)
    light['_qle_aim_mode'] = 'TARGET'
    position.set_follow(scene, light, True)


def delete(scene, light):
    require_light(scene, light)
    private = env.private_target(scene, light)
    reference = position.reference_for(scene, light)
    env.remove_objects(scene, [light])
    if reference is not None:
        env.remove_objects(scene, [reference])
    if private is not None:
        env.remove_objects(scene, [private])
    env.remove_empty_collections(scene)


def set_enabled(scene, light, enabled):
    require_light(scene, light)
    light.hide_viewport = not enabled
    light.hide_render = not enabled
