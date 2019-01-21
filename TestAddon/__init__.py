import os
import sys
import math

import bpy
import mathutils
import numpy as np

from bpy_extras.object_utils import AddObjectHelper, object_data_add

sys.path.append(os.path.dirname(__file__) + "/dep")

import srtm

from bpy.types import(
        Panel,
        Operator,
        PropertyGroup,
        UIList
    )

from bpy.props import(
        StringProperty,
        PointerProperty,
        FloatProperty,
        IntProperty,
        EnumProperty,
        CollectionProperty,
    )

bl_info = {
	'name': 'Landscape Generator',
	'description': 'A tool for importing SRTM data into blender.',
	'author': 'Joshua Ganter, Philipp Kern, Simon Löffler',
	'license': 'GPL',
	'deps': '',
	'version': (0, 0, 0),
	'blender': (2, 7, 8),
	'location': 'View3D > Tools > Landscape',
	'warning': '',
	'wiki_url': 'https://github.com/JoshuaGanter/Landschaftsgenerator/wiki',
	'tracker_url': 'https://github.com/JoshuaGanter/Landschaftsgenerator/issues',
	'link': 'https://github.com/JoshuaGanter/Landschaftsgenerator',
	'support': 'TESTING',
	'category': '3D View'
}

class LandscapeGeneratorPanel(Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Create"
    bl_label = "Create Landscape"

    def draw(self, context) :
        scene = context.scene.properties

        column = self.layout.column(align = True)
        column.prop(scene, "latitude")
        column = self.layout.column(align = True)
        column.prop(scene, "longitude")
        column = self.layout.column(align = True)
        column.prop(scene, "size")
        column = self.layout.column(align = True)
        column.operator("mesh.create_landscape", text = "Create Landscape")
    #end draw

#end LandscapeGeneratorPanel

class TextureGeneratorPanel(Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Create"
    bl_label = "Create Texture"

    def draw(self, context) :
        scene = context.scene.properties
        layout = self.layout

        column = self.layout.column(align = True)
        column.prop(scene, "layers")

        column.label("Layers:")
        layout.template_list(
            "LayerList", 
            "my_layer_list", 
            scene,
            "layers_list",
            scene,
            "active_layer_index",
            type='DEFAULT'
        )

        row = layout.row(align=True)
        row.operator("scene.add_my_list_item")
        row.operator("scene.remove_my_list_item")

        column = self.layout.column(align = True)
        column.prop(scene, "layer_blending")

        column = self.layout.column(align = True)
        column.prop(scene, "steepness_layer_name")
        column = self.layout.column(align = True)
        column.prop(scene, "steepness_threshold")

        column = self.layout.column(align = True)
        column.operator("mesh.create_texture", text = "Create Texture")
    #end draw

#end TextureGeneratorPanel

class CreateLandscape(bpy.types.Operator) :
    bl_idname = "mesh.create_landscape"
    bl_label = "Create Landscape"
    bl_options = {"UNDO"}

    def invoke(self, context, event) :

        #procedure for generating landscape

        scene = context.scene.properties

        geo_elevation_data = srtm.get_data()
        #map_center = [20.836962, -156.910592]
        latitude = scene.latitude
        longitude = scene.longitude
        map_size = scene.size
        depth = 20

        lat_1 = latitude - map_size / 2
        lat_2 = latitude + map_size / 2
        long_1 = longitude - map_size / 2
        long_2 = longitude + map_size / 2
        height = (lat_2 - lat_1) * 500
        width = (long_2 - long_1) * 500
        max_elevation = 0
        data = geo_elevation_data.get_image((width,height), (lat_1, lat_2), (long_1, long_2), max_elevation, mode="array").astype(np.int16)

        data = (data / np.amax(data)) * depth

        width = data.shape[1]
        height = data.shape[0]

        print(data.shape)

        # generate Vertices
        verts = [None] * (width * height) # width * height
        vert_counter = 0
        for x in range (height):
            for y in range (width):
                verts[vert_counter] = (x, y, data[x, y])
                vert_counter += 1

        edges = []
        face_counter = 0
        faces = [None] * ((width-1) * (height-1))
        for x in range (height-1):
            for y in range (width-1):   
                faces[face_counter] = [x*width+y, x*width+y+1, x*width+y + width + 1, x*width+y + width]
                face_counter += 1

        mesh = bpy.data.meshes.new(name="NewObject")  # add a new mesh
        mesh.from_pydata(verts, edges, faces)
        mesh.update(calc_edges=True)
        for f in mesh.polygons:
            f.use_smooth = True
        #object_data_add(context, mesh, operator=self)

        obj = bpy.data.objects.new("RandomObject", mesh)
        mod = obj.modifiers.new("Subsurf", "SUBSURF")
        mod.levels = 2
        mod.render_levels = 2
        scene = bpy.context.scene
        scene.objects.link(obj)

        print("FINISHED")

        return {"FINISHED"}
    #end invoke

#end CreateLandscape

class CreateTexture(bpy.types.Operator):
    bl_idname = "mesh.create_texture"
    bl_label = "Create Texture"
    bl_options = {"UNDO"}

    def invoke(self, context, event) :

        #create Texture

        print("FINISHED")

        return {"FINISHED"}
    #end invoke

#end CreateTexture

#UIList
class LayerList (UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label("", icon="TPAINT_HLT")
        layout.prop(item, "name")
        layout.prop(item, "start_height")
        layout.prop(item, "end_height")

class MyListItem(PropertyGroup):
    name = StringProperty(name="Name", default="Layer Name")

    start_height = FloatProperty(
        name = "Start Height",
        description = "Where this layer begins",
        default = 0,
    )

    end_height = FloatProperty(
        name = "End Height",
        description = "Where this layer ends",
        default = 0,
    )

class AddMyListItem(Operator):
    bl_idname = "scene.add_my_list_item"
    bl_label = "Add Entry"
    bl_options = set()

    def execute(self, context):
        settings = context.scene.properties
        settings.layers_list.add()
        settings.active_layer_index = len(settings.layers_list) - 1
        return {'FINISHED'}

class RemoveMyListItem(Operator):
    bl_idname = "scene.remove_my_list_item"
    bl_label = "Remove Active Entry"
    bl_options = set()

    @classmethod
    def poll(cls, context):
        return context.scene.properties.active_layer_index >= 0

    def execute(self, context):
        settings = context.scene.properties  
        settings.layers_list.remove(settings.active_layer_index)
        settings.active_layer_index -= 1
        return {'FINISHED'}

#Properties
class Addon_Properties(PropertyGroup):

    latitude = FloatProperty(
        name = "Lat",
        description = "Latitude of your Map Center",
        default = 1.0,
        ) 

    longitude = FloatProperty(
        name = "Long",
        description = "Longitude of your Map Center",
        default = 1.0,
        ) 

    size = FloatProperty(
        name = "Size",
        description = "Edge length of your map in degree",
        default = 0.5,
        ) 
    
    layers = IntProperty(
        name = "Layers",
        description = "Number of different texture layers",
        default = 0,
        )

    layer_blending = FloatProperty(
        name = "Layer Blending",
        description = "Blending value for layer borders",
        default = 0,
        ) 

    steepness_layer_name = StringProperty(
        name = "Steepness Layer Name",
        description = "Name of steepness layer",
        default = "Steepness Layer",
        )

    steepness_threshold = FloatProperty(
        name = "Steepness Threshold", 
        description = "Threshold for the steepness layer", #measure unit?
        default = 0.8,
        )

    layers_list = CollectionProperty(
        type=MyListItem, 
        name="Layer List"
        )

    active_layer_index = IntProperty(
        name="Active layer", 
        default=-1
        )

classes = (
    LandscapeGeneratorPanel,
    TextureGeneratorPanel,
    CreateLandscape,
    CreateTexture,
    LayerList,
    MyListItem,
    AddMyListItem,
    RemoveMyListItem,
    Addon_Properties
    )

def register() :
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.properties = PointerProperty(type=Addon_Properties)
#end register

def unregister() :
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.properties
#end unregister

if __name__ == "__main__" :
    register()
#end if