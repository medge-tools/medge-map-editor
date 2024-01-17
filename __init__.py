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
from .t3d.exporter import ME_OT_Exporter
from .b3d.props import *
from .b3d.gui import *
from . import auto_load

# =============================================================================
def menu_func_export(self, context):
    self.layout.operator(ME_OT_Exporter.bl_idname, text='UDK T3D (.t3d)')

# =============================================================================
def register():
    auto_load.init()
    auto_load.register()
    bpy.types.Object.me_actor = bpy.props.PointerProperty(type=ME_OBJECT_PG_Actor)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    utils.add_callback(depsgraph_update_post, utils.on_depsgraph_update_post)

# =============================================================================
def unregister():
    utils.remove_callback(depsgraph_update_post, utils.on_depsgraph_update_post)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    del bpy.types.Object.me_actor
    auto_load.unregister()
