import os
import sys
import math

import bpy
import mathutils
import numpy

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

        # TODO: add in procedure for generating landscape

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