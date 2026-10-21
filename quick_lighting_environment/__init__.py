# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

from . import environment, operators, panels, position, properties, stage_colors
from .defaults import LIGHT_SETTINGS
from .state import IDENTITY, QLESettings

bl_info = {
    "name": "QLE (Quick Lighting Environment)",
    "description": "Add Area Lights & Sets World Surface",
    "author": "Don Schnitzius",
    "version": (2, 0, 11),
    "blender": (4, 5, 0),
    "location": "3D Viewport > Sidebar > Quick Tools",
    "doc_url": "https://github.com/don1138/blender-qle",
    "support": "COMMUNITY",
    "category": "Lighting",
}


def setup_qle_environment():
    return environment.add_environment(bpy.context.scene)


def clear_qle_environment():
    return environment.clear_environment(bpy.context.scene)


class QLEOperator:
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def run_action(self, context, action):
        try:
            warnings = action(context.scene)
        except environment.QLEError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        for warning in warnings:
            self.report({'WARNING'}, warning)
        return {'FINISHED'}


class AddLights(QLEOperator, bpy.types.Operator):
    """Create QLE or restore missing default parts without resetting adjustments"""
    bl_idname = "qle.add_lights"
    bl_label = "Add Environment"

    def execute(self, context):
        return self.run_action(context, environment.add_environment)


class ClearLights(QLEOperator, bpy.types.Operator):
    """Remove unprotected QLE content and restore the previous World"""
    bl_idname = "qle.clear_lights"
    bl_label = "Clear Environment"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(
            self, event, title="Clear Environment?",
            message="Delete unprotected QLE content and restore the previous World. Protected lights remain.",
            confirm_text="Clear",
        )

    def execute(self, context):
        return self.run_action(context, environment.clear_environment)


class ResetEnvironment(QLEOperator, bpy.types.Operator):
    """Restore QLE defaults, removing added unprotected lights and adjustments"""
    bl_idname = "qle.reset_environment"
    bl_label = "Reset Environment"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(
            self, event, title="Reset Environment?",
            message="Restore default lights, target, stage, and World. Added unprotected lights and adjustments are lost. Protected lights remain.",
            confirm_text="Reset",
        )

    def execute(self, context):
        return self.run_action(context, environment.reset_environment)


class ProtectLight(QLEOperator, bpy.types.Operator):
    """Keep this QLE light when the environment is cleared or reset"""
    bl_idname = "qle.protect_light"
    bl_label = "Protect Light"

    light_id: bpy.props.StringProperty()
    protect: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        light = next((obj for obj in environment.lights(context.scene)
                      if obj.get(IDENTITY) == self.light_id), None)
        if light is None:
            self.report({'WARNING'}, "The QLE light is no longer available")
            return {'CANCELLED'}
        try:
            environment.set_protected(context.scene, light, self.protect)
        except environment.QLEError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


_classes = [QLESettings, AddLights, ClearLights, ResetEnvironment, ProtectLight,
            *operators.CLASSES, *panels.CLASSES]


def register():
    registered = []
    try:
        for cls in _classes:
            bpy.utils.register_class(cls)
            registered.append(cls)
        bpy.types.Scene.qle_settings = bpy.props.PointerProperty(type=QLESettings)
        properties.register()
        position.register()
        stage_colors.load()
    except Exception:
        # Registration is the only transaction boundary that catches every
        # exception: unwind partial registration, then preserve the traceback.
        stage_colors.unload()
        position.unregister()
        properties.unregister()
        if hasattr(bpy.types.Scene, 'qle_settings'):
            del bpy.types.Scene.qle_settings
        for cls in reversed(registered):
            bpy.utils.unregister_class(cls)
        raise


def unregister():
    stage_colors.unload()
    position.unregister()
    properties.unregister()
    if hasattr(bpy.types.Scene, 'qle_settings'):
        del bpy.types.Scene.qle_settings
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
