import bpy
import bmesh
from bpy.types import Object, Scene, Depsgraph
from mathutils import Vector, Matrix

from ..io.t3d.scene import ActorType
from .. import b3d_utils
from .props import *

COLLECTION_WIDGETS = 'WIDGET'
DEFAULT_PACKAGE = 'MyPackage'


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def get_actor(obj: Object) -> MET_OBJECT_PG_Actor:
    return obj.medge_actor
    

# -----------------------------------------------------------------------------
def cleanup_widgets():
    collection = bpy.context.blend_data.collections.get(COLLECTION_WIDGETS)
    if collection is not None:
        for child in collection.objects:
            if child.parent != None: continue
            bpy.data.objects.remove(child)

# -----------------------------------------------------------------------------
# CREATORS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def new_actor(actor_type: ActorType, object_type = 'MESH', data = None):
    match(object_type):
        case 'MESH':
            obj = b3d_utils.new_object('ACTOR', b3d_utils.create_cube())
        case 'CURVE':
            obj = b3d_utils.new_object('ACTOR', b3d_utils.create_curve())
    obj.location = bpy.context.scene.cursor.location
    me_actor = get_actor(obj)
    me_actor.type = actor_type
    if data is not None:
        b3d_utils.set_mesh(obj, data)
    return obj


# -----------------------------------------------------------------------------
def create_player_start(scale: tuple[float, float, float] = (1, 1, 1)):
    verts = [
        Vector((-0.5        * scale[0], -1 * scale[1], 0)),
        Vector((-0.5        * scale[0],  1 * scale[1], 0)),
        Vector(( 0.866025   * scale[0],  0           , 0)),
        Vector((-0.5        * scale[0],  0           , 1 * scale[2])),
    ]
    faces = [
        (2, 1, 0),
        (0, 1, 3),
        (1, 2, 3),
        (0, 3, 2)
    ]
    return b3d_utils.create_mesh(verts, [], faces, 'PLAYER START')


# -----------------------------------------------------------------------------
def create_springboard(scale: tuple[float, float, float] = (1, 1, 1)):
    small_step = b3d_utils.create_cube((.24, .48, .32))
    b3d_utils.transform(small_step, [Matrix.Translation((0.24, .72, .32))])
    big_step = b3d_utils.create_cube((.51, .8, .72))
    b3d_utils.transform(big_step, [Matrix.Translation((1.82, .8, .72))])
    return b3d_utils.join_meshes([small_step, big_step])


# -----------------------------------------------------------------------------
def create_zipline():
    zipline = new_actor(ActorType.STATIC_MESH, 'CURVE')
    b3d_utils.set_mesh(zipline, b3d_utils.create_curve(step=8, dir=(1, 0, 0)))
    zipline.name= 'Zipline'
    zipline.data.bevel_depth = 0.04
    zipline.data.use_fill_caps = True
    sm = get_actor(zipline).static_mesh
    sm.ase_export = True
    return zipline


# -----------------------------------------------------------------------------
def create_checkpoint():
    return b3d_utils.create_cylinder(make_faces=False)


# -----------------------------------------------------------------------------
def create_skydome():
    bpy.ops.mesh.primitive_uv_sphere_add()
    obj = bpy.context.object
    obj.name = 'Skydome'

    actor = get_actor(obj)
    actor.type = ActorType.STATIC_MESH
    
    sm = actor.static_mesh
    sm.use_prefab = True

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    for v in bm.verts:
        if v.co.z < 0:
            bm.verts.remove(v)

    bm.to_mesh(obj.data)
    bm.free()

# -----------------------------------------------------------------------------
# CALLBACKS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def on_depsgraph_update_post(scene: Scene, depsgraph: Depsgraph):
    for obj in scene.objects:

        actor = get_actor(obj)
        
        match(obj.type):
            case 'LIGHT' | 'CURVE': 
                actor.user_editable = False

        match(actor.type):
            case ActorType.ZIPLINE:
                actor.zipline.update_bounds()