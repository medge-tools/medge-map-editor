import bpy
from . import props
from . import medge_tools
from . import utils
# =============================================================================
class ME_OT_AddActor(bpy.types.Operator):
    bl_idname = 'met.add_actor'
    bl_label = 'Add Actor'
    bl_options = {'UNDO'}

    type: props.ActorTypeProperty()

    def execute(self, context : bpy.types.Context):
        medge_tools.new_actor(self.type)
        return {'FINISHED'}

# =============================================================================
class ME_OT_CleanupWidgets(bpy.types.Operator):
    bl_idname = 'met.cleanup_gizmos'
    bl_label = 'Cleanup Gizmos'
    bl_options = {'UNDO'}

    def execute(self, context: bpy.types.Context):
        medge_tools.cleanup_widgets()
        return {'FINISHED'}
