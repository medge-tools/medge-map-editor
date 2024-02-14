bl_info = {
    "name" : "MEdge Tools: Map Editor",
    "author" : "Tariq Bakhtali (didibib)",
    "description" : "",
    "blender" : (3, 4, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "MEdge Tools"
}


# -----------------------------------------------------------------------------
import bpy
from .io.t3d.exporter import MET_OT_T3D_Export
from .io.ase.exporter import MET_OT_ASE_Export
from .map_editor.props import *
from .map_editor.gui import *
from . import auto_load


# -----------------------------------------------------------------------------
def menu_func_export_t3d(self, context):
    self.layout.operator(MET_OT_T3D_Export.bl_idname, text='MEdge T3D (.t3d)')


# -----------------------------------------------------------------------------
def menu_func_export_ase(self, context):
    self.layout.operator(MET_OT_ASE_Export.bl_idname, text='MEdge ASE (.ase)')


# -----------------------------------------------------------------------------
def register():
    auto_load.init()
    auto_load.register()

    bpy.types.Object.medge_actor = bpy.props.PointerProperty(type=MET_OBJECT_PG_Actor)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_t3d)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_ase)


# -----------------------------------------------------------------------------
def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_ase)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_t3d)

    del bpy.types.Object.medge_actor
    
    auto_load.unregister()
    