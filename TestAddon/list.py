import bpy

def get_color_enum(self):
    return self.get('color_enum', 0) 

def set_color_enum(self, value):
    COLORS = (
        (1.0, 0.0, 1.0), (1.0, 1.0, 0.0), (0.0, 1.0, 1.0),
        (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    self['color_enum'] = value
    self['color_value'] = COLORS[value]

def get_color_value(self):
    return self.get('color_value', (1.0, 0.0, 1.0))

def set_color_value(self, value):
    self['color_value'] = value
    self['color_enum'] = 6

class MyListItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name", default="Name")
    color_enum = bpy.props.EnumProperty(
        name="Color",
        items=(
            ("PINK",    "Pink",   "", 0),
            ("YELLOW",  "Yellow", "", 1),
            ("CYAN",    "Cyan",   "", 2),
            ("RED",     "Red",    "", 3),
            ("GREEN",   "Green",  "", 4),
            ("BLUE",    "Blue",   "", 5),
            ("CUSTOM",  "Custom", "", 6)),
        get=get_color_enum,
        set=set_color_enum
    )
    color_value = bpy.props.FloatVectorProperty(
        name="Color", 
        subtype="COLOR", 
        min=0.0, 
        max=1.0,
        get=get_color_value,
        set=set_color_value
    )

class MyExportSettings(bpy.types.PropertyGroup):
    colors = bpy.props.CollectionProperty(type=MyListItem, name="Colors")
    active_color_index = bpy.props.IntProperty(name="Active Color", default=-1)
    # ...

class SCENE_UL_my_color_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label("", icon="COLOR")
        layout.prop(item, "name",  "")
        layout.prop(item, "color_enum", "")
        layout.prop(item, "color_value", "")

class MyExportPanel(bpy.types.Panel):
    bl_label = "Colors Export Panel"
    bl_idname = "SCENE_PT_my_export_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.my_export_settings

        layout.template_list(
            "SCENE_UL_my_color_list", 
            "my_color_list", 
            settings,
            "colors",
            settings,
            "active_color_index",
            type='DEFAULT'
        )

        row = layout.row(align=True)
        row.operator("scene.add_my_list_item")
        row.operator("scene.remove_my_list_item")

class AddMyListItem(bpy.types.Operator):
    bl_idname = "scene.add_my_list_item"
    bl_label = "Add Entry"
    bl_options = set()

    def execute(self, context):
        settings = context.scene.my_export_settings
        settings.colors.add()
        settings.active_color_index = len(settings.colors) - 1
        return {'FINISHED'}

class RemoveMyListItem(bpy.types.Operator):
    bl_idname = "scene.remove_my_list_item"
    bl_label = "Remove Active Entry"
    bl_options = set()

    @classmethod
    def poll(cls, context):
        return context.scene.my_export_settings.active_color_index >= 0

    def execute(self, context):
        settings = context.scene.my_export_settings    
        settings.colors.remove(settings.active_color_index)
        settings.active_color_index -= 1
        return {'FINISHED'}

def register():
    for cls in (MyListItem, MyExportSettings, SCENE_UL_my_color_list, MyExportPanel, AddMyListItem, RemoveMyListItem):
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_export_settings = bpy.props.PointerProperty(type=MyExportSettings)  

if __name__ == "__main__":
    register()