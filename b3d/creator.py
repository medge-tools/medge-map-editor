from .utils import *
from mathutils import Vector

# =============================================================================
# CREATORS
# -----------------------------------------------------------------------------
# =============================================================================
def new_actor(type: ActorType) -> bpy.types.Object:
    obj = new_object('ACTOR', create_cube())
    obj.location = bpy.context.scene.cursor.location
    me_actor = get_me_actor(obj)
    me_actor.type = type
    return obj
    
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
    return create_mesh(verts, [], faces, 'CUBE')

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
    return create_mesh(verts, edges, [], 'ARROW')

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
    return create_mesh(verts, [], faces, 'FLAG')

# =============================================================================
def create_springboard(scale: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Mesh:
    small_step = create_cube((.24, .48, .32))
    transform(small_step, [Matrix.Translation((0.24, .72, .32))])
    big_step = create_cube((.51, .8, .72))
    transform(big_step, [Matrix.Translation((1.82, .8, .72))])
    return join_meshes([small_step, big_step])

# =============================================================================
#https://blender.stackexchange.com/questions/127603/how-to-specify-nurbs-path-vertices-in-python
def create_curve(step: int = 1) -> bpy.types.Curve:
    curve = bpy.data.curves.new('CURVE', 'CURVE')
    path = curve.splines.new('NURBS')
    curve.dimensions = '3D'
    points = [(0, 0, 0, 1), (1 * step, 0, 0, 1), (2 * step, 0, 0, 1)]
    path.points.add(len(points)-1)
    for k, point in enumerate(points):
        path.points[k].co = point
    path.use_endpoint_u = True
    return curve
