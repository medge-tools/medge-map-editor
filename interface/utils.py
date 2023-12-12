import bpy
from mathutils import Matrix
from ..scene.types import ActorType

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
        (-1,   .5, 0),
        ( 0,   .5, 0),
        ( 0,  1.5, 0), 
        ( 2,  0  , 0), 
        ( 0, -1.5, 0), 
        ( 0,  -.5, 0),
        (-1,  -.5, 0)
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
    obj = create_mesh_object(verts, edges, [], 'Direction', 'Gizmo')
    set_obj_selectable(obj, True)
    return obj

# =============================================================================
def add_brush(type: ActorType, 
              scale: tuple[float, float, float] = (1, 1, 1), 
              name: str = "Actor") -> bpy.types.Object:
    verts = [
        (-1.0, -1.0, -1.0),
        (-1.0,  1.0, -1.0),
        ( 1.0,  1.0, -1.0),
        ( 1.0, -1.0, -1.0),
        (-1.0, -1.0,  1.0),
        (-1.0,  1.0,  1.0),
        ( 1.0,  1.0,  1.0),
        ( 1.0, -1.0,  1.0),
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

def mirror_quaternion_x_axis(obj: bpy.types.Object):
    """
    Rotation mode: 
        https://gist.github.com/behreajj/2dbb6fb7cee78c167cd85085e67bcdf6
    Mirror rotation: 
        https://www.gamedev.net/forums/topic/599824-mirroring-a-quaternion-against-the-yz-plane/
    """
    prev_rot_mode = obj.rotation_mode
    obj.rotation_mode = 'QUATERNION'
    q = obj.rotation_quaternion
    q.x *= -1
    q.w *= -1
    obj.rotation_quaternion = q
    obj.rotation_mode = prev_rot_mode

def apply_scale(obj: bpy.types.Object):
    """
    Apply transforms without using operators:
        https://blender.stackexchange.com/a/283228
    """
    mlocal = obj.matrix_local
    _, _, mscale = mlocal.decompose()
    mscale = Matrix.LocRotScale(None, None, mscale)
    obj.data.transform(mscale)
    obj.scale = 1, 1, 1

def apply_all_transforms(obj: bpy.types.Object):
    mat = obj.matrix_local
    obj.data.transform(mat)
    obj.matrix_local = Matrix()
    # the above line is equivalent to:
    # C.object.location = 0, 0, 0
    # C.object.rotation_euler = 0,

def deepcopy(obj: bpy.types.Object) -> bpy.types.Object:
    o = obj.copy()
    o.data = obj.data.copy()
    return o