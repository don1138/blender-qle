# SPDX-License-Identifier: GPL-3.0-or-later
"""Small undoable actions behind the N-panel."""
import bpy
from . import backdrops, colors, environment as env, light_controls, temperatures
from .state import IDENTITY

BACKDROP_ITEMS = [
    ('C_BACKDROP', 'C Backdrop', 'Original QLE backdrop'),
    ('L_BACKDROP', 'L Backdrop', 'Floor sweeping into a back wall'),
    ('FLAT_BACKGROUND', 'Flat Background', 'Upright background without a floor'),
    ('FLOOR', 'Floor', 'Ground surface without a back wall'),
    ('NONE', 'None', 'Remove backdrop geometry'),
]


def find_light(scene, identity):
    light = next((obj for obj in env.lights(scene) if obj.get(IDENTITY) == identity), None)
    if light is None:
        raise env.QLEError('The QLE light is no longer available')
    return light


class Action:
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            self.action(context)
        except env.QLEError as error:
            self.report({'WARNING'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class AddLight(Action, bpy.types.Operator):
    """Add a white 100 W Area light aimed at the shared target"""
    bl_idname = 'qle.add_light'
    bl_label = 'Add Light'

    @classmethod
    def poll(cls, context):
        return context.scene is not None and env.environment_exists(context.scene)

    def action(self, context):
        light_controls.add(context.scene)


class ResetLight(Action, bpy.types.Operator):
    """Restore this light's default settings and position; keep its name and protection"""
    bl_idname = 'qle.reset_light'
    bl_label = 'Reset Light'
    light_id: bpy.props.StringProperty()

    def action(self, context):
        light_controls.reset(context.scene, find_light(context.scene, self.light_id))


class DeleteLight(Action, bpy.types.Operator):
    """Delete only this light and its private helpers"""
    bl_idname = 'qle.delete_light'
    bl_label = 'Delete Light'
    light_id: bpy.props.StringProperty()

    def action(self, context):
        light_controls.delete(context.scene, find_light(context.scene, self.light_id))


class EnableLight(Action, bpy.types.Operator):
    """Enable or disable this light in both viewport and render"""
    bl_idname = 'qle.enable_light'
    bl_label = 'Enable Light'
    light_id: bpy.props.StringProperty()
    enabled: bpy.props.BoolProperty()

    def action(self, context):
        light_controls.set_enabled(context.scene, find_light(context.scene, self.light_id), self.enabled)


class SelectItem(Action, bpy.types.Operator):
    """Select the actual QLE object for normal Blender editing"""
    bl_idname = 'qle.select_item'
    bl_label = 'Select'
    object_id: bpy.props.StringProperty()

    def action(self, context):
        obj = next((obj for obj in env.objects_for(context.scene) if obj.get(IDENTITY) == self.object_id), None)
        if obj is None or obj.name not in context.view_layer.objects or obj.hide_viewport:
            raise env.QLEError('This object is not available in the current View Layer')
        for selected in context.selected_objects:
            selected.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj


class SetBackdrop(Action, bpy.types.Operator):
    """Replace backdrop geometry while preserving its surface and enabled state"""
    bl_idname = 'qle.set_backdrop'
    bl_label = 'Backdrop Type'
    kind: bpy.props.EnumProperty(items=BACKDROP_ITEMS)

    def action(self, context):
        backdrops.apply(context.scene, self.kind)


class EnableBackdrop(Action, bpy.types.Operator):
    """Enable or disable the backdrop in both viewport and render"""
    bl_idname = 'qle.enable_backdrop'
    bl_label = 'Enable Backdrop'
    enabled: bpy.props.BoolProperty()

    def action(self, context):
        env.check_scene_isolation(context.scene, env.objects_for(context.scene))
        for obj in backdrops.objects(context.scene):
            obj.hide_viewport = not self.enabled
            obj.hide_render = not self.enabled
        context.scene.qle_settings.backdrop_last_enabled = self.enabled


class SetFinish(Action, bpy.types.Operator):
    """Apply a reflective, satin, or matte surface finish"""
    bl_idname = 'qle.set_finish'
    bl_label = 'Surface Finish'
    finish: bpy.props.EnumProperty(items=[(name, name.title(), '') for name in backdrops.FINISHES])

    def action(self, context):
        backdrops.set_roughness(context.scene, backdrops.FINISHES[self.finish])


class SetTemperature(Action, bpy.types.Operator):
    """Use a Kelvin preset without adding RGB tint"""
    bl_idname = 'qle.set_temperature'
    bl_label = 'Temperature'
    light_id: bpy.props.StringProperty()
    preset: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        preset = temperatures.PRESETS.get(properties.preset)
        return preset[2] if preset is not None else 'Use a Kelvin preset without adding RGB tint'

    def action(self, context):
        if self.preset not in temperatures.PRESETS:
            raise env.QLEError('Unknown temperature preset')
        scene = context.scene
        data = find_light(scene, self.light_id).data if self.light_id else scene.qle_settings.managed_world
        if data is None:
            raise env.QLEError('Add QLE to restore the World controls')
        colors.set_mode(data, 1)
        colors.set_kelvin(data, temperatures.PRESETS[self.preset][0])
        data['qle_temperature_preset'] = self.preset


CLASSES = [AddLight, ResetLight, DeleteLight, EnableLight, SelectItem, SetBackdrop,
           EnableBackdrop, SetFinish, SetTemperature]
