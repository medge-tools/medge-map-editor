from bpy.types import Operator, Context

from ..io.t3d.scene import ActorType
from .props         import ActorTypeEnumProperty, new_actor, create_skydome, cleanup_widgets


# -----------------------------------------------------------------------------
class MET_OT_AddActor(Operator):
    bl_idname  = 'medge_map_editor.add_actor'
    bl_label   = 'Add Actor'
    bl_options = {'UNDO'}

    type: ActorTypeEnumProperty()


    def execute(self, _context:Context):
        new_actor(ActorType[self.type])
        
        return {'FINISHED'}


# -----------------------------------------------------------------------------
class MET_OT_AddSkydome(Operator):
    bl_idname  = 'medge_map_editor.add_skydome'
    bl_label   = 'Add Skydome'
    bl_options = {'UNDO'}


    def execute(self, _context:Context):
        create_skydome()

        return {'FINISHED'}


# -----------------------------------------------------------------------------
class MET_OT_CleanupWidgets(Operator):
    bl_idname  = 'medge_map_editor.cleanup_gizmos'
    bl_label   = 'Cleanup Gizmos'
    bl_options = {'UNDO'}


    def execute(self, _context:Context):
        cleanup_widgets()

        return {'FINISHED'}