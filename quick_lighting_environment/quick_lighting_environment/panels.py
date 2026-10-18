# SPDX-License-Identifier: GPL-3.0-or-later
"""The agreed compact N-panel; drawing is read-only."""
import bpy
from . import backdrops, colors, environment as env, operators, temperatures
from .state import IDENTITY, PROTECTED, SLOT


def select_button(row, context, obj):
    button = row.row(align=True)
    button.enabled = obj is not None and obj.name in context.view_layer.objects and not obj.hide_viewport
    op = button.operator('qle.select_item', text='', icon='RESTRICT_SELECT_OFF')
    op.object_id = obj.get(IDENTITY, '') if obj is not None else ''


def temperature_label(data):
    preset = temperatures.PRESETS.get(data.get('qle_temperature_preset', ''))
    kelvin = colors.get_kelvin(data)
    return f'{preset[1]} — {kelvin:g} K' if preset and abs(preset[0] - kelvin) < 0.5 else f'Custom — {kelvin:g} K'


def color_fields(layout, data, owner):
    layout.prop(data, 'qle_color_mode', expand=True)
    if data.qle_color_mode == 'RGB':
        layout.prop(data, 'qle_rgb')
    else:
        layout.context_pointer_set('qle_color_owner', owner)
        layout.menu('QLE_MT_temperatures', text=temperature_label(data))
        layout.prop(data, 'qle_kelvin')


class TemperatureMenu(bpy.types.Menu):
    bl_idname = 'QLE_MT_temperatures'
    bl_label = 'Temperature'

    def draw(self, context):
        owner = getattr(context, 'qle_color_owner', None)
        if owner is None:
            return
        for group, names in temperatures.GROUPS:
            self.layout.label(text=group)
            for name in names:
                kelvin, label, _description = temperatures.PRESETS[name]
                op = self.layout.operator('qle.set_temperature', text=f'{label} — {kelvin:g} K')
                op.light_id = owner.get(IDENTITY, '') if isinstance(owner, bpy.types.Object) else ''
                op.preset = name
            self.layout.separator()


def light_item(layout, context, light):
    identity = light[IDENTITY]
    header, body = layout.panel(f'QLE_LIGHT_{identity}', default_closed=True)
    header.use_property_split = False
    header.prop(light, 'name', text='')
    select_button(header, context, light)
    protected = light.get(PROTECTED, False)
    op = header.operator('qle.protect_light', text='', icon='LOCKED' if protected else 'UNLOCKED', emboss=False)
    op.light_id = identity
    op.protect = not protected
    enabled = not light.hide_viewport and not light.hide_render
    op = header.operator('qle.enable_light', text='', icon='HIDE_OFF' if enabled else 'HIDE_ON', emboss=False)
    op.light_id = identity
    op.enabled = not enabled
    if body is None:
        return
    body.use_property_split = True
    body.use_property_decorate = False
    body.prop(light.data, 'energy', text='Power')
    color_fields(body, light.data, light)
    header, position = body.panel(f'QLE_POSITION_{identity}', default_closed=True)
    header.label(text='Position')
    if position is not None:
        position.prop(light, 'qle_follow_target')
        position.prop(light, 'qle_around')
        position.prop(light, 'qle_elevation')
        position.prop(light, 'qle_distance')
    header, aim = body.panel(f'QLE_AIM_{identity}', default_closed=True)
    header.label(text='Aim')
    if aim is not None:
        aim.prop(light, 'qle_aim_mode', expand=True)
        if light.qle_aim_mode == 'MANUAL':
            aim.prop(light, 'rotation_euler', text='Rotation')
    header, shape = body.panel(f'QLE_SHAPE_{identity}', default_closed=True)
    header.label(text='Shape')
    if shape is not None:
        if light.data.type == 'AREA':
            shape.prop(light.data, 'shape')
            shape.prop(light.data, 'size', text='Size X' if light.data.shape in {'RECTANGLE', 'ELLIPSE'} else 'Size')
            if light.data.shape in {'RECTANGLE', 'ELLIPSE'}:
                shape.prop(light.data, 'size_y', text='Size Y')
        else:
            shape.label(text='Reset Light to restore its Area type')
    row = body.row(align=True)
    row.operator('qle.reset_light', text='Reset Light', icon='FILE_REFRESH').light_id = identity
    row.operator('qle.delete_light', text='Delete Light', icon='REMOVE').light_id = identity


class LightingPanel(bpy.types.Panel):
    bl_label = 'Quick Lighting Environment'
    bl_idname = 'VIEW3D_PT_quick_lighting_environment'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Quick Tools'

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.use_property_decorate = False
        actions = layout.row(align=True)
        actions.operator('qle.add_lights', text='Add', icon='ADD')
        actions.operator('qle.reset_environment', text='Reset', icon='FILE_REFRESH')
        actions.operator('qle.clear_lights', text='Clear', icon='REMOVE')
        if not env.environment_exists(scene) and not env.lights(scene):
            return
        try:
            env.check_scene_isolation(scene, env.objects_for(scene))
            owner = scene.qle_settings.environment_id
            if owner and any(other is not scene and other.qle_settings.environment_id == owner for other in bpy.data.scenes):
                raise env.QLEError('This QLE setup shares an identity with another scene')
        except env.QLEError as error:
            layout.label(text=str(error), icon='ERROR')
            return
        header, adjustments = layout.panel('QLE_ADJUSTMENTS', default_closed=True)
        header.label(text='Adjustments')
        if adjustments is None:
            return
        adjustments.use_property_split = True
        adjustments.use_property_decorate = False
        header, light_body = adjustments.panel('QLE_LIGHTS', default_closed=False)
        header.label(text='Lights')
        if light_body is not None:
            row = light_body.row()
            row.enabled = env.environment_exists(scene)
            row.operator('qle.add_light', icon='ADD')
            order = {name: index for index, name in enumerate(('Area_Left', 'Area_Right', 'Area_Fill', 'Area_Back'))}
            for light in sorted(env.lights(scene), key=lambda obj: (order.get(obj.get(SLOT), 4), obj.name.casefold())):
                light_item(light_body, context, light)
        target = env.target(scene)
        if target is not None:
            header, target_body = adjustments.panel('QLE_TARGET', default_closed=True)
            header.label(text='Target')
            select_button(header, context, target)
            if target_body is not None:
                target_body.prop(target, 'qle_follow_mode', expand=True)
                if target.qle_follow_mode == 'OBJECT':
                    target_body.prop(target, 'qle_follow_object')
                target_body.prop(target, 'qle_target_position')
        if env.environment_exists(scene):
            self.draw_backdrop(adjustments, context)
            self.draw_world(adjustments, scene)

    def draw_backdrop(self, layout, context):
        scene = context.scene
        settings = scene.qle_settings
        objects = backdrops.objects(scene)
        header, body = layout.panel('QLE_BACKDROP', default_closed=True)
        header.label(text='Backdrop')
        select_button(header, context, objects[0] if objects else None)
        enabled = bool(objects) and all(not obj.hide_viewport and not obj.hide_render for obj in objects)
        row = header.row()
        row.enabled = bool(objects)
        row.operator('qle.enable_backdrop', text='', icon='HIDE_OFF' if enabled else 'HIDE_ON').enabled = not enabled
        if body is None:
            return
        label = next(item[1] for item in operators.BACKDROP_ITEMS if item[0] == settings.backdrop_type)
        row = body.row()
        row.label(text='Type')
        row.operator_menu_enum('qle.set_backdrop', 'kind', text=label)
        controls = body.column()
        controls.enabled = bool(objects)
        controls.prop(settings, 'backdrop_color')
        finish = controls.row(align=True)
        roughness = backdrops.roughness(scene)
        is_principled = backdrops.surface_node(backdrops.material(scene))
        for name, value in backdrops.FINISHES.items():
            active = is_principled is not None and is_principled.type == 'BSDF_PRINCIPLED' and abs(value - roughness) < 0.0001
            finish.operator('qle.set_finish', text=name.title(), depress=active).finish = name
        controls.prop(settings, 'backdrop_roughness')
        header, position = body.panel('QLE_BACKDROP_POSITION', default_closed=True)
        header.enabled = bool(objects)
        header.label(text='Position')
        if position is not None:
            position.enabled = bool(objects)
            position.prop(settings, 'backdrop_position')

    def draw_world(self, layout, scene):
        header, body = layout.panel('QLE_WORLD', default_closed=True)
        header.label(text='World')
        if body is None:
            return
        world = scene.qle_settings.managed_world
        node = colors.background(world)
        if world is None or node is None:
            body.label(text='Click Add to restore World controls', icon='INFO')
            return
        if scene.world != world:
            body.label(text='Click Add to reactivate QLE World', icon='INFO')
        body.prop(node.inputs['Strength'], 'default_value', text='Strength')
        color_fields(body, world, world)


CLASSES = [TemperatureMenu, LightingPanel]
