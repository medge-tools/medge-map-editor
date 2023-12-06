bl_info = {
    "name" : "Mirror's Edge Editor",
    "author" : "Tariq Bakhtali (didibib)",
    "description" : "",
    "blender" : (3, 4, 0),
    "version" : (0, 6, 9),
    "location" : "",
    "warning" : "",
    "category" : "MEdge Tools"
}

import bpy
from .t3d import exporter

def menu_func_export(self, context):
    self.layout.operator(exporter.T3D_OT_Exporter.bl_idname, text="T3D Scene Export (.t3d)")

def register():  
    for cls in exporter.classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():   
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in exporter.classes:
        bpy.utils.unregister_class(cls)