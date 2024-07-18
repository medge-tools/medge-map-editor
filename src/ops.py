import bpy
import bmesh
from bpy.types import Operator, Context

from .t3d.scene import ActorType
from .props     import ActorTypeEnumProperty, new_actor, cleanup_widgets, get_actor_prop


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
        bpy.ops.mesh.primitive_uv_sphere_add()
        obj = bpy.context.object
        obj.name = 'Skydome'

        actor = get_actor_prop(obj)
        actor.type = ActorType.STATIC_MESH.name
        
        sm = actor.static_mesh
        sm.use_prefab = True

        # Remove bottom half
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        for v in bm.verts:
            if v.co.z < 0:
                bm.verts.remove(v)

        bm.to_mesh(obj.data)
        bm.free()

        return {'FINISHED'}
    

# -----------------------------------------------------------------------------
class MET_OT_CleanupWidgets(Operator):
    bl_idname  = 'medge_map_editor.cleanup_gizmos'
    bl_label   = 'Cleanup Gizmos'
    bl_options = {'UNDO'}


    def execute(self, _context:Context):
        cleanup_widgets()

        return {'FINISHED'}