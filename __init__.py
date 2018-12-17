import os
import sys
import math

import bpy
import mathutils
import numpy as np

from bpy_extras.object_utils import AddObjectHelper, object_data_add

sys.path.append(os.path.dirname(__file__) + "/dep")

import srtm

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

class LandscapeGeneratorPanel(bpy.types.Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Create"
    bl_label = "Create Landscape"

    def draw(self, context) :
        column = self.layout.column(align = True)
        column.operator("mesh.create_landscape", text = "Create Landscape")
    #end draw

#end LandscapeGeneratorPanel

class CreateLandscape(bpy.types.Operator) :
    bl_idname = "mesh.create_landscape"
    bl_label = "Create Landscape"
    bl_options = {"UNDO"}

    def invoke(self, context, event) :

        #procedure for generating landscape

        geo_elevation_data = srtm.get_data()
        map_center = [20.836962, -156.910592]
        map_size = 0.4
        depth = 20
        mask_width = 2048
        mask_height = 2048

        lat1 = map_center[0] - map_size / 2
        lat2 = map_center[0] + map_size / 2
        long1 = map_center[1] - map_size / 2
        long2 = map_center[1] + map_size / 2
        height = (lat2 - lat1) * 500
        width = (long2 - long1) * 500
        max_elevation = 0
        data = geo_elevation_data.get_image((width,height), (lat1, lat2), (long1, long2), max_elevation, mode="array").astype(np.int16)

        data = (data / np.amax(data)) * depth

        width = data.shape[1]
        height = data.shape[0]

        print(data.shape)

        def prepare_image(image_name, width, height, value=[0,0,0,1]):
            img = bpy.data.images[image_name]
            img.scale(width, height)
            pixels = [None] * (width * height)
            
            for i in range(width * height):
                pixels[i] = value

            img.pixels = [chan for px in pixels for chan in px]
            img.update()

        def finish_image(image_name, arr, width = 1024, height = 1024):
            img = bpy.data.images[image_name]
            img.pixels = [chan for px in arr for chan in px]
            img.scale(width, height)
            img.update()

        # Fill Grass Mask
        prepare_image("GrassMask", width, height)
        prepare_image("SnowMask", width, height)
        prepare_image("WaterMask", width, height)
        prepare_image("StoneMask", width, height)

        pixels_grass = [None] * (width * height)
        pixels_snow = [None] * (width * height)
        pixels_water = [None] * (width * height)
        pixels_stone = [None] * (width * height)

        for x in range(width):
            for y in range(height):
                val = data[x, y] / depth
                
                # Grass Mask
                r = g = b = 1 if val > 0 and val < 0.6 else 0
                pixels_grass[(y * height) + x] = [r,g,b,1]
                
                # Snow Mask
                r = g = b = 1 if val > 0.8 else 0
                pixels_snow[(y * height) + x] = [r,g,b,1]
                
                # Water Mask
                r = g = b = 1 if val == 0 else 0
                pixels_water[(y * height) + x] = [r,g,b,1]
                
                # Stone Mask
                r = g = b = 1 if val > 0.6 and val < 0.8 else 0
                pixels_stone[(y * height) + x] = [r,g,b,1]
                
        pixels_grass = pixels_grass
        pixels_snow = pixels_snow
        pixels_water = pixels_water
        pixels_stone = pixels_stone

        finish_image("GrassMask", pixels_grass)
        finish_image("SnowMask", pixels_snow)
        finish_image("WaterMask", pixels_water)
        finish_image("StoneMask", pixels_stone)

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

        obj = bpy.data.objects.new("RandomObject", mesh)
        obj.data.materials.append(bpy.data.materials["LandscapeMaterial"])
        mod = obj.modifiers.new("Subsurf", "SUBSURF")
        mod.levels = 2
        mod.render_levels = 2
        scene = bpy.context.scene
        scene.objects.link(obj)

        print("FINISHED")

        return {"FINISHED"}
    #end invoke

#end CreateLandscape

def register() :
    bpy.utils.register_class(CreateLandscape)
    bpy.utils.register_class(LandscapeGeneratorPanel)
#end register

def unregister() :
    bpy.utils.unregister_class(CreateLandscape)
    bpy.utils.unregister_class(LandscapeGeneratorPanel)
#end unregister

if __name__ == "__main__" :
    register()
#end if