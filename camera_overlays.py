bl_info = {
    "name": "Camera Overlays",
    "description": "Show/Hide Harmony and Golden Ratios and Triangles",
    "author": "Don Schnitzius",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Context Menu (Right Mouse Button)",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Camera",
}


import bpy


class CAMERA_SCT_overlays(bpy.types.Operator):
    """Show/Hide Harmony Overlays"""
    bl_idname = "camera.harmony_overlays"
    bl_label = "Show Harmony Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return ob and ob.type == 'CAMERA'

    def execute(self, context):
        ob = bpy.context.object.data
        if ob.show_composition_thirds == False:
            ob.show_composition_thirds = True
            ob.show_composition_harmony_tri_a = True
            ob.show_composition_harmony_tri_b = True
        else:
            ob.show_composition_thirds = False
            ob.show_composition_harmony_tri_a = False
            ob.show_composition_harmony_tri_b = False

        return {'FINISHED'}


class CAMERA_SCG_overlays(bpy.types.Operator):
    """Show/Hide Golden Overlays"""
    bl_idname = "camera.golden_overlays"
    bl_label = "Show Golden Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = bpy.context.active_object
        return ob and ob.type == 'CAMERA'

    def execute(self, context):
        ob = bpy.context.object.data

        if ob.show_composition_golden == False:
            ob.show_composition_golden = True
            ob.show_composition_golden_tria_a = True
            ob.show_composition_golden_tria_b = True
        else:
            ob.show_composition_golden = False
            ob.show_composition_golden_tria_a = False
            ob.show_composition_golden_tria_b = False

        return {'FINISHED'}


classes = [
    CAMERA_SCT_overlays,
    CAMERA_SCG_overlays,
]


def draw_inmenu(self, context):
    self.layout.separator()
    self.layout.operator("camera.harmony_overlays", text="Harmony Overlays")
    self.layout.operator("camera.golden_overlays", text="Golden Overlays")


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