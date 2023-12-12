import bpy
import bmesh
from mathutils import Matrix, Vector
from ..scene.types import ActorType

COLL_GIZMO = 'GIZMOS'

# =============================================================================
def get_me_actor(obj: bpy.types.Object):
    return obj.me_actor

# =============================================================================
def set_active(obj: bpy.types.Object):
    bpy.context.view_layer.objects.active = obj

# =============================================================================
def set_obj_mode(obj: bpy.types.Object, m = 'OBJECT'):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode=m)

# =============================================================================
def set_obj_selectable(obj: bpy.types.Object, select: bool):
    obj.hide_select = select

# =============================================================================
def create_mesh_object(
        verts: list[tuple[float, float, float]], 
        edges: list[tuple[int, int]], 
        faces: list[tuple[int, ...]], 
        name: str,
        collection: str = None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)
    if collection is not None:
        c = bpy.context.blend_data.collections.get(collection)
        if c == None:
            c = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(c)
        c.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
    return obj

# =============================================================================
def add_arrow(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Object:
    verts = [
        Vector((-1,   .5, 0)),
        Vector(( 0,   .5, 0)),
        Vector(( 0,  1.5, 0)), 
        Vector(( 2,  0  , 0)), 
        Vector(( 0, -1.5, 0)), 
        Vector(( 0,  -.5, 0)),
        Vector((-1,  -.5, 0))
    ]
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 0)
    ]
    obj = create_mesh_object(verts, edges, [], 'Direction', COLL_GIZMO)
    obj.scale = scale
    set_obj_selectable(obj, True)
    return obj

# =============================================================================
def add_brush(type: ActorType, 
              scale: tuple[float, float, float] = (1, 1, 1), 
              name: str = "Actor") -> bpy.types.Object:
    verts = [
        Vector((-1.0, -1.0, -1.0)),
        Vector((-1.0,  1.0, -1.0)),
        Vector(( 1.0,  1.0, -1.0)),
        Vector(( 1.0, -1.0, -1.0)),
        Vector((-1.0, -1.0,  1.0)),
        Vector((-1.0,  1.0,  1.0)),
        Vector(( 1.0,  1.0,  1.0)),
        Vector(( 1.0, -1.0,  1.0)),
    ]
    faces = [
        (0, 1, 2, 3),
        (7, 6, 5, 4),
        (4, 5, 1, 0),
        (7, 4, 0, 3),
        (6, 7, 3, 2),
        (5, 6, 2, 1),
    ]
    obj = create_mesh_object(verts, [], faces, name)
    set_active(obj)
    obj.me_actor.type = type
    obj.scale = scale
    return obj

# =============================================================================
def cleanup_gizmos():
    coll = bpy.context.blend_data.collections.get(COLL_GIZMO)
    if coll is not None:
        for child in coll.objects:
            bpy.data.objects.remove(child)

# =============================================================================
def transform(obj: bpy.types.Object, transforms: list[Matrix]):
    set_obj_mode(obj, 'OBJECT')
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    for m in transforms:
        bmesh.ops.transform(bm, matrix=m, space=obj.matrix_local, verts=bm.verts)

    bm.to_mesh(obj.data)
    bm.free()

# =============================================================================
# Rotation mode: 
#   https://gist.github.com/behreajj/2dbb6fb7cee78c167cd85085e67bcdf6
# Mirror rotation: 
#   https://www.gamedev.net/forums/topic/# 599824-mirroring-a-quaternion-against-the-yz-plane/
def mirror_quaternion_x_axis(obj: bpy.types.Object):
    prev_rot_mode = obj.rotation_mode
    obj.rotation_mode = 'QUATERNION'
    q = obj.rotation_quaternion
    q.x *= -1
    q.w *= -1
    obj.rotation_quaternion = q
    obj.rotation_mode = prev_rot_mode

# =============================================================================
def deepcopy(obj: bpy.types.Object) -> bpy.types.Object:
    o = obj.copy()
    o.data = obj.data.copy()
    return o