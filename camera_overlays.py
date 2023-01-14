bl_info = {
    "name"       : "Camera Overlays",
    "description": "Show/Hide Harmony and Golden Ratios and Triangles",
    "author"     : "Don Schnitzius",
    "version"    : (1, 2, 2),
    "blender"    : (3, 0, 0),
    "location"   : "Context Menu (Right Mouse Button)",
    "warning"    : "",
    "doc_url"    : "https://github.com/don1138/blender-qle",
    "tracker_url": "",
    "support"    : "COMMUNITY",
    "category"   : "Camera",
}


import bpy


class CAMERA_SCC_overlays(bpy.types.Operator):
    """Show/Hide Center Overlays"""
    bl_idname = "camera.center_overlays"
    bl_label = "Show Center Overlays"
    bl_options = {'REGISTER', 'UNDO'}

#    @classmethod
#    def poll(cls, context):
#        ob = bpy.context.active_object
#        return ob and ob.type == 'CAMERA'

    def execute(self, context):
        ob = bpy.context.scene.camera.data

        if ob.show_composition_center == False:
            ob.show_composition_center = True
            ob.show_composition_center_diagonal = True
        else:
            ob.show_composition_center = False
            ob.show_composition_center_diagonal = False

        return {'FINISHED'}


class CAMERA_SCG_overlays(bpy.types.Operator):
    """Show/Hide Golden Overlays"""
    bl_idname = "camera.golden_overlays"
    bl_label = "Show Golden Overlays"
    bl_options = {'REGISTER', 'UNDO'}

#    @classmethod
#    def poll(cls, context):
#        ob = bpy.context.active_object
#        return ob and ob.type == 'CAMERA'

    def execute(self, context):
        ob = bpy.context.scene.camera.data

        if ob.show_composition_golden == False:
            self.show_golden(True, ob)
        else:
            self.show_golden(False, ob)
        return {'FINISHED'}

    def show_golden(self, bool, ob):
        ob.show_composition_golden = bool
        ob.show_composition_golden_tria_a = bool
        ob.show_composition_golden_tria_b = bool


class CAMERA_SCH_overlays(bpy.types.Operator):
    """Show/Hide Harmony Overlays"""
    bl_idname = "camera.harmony_overlays"
    bl_label = "Show Harmony Overlays"
    bl_options = {'REGISTER', 'UNDO'}

#    @classmethod
#    def poll(cls, context):
#        ob = bpy.context.active_object
#        return ob and ob.type == 'CAMERA'

    def execute(self, context):
        ob = bpy.context.scene.camera.data

        if ob.show_composition_thirds == False:
            self.show_harmony(True, ob)
        else:
            self.show_harmony(False, ob)
        return {'FINISHED'}

    def show_harmony(self, bool, ob):
        ob.show_composition_thirds = bool
        ob.show_composition_harmony_tri_a = bool
        ob.show_composition_harmony_tri_b = bool


class CAMERA_SP_passepartout(bpy.types.Operator):
    """Toggle Passepartout"""
    bl_idname = "camera.passepartout_toggle"
    bl_label = "Toggle Passepartout"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     ob = bpy.context.active_object
    #     return ob and ob.type == 'CAMERA'

    def execute(self, context):
        ob = bpy.context.scene.camera.data

        ob.passepartout_alpha = 1 if ob.passepartout_alpha != 1 else 0.5
        return {'FINISHED'}


classes = [
    CAMERA_SCC_overlays,
    CAMERA_SCG_overlays,
    CAMERA_SCH_overlays,
    CAMERA_SP_passepartout,
]


def draw_inmenu(self, context):
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
