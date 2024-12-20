bl_info = {
    "name"       : "QCO (QuickCamera Overlays)",
    "description": "Show/Hide Center, Harmony, and Golden Ratio Camera Overlays",
    "author"     : "Don Schnitzius",
    "version"    : (1, 2, 3),
    "blender"    : (3, 0, 0),
    "location"   : "Context Menu (Right Mouse Button)",
    "warning"    : "",
    "doc_url"    : "https://github.com/don1138/blender-qle",
    "tracker_url": "",
    "support"    : "COMMUNITY",
    "category"   : "Camera",
}

import bpy


def is_camera_view_active(context):
    """
    Check if the current context is in the 3D View and the perspective is set to CAMERA.
    """
    area = context.area
    if area and area.type == 'VIEW_3D':
        region_3d = area.spaces.active.region_3d
        if region_3d and region_3d.view_perspective == 'CAMERA':
            return True
    return False


def toggle_properties(obj, props_to_toggle):
    """
    Toggle the specified boolean properties on the given object.
    The new state is the opposite of the first property's current value.
    """
    current_state = getattr(obj, props_to_toggle[0])
    new_state = not current_state
    for prop in props_to_toggle:
        setattr(obj, prop, new_state)


class CAMERA_SCC_overlays(bpy.types.Operator):
    """Show/Hide Center Overlays"""
    bl_idname = "camera.center_overlays"
    bl_label = "Show Center Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.camera and
                context.scene.camera.type == 'CAMERA' and
                is_camera_view_active(context))

    def execute(self, context):
        ob = context.scene.camera.data
        center_props = ["show_composition_center", "show_composition_center_diagonal"]
        toggle_properties(ob, center_props)
        return {'FINISHED'}


class CAMERA_SCG_overlays(bpy.types.Operator):
    """Show/Hide Golden Overlays"""
    bl_idname = "camera.golden_overlays"
    bl_label = "Show Golden Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.camera and
                context.scene.camera.type == 'CAMERA' and
                is_camera_view_active(context))

    def execute(self, context):
        ob = context.scene.camera.data
        golden_props = ["show_composition_golden", "show_composition_golden_tria_a", "show_composition_golden_tria_b"]
        toggle_properties(ob, golden_props)
        return {'FINISHED'}


class CAMERA_SCH_overlays(bpy.types.Operator):
    """Show/Hide Harmony Overlays"""
    bl_idname = "camera.harmony_overlays"
    bl_label = "Show Harmony Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.camera and
                context.scene.camera.type == 'CAMERA' and
                is_camera_view_active(context))

    def execute(self, context):
        ob = context.scene.camera.data
        harmony_props = ["show_composition_thirds", "show_composition_harmony_tri_a", "show_composition_harmony_tri_b"]
        toggle_properties(ob, harmony_props)
        return {'FINISHED'}


class CAMERA_SP_passepartout(bpy.types.Operator):
    """Toggle Passepartout"""
    bl_idname = "camera.passepartout_toggle"
    bl_label = "Toggle Passepartout"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.camera and
                context.scene.camera.type == 'CAMERA' and
                is_camera_view_active(context))

    def execute(self, context):
        ob = context.scene.camera.data
        # If passepartout_alpha is not 1.0, set it to 1.0; otherwise set to 0.5
        ob.passepartout_alpha = 1.0 if ob.passepartout_alpha != 1.0 else 0.5
        return {'FINISHED'}


classes = [
    CAMERA_SCC_overlays,
    CAMERA_SCG_overlays,
    CAMERA_SCH_overlays,
    CAMERA_SP_passepartout,
]


def draw_inmenu(self, context):
    """
    Append camera overlay toggle operators to the object context menu.
    They will only appear if the poll conditions are satisfied (in camera view).
    """
    self.layout.separator()
    self.layout.operator("camera.center_overlays",     text="Center Overlays")
    self.layout.operator("camera.golden_overlays",     text="Golden Overlays")
    self.layout.operator("camera.harmony_overlays",    text="Harmony Overlays")
    self.layout.operator("camera.passepartout_toggle", text="Passepartout Toggle")
    self.layout.separator()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(draw_inmenu)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_inmenu)


if __name__ == "__main__":
    register()
