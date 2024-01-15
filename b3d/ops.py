import bpy
from . import utils
from . import props
from . import creator

# =============================================================================
class ME_OT_AddActor(bpy.types.Operator):
    bl_idname = 'met.add_actor'
    bl_label = 'Add Actor'
    bl_options = {'UNDO'}

    type: props.ActorTypeProperty()

    def execute(self, context : bpy.types.Context):
        creator.new_actor(self.type)
        return {'FINISHED'}

# =============================================================================
class ME_OT_AddPlaceholder(bpy.types.Operator):
    bl_idname = 'met.add_placeholder'
    bl_label = 'Add Placeholder'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return utils.get_me_actor(obj).static_mesh_prefab

    def execute(self, context : bpy.types.Context):
        obj = context.active_object
        me_actor = utils.get_me_actor(obj)
        me_actor.add_static_mesh(context)
        return {'FINISHED'}
    
# =============================================================================
class ME_OT_CleanupGizmos(bpy.types.Operator):
    bl_idname = 'met.cleanup_gizmos'
    bl_label = 'Cleanup Gizmos'
    bl_options = {'UNDO'}

    def execute(self, context: bpy.types.Context):
        utils.cleanup_widgets()
        return {'FINISHED'}
