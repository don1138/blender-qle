# SPDX-License-Identifier: GPL-3.0-or-later
"""Exclusive RGB/Kelvin modes with separate saved values for Lights and World."""
import bpy
from . import environment as env
from .defaults import DEFAULT_KELVIN


def background(world):
    if world is None or world.node_tree is None:
        return None
    return next((node for node in world.node_tree.nodes if node.type == 'BACKGROUND'), None)


def blackbody(world):
    node = background(world)
    if node is None:
        return None
    return next((link.from_node for link in node.inputs['Color'].links
                 if link.from_node.type == 'BLACKBODY'), None)


def get_mode(data):
    if isinstance(data, bpy.types.Light):
        return int(data.use_temperature)
    return int(blackbody(data) is not None)


def get_rgb(data):
    if isinstance(data, bpy.types.Light):
        if not data.use_temperature:
            return tuple(data.color)
    else:
        node = background(data)
        if node is not None and not node.inputs['Color'].is_linked:
            return tuple(node.inputs['Color'].default_value)[:3]
    return tuple(data.get('_qle_rgb', (1.0, 1.0, 1.0)))


def get_kelvin(data):
    if isinstance(data, bpy.types.Light):
        return data.temperature
    node = blackbody(data)
    return node.inputs['Temperature'].default_value if node is not None else data.get('_qle_kelvin', 5454.0)


def set_rgb(data, value):
    data['_qle_rgb'] = tuple(value)
    if get_mode(data) == 0:
        if isinstance(data, bpy.types.Light):
            data.color = value
        else:
            node = background(data)
            if node is None:
                raise env.QLEError('Add QLE to restore its World background controls')
            node.inputs['Color'].default_value = (*value, 1.0)


def set_kelvin(data, value):
    data['_qle_kelvin'] = value
    if isinstance(data, bpy.types.Light):
        data.temperature = value
    elif get_mode(data) == 1:
        blackbody(data).inputs['Temperature'].default_value = value


def set_mode(data, value):
    if get_mode(data) == value:
        return
    data['_qle_rgb'] = get_rgb(data)
    data['_qle_kelvin'] = get_kelvin(data)
    if isinstance(data, bpy.types.Light):
        data.use_temperature = bool(value)
        data.color = (1, 1, 1) if value else data['_qle_rgb']
        if value:
            data.temperature = data['_qle_kelvin']
        return
    node = background(data)
    if node is None:
        raise env.QLEError('Add QLE to restore its World background controls')
    socket = node.inputs['Color']
    for link in tuple(socket.links):
        data.node_tree.links.remove(link)
    if value:
        temperature = data.node_tree.nodes.get('QLE Temperature')
        if temperature is None or temperature.type != 'BLACKBODY':
            temperature = data.node_tree.nodes.new('ShaderNodeBlackbody')
            temperature.name = 'QLE Temperature'
        temperature.inputs['Temperature'].default_value = data['_qle_kelvin']
        socket.default_value = (1, 1, 1, 1)
        data.node_tree.links.new(temperature.outputs['Color'], socket)
    else:
        socket.default_value = (*data['_qle_rgb'], 1.0)


def reset_light(data, color, kelvin=DEFAULT_KELVIN):
    data['_qle_rgb'] = tuple(color)
    data['_qle_kelvin'] = kelvin
    data.use_temperature = False
    data.color = color
    data.temperature = kelvin


def reset_world(world):
    for key in ('_qle_rgb', '_qle_kelvin'):
        if key in world:
            del world[key]
