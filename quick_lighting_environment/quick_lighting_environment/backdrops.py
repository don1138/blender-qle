# SPDX-License-Identifier: GPL-3.0-or-later
"""Stage selection and live surface controls, preserving legacy Diffuse defaults."""
from pathlib import Path
import bpy

from . import environment as env

ASSETS = {'L_BACKDROP': 'L Backdrop', 'FLAT_BACKGROUND': 'Flat Background', 'FLOOR': 'Floor'}
FINISHES = {'REFLECTIVE': 0.10, 'SATIN': 0.35, 'MATTE': 0.70}


def objects(scene):
    return env.objects_for(scene, 'backdrop')


def surface_node(material):
    if material is None or material.node_tree is None:
        return None
    output = next((node for node in material.node_tree.nodes if node.type == 'OUTPUT_MATERIAL' and node.is_active_output), None)
    if output is None:
        return None
    return next((link.from_node for link in output.inputs['Surface'].links
                 if link.from_node.type in {'BSDF_PRINCIPLED', 'BSDF_DIFFUSE'}), None)


def material(scene):
    # Prefer the actual material, so changes made with Blender's tools are live.
    for obj in objects(scene):
        if obj.active_material is not None:
            return obj.active_material
    return scene.qle_settings.backdrop_material


def color(scene):
    mat = material(scene)
    node = surface_node(mat)
    if node is not None:
        key = 'Base Color' if node.type == 'BSDF_PRINCIPLED' else 'Color'
        return tuple(node.inputs[key].default_value)
    return tuple(mat.diffuse_color) if mat is not None else (0.2158603, 0.2158603, 0.2158605, 1)


def roughness(scene):
    mat = material(scene)
    node = surface_node(mat)
    if node is not None:
        return node.inputs['Roughness'].default_value
    return mat.roughness if mat is not None else 1.0


def editable_material(scene):
    mat = material(scene)
    if mat is None:
        raise env.QLEError('Add a stage to restore its surface controls')
    # Do not change another scene or an unrelated object sharing this material.
    stage = objects(scene)
    external = any(obj not in stage and obj.type == 'MESH'
                   and any(slot.material == mat for slot in obj.material_slots)
                   for obj in bpy.data.objects)
    if not env.owned(mat, scene, 'backdrop_material') or external:
        mat = mat.copy()
        mat.name = 'QLE Stage Surface'
        env.mark(mat, scene, 'backdrop_material')
        for obj in stage:
            if obj.data.users > 1:
                obj.data = obj.data.copy()
                env.mark(obj.data, scene, 'backdrop_mesh')
            obj.data.materials.clear()
            obj.data.materials.append(mat)
    scene.qle_settings.backdrop_material = mat
    return mat


def set_color(scene, value):
    mat = editable_material(scene)
    node = surface_node(mat)
    if node is None:
        raise env.QLEError('This material has no directly editable Diffuse or Principled surface')
    key = 'Base Color' if node.type == 'BSDF_PRINCIPLED' else 'Color'
    for link in tuple(node.inputs[key].links):
        mat.node_tree.links.remove(link)
    node.inputs[key].default_value = value
    mat.diffuse_color = value


def set_roughness(scene, value):
    old_color = color(scene)
    mat = editable_material(scene)
    node = surface_node(mat)
    if node is None:
        raise env.QLEError('This material has no directly editable Diffuse or Principled surface')
    if node.type == 'BSDF_DIFFUSE':
        # Preserve the original Diffuse shader until the user intentionally
        # requests a finish change. Reflective needs a reflecting shader.
        output = next(node for node in mat.node_tree.nodes if node.type == 'OUTPUT_MATERIAL' and node.is_active_output)
        node = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        node.inputs['Base Color'].default_value = old_color
        mat.node_tree.links.new(node.outputs['BSDF'], output.inputs['Surface'])
    node.inputs['Roughness'].default_value = value
    mat.roughness = value


def prepare(kind):
    if kind == 'C_BACKDROP':
        return env.prepare_backdrop()
    name = ASSETS.get(kind)
    if name is None:
        raise env.QLEError('Unknown stage type')
    path = Path(__file__).with_name('_backdrops.blend')
    if not path.is_file():
        raise env.QLEError('The packaged stage options are missing; reinstall QLE')
    try:
        with bpy.data.libraries.load(str(path), link=False) as (source, destination):
            if name not in source.objects:
                raise env.QLEError(f'The packaged {name} is missing; reinstall QLE')
            destination.objects = [name]
    except (OSError, RuntimeError) as error:
        if isinstance(error, env.QLEError):
            raise
        raise env.QLEError(f'Cannot load {name}: {error}') from error
    obj = destination.objects[0]
    if obj is None or obj.type != 'MESH':
        if obj is not None:
            bpy.data.objects.remove(obj)
        raise env.QLEError(f'The packaged {name} is not a mesh')
    obj.use_fake_user = False
    obj.data.use_fake_user = False
    return obj


def apply(scene, kind):
    if not env.environment_exists(scene):
        raise env.QLEError('Add QLE before changing its stage')
    env.check_scene_isolation(scene, env.objects_for(scene))
    # Prepare first; a missing asset cannot destroy the working stage.
    replacement = None if kind == 'NONE' else prepare(kind)
    old_objects = objects(scene)
    mat = material(scene)
    if mat is not None:
        mat = editable_material(scene)
    enabled = all(not obj.hide_viewport and not obj.hide_render for obj in old_objects) if old_objects else scene.qle_settings.backdrop_last_enabled
    if replacement is not None:
        if mat is not None:
            imported_materials = list(replacement.data.materials)
            replacement.data.materials.clear()
            replacement.data.materials.append(mat)
            for imported in imported_materials:
                if imported is not None and imported.users == 0:
                    bpy.data.materials.remove(imported)
        env.attach_backdrop(scene, env.collection_for(scene, 'environment'), replacement)
        replacement.hide_viewport = not enabled
        replacement.hide_render = not enabled
    env.remove_objects(scene, old_objects)
    scene.qle_settings.backdrop_type = kind
    scene.qle_settings.backdrop_last_enabled = enabled


def position(scene):
    return tuple(objects(scene)[0].matrix_world.translation) if objects(scene) else (0, 0, 0)


def set_position(scene, value):
    for obj in objects(scene):
        matrix = obj.matrix_world.copy()
        matrix.translation = value
        obj.matrix_world = matrix


def cleanup(scene):
    mat = scene.qle_settings.backdrop_material
    scene.qle_settings.backdrop_material = None
    if mat is not None and mat.users == 0 and env.owned(mat, scene, 'backdrop_material'):
        bpy.data.materials.remove(mat)
