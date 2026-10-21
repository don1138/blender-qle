# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent scene state and internal identities for QLE."""

import bpy

OWNER = "qle_owner"
ROLE = "qle_role"
IDENTITY = "qle_id"
SLOT = "qle_original_slot"
PROTECTED = "qle_protected"
AIM_CONSTRAINT = "qle_aim_constraint"
DEPENDENCY = "qle_dependency_for"


def backdrop_color_get(settings):
    from . import backdrops
    return backdrops.color(settings.id_data)


def backdrop_color_set(settings, value):
    from . import backdrops
    backdrops.set_color(settings.id_data, value)


def backdrop_roughness_get(settings):
    from . import backdrops
    return backdrops.roughness(settings.id_data)


def backdrop_roughness_set(settings, value):
    from . import backdrops
    backdrops.set_roughness(settings.id_data, value)


def backdrop_position_get(settings):
    from . import backdrops
    return backdrops.position(settings.id_data)


def backdrop_position_set(settings, value):
    from . import backdrops
    backdrops.set_position(settings.id_data, value)


class QLESettings(bpy.types.PropertyGroup):
    environment_id: bpy.props.StringProperty(options={'HIDDEN'})
    original_world: bpy.props.PointerProperty(type=bpy.types.World)
    original_world_captured: bpy.props.BoolProperty(default=False)
    original_world_was_none: bpy.props.BoolProperty(default=False)
    original_world_unknown: bpy.props.BoolProperty(default=False)
    managed_world: bpy.props.PointerProperty(type=bpy.types.World)
    backdrop_material: bpy.props.PointerProperty(type=bpy.types.Material)
    backdrop_last_enabled: bpy.props.BoolProperty(default=True)
    backdrop_color: bpy.props.FloatVectorProperty(
        name='Color', subtype='COLOR', size=4, min=0, max=1,
        get=backdrop_color_get, set=backdrop_color_set)
    backdrop_roughness: bpy.props.FloatProperty(
        name='Roughness', min=0, max=1,
        get=backdrop_roughness_get, set=backdrop_roughness_set)
    backdrop_position: bpy.props.FloatVectorProperty(
        name='Position', subtype='TRANSLATION',
        get=backdrop_position_get, set=backdrop_position_set)
    backdrop_type: bpy.props.EnumProperty(
        items=[
            ('C_BACKDROP', 'C Stage', ''),
            ('L_BACKDROP', 'L Stage', ''),
            ('FLAT_BACKGROUND', 'Flat Background', ''),
            ('FLOOR', 'Floor', ''),
            ('NONE', 'None', ''),
        ],
        default='C_BACKDROP',
    )
