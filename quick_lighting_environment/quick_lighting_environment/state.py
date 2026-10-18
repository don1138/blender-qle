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


class QLESettings(bpy.types.PropertyGroup):
    environment_id: bpy.props.StringProperty(options={'HIDDEN'})
    original_world: bpy.props.PointerProperty(type=bpy.types.World)
    original_world_captured: bpy.props.BoolProperty(default=False)
    original_world_was_none: bpy.props.BoolProperty(default=False)
    original_world_unknown: bpy.props.BoolProperty(default=False)
    managed_world: bpy.props.PointerProperty(type=bpy.types.World)
    backdrop_type: bpy.props.EnumProperty(
        items=[
            ('C_BACKDROP', 'C Backdrop', ''),
            ('L_BACKDROP', 'L Backdrop', ''),
            ('FLAT_BACKGROUND', 'Flat Background', ''),
            ('FLOOR', 'Floor', ''),
            ('NONE', 'None', ''),
        ],
        default='C_BACKDROP',
    )
