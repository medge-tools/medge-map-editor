import bpy
import bmesh
from mathutils import Matrix, Vector, Euler
from ..t3d.scene import ActorType

COLLECTION_WIDGET = 'WIDGET'

# =============================================================================
# HELPERS
# -----------------------------------------------------------------------------
# =============================================================================
def get_me_actor(obj: bpy.types.Object):
    return obj.me_actor

# =============================================================================
def cleanup_widgets():
    collection = bpy.context.blend_data.collections.get(COLLECTION_WIDGET)
    if collection is not None:
        for child in collection.objects:
            if child.parent != None: continue
            bpy.data.objects.remove(child)

# =============================================================================
def set_active(obj: bpy.types.Object):
    active = bpy.context.active_object
    if active: active.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

# =============================================================================
def set_obj_mode(obj: bpy.types.Object, m = 'OBJECT'):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode=m)

# =============================================================================
def set_obj_selectable(obj: bpy.types.Object, select: bool):
    obj.hide_select = not select

# =============================================================================
def add_obj_to_collection(obj: bpy.types.Object, collection: str = None):
    if collection is not None:
        c = bpy.context.blend_data.collections.get(collection)
        if c == None:
            c = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(c)
        c.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)

# =============================================================================
def transform(mesh: bpy.types.Mesh, transforms: list[Matrix]):
    mode = bpy.context.mode
    bm = bmesh.new()

    if mode == 'OBJECT':
        bm.from_mesh(mesh)
    elif mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(mesh)

    for m in transforms:
        bmesh.ops.transform(bm, matrix=m, verts=bm.verts)

    if mode == 'OBJECT':
        bm.to_mesh(mesh)
    elif mode == 'EDIT_MESH':
        bmesh.update_edit_mesh(mesh)  
    bm.free()

# =============================================================================
# Rotation mode: 
#   https://gist.github.com/behreajj/2dbb6fb7cee78c167cd85085e67bcdf6
# Mirror rotation: 
#   https://www.gamedev.net/forums/topic/# 599824-mirroring-a-quaternion-against-the-yz-plane/
def get_rotation_mirrored_x_axis(obj: bpy.types.Object) -> Euler:
    prev_rot_mode = obj.rotation_mode
    obj.rotation_mode = 'QUATERNION'
    q = obj.rotation_quaternion.copy()
    q.x *= -1
    q.w *= -1
    obj.rotation_mode = prev_rot_mode
    return q.to_euler()

# =============================================================================
def remove_mesh(mesh: bpy.types.Mesh):
    # Extra test because this can crash Blender if not done correctly.
    result = False
    if mesh and mesh.users == 0: 
        try:
            mesh.user_clear()
            can_continue = True
        except: can_continue = False
        if can_continue == True:
            try:
                bpy.data.meshes.remove(mesh)
                result = True
            except: result = False
    else: result = True
    return result

# =============================================================================
# https://blenderartists.org/t/how-to-replace-a-mesh/596225/4
def set_mesh(obj: bpy.types.Object, mesh: bpy.types.Mesh):
    old_mesh = obj.data
    obj.data = mesh
    remove_mesh(old_mesh)

# =============================================================================
# CREATORS
# -----------------------------------------------------------------------------
# =============================================================================
def new_object(name: str, data : bpy.types.ID, collection: str = None):
    obj = bpy.data.objects.new(name, data)
    add_obj_to_collection(obj, collection)
    set_active(obj)
    return obj

# =============================================================================
def new_actor(type: ActorType):
    obj = new_object('ACTOR', create_cube())
    obj.location = bpy.context.scene.cursor.location
    actor = get_me_actor(obj)
    actor.type = type
    
# =============================================================================
# https://blender.stackexchange.com/questions/50160/scripting-low-level-join-meshes-elements-hopefully-with-bmesh
def join_meshes(meshes: list[bpy.types.Mesh]):
    bm = bmesh.new()
    bm_verts = bm.verts.new
    bm_faces = bm.faces.new
    bm_edges = bm.edges.new

    for mesh in meshes:
        bm_to_add = bmesh.new()
        bm_to_add.from_mesh(mesh)
        offset = len(bm.verts)

        for v in bm_to_add.verts:
            bm_verts(v.co)

        bm.verts.index_update()
        bm.verts.ensure_lookup_table()

        if bm_to_add.faces:
            for face in bm_to_add.faces:
                bm_faces(tuple(bm.verts[i.index+offset] for i in face.verts))
            bm.faces.index_update()

        if bm_to_add.edges:
            for edge in bm_to_add.edges:
                edge_seq = tuple(bm.verts[i.index+offset] for i in edge.verts)
                try: bm_edges(edge_seq)
                except ValueError: # edge exists!
                    pass
            bm.edges.index_update()
        bm_to_add.free()

    bm.normal_update()
    bm.to_mesh(meshes[0])
    bm.free()
    return meshes[0]

# =============================================================================
def create_mesh(
        verts: list[tuple[float, float, float]], 
        edges: list[tuple[int, int]], 
        faces: list[tuple[int, ...]], 
        name: str) -> bpy.types.Mesh:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    return mesh

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
