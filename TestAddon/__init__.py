import os
import sys
import math

import bpy
import mathutils
import numpy as np

from bpy_extras.object_utils import AddObjectHelper, object_data_add
from .material_layering import *

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
	'version': (0, 1, 3),
	'blender': (2, 7, 9),
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
        column.prop(scene, "depth")
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

        # column = self.layout.column(align = True)
        # column.prop(scene, "layers")
        column = self.layout.column(align = True)
        column.operator("mesh.create_texture", text = "Create Texture")

        column = self.layout.column(align = True)
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
        column.prop(scene, "texture_scaling")
    #end draw

#end TextureGeneratorPanel

class CreateLandscape(bpy.types.Operator) :
    bl_idname = "mesh.create_landscape"
    bl_label = "Create Landscape"
    bl_options = {"UNDO"}

    def invoke(self, context, event) :

        #procedure for generating landscape

        settings = context.scene.properties

        geo_elevation_data = srtm.get_data()
        #map_center = [20.836962, -156.910592]
        latitude = settings.latitude
        longitude = settings.longitude
        map_size = settings.size
        depth = settings.depth

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
        
        settings = context.scene.properties

        lanndscape_mat = create_landscape_material(settings.depth, settings.texture_scaling)
        create_steepness_layer(settings.steepness_layer_name, settings.steepness_threshold)
        link_selection_to_material(context)
        load_default_layer_materials()

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

    # context = None

    # def set_context(self, context):
    #     self.context = context
    
    # def update_layer_name (self, value):
    #     #settings = self.context.scene.properties
    #     settings = value.scene.properties
    #     update_landscape_layer(settings.active_layer_index, settings.layers_list[settings.active_layer_index].name, self.start_height, self.end_height, settings.layer_blending, settings.layer_blending)

    # def update_layer_start_height (self, value):
    #     #settings = self.context.scene.properties
    #     settings = value.scene.properties
    #     update_landscape_layer(settings.active_layer_index, self.name, settings.layers_list[settings.active_layer_index].start_height, self.end_height, settings.layer_blending, settings.layer_blending)

    # def update_layer_end_height (self, value):
    #     #settings = self.context.scene.properties
    #     settings = value.scene.properties
    #     update_landscape_layer(settings.active_layer_index, self.name, self.start_height, settings.layers_list[settings.active_layer_index].end_height, settings.layer_blending, settings.layer_blending)

    def update_layer (self, value):
        settings = value.scene.properties
        layer = settings.layers_list[settings.active_layer_index]
        update_landscape_layer(settings.active_layer_index, layer.name, layer.start_height, layer.end_height, settings.layer_blending, settings.layer_blending)

    name = StringProperty(
        name="Name", 
        default="Layer",
        update = update_layer
    )

    start_height = FloatProperty(
        name = "Start Height",
        description = "Where this layer begins",
        default = 0,
        update = update_layer
    )

    end_height = FloatProperty(
        name = "End Height",
        description = "Where this layer ends",
        default = 0,
        update = update_layer
    )

class AddMyListItem(Operator):
    bl_idname = "scene.add_my_list_item"
    bl_label = "Add Entry"
    bl_options = set()

    def execute(self, context):
        settings = context.scene.properties
        settings.layers_list.add()
        settings.active_layer_index = len(settings.layers_list) - 1
        #settings.layers_list[settings.active_layer_index].set_context(context)

        create_landscape_layer(
            settings.active_layer_index, 
            settings.layers_list[settings.active_layer_index].name, 
            settings.layers_list[settings.active_layer_index].start_height, 
            settings.layers_list[settings.active_layer_index].end_height,
            settings.layer_blending,
            settings.layer_blending)

        link_landscape_layers(len(settings.layers_list))

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

        delete_landscape_layer(settings.active_layer_index, len(settings.layers_list))

        settings.active_layer_index -= 1
        return {'FINISHED'}

#Properties
class Addon_Properties(PropertyGroup):

    # def update_steepness_layer_name (self, value):
    #     settings = value.scene.properties
    #     update_steepness_layer(settings.steepness_layer_name, self.steepness_threshold)

    # def update_steepness_layer_threshold (self, value):
    #     settings = value.scene.properties
    #     update_steepness_layer (self.steepness_layer_name, settings.steepness_threshold)
    
    def update_layers (self, value):
        settings = value.scene.properties
        for i in range(len(self.layers_list)):
            layer = self.layers_list[i]
            update_landscape_layer(i, layer.name, layer.start_height, layer.end_height, settings.layer_blending, settings.layer_blending)

    def update_steepness_l (self, value):
        settings = value.scene.properties
        update_steepness_layer(settings.steepness_layer_name, settings.steepness_threshold)
    
    def update_textures(self, value):
        settings = value.scene.properties
        update_landscape_textures(settings.texture_scaling)

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

    depth = FloatProperty(
        name = "Depth",
        description = "Depth Scaling of your Map",
        default = 10,
        ) 
    
    # layers = IntProperty(
    #     name = "Layers",
    #     description = "Number of different texture layers",
    #     default = 0,
    #     )

    layer_blending = FloatProperty(
        name = "Layer Blending",
        description = "Blending value for layer borders",
        default = 0,
        update = update_layers
        ) 

    steepness_layer_name = StringProperty(
        name = "Steepness Layer Name",
        description = "Name of steepness layer",
        default = "Steepness Layer",
        update = update_steepness_l
        )

    steepness_threshold = FloatProperty(
        name = "Steepness Threshold", 
        description = "Threshold for the steepness layer", #measure unit?
        default = 45,
        update = update_steepness_l
        )

    texture_scaling = FloatProperty(
        name = "Texture Scaling", 
        description = "Scaling for the Textures", #measure unit?
        default = 1000,
        update = update_textures
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