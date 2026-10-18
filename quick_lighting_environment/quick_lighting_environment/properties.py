# SPDX-License-Identifier: GPL-3.0-or-later
"""Live control properties; drawing their values never changes scene data."""
from math import pi
import bpy

from . import colors, environment as env, position

_registered = []


def orbit_getter(component):
    def get(obj):
        return position.orbit(obj)[component]
    return get


def orbit_setter(component):
    def set_value(obj, value):
        position.set_orbit(obj, component, value)
    return set_value


def follow_get(light):
    return light.get('_qle_follow_target', True)


def follow_set(light, enabled):
    scene = position.scene_for(light)
    if scene is not None:
        position.set_follow(scene, light, enabled)


def aim_get(light):
    scene = position.scene_for(light)
    constraint = env.aim_constraint(scene, light) if scene is not None else None
    return int(constraint is not None and constraint.mute)


def aim_set(light, mode):
    scene = position.scene_for(light)
    if scene is not None:
        position.set_aim(scene, light, ('TARGET', 'MANUAL')[mode])


def target_position_set(obj, value):
    scene = position.scene_for(obj)
    if scene is not None:
        position.update_scene(scene)
        position.set_world_position(obj, value, position.TARGET_FOLLOW)
        position.update_scene(scene)


def register_property(owner, name, definition):
    setattr(owner, name, definition)
    _registered.append((owner, name))


def register():
    for section in ('light', 'position', 'aim', 'shape'):
        register_property(bpy.types.Object, f'qle_ui_{section}_open', bpy.props.BoolProperty(
            name=section.title(), default=False))
    register_property(bpy.types.Object, 'qle_follow_target', bpy.props.BoolProperty(
        name='Follow Target', description='Parent this light to its translation target, keeping its world transform',
        get=follow_get, set=follow_set))
    for name, label, component, options in (
        ('qle_around', 'Around Subject', 0, {'subtype': 'ANGLE', 'soft_min': -pi, 'soft_max': pi}),
        ('qle_elevation', 'Elevation', 1, {'subtype': 'ANGLE', 'min': -pi / 2, 'max': pi / 2}),
        ('qle_distance', 'Distance', 2, {'subtype': 'DISTANCE', 'min': 0.0001, 'soft_max': 20}),
    ):
        register_property(bpy.types.Object, name, bpy.props.FloatProperty(
            name=label, get=orbit_getter(component), set=orbit_setter(component), **options))
    register_property(bpy.types.Object, 'qle_aim_mode', bpy.props.EnumProperty(
        name='Aim', items=[('TARGET', 'Target', 'Point at the lighting target'), ('MANUAL', 'Manual', 'Rotate this light freely')],
        get=aim_get, set=aim_set))
    register_property(bpy.types.Object, 'qle_follow_mode', bpy.props.EnumProperty(
        name='Follow', items=[('FREE', 'Free', 'Stay at this position'), ('OBJECT', 'Object', 'Follow an object; choosing it snaps to its origin')],
        get=lambda obj: int(obj.get('_qle_target_follow', 'FREE') == 'OBJECT'), set=position.set_target_mode))
    register_property(bpy.types.Object, 'qle_follow_object', bpy.props.PointerProperty(
        name='Object', type=bpy.types.Object, poll=position.target_object_allowed, update=position.update_target_object))
    register_property(bpy.types.Object, 'qle_target_position', bpy.props.FloatVectorProperty(
        name='Position', subtype='TRANSLATION', get=lambda obj: tuple(position.world_position(obj)), set=target_position_set))
    for owner in (bpy.types.Light, bpy.types.World):
        register_property(owner, 'qle_color_mode', bpy.props.EnumProperty(
            name='Color Mode', items=[('RGB', 'RGB', 'Use the saved RGB color'), ('KELVIN', 'Kelvin', 'Use temperature without RGB tint')],
            get=colors.get_mode, set=colors.set_mode))
        register_property(owner, 'qle_rgb', bpy.props.FloatVectorProperty(
            name='Color', subtype='COLOR', min=0, max=1, get=colors.get_rgb, set=colors.set_rgb))
        register_property(owner, 'qle_kelvin', bpy.props.FloatProperty(
            name='Kelvin', min=800, max=20000, get=colors.get_kelvin, set=colors.set_kelvin))


def unregister():
    for owner, name in reversed(_registered):
        if hasattr(owner, name):
            delattr(owner, name)
    _registered.clear()
