import bpy
from mathutils import Vector, Matrix
from ..t3d.scene import ActorType
from . import utils
from . import props


COLLECTION_WIDGET = 'WIDGET'
# =============================================================================
# CREATORS
# -----------------------------------------------------------------------------
# =============================================================================
def get_me_actor(obj: bpy.types.Object) -> props.ME_OBJECT_PG_Actor:
    return obj.me_actor

# =============================================================================
def new_actor(actor_type: ActorType, object_type = 'MESH', data = None) -> bpy.types.Object:
    match(object_type):
        case 'MESH':
            obj = utils.new_object('ACTOR', create_cube())
        case 'CURVE':
            obj = utils.new_object('ACTOR', create_curve())
    obj.location = bpy.context.scene.cursor.location
    me_actor = get_me_actor(obj)
    me_actor.type = actor_type
    if data is not None:
        utils.set_mesh(obj, data)
    return obj

# =============================================================================
def cleanup_widgets():
    collection = bpy.context.blend_data.collections.get(COLLECTION_WIDGET)
    if collection is not None:
        for child in collection.objects:
            if child.parent != None: continue
            bpy.data.objects.remove(child)


# =============================================================================
def curve_to_mesh(obj : bpy.types.Object) -> bpy.types.Object:
    if obj.type != 'CURVE': return None
    
    mesh = bpy.data.meshes.new_from_object(obj)
    new_obj = new_actor(ActorType.STATICMESH, data=mesh)
    new_obj.matrix_world = obj.matrix_world
    props.copy_me_actor(obj.me_actor, new_obj.me_actor)
    return new_obj

# =============================================================================
def create_cube(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Mesh:
    verts = [
        Vector((-1 * scale[0], -1 * scale[1], -1 * scale[2])),
        Vector((-1 * scale[0],  1 * scale[1], -1 * scale[2])),
        Vector(( 1 * scale[0],  1 * scale[1], -1 * scale[2])),
        Vector(( 1 * scale[0], -1 * scale[1], -1 * scale[2])),
        Vector((-1 * scale[0], -1 * scale[1],  1 * scale[2])),
        Vector((-1 * scale[0],  1 * scale[1],  1 * scale[2])),
        Vector(( 1 * scale[0],  1 * scale[1],  1 * scale[2])),
        Vector(( 1 * scale[0], -1 * scale[1],  1 * scale[2])),
    ]
    faces = [
        (0, 1, 2, 3),
        (7, 6, 5, 4),
        (4, 5, 1, 0),
        (7, 4, 0, 3),
        (6, 7, 3, 2),
        (5, 6, 2, 1),
    ]
    return utils.create_mesh(verts, [], faces, 'CUBE')

# =============================================================================
def create_arrow(scale: tuple[float, float] = (1, 1)) -> bpy.types.Mesh:
    verts = [
        Vector((-1 * scale[0],  0.4 * scale[1], 0)),
        Vector(( 0 * scale[0],  0.4 * scale[1], 0)),
        Vector(( 0 * scale[0],  1   * scale[1], 0)), 
        Vector(( 1 * scale[0],  0   * scale[1], 0)), 
        Vector(( 0 * scale[0], -1   * scale[1], 0)), 
        Vector(( 0 * scale[0], -0.4 * scale[1], 0)),
        Vector((-1 * scale[0], -0.4 * scale[1], 0)),
    ]
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 0),
    ]
    return utils.create_mesh(verts, edges, [], 'ARROW')

# =============================================================================
def create_flag(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Mesh:
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
    return utils.create_mesh(verts, [], faces, 'FLAG')

# =============================================================================
def create_springboard(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Mesh:
    small_step = create_cube((.24, .48, .32))
    utils.transform(small_step, [Matrix.Translation((0.24, .72, .32))])
    big_step = create_cube((.51, .8, .72))
    utils.transform(big_step, [Matrix.Translation((1.82, .8, .72))])
    return utils.join_meshes([small_step, big_step])

def create_zipline() -> bpy.types.Object:
    zipline = new_actor(ActorType.STATICMESH, 'CURVE')
    utils.set_mesh(zipline, utils.create_curve(step=8))
    me_actor = get_me_actor(zipline)
    me_actor.static_mesh_name = 'Zipline'
    me_actor.ase_export = True
    zipline.data.bevel_depth = 0.04
    zipline.data.use_fill_caps = True
    return zipline