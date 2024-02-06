import bpy
from bpy.types import Operator
from . import props
from . import scene_utils as scene

# =============================================================================
# ACTOR
# -----------------------------------------------------------------------------
# =============================================================================
class MET_OT_AddActor(Operator):
    bl_idname   = 'medge_map_editor.add_actor'
    bl_label    = 'Add Actor'
    bl_options  = {'UNDO'}

    type: props.ActorTypeProperty()

    def execute(self, context : bpy.types.Context):
        scene.new_actor(self.type)
        return {'FINISHED'}

# =============================================================================
# HELPERS
# -----------------------------------------------------------------------------
# =============================================================================
class MET_OT_CleanupWidgets(Operator):
    bl_idname   = 'medge_map_editor.cleanup_gizmos'
    bl_label    = 'Cleanup Gizmos'
    bl_options  = {'UNDO'}

    def execute(self, context: bpy.types.Context):
        scene.cleanup_widgets()
        return {'FINISHED'}