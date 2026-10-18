# SPDX-License-Identifier: GPL-3.0-or-later
"""Native-object positioning with live spherical controls and translation follow."""
from math import asin, atan2, cos, hypot, pi, sin

import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

from . import environment as env
from .state import DEPENDENCY, IDENTITY, OWNER, PROTECTED, ROLE

FOLLOW = 'qle_position_constraint'
TARGET_FOLLOW = 'qle_target_constraint'
_guard = False


def scene_for(obj):
    return next((scene for scene in obj.users_scene
                 if scene.qle_settings.environment_id == obj.get(OWNER)), None)


def update_scene(scene):
    scene.view_layers[0].update()


def follow_constraint(obj, key=FOLLOW):
    constraint = obj.constraints.get(obj.get(key, ''))
    return constraint if constraint is not None and constraint.type == 'COPY_LOCATION' else None


def world_position(obj):
    return obj.matrix_world.translation.copy()


def set_world_position(obj, value, key=FOLLOW):
    """Assign a world-space point, accounting for our world-space offset constraint."""
    matrix = obj.matrix_world.copy()
    destination = Vector(value)
    constraint = follow_constraint(obj, key)
    if constraint is not None and constraint.target is not None and not constraint.mute:
        destination -= world_position(constraint.target)
    matrix.translation = destination
    obj.matrix_world = matrix


def light_target(scene, light):
    constraint = env.aim_constraint(scene, light)
    if constraint is not None and constraint.target is not None:
        return constraint.target
    if light.get(PROTECTED):
        return env.private_target(scene, light)
    return env.target(scene)


def add_follow_constraint(obj, target, key):
    constraint = obj.constraints.new('COPY_LOCATION')
    constraint.name = f'QLE Follow {obj[IDENTITY]}'
    obj[key] = constraint.name
    constraint.target = target
    constraint.use_offset = True
    constraint.owner_space = 'WORLD'
    constraint.target_space = 'WORLD'
    # Follow position before our Track To computes direction.
    index = list(obj.constraints).index(constraint)
    obj.constraints.move(index, 0)
    return constraint


def set_follow(scene, light, enabled):
    update_scene(scene)
    position = world_position(light)
    constraint = follow_constraint(light)
    if constraint is not None:
        light.constraints.remove(constraint)
    reference = reference_for(scene, light)
    if reference is not None:
        env.remove_objects(scene, [reference])
    if enabled:
        center = light_target(scene, light)
        if center is not None:
            reference = bpy.data.objects.new(f'{light.name} Follow', None)
            role = 'protected_collection' if light.get(PROTECTED) else 'environment'
            env.ensure_collection(scene, role).objects.link(reference)
            env.mark(reference, scene, 'position_reference')
            reference[DEPENDENCY] = light[IDENTITY]
            reference.empty_display_size = 0.01
            reference.hide_render = True
            add_follow_constraint(reference, center, TARGET_FOLLOW)
            reference.location = -world_position(center)
            update_scene(scene)
            for layer in scene.view_layers:
                if reference.name in layer.objects:
                    reference.hide_set(True, view_layer=layer)
            add_follow_constraint(light, reference, FOLLOW)
    light['_qle_follow_target'] = enabled
    set_world_position(light, position)
    update_scene(scene)
    light['_qle_last_position'] = tuple(position)


def reference_for(scene, light):
    return next((obj for obj in env.objects_for(scene, 'position_reference')
                 if obj.get(DEPENDENCY) == light.get(IDENTITY)), None)


def initialize_light(scene, light):
    if light.get(PROTECTED) and light_target(scene, light) is None:
        center = bpy.data.objects.new(f'{light.name} Target', None)
        env.ensure_collection(scene, 'protected_collection').objects.link(center)
        env.mark(center, scene, 'private_target')
        center[DEPENDENCY] = light[IDENTITY]
        shared = env.target(scene)
        default = tuple(world_position(shared)) if shared is not None else (0, 0, 1)
        center.location = light.get('_qle_last_center', default)
        constraint = env.ensure_aim(scene, light, center)
        constraint.target = center
        constraint.mute = light.get('_qle_aim_mode', 'TARGET') == 'MANUAL'
    if not light.get('_qle_position_initialized'):
        if env.owned(light.parent, scene):
            update_scene(scene)
            matrix = light.matrix_world.copy()
            light.parent = None
            light.matrix_world = matrix
        set_follow(scene, light, True)
        if not light.data.use_temperature:
            light.data.temperature = 5454.0
        light['_qle_position_initialized'] = True
    elif light.get('_qle_follow_target', True):
        constraint = follow_constraint(light)
        center = light_target(scene, light)
        reference = reference_for(scene, light)
        reference_constraint = follow_constraint(reference, TARGET_FOLLOW) if reference is not None else None
        if center is not None and (constraint is None or reference_constraint is None or reference_constraint.target != center):
            set_follow(scene, light, True)


def rebind(scene, light):
    if light.get('_qle_position_initialized'):
        set_follow(scene, light, light.get('_qle_follow_target', True))


def orbit(light):
    scene = scene_for(light)
    center = light_target(scene, light) if scene is not None else None
    if center is None:
        return (0.0, 0.0, 0.0)
    offset = world_position(light) - world_position(center)
    distance = offset.length
    horizontal = hypot(offset.x, offset.y)
    around = atan2(offset.x, -offset.y) if horizontal > 1e-8 else light.get('_qle_last_around', 0.0)
    elevation = asin(max(-1.0, min(1.0, offset.z / distance))) if distance > 1e-8 else 0.0
    return around, elevation, distance


def set_orbit(light, component, value):
    scene = scene_for(light)
    if scene is None:
        return
    update_scene(scene)
    center = light_target(scene, light)
    if center is None:
        raise env.QLEError('Add QLE to restore this light\'s missing target')
    values = list(orbit(light))
    values[component] = value
    around, elevation, distance = values
    distance = max(0.0001, distance)
    elevation = max(-pi / 2, min(pi / 2, elevation))
    offset = Vector((sin(around) * cos(elevation), -cos(around) * cos(elevation), sin(elevation))) * distance
    set_world_position(light, world_position(center) + offset)
    light['_qle_last_around'] = around
    update_scene(scene)


def set_aim(scene, light, mode):
    update_scene(scene)
    matrix = light.matrix_world.copy()
    center = light_target(scene, light)
    if center is None:
        raise env.QLEError('Add QLE to restore the missing target before changing Aim')
    constraint = env.ensure_aim(scene, light, center)
    constraint.mute = mode == 'MANUAL'
    if mode == 'MANUAL':
        # Keep the current evaluated direction rather than jumping back to
        # an old unconstrained rotation when tracking is disabled.
        light.rotation_mode = 'XYZ'
        light.matrix_world = matrix
        set_world_position(light, matrix.translation)
    light['_qle_aim_mode'] = mode
    update_scene(scene)


def target_object_allowed(obj, candidate):
    scene = scene_for(obj)
    return bool(scene is not None and candidate is not obj and not candidate.get(OWNER)
                and candidate.name in scene.objects)


def apply_target_follow(obj, snap=False):
    scene = scene_for(obj)
    if scene is None:
        return
    update_scene(scene)
    position = world_position(obj)
    constraint = follow_constraint(obj, TARGET_FOLLOW)
    if constraint is not None:
        obj.constraints.remove(constraint)
    source = obj.qle_follow_object
    if obj.get('_qle_target_follow', 'FREE') == 'OBJECT' and source is not None:
        if not target_object_allowed(obj, source):
            raise env.QLEError('Choose an ordinary object from this scene, outside QLE')
        add_follow_constraint(obj, source, TARGET_FOLLOW)
        obj['_qle_follow_had_object'] = True
        if snap:
            position = world_position(source)
    set_world_position(obj, position, TARGET_FOLLOW)
    obj['_qle_last_target_position'] = tuple(position)
    update_scene(scene)


def set_target_mode(obj, value):
    if value == 1 and obj.qle_follow_object is None:
        obj['_qle_follow_had_object'] = False
    obj['_qle_target_follow'] = ('FREE', 'OBJECT')[value]
    apply_target_follow(obj, snap=value == 1)


def update_target_object(obj, _context):
    if obj.get('_qle_target_follow', 'FREE') == 'OBJECT':
        if obj.qle_follow_object is None:
            if obj.get('_qle_follow_had_object', False):
                freeze_target(obj)
        else:
            apply_target_follow(obj, snap=True)


def freeze_target(obj):
    position = obj.get('_qle_last_target_position', tuple(world_position(obj)))
    constraint = follow_constraint(obj, TARGET_FOLLOW)
    if constraint is not None:
        obj.constraints.remove(constraint)
    obj['_qle_target_follow'] = 'FREE'
    obj['_qle_follow_had_object'] = False
    set_world_position(obj, position, TARGET_FOLLOW)


@persistent
def synchronize(scene, _depsgraph=None):
    """Cache evaluated positions for deletion fallback; native constraints do motion."""
    global _guard
    if _guard or not hasattr(scene, 'qle_settings'):
        return
    _guard = True
    try:
        for obj in env.objects_for(scene):
            role = obj.get(ROLE)
            if role in {'target', 'private_target'}:
                if (obj.get('_qle_target_follow') == 'OBJECT' and obj.qle_follow_object is None
                        and obj.get('_qle_follow_had_object', False)):
                    freeze_target(obj)
                value = tuple(world_position(obj))
                if tuple(obj.get('_qle_last_target_position', ())) != value:
                    obj['_qle_last_target_position'] = value
            elif role == 'light' and obj.get('_qle_position_initialized'):
                constraint = follow_constraint(obj)
                reference = constraint.target if constraint is not None else None
                target_constraint = follow_constraint(reference, TARGET_FOLLOW) if reference is not None else None
                if constraint is not None and (constraint.target is None or (target_constraint is not None and target_constraint.target is None)):
                    position = obj.get('_qle_last_position', tuple(world_position(obj)))
                    obj.constraints.remove(constraint)
                    set_world_position(obj, position)
                value = tuple(world_position(obj))
                if tuple(obj.get('_qle_last_position', ())) != value:
                    obj['_qle_last_position'] = value
                center = light_target(scene, obj)
                if center is not None:
                    value = tuple(world_position(center))
                    if tuple(obj.get('_qle_last_center', ())) != value:
                        obj['_qle_last_center'] = value
    finally:
        _guard = False


def register():
    for handlers in (bpy.app.handlers.depsgraph_update_post, bpy.app.handlers.frame_change_post):
        if synchronize not in handlers:
            handlers.append(synchronize)


def unregister():
    for handlers in (bpy.app.handlers.depsgraph_update_post, bpy.app.handlers.frame_change_post):
        if synchronize in handlers:
            handlers.remove(synchronize)
