# SPDX-License-Identifier: GPL-3.0-or-later
"""Scene-local QLE ownership, migration, lifecycle, and protected lights.

Only metadata-owned content is removed. Unrecognized objects, even inside a
QLE collection, are left alone. Display names never confer ownership.
"""

from pathlib import Path
from uuid import uuid4

import bpy

from .defaults import LIGHT_SETTINGS, kelvin_for
from .state import (
    AIM_CONSTRAINT, DEPENDENCY, IDENTITY, OWNER, PROTECTED, ROLE, SLOT,
)


class QLEError(RuntimeError):
    """An expected failure that an operator can report to the user."""


def scene_collections(scene):
    seen = set()

    def visit(collection):
        if collection in seen:
            return
        seen.add(collection)
        yield collection
        for child in collection.children:
            yield from visit(child)

    yield from visit(scene.collection)


def owned(block, scene, role=None):
    owner = scene.qle_settings.environment_id
    return bool(
        block is not None and owner and block.get(OWNER) == owner
        and (role is None or block.get(ROLE) == role)
    )


def mark(block, scene, role):
    block[OWNER] = scene.qle_settings.environment_id
    block[ROLE] = role
    if not block.get(IDENTITY):
        block[IDENTITY] = uuid4().hex


def ensure_identity(scene):
    settings = scene.qle_settings
    if not settings.environment_id:
        settings.environment_id = uuid4().hex
    # Full-copy and linked-copy scenes can inherit settings and ownership.
    # Do not silently operate on another scene's environment.
    if any(
        other is not scene
        and other.qle_settings.environment_id == settings.environment_id
        for other in bpy.data.scenes
    ):
        raise QLEError('This scene shares a QLE identity with another scene; separate the setups before editing')


def collection_for(scene, role):
    return next((col for col in scene_collections(scene) if owned(col, scene, role)), None)


def objects_for(scene, role=None):
    return [obj for obj in scene.objects if owned(obj, scene, role)]


def lights(scene):
    return [obj for obj in objects_for(scene, 'light') if obj.type == 'LIGHT']


def target(scene):
    return next(iter(objects_for(scene, 'target')), None)


def environment_exists(scene):
    return collection_for(scene, 'environment') is not None


def ensure_collection(scene, role):
    collection = collection_for(scene, role)
    if collection is None:
        name = 'QLE Protected' if role == 'protected_collection' else 'QLE'
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
        mark(collection, scene, role)
    return collection


def check_scene_isolation(scene, objects):
    for obj in objects:
        if obj.library is not None:
            raise QLEError(f'"{obj.name}" is linked from a library; QLE cannot safely edit it')
        if any(other is not scene for other in obj.users_scene):
            raise QLEError(f'"{obj.name}" is shared with another scene; QLE will not modify it')


def legacy_candidates(scene):
    """Recognize the legacy graph inside QLE, never global object names alone."""
    collection = next((col for col in scene_collections(scene)
                       if col.name == 'QLE' and not col.get(OWNER)), None)
    if collection is None:
        return None
    members = list(collection.objects)
    named_lights = [obj for obj in members
                    if obj.name in LIGHT_SETTINGS and obj.type == 'LIGHT'
                    and obj.data.type == 'AREA' and not obj.get(OWNER)]
    targets = {constraint.target for obj in named_lights for constraint in obj.constraints
               if constraint.type == 'TRACK_TO' and constraint.target in members
               and constraint.target.type == 'EMPTY' and not constraint.target.get(OWNER)}
    legacy_target = next(iter(targets)) if len(targets) == 1 else None
    backdrop = next((obj for obj in members if obj.name == 'Backdrop'
                     and obj.type == 'MESH' and not obj.get(OWNER)), None)
    named_target = next((obj for obj in members if obj.name == 'Lights_Target'
                         and obj.type == 'EMPTY' and not obj.get(OWNER)), None)
    if legacy_target is None:
        # A partial setup with a deleted target is recognizable from several
        # original Area lights, or the original backdrop + named target pair.
        dangling_legacy_tracks = [obj for obj in named_lights if any(
            c.type == 'TRACK_TO' and c.target is None
            and c.track_axis == 'TRACK_NEGATIVE_Z' and c.up_axis == 'UP_Y'
            for c in obj.constraints
        )]
        if len(dangling_legacy_tracks) >= 2:
            legacy_target = named_target
        elif named_target is not None and backdrop is not None:
            legacy_target = named_target
        else:
            return None
    adopted = list(named_lights)
    if legacy_target is not None:
        # Renamed legacy lights can be adopted through the shared target, but
        # their original slot cannot safely be inferred from appearance.
        adopted.extend(obj for obj in members if obj not in adopted
                       and obj.type == 'LIGHT' and not obj.get(OWNER)
                       and any(c.type == 'TRACK_TO' and c.target == legacy_target
                               for c in obj.constraints))
    return collection, adopted, legacy_target, backdrop


def validate_legacy(scene, candidate):
    if candidate is None:
        return
    collection, adopted, legacy_target, backdrop = candidate
    if any(other is not scene and collection in set(scene_collections(other))
           for other in bpy.data.scenes):
        raise QLEError('The legacy QLE collection is shared between scenes; separate it before upgrading')
    check_scene_isolation(scene, adopted + [obj for obj in (legacy_target, backdrop) if obj])


def capture_original_world(scene, unknown=False):
    settings = scene.qle_settings
    if settings.original_world_captured:
        return
    settings.original_world = None if unknown else scene.world
    settings.original_world_was_none = scene.world is None and not unknown
    settings.original_world_unknown = unknown
    settings.original_world_captured = True


def adopt_legacy(scene, candidate):
    if candidate is None:
        return []
    collection, adopted, legacy_target, backdrop = candidate
    mark(collection, scene, 'environment')
    if legacy_target is not None:
        mark(legacy_target, scene, 'target')
    for obj in adopted:
        mark(obj, scene, 'light')
        obj[SLOT] = obj.name if obj.name in LIGHT_SETTINGS else ''
        obj[PROTECTED] = False
        if legacy_target is not None:
            matching = [c for c in obj.constraints
                        if c.type == 'TRACK_TO' and c.target == legacy_target]
            if len(matching) == 1:
                obj[AIM_CONSTRAINT] = matching[0].name
    # A user often renames only the Object, leaving the legacy Light data
    # name intact. Recover that slot only inside an established legacy graph,
    # when it is unique and no named original already occupies the slot.
    assigned = {obj.get(SLOT) for obj in adopted if obj.get(SLOT)}
    for slot in LIGHT_SETTINGS:
        matches = [obj for obj in adopted if not obj.get(SLOT) and obj.data.name == slot]
        if slot not in assigned and len(matches) == 1:
            matches[0][SLOT] = slot
            assigned.add(slot)
    if backdrop is not None:
        mark(backdrop, scene, 'backdrop')
    settings = scene.qle_settings
    previous = scene.world
    unknown = previous is not None and previous.name == 'QLE World'
    capture_original_world(scene, unknown=unknown)
    if previous is not None:
        # Keep the legacy appearance, without claiming a potentially shared
        # World datablock or changing another scene when this one is reset.
        world = previous.copy()
        world.name = 'QLE World'
        mark(world, scene, 'world')
        settings.managed_world = world
        scene.world = world
    if unknown:
        return ['Legacy QLE did not save its previous World; Clear will use a new fallback World']
    return []


def aim_constraint(scene, light):
    name = light.get(AIM_CONSTRAINT, '')
    constraint = light.constraints.get(name) if name else None
    if constraint is not None and constraint.type == 'TRACK_TO':
        return constraint
    return None


def ensure_aim(scene, light, aim_target, reset=False):
    constraint = aim_constraint(scene, light)
    if constraint is None:
        constraint = light.constraints.new('TRACK_TO')
        constraint.name = f'QLE Aim {light[IDENTITY]}'
        light[AIM_CONSTRAINT] = constraint.name
        reset = True
    if constraint.target is None or reset:
        constraint.target = aim_target
    if reset:
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        constraint.mute = False
        constraint.influence = 1.0
    return constraint


def ensure_target(scene, collection):
    obj = target(scene)
    if obj is None:
        obj = bpy.data.objects.new('Lights_Target', None)
        collection.objects.link(obj)
        mark(obj, scene, 'target')
        obj.empty_display_type = 'PLAIN_AXES'
        obj.location = (0, 0, 1)
    return obj


def configure_light(scene, light, definition):
    if light.data.users > 1:
        light.data = light.data.copy()
    data = light.data
    mark(data, scene, 'light_data')
    data.type = 'AREA'
    data.use_nodes = False
    data.shape = definition['shape']
    data.energy = definition['energy']
    data.size = definition['size_x']
    data.size_y = definition['size_y']
    data.color = definition['color']
    data.use_temperature = False
    data.temperature = kelvin_for(light.get(SLOT))
    data['_qle_kelvin'] = data.temperature
    data.exposure = 0.0
    data.normalize = True
    light.location = definition['loc']


def ensure_default_lights(scene, collection, aim_target):
    from . import position
    for slot, definition in LIGHT_SETTINGS.items():
        matching = [obj for obj in lights(scene) if obj.get(SLOT) == slot]
        if matching:
            # Protected originals satisfy their slots, even after renaming.
            for obj in matching:
                if not obj.get(PROTECTED):
                    ensure_aim(scene, obj, aim_target)
                position.initialize_light(scene, obj)
            continue
        data = bpy.data.lights.new(slot, 'AREA')
        light = bpy.data.objects.new(slot, data)
        collection.objects.link(light)
        mark(light, scene, 'light')
        light[SLOT] = slot
        light[PROTECTED] = False
        configure_light(scene, light, definition)
        ensure_aim(scene, light, aim_target, reset=True)
        position.initialize_light(scene, light)


def backdrop_path():
    return Path(__file__).with_name('_backdrop.blend')


def preflight_backdrop():
    path = backdrop_path()
    if not path.is_file():
        raise QLEError('The packaged _backdrop.blend is missing; reinstall QLE')
    try:
        with bpy.data.libraries.load(str(path), link=False) as (source, _destination):
            if 'Backdrop' not in source.objects:
                raise QLEError('The packaged Stage asset is invalid (missing required Backdrop object); reinstall QLE')
    except (OSError, RuntimeError) as error:
        if isinstance(error, QLEError):
            raise
        raise QLEError(f'Cannot read the packaged backdrop: {error}') from error


def prepare_backdrop():
    """Load and validate before changing the working environment."""
    preflight_backdrop()
    with bpy.data.libraries.load(str(backdrop_path()), link=False) as (_source, destination):
        destination.objects = ['Backdrop']
    obj = destination.objects[0]
    if obj is None or obj.type != 'MESH':
        if obj is not None:
            bpy.data.objects.remove(obj)
        raise QLEError('The packaged Stage asset is invalid (Backdrop is not a mesh); reinstall QLE')
    from . import backdrops
    try:
        backdrops.configure_default_material(obj.active_material)
    except Exception:
        discard_backdrop(obj)
        raise
    return obj


def discard_backdrop(obj):
    """Discard only data just appended for an operation that cannot proceed."""
    mesh = obj.data
    materials = set(material for material in mesh.materials if material)
    bpy.data.objects.remove(obj)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
    for material in materials:
        if material.users == 0:
            bpy.data.materials.remove(material)


def attach_backdrop(scene, collection, obj):
    collection.objects.link(obj)
    mark(obj, scene, 'backdrop')
    mark(obj.data, scene, 'backdrop_mesh')
    for material in obj.data.materials:
        if material is not None:
            mark(material, scene, 'backdrop_material')
    return obj


def configure_world(world):
    from . import colors
    colors.reset_world(world)
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    background = nodes.new('ShaderNodeBackground')
    background.location = (-200, 0)
    background.inputs['Strength'].default_value = 0.25
    blackbody = nodes.new('ShaderNodeBlackbody')
    blackbody.name = 'QLE Temperature'
    blackbody.location = (-400, 0)
    blackbody.inputs['Temperature'].default_value = 5454.0
    output = nodes.new('ShaderNodeOutputWorld')
    output.location = (0, 0)
    world.node_tree.links.new(blackbody.outputs['Color'], background.inputs['Color'])
    world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])


def ensure_world(scene, reset=False):
    settings = scene.qle_settings
    world = settings.managed_world
    if not owned(world, scene, 'world'):
        world = bpy.data.worlds.new('QLE World')
        mark(world, scene, 'world')
        configure_world(world)
        settings.managed_world = world
    elif reset:
        if any(other is not scene and other.world == world for other in bpy.data.scenes):
            world = world.copy()
            mark(world, scene, 'world')
            settings.managed_world = world
        configure_world(world)
    scene.world = world


def remove_objects(scene, objects):
    """Remove owned objects and only their unused, owned data; never purge."""
    data_blocks = []
    materials = set()
    for obj in objects:
        if not owned(obj, scene):
            continue
        if obj.data is not None:
            data_blocks.append(obj.data)
            if obj.type == 'MESH':
                materials.update(material for material in obj.data.materials if material)
        bpy.data.objects.remove(obj, do_unlink=True)
    for data in set(data_blocks):
        if data.users == 0 and owned(data, scene):
            if isinstance(data, bpy.types.Light):
                bpy.data.lights.remove(data)
            elif isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
    for material in materials:
        if material.users == 0 and owned(material, scene, 'backdrop_material'):
            bpy.data.materials.remove(material)


def remove_empty_collections(scene):
    for collection in reversed(list(scene_collections(scene))):
        if owned(collection, scene) and not collection.objects and not collection.children:
            bpy.data.collections.remove(collection)


def private_target(scene, light):
    return next((obj for obj in objects_for(scene, 'private_target')
                 if obj.get(DEPENDENCY) == light[IDENTITY]), None)


def protect_target(scene, light):
    constraint = aim_constraint(scene, light)
    if constraint is None or constraint.target is None or not owned(constraint.target, scene, 'target'):
        return
    copy = private_target(scene, light)
    if copy is None:
        copy = constraint.target.copy()
        copy.name = f'{light.name} Target'
        copy[IDENTITY] = uuid4().hex
        mark(copy, scene, 'private_target')
        copy[DEPENDENCY] = light[IDENTITY]
        ensure_collection(scene, 'protected_collection').objects.link(copy)
    constraint.target = copy


def set_protected(scene, light, protect):
    ensure_identity(scene)
    if not owned(light, scene, 'light'):
        raise QLEError('Only a QLE-owned light can be protected')
    check_scene_isolation(scene, objects_for(scene))
    if bool(light.get(PROTECTED)) == protect:
        return
    if protect:
        destination = ensure_collection(scene, 'protected_collection')
        protect_target(scene, light)
        if owned(light.parent, scene):
            # A legacy light may have been parented to the target or backdrop.
            # Do not leave a protected light dependent on deletable content.
            scene.view_layers[0].update()
            pose = light.matrix_world.copy()
            light.parent = None
            light.matrix_world = pose
            from .position import set_world_position
            set_world_position(light, pose.translation)
    else:
        destination = ensure_collection(scene, 'environment')
        aim_target = ensure_target(scene, destination)
        constraint = aim_constraint(scene, light)
        if constraint is not None and owned(constraint.target, scene, 'private_target'):
            constraint.target = aim_target
    # Preserve unrelated collection memberships; only QLE links are moved.
    for collection in list(light.users_collection):
        if owned(collection, scene) and collection != destination:
            collection.objects.unlink(light)
    if light.name not in destination.objects:
        destination.objects.link(light)
    light[PROTECTED] = protect
    from . import position
    position.rebind(scene, light)
    if not protect:
        copy = private_target(scene, light)
        if copy is not None:
            remove_objects(scene, [copy])
    remove_empty_collections(scene)


def prepare(scene):
    candidate = None if environment_exists(scene) else legacy_candidates(scene)
    validate_legacy(scene, candidate)
    ensure_identity(scene)
    check_scene_isolation(scene, objects_for(scene))
    return adopt_legacy(scene, candidate)


def add_environment(scene):
    from . import backdrops
    settings = scene.qle_settings
    needs_backdrop = settings.backdrop_type != 'NONE' and not objects_for(scene, 'backdrop')
    candidate = None if environment_exists(scene) else legacy_candidates(scene)
    if candidate is not None and candidate[3] is not None:
        needs_backdrop = False
    prepared_backdrop = backdrops.prepare(settings.backdrop_type) if needs_backdrop else None
    try:
        warnings = prepare(scene)
    except QLEError:
        if prepared_backdrop is not None:
            discard_backdrop(prepared_backdrop)
        raise
    capture_original_world(scene)
    collection = ensure_collection(scene, 'environment')
    if prepared_backdrop is not None:
        if settings.backdrop_material is not None:
            prepared_backdrop.data.materials.clear()
            prepared_backdrop.data.materials.append(settings.backdrop_material)
        attach_backdrop(scene, collection, prepared_backdrop)
        if settings.backdrop_material is None:
            settings.backdrop_material = prepared_backdrop.active_material
        prepared_backdrop.hide_viewport = not settings.backdrop_last_enabled
        prepared_backdrop.hide_render = not settings.backdrop_last_enabled
    aim_target = ensure_target(scene, collection)
    ensure_default_lights(scene, collection, aim_target)
    ensure_world(scene)
    return warnings


def reset_environment(scene):
    prepared_backdrop = prepare_backdrop()
    try:
        warnings = prepare(scene)
    except QLEError:
        discard_backdrop(prepared_backdrop)
        raise
    capture_original_world(scene)
    collection = ensure_collection(scene, 'environment')
    # Prepare the fresh factory asset before deleting the working backdrop.
    old_backdrops = objects_for(scene, 'backdrop')
    attach_backdrop(scene, collection, prepared_backdrop)
    for light in lights(scene):
        if light.get(PROTECTED):
            protect_target(scene, light)
    protected_ids = {light[IDENTITY] for light in lights(scene) if light.get(PROTECTED)}
    remove_objects(scene, [obj for obj in objects_for(scene)
                           if (obj.get(ROLE) == 'light' and not obj.get(PROTECTED))
                           or (obj.get(ROLE) == 'position_reference' and obj.get(DEPENDENCY) not in protected_ids)])
    remove_objects(scene, objects_for(scene, 'target') + old_backdrops)
    aim_target = ensure_target(scene, collection)
    ensure_default_lights(scene, collection, aim_target)
    settings = scene.qle_settings
    previous_material = settings.backdrop_material
    settings.backdrop_material = prepared_backdrop.active_material
    if previous_material is not None and previous_material.users == 0 and owned(previous_material, scene, 'backdrop_material'):
        bpy.data.materials.remove(previous_material)
    settings.backdrop_last_enabled = True
    settings.backdrop_type = 'C_BACKDROP'
    ensure_world(scene, reset=True)
    return warnings


def clear_environment(scene):
    from . import backdrops
    # Clearing an untouched scene must not create an environment or World.
    if (not environment_exists(scene) and legacy_candidates(scene) is None
            and not scene.qle_settings.original_world_captured):
        return []
    warnings = prepare(scene)
    settings = scene.qle_settings
    for light in lights(scene):
        if light.get(PROTECTED):
            protect_target(scene, light)
    protected_ids = {light[IDENTITY] for light in lights(scene) if light.get(PROTECTED)}
    victims = [obj for obj in objects_for(scene)
               if not (obj.get(ROLE) == 'light' and obj.get(PROTECTED))
               and not (obj.get(ROLE) in {'private_target', 'position_reference'} and obj.get(DEPENDENCY) in protected_ids)]
    remove_objects(scene, victims)
    backdrops.cleanup(scene)
    settings.backdrop_type = 'C_BACKDROP'
    settings.backdrop_last_enabled = True
    remove_empty_collections(scene)
    managed = settings.managed_world
    if settings.original_world_captured:
        if settings.original_world is not None or settings.original_world_was_none:
            scene.world = settings.original_world
        else:
            fallback = bpy.data.worlds.new('QLE Restored World')
            fallback.use_nodes = True
            scene.world = fallback
            warnings.append('The previous World is unavailable; restored a new fallback World')
    settings.managed_world = None
    settings.original_world = None
    settings.original_world_captured = False
    settings.original_world_was_none = False
    settings.original_world_unknown = False
    if managed is not None and owned(managed, scene, 'world') and managed.users == 0:
        bpy.data.worlds.remove(managed)
    return warnings
