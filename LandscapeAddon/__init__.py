bl_info = {
    "name": "Landscape Generator",
    "author": "Joshua Ganter, Philipp Kern, Simon Löffler",
    "version": (0, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool Shelf",
    "description": "Create Landscape from SRTM data (including vegetation)",
    "warning": "",
    "wiki_url": ""
                "",
    "category": "Add Mesh",
}

import os,sys

def _checkPath():
    path = os.path.dirname(__file__)
    print(path)
    print(sys.path)
    if path in sys.path:
        sys.path.remove(path)
    # make <path> the first one to search for a module --> current path is the first one to check
    sys.path.insert(0, path)
_checkPath()

import bpy
from bpy_extras.io_utils import ImportHelper

sys.path.append(os.path.dirname(__file__) + "/Dependencies")
print(sys.path)

import srtm
import numpy as np
import bmesh

from bpy_extras.object_utils import AddObjectHelper, object_data_add

print("SRTM Name:" + srtm.__name__)

class LandscapeGenerator(bpy.types.Operator):
    bl_idname = "mesh.matrix_extrude"
    bl_label = "Matrix Extrude selected faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        geo_elevation_data = srtm.get_data()
        map_center = [48, 8]
        map_size = 6

        lat1 = map_center[0] - map_size / 2
        lat2 = map_center[0] + map_size / 2
        long1 = map_center[1] - map_size / 2
        long2 = map_center[1] + map_size / 2
        height = (lat2 - lat1) * 100
        width = (long2 - long1) * 100
        max_elevation = 1000
        data = geo_elevation_data.get_image((width,height), (lat1, lat2), (long1, long2), max_elevation, mode="array").astype(np.int16)

        #create plane at 3D Cursor
        #bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, 
        #location=bpy.context.scene.cursor_location, 
        #layers=(True, False, False, False, False, False, False, False, False, False, False, 
        #False, False, False, False, False, False, False, False, False))

        # generate Vertices
        verts = [None] * (data.shape[1] * data.shape[0]) # width * height
        vert_counter = 0
        for x in range (data.shape[0]):
            for y in range (data.shape[1]):
                verts[vert_counter] = (x, y, data[x, y])
                vert_counter += 1

        edges = []
 
        faces = [None] * (data.shape[1]-1 * data.shape[0]-1)
        face_counter = 0
        for x in range (data.shape[0]-1):
            for y in range (data.shape[1]-1):
                faces[face_counter] = [x*data.shape[1]+y, x*data.shape[1]+y, x*data.shape[1]+y + data.shape[1] + 1, x*data.shape[1]+y + data.shape[1]]
                face_counter += 1

        mesh = bpy.data.meshes.new(name="NewObject")  # add a new mesh
        mesh.from_pydata(verts, edges, faces)
        object_data_add(context, mesh, operator=self)

        print("Finished")

def register():
    print("Registering Landscape Generator")
    bpy.utils.register_class(LandscapeGenerator)

def unregister():
    print("Unregistering Landscape Generator")
    bpy.utils.unregister_class(LandscapeGenerator)



