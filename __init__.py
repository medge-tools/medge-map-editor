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

# =============================================================================
import bpy
from bpy.app.handlers import depsgraph_update_post
from .t3d.exporter import ME_OT_T3D_Export
from .ase.exporter import ME_OT_ASE_Export
from .b3d.props import *
from .b3d.gui import *
from . import auto_load

# =============================================================================
def menu_func_export_t3d(self, context):
    self.layout.operator(ME_OT_T3D_Export.bl_idname, text='MEdge T3D (.t3d)')

# =============================================================================
def menu_func_export_ase(self, context):
    self.layout.operator(ME_OT_ASE_Export.bl_idname, text='MEdge ASE (.ase)')

# =============================================================================
def register():
    auto_load.init()
    auto_load.register()
    bpy.types.Object.me_actor = bpy.props.PointerProperty(type=ME_OBJECT_PG_Actor)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_t3d)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_ase)

# =============================================================================
def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_ase)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_t3d)

    del bpy.types.Object.me_actor
    
    auto_load.unregister()
    