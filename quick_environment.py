bl_info = {
    "name": "Quick Lighting Environment",
    "author": "Don Schnitzius",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Scene",
    "description": "Adds Three Area Lights and Sets World Surface to Black",
    "warning": "",
    "wiki_url": "",
    "category": "Scene",
}


import bpy


def btn_01(context):

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
    bpy.context.active_object.name = "Lights_Target"

    bpy.ops.object.light_add(type='AREA', radius=10, location=(5, 1.5, 5))
    bpy.context.active_object.name = "Area_Right"
    bpy.context.active_object.data.shape = 'RECTANGLE'
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 1
    bpy.context.active_object.data.size_y = 3
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.active_object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.active_object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.active_object.constraints["Track To"].target = bpy.data.objects["Lights_Target"]

    bpy.ops.object.light_add(type='AREA', radius=10, location=(-5, 1.5, 5))
    bpy.context.active_object.name = "Area_Left"
    bpy.context.active_object.data.shape = 'RECTANGLE'
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 1
    bpy.context.active_object.data.size_y = 3
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.active_object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.active_object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.active_object.constraints["Track To"].target = bpy.data.objects["Lights_Target"]

    bpy.ops.object.light_add(type='AREA', radius=10, location=(0, -5, 5))
    bpy.context.active_object.name = "Area_Fill"
    bpy.context.active_object.data.shape = 'RECTANGLE'
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 6
    bpy.context.active_object.data.size_y = 4
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.active_object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.active_object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.active_object.constraints["Track To"].target = bpy.data.objects["Lights_Target"]


class AddLights(bpy.types.Operator):
    """Add Lights"""
    bl_idname = "dms.add_lights"
    bl_label = "Add Environment"

    def execute(self, context):
        btn_01(context)
        return {'FINISHED'}


def btn_02(context):

    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.select_by_type(type='EMPTY')
    bpy.ops.object.delete(use_global=False)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 1


class ClearLights(bpy.types.Operator):
    """Remove Lights"""
    bl_idname = "dms.clear_lights"
    bl_label = "Clear Environment"

    def execute(self, context):
        btn_02(context)
        return {'FINISHED'}


class LayoutLightsPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Add Quick Environment"
    bl_idname = "SCENE_PT_quickEnvironment"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("dms.add_lights")

        # Big render button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("dms.clear_lights")

        # Different sizes in a row
#        layout.label(text="Simple Studio Lights:")
#        row = layout.row(align=True)
#        row.operator("dms.add_lights")
#        row.operator("dms.clear_lights")


def register():
    bpy.utils.register_class(AddLights)
    bpy.utils.register_class(ClearLights)
    bpy.utils.register_class(LayoutLightsPanel)


def unregister():
    bpy.utils.unregister_class(AddLights)
    bpy.utils.unregister_class(ClearLights)
    bpy.utils.unregister_class(LayoutLightsPanel)


if __name__ == "__main__":
    register()
