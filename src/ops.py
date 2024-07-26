import bpy
import bmesh
from bpy.types import Operator, Context
from mathutils import Matrix

from ..         import b3d_utils
from .t3d.scene import ActorType
from .props     import ActorTypeEnumProperty, new_actor, cleanup_widgets, get_actor_prop


# -----------------------------------------------------------------------------
class MET_OT_add_actor(Operator):
    bl_idname  = 'medge_map_editor.add_actor'
    bl_label   = 'Add Actor'
    bl_options = {'UNDO'}

    type: ActorTypeEnumProperty()


    def execute(self, _context:Context):
        new_actor(ActorType[self.type])
        
        return {'FINISHED'}


# -----------------------------------------------------------------------------
class MET_OT_cleanup_widgets(Operator):
    bl_idname  = 'medge_map_editor.cleanup_gizmos'
    bl_label   = 'Cleanup Gizmos'
    bl_options = {'UNDO'}


    def execute(self, _context:Context):
        cleanup_widgets()

        return {'FINISHED'}
    

# -----------------------------------------------------------------------------
class MET_OT_add_skydome(Operator):
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
class MET_OT_add_springboard(Operator):
    bl_idname  = 'medge_map_editor.add_springboard'
    bl_label   = 'Add Springboard'
    bl_options = {'UNDO'}


    def execute(self, _context:Context):       
        # Get prefab 
        name = 'SpringBoardHigh_ColMesh'
        prefab = _context.scene.objects.get(name)
        
        if not prefab:
            coll = b3d_utils.new_collection('P_Gameplay.SpringBoard', True, 'GenericBrowser')

            prefab = b3d_utils.new_object(self.create_springboard(), name, coll)
            prefab.location = 12, 0, 0

        # Create instance
        obj = new_actor(ActorType.STATIC_MESH)

        actor = get_actor_prop(obj)
        sm = actor.get_static_mesh()
        sm.use_prefab = True
        sm.prefab = prefab

        return {'FINISHED'}
    
    
    def create_springboard(self):
        small_step = b3d_utils.create_cube((.48, .96, .62))
        b3d_utils.transform(small_step, [Matrix.Translation((.48, .96, .31))])

        big_step = b3d_utils.create_cube((1.02, 1.6, 1.42))
        b3d_utils.transform(big_step, [Matrix.Translation((1.82, .8, .72))])

        return b3d_utils.join_meshes([small_step, big_step])