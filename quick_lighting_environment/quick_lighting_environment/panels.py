# SPDX-License-Identifier: GPL-3.0-or-later
"""The agreed compact N-panel; drawing is read-only."""
import bpy
from . import backdrops, colors, environment as env, operators, temperatures, stage_colors
from .constants import version_label
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


def field_row(layout, label, height=1.25):
    row = layout.row()
    row.scale_y = height
    row.use_property_split = False
    split = row.split(factor=0.4)
    caption = split.column()
    caption.alignment = 'RIGHT'
    caption.label(text=label)
    return split.row(align=True)


def mode_buttons(layout, data, prop, label):
    buttons = field_row(layout, label)
    for item in data.bl_rna.properties[prop].enum_items:
        buttons.prop_enum(data, prop, item.identifier, text=item.name)


def disclosure(layout, light, section, label):
    name = f'qle_ui_{section}_open'
    opened = getattr(light, name)
    row = layout.row(align=True)
    row.use_property_split = False
    row.prop(light, name, text=label, icon='TRIA_DOWN' if opened else 'TRIA_RIGHT', emboss=False)
    if not opened:
        return None
    body = layout.column()
    body.use_property_split = True
    body.use_property_decorate = False
    return body


def color_fields(layout, data, owner):
    mode_buttons(layout, data, 'qle_color_mode', 'Color Mode')
    if data.qle_color_mode == 'RGB':
        layout.prop(data, 'qle_rgb')
    else:
        row = field_row(layout, 'Temperature')
        row.context_pointer_set('qle_color_owner', owner)
        row.menu('QLE_MT_temperatures', text=temperature_label(data))
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


class StudioColorsMenu(bpy.types.Menu):
    bl_idname = 'QLE_MT_studio_colors'
    bl_label = 'Studio Colors'

    def draw(self, context):
        active = stage_colors.active(context.scene)
        for index, (group, names) in enumerate(stage_colors.GROUPS):
            if index:
                self.layout.separator()
            self.layout.label(text=group)
            for name in names:
                label = stage_colors.PRESETS[name][0]
                if name == active:
                    label += ' ✓'
                op = self.layout.operator('qle.set_stage_color', text=label, icon_value=stage_colors.icon(name))
                op.preset = name


def light_item(layout, context, light):
    identity = light[IDENTITY]
    box = layout.box()
    header = box.row(align=True)
    header.use_property_split = False
    opened = light.qle_ui_light_open
    header.prop(light, 'qle_ui_light_open', text='', icon='TRIA_DOWN' if opened else 'TRIA_RIGHT', emboss=False)
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
    if not opened:
        return
    body = box.column()
    body.use_property_split = True
    body.use_property_decorate = False
    row = body.row(align=True)
    row.scale_y = 1.25
    row.operator('qle.reset_light', text='Reset Light', icon='FILE_REFRESH').light_id = identity
    row.operator('qle.delete_light', text='Delete Light', icon='REMOVE').light_id = identity
    body.separator()
    body.prop(light.data, 'energy', text='Power')
    color_fields(body, light.data, light)
    body.separator()
    position = disclosure(body, light, 'position', 'Position')
    if position is not None:
        position.prop(light, 'qle_follow_target')
        position.prop(light, 'qle_around')
        position.prop(light, 'qle_elevation')
        position.prop(light, 'qle_distance')
    aim = disclosure(body, light, 'aim', 'Aim')
    if aim is not None:
        mode_buttons(aim, light, 'qle_aim_mode', 'Aim')
        if light.qle_aim_mode == 'MANUAL':
            aim.prop(light, 'rotation_euler', text='Rotation')
    shape = disclosure(body, light, 'shape', 'Shape')
    if shape is not None:
        if light.data.type == 'AREA':
            shape_row = shape.row()
            shape_row.scale_y = 1.25
            shape_row.prop(light.data, 'shape')
            shape.prop(light.data, 'size', text='Size X' if light.data.shape in {'RECTANGLE', 'ELLIPSE'} else 'Size')
            if light.data.shape in {'RECTANGLE', 'ELLIPSE'}:
                shape.prop(light.data, 'size_y', text='Size Y')
        else:
            shape.label(text='Reset Light to restore its Area type')


class LightingPanel(bpy.types.Panel):
    bl_label = f'Quick Lighting Environment — {version_label()}'
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
        actions.scale_y = 1.5
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
        layout.separator()
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
            row.scale_y = 1.25
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
                mode_buttons(target_body, target, 'qle_follow_mode', 'Follow')
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
        header.label(text='Stage')
        select_button(header, context, objects[0] if objects else None)
        enabled = bool(objects) and all(not obj.hide_viewport and not obj.hide_render for obj in objects)
        row = header.row()
        row.enabled = bool(objects)
        row.operator('qle.enable_backdrop', text='', icon='HIDE_OFF' if enabled else 'HIDE_ON').enabled = not enabled
        if body is None:
            return
        label = next(item[1] for item in operators.BACKDROP_ITEMS if item[0] == settings.backdrop_type)
        field_row(body, 'Stage').operator_menu_enum('qle.set_backdrop', 'kind', text=label)
        body.separator()
        header, position = body.panel('QLE_BACKDROP_POSITION', default_closed=True)
        header.enabled = bool(objects)
        header.label(text='Position')
        if position is not None:
            position.enabled = bool(objects)
            position.prop(settings, 'backdrop_position', text='Position')
        header, surface = body.panel('QLE_STAGE_SURFACE', default_closed=False)
        header.label(text='Surface')
        if surface is None:
            return
        controls = surface.column()
        controls.enabled = bool(objects)
        field_row(controls, 'Color').menu('QLE_MT_studio_colors', text=stage_colors.label(scene),
                                       icon_value=stage_colors.icon(stage_colors.active(scene)))
        controls.prop(settings, 'backdrop_color', text='Custom')
        row = controls.row()
        row.scale_y = 1.25
        row.use_property_split = False
        split = row.split(factor=0.4)
        caption = split.column()
        caption.alignment = 'RIGHT'
        caption.label(text='Finish')
        buttons = split.column(align=True)
        roughness = backdrops.roughness(scene)
        node = backdrops.surface_node(backdrops.material(scene))
        for name, value in backdrops.FINISHES.items():
            active = node is not None and node.type == 'BSDF_PRINCIPLED' and abs(value - roughness) < 0.0001
            buttons.operator('qle.set_finish', text=name.title(), depress=active).finish = name
        controls.prop(settings, 'backdrop_roughness', text='Roughness')

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


CLASSES = [TemperatureMenu, StudioColorsMenu, LightingPanel]
