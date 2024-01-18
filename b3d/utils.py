import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

# =============================================================================
# HELPERS
# -----------------------------------------------------------------------------
# =============================================================================
def set_active(obj: bpy.types.Object) -> None:
    active = bpy.context.active_object
    if active: active.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

# =============================================================================
def set_obj_mode(obj: bpy.types.Object, m = 'OBJECT') -> None:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode=m)

# =============================================================================
def set_obj_selectable(obj: bpy.types.Object, select: bool) -> None:
    obj.hide_select = not select

# =============================================================================
def select_obj(obj: bpy.types.Object):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

# =============================================================================
def deselect_all() -> None:
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

# =============================================================================
def add_obj_to_scene(obj: bpy.types.Object, collection: str = None) -> None:
    if collection is not None:
        c = bpy.context.blend_data.collections.get(collection)
        if c == None:
            c = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(c)
        c.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)

# =============================================================================
def new_object(name: str, data: bpy.types.ID, collection: str = None, parent: bpy.types.Object = None) -> None:
    obj = bpy.data.objects.new(name, data)
    add_obj_to_scene(obj, collection)
    if(parent): obj.parent = parent
    set_active(obj)
    return obj

# =============================================================================
def remove_object(obj: bpy.types.Object) -> None:
    bpy.data.objects.remove(obj)

# =============================================================================
def copy_object(obj: bpy.types.Object) -> bpy.types.Object:
    copy = obj.copy()
    copy.data = obj.data.copy()
    add_obj_to_scene(copy)
    return copy

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
def remove_mesh(mesh: bpy.types.Mesh) -> None:
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
def set_mesh(obj: bpy.types.Object, mesh: bpy.types.Mesh) -> None:
    old_mesh = obj.data
    obj.data = mesh
    remove_mesh(old_mesh)

# =============================================================================
# https://blender.stackexchange.com/questions/50160/scripting-low-level-join-meshes-elements-hopefully-with-bmesh
def join_meshes(meshes: list[bpy.types.Mesh]) -> None:
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
#https://blender.stackexchange.com/questions/127603/how-to-specify-nurbs-path-vertices-in-python
def create_curve(num_points : int = 3, step: int = 1, dir : tuple[float, float, float] = (1, 0, 0)) -> bpy.types.Curve:
    curve = bpy.data.curves.new('CURVE', 'CURVE')
    path = curve.splines.new('NURBS')
    curve.dimensions = '3D'
    points = []
    for k in range(num_points):
        p = Vector(dir) * Vector((1, 1, 1)) * step * k
        points.append((*p, 1))
    path.points.add(len(points)-1)
    for k, point in enumerate(points):
        path.points[k].co = point
    path.use_endpoint_u = True
    return curve

# =============================================================================
def transform(mesh: bpy.types.Mesh, transforms: list[Matrix]) -> None:
    mode = bpy.context.mode
    bm = bmesh.new()

    if mode == 'OBJECT':
        bm.from_mesh(mesh)
    elif mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(mesh)

    for m in transforms:
        bmesh.ops.transform(bm, matrix=m, verts=bm.verts)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

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
# https://blender.stackexchange.com/questions/159538/how-to-apply-all-transformations-to-an-object-at-low-level
def apply_all_transforms(obj: bpy.types.Object) -> None:
    mb = obj.matrix_basis
    if hasattr(obj.data, 'transform'):
        obj.data.transform(mb)
    for c in obj.children:
        c.matrix_local = mb @ c.matrix_local
        
    obj.matrix_basis.identity()

# =============================================================================
# HANDLER CALLBACK
# -----------------------------------------------------------------------------
# =============================================================================
def add_callback(handler, function) -> None:
    for fn in handler:
        if fn.__name__ == function.__name__: return
    handler.append(function)

# =============================================================================
def remove_callback(handler, function) -> None:
    for fn in handler:
        if fn.__name__ == function.__name__:
            handler.remove(fn)

