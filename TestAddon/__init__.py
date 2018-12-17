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
        PropertyGroup
        )

from bpy.props import(
        StringProperty,
        PointerProperty,
        FloatProperty
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

class LandscapeGeneratorPanel(bpy.types.Panel) :
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

        lat1 = latitude - map_size / 2
        lat2 = latitude + map_size / 2
        long1 = longitude - map_size / 2
        long2 = longitude + map_size / 2
        height = (lat2 - lat1) * 500
        width = (long2 - long1) * 500
        max_elevation = 0
        data = geo_elevation_data.get_image((width,height), (lat1, lat2), (long1, long2), max_elevation, mode="array").astype(np.int16)

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

classes = (
    LandscapeGeneratorPanel,
    Addon_Properties,
    CreateLandscape
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