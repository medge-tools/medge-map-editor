import bpy
import bmesh
from bpy.types import Object
from mathutils import Vector, Matrix, Euler

import math
import numpy as np

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def set_active(obj: Object) -> None:
    active = bpy.context.active_object
    if active: active.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


# -----------------------------------------------------------------------------
def set_object_mode(obj: Object, m = 'OBJECT') -> None:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode=m)


# -----------------------------------------------------------------------------
def set_object_selectable(obj: Object, select: bool) -> None:
    obj.hide_select = not select


# -----------------------------------------------------------------------------
def select_object(obj: Object):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


# -----------------------------------------------------------------------------
def select_all_objects() -> None:
    for obj in bpy.context.scene.objects:
        select_object(obj)


# -----------------------------------------------------------------------------
def deselect_all_objects() -> None:
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


# -----------------------------------------------------------------------------
def link_to_scene(obj: Object, collection: str = None) -> None:
    """If the collection == None, then the object will be linked to the root collection"""
    for uc in obj.users_collection:
        uc.objects.unlink(obj)

    if collection is not None:
        c = bpy.context.blend_data.collections.get(collection)
        if c == None:
            c = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(c)
        c.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)


# -----------------------------------------------------------------------------
def auto_gui_properties(data, layout: bpy.types.UILayout):
    for key in data.__annotations__.keys():
        layout.prop(data, key)


# -----------------------------------------------------------------------------
# HANDLER CALLBACK
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def add_callback(handler, function) -> None:
    for fn in handler:
        if fn.__name__ == function.__name__: return
    handler.append(function)


# -----------------------------------------------------------------------------
def remove_callback(handler, function) -> None:
    for fn in handler:
        if fn.__name__ == function.__name__:
            handler.remove(fn)


# -----------------------------------------------------------------------------
# SCENE
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def new_object(name: str, data: bpy.types.ID, collection: str = None, parent: bpy.types.Object = None) -> None:
    obj = bpy.data.objects.new(name, data)
    link_to_scene(obj, collection)
    if(parent): obj.parent = parent
    set_active(obj)
    return obj


# -----------------------------------------------------------------------------
def remove_object(obj: Object) -> None:
    bpy.data.objects.remove(obj)


# -----------------------------------------------------------------------------
def copy_object(obj: Object) -> bpy.types.Object:
    copy = obj.copy()
    copy.data = obj.data.copy()
    link_to_scene(copy)
    return copy


# -----------------------------------------------------------------------------
def create_mesh(
        verts: list[tuple[float, float, float]], 
        edges: list[tuple[int, int]], 
        faces: list[tuple[int, ...]], 
        name: str) -> bpy.types.Mesh:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    return mesh


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# https://blenderartists.org/t/how-to-replace-a-mesh/596225/4
def set_mesh(obj: Object, mesh: bpy.types.Mesh) -> None:
    old_mesh = obj.data
    obj.data = mesh
    remove_mesh(old_mesh)


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
def convert_to_mesh_in_place(obj: Object):
    set_active(obj)
    bpy.ops.object.convert(target='MESH') 


# -----------------------------------------------------------------------------
def convert_to_new_mesh(obj: Object) -> bpy.types.Object:
    mesh = bpy.data.meshes.new_from_object(obj)
    new_obj = new_object(obj.name, mesh)
    new_obj.matrix_world = obj.matrix_world 
    return new_obj


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# Rotation mode: 
#   https://gist.github.com/behreajj/2dbb6fb7cee78c167cd85085e67bcdf6
# Mirror rotation: 
#   https://www.gamedev.net/forums/topic/# 599824-mirroring-a-quaternion-against-the-yz-plane/
def get_rotation_mirrored_x_axis(obj: Object) -> Euler:
    prev_rot_mode = obj.rotation_mode
    obj.rotation_mode = 'QUATERNION'
    q = obj.rotation_quaternion.copy()
    q.x *= -1
    q.w *= -1
    obj.rotation_mode = prev_rot_mode
    return q.to_euler()


# -----------------------------------------------------------------------------
# https://blender.stackexchange.com/questions/159538/how-to-apply-all-transformations-to-an-object-at-low-level
def apply_all_transforms(obj: Object) -> None:
    mb = obj.matrix_basis
    if hasattr(obj.data, 'transform'):
        obj.data.transform(mb)
    for c in obj.children:
        c.matrix_local = mb @ c.matrix_local
        
    obj.matrix_basis.identity()


# -----------------------------------------------------------------------------
# https://blender.stackexchange.com/questions/9200/how-to-make-object-a-a-parent-of-object-b-via-blenders-python-api
def set_parent(child: Object, parent: Object, keep_world_location = True):
    child.parent = parent
    if keep_world_location:
        child.matrix_parent_inverse = parent.matrix_world.inverted()


# -----------------------------------------------------------------------------
# https://blender.stackexchange.com/questions/9200/how-to-make-object-a-a-parent-of-object-b-via-blenders-python-api
def unparent(obj: Object, keep_world_location = True):
    parented_wm = obj.matrix_world.copy()
    obj.parent = None
    if keep_world_location:
        obj.matrix_world = parented_wm


# -----------------------------------------------------------------------------
# CREATE
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
def circle(radius, 
           location, 
           angle_step = 10) -> list[tuple[float, float, float]]:
    (a, b, c) = location

    verts = []
    for angle in range(0, 360, angle_step):
        angle_radius = math.radians(angle)
        x = a + radius * math.cos(angle_radius)
        y = b + radius * math.sin(angle_radius)
        verts.append((x, y, c))
    # Adding the first vertex as last vertex to close the loop
    verts.append(verts[0])
    return verts


# -----------------------------------------------------------------------------
def create_cylinder(radius = 2, 
                    height = 2, 
                    row_height = 2, 
                    angle_step = 10, 
                    make_faces = True) -> bpy.types.Mesh:
    height += 1
    verts = []
    per_circle_verts = 0

    for z in np.arange(0, height, row_height):
        c = circle(radius, (0, 0, z), angle_step)
        per_circle_verts = len(c)
        verts += c

    rows = int(height / row_height)
    faces = []

    if make_faces:
        for row in range(0, rows - 1):
            for index in range(0, per_circle_verts - 1):
                v1 = index + (row * per_circle_verts)
                v2 = v1 + 1
                v3 = v1 + per_circle_verts
                v4 = v2 + per_circle_verts
                faces.append((v1, v3, v4, v2))

    return create_mesh(verts, [], faces, 'CYLINDER')


# -----------------------------------------------------------------------------
#https://blender.stackexchange.com/questions/127603/how-to-specify-nurbs-path-vertices-in-python
def create_curve(num_points = 3, 
                 step = 1, 
                 dir: tuple[float, float, float] = (1, 0, 0)) -> bpy.types.Curve:
    curve = bpy.data.curves.new('CURVE', 'CURVE')
    path = curve.splines.new('NURBS')
    curve.dimensions = '3D'
    path.points.add(num_points - 1)

    for k in range(num_points):
        p = Vector(dir) * Vector((1, 1, 1)) * step * k
        path.points[k].co = (*p, 1)

    path.use_endpoint_u = True
    return curve