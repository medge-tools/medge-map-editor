import bpy
from mathutils import Vector, Matrix
from ..io.t3d.scene import ActorType
from . import b3d_utils
from . import props

COLLECTION_WIDGETS = 'WIDGET'
DEFAULT_PACKAGE = 'MyPackage'


# =============================================================================
# HELPERS
# -----------------------------------------------------------------------------
# =============================================================================
def get_me_actor(obj: bpy.types.Object) -> props.ME_OBJECT_PG_Actor:
    return obj.me_actor

# =============================================================================
def cleanup_widgets():
    collection = bpy.context.blend_data.collections.get(COLLECTION_WIDGETS)
    if collection is not None:
        for child in collection.objects:
            if child.parent != None: continue
            bpy.data.objects.remove(child)

# =============================================================================
# CREATORS
# -----------------------------------------------------------------------------
# =============================================================================
def new_actor(actor_type: ActorType, object_type = 'MESH', data = None) -> bpy.types.Object:
    match(object_type):
        case 'MESH':
            obj = b3d_utils.new_object('ACTOR', b3d_utils.create_cube())
        case 'CURVE':
            obj = b3d_utils.new_object('ACTOR', b3d_utils.create_curve())
    obj.location = bpy.context.scene.cursor.location
    me_actor = get_me_actor(obj)
    me_actor.type = actor_type
    if data is not None:
        b3d_utils.set_mesh(obj, data)
    return obj


# =============================================================================
def create_player_start(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Mesh:
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


# =============================================================================
def create_springboard(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Mesh:
    small_step = b3d_utils.create_cube((.24, .48, .32))
    b3d_utils.transform(small_step, [Matrix.Translation((0.24, .72, .32))])
    big_step = b3d_utils.create_cube((.51, .8, .72))
    b3d_utils.transform(big_step, [Matrix.Translation((1.82, .8, .72))])
    return b3d_utils.join_meshes([small_step, big_step])


# =============================================================================
def create_zipline() -> bpy.types.Object:
    zipline = new_actor(ActorType.STATIC_MESH, 'CURVE')
    b3d_utils.set_mesh(zipline, b3d_utils.create_curve(step=8))
    zipline.name= 'Zipline'
    zipline.data.bevel_depth = 0.04
    zipline.data.use_fill_caps = True
    sm = get_me_actor(zipline).static_mesh
    sm.ase_export = True
    return zipline


# =============================================================================
def create_checkpoint() -> bpy.types.Object:
    return b3d_utils.create_cylinder(make_faces=False)