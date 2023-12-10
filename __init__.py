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
from .t3d.exporter import T3D_OT_Exporter
from .interface.props import MET_PG_MESH_Actor
from .interface.gui import *
from . import auto_load

# =============================================================================
def menu_func_export(self, context):
    self.layout.operator(T3D_OT_Exporter.bl_idname, text='T3D Scene Export (.t3d)')

# =============================================================================
def register():
    # Register before auto-load to prevent error: 'NameError: name 'EnumProperty' is not defined'
    bpy.utils.register_class(MET_OT_AddVolume)
    auto_load.init()
    auto_load.register()
    bpy.types.Mesh.me_actor = bpy.props.PointerProperty(type=MET_PG_MESH_Actor)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

# =============================================================================
def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    del bpy.types.Mesh.me_actor
    auto_load.unregister()
    bpy.utils.unregister_class(MET_OT_AddVolume)
