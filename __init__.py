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
from bpy.app.handlers import depsgraph_update_post

from .io.t3d.exporter import MET_OT_T3D_Export
from .io.ase.exporter import MET_OT_ASE_Export
from .map_editor.props import *
from .map_editor.gui import *
from . import auto_load
from . import b3d_utils
from .map_editor import scene_utils


# -----------------------------------------------------------------------------
def register():
    auto_load.init()
    auto_load.register()


# -----------------------------------------------------------------------------
def unregister():
    auto_load.unregister()
    