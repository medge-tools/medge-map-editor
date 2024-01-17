import bpy
import bmesh
from mathutils import Matrix, Euler
from . import props

COLLECTION_WIDGET = 'WIDGET'
# =============================================================================
# HELPERS
# -----------------------------------------------------------------------------
# =============================================================================
def get_me_actor(obj: bpy.types.Object) -> props.ME_OBJECT_PG_Actor:
    return obj.me_actor

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
def new_object(name: str, data : bpy.types.ID, collection: str = None, parent: bpy.types.Object = None):
    obj = bpy.data.objects.new(name, data)
    add_obj_to_collection(obj, collection)
    if(parent): obj.parent = parent
    set_active(obj)
    return obj

# =============================================================================
def cleanup_widgets():
    collection = bpy.context.blend_data.collections.get(COLLECTION_WIDGET)
    if collection is not None:
        for child in collection.objects:
            if child.parent != None: continue
            bpy.data.objects.remove(child)

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
def remove_object(obj : bpy.types.Object):
    bpy.data.objects.remove(obj)

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
def deselect_all():
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

# =============================================================================
# HANDLER CALLBACK
# -----------------------------------------------------------------------------
# =============================================================================
def add_callback(handler, function):
    for fn in handler:
        if fn.__name__ == function.__name__: return
    handler.append(function)

# =============================================================================
def remove_callback(handler, function):
    for fn in handler:
        if fn.__name__ == function.__name__:
            handler.remove(fn)

# =============================================================================
def on_depsgraph_update_post(scene : bpy.types.Scene, depsgraph : bpy.types.Depsgraph):
    for obj in scene.objects:
        me_actor = get_me_actor(obj)
        if me_actor is None: continue
        if me_actor.static_mesh_name != obj.name:
            me_actor.static_mesh_name = obj.name