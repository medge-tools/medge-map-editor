bl_info = {
    'name' : 'Map Editor',
    'author' : 'Tariq Bakhtali (didibib)',
    'description' : '',
    'blender' : (3, 4, 0),
    'version' : (1, 0, 0),
    'location' : '',
    'warning' : '',
    'category' : 'MEdge Tools'
}


# -----------------------------------------------------------------------------
from bpy.utils import register_class

from . import auto_load
from .map_editor.gui import MET_PT_map_editor, MET_PT_actors, MET_PT_selected_actor, MET_PT_measurements


# -----------------------------------------------------------------------------
def register():
    register_class(MET_PT_map_editor)
    register_class(MET_PT_selected_actor)
    register_class(MET_PT_actors)
    register_class(MET_PT_measurements)

    auto_load.init()
    auto_load.register()


# -----------------------------------------------------------------------------
def unregister():
    auto_load.unregister()
    