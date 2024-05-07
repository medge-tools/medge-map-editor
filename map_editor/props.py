import bpy
import bmesh
from bpy.props        import EnumProperty, PointerProperty, CollectionProperty, BoolProperty, IntProperty, FloatVectorProperty, FloatProperty
from bpy.types        import Scene, Depsgraph, Object, Mesh, PropertyGroup, Context, UILayout
from bpy.app.handlers import depsgraph_update_post
from mathutils        import Vector, Matrix

import math
from typing    import Callable
from mathutils import Matrix, Vector, geometry

from ..io.t3d.scene import ActorType, TrackIndex
from ..             import b3d_utils

# ACTOR_DEFAULT_STATIC_MESH = {
#     ActorType.PLAYERSTART   : ('MyPackage', ''),
#     ActorType.BRUSH         : ('MyPackage', ''),
#     ActorType.LADDER        : ('P_Generic.Ladders', 'S_LadderSystem_01b'),
#     ActorType.PIPE          : ('P_Pipes.PipeSystem_03', 'S_PipeSystem_03h'),
#     ActorType.SWING         : ('P_RunnerObjects.SwingPole_01', 'S_SwingPole_01c'),
#     ActorType.ZIPLINE       : ('MyPackage', ''),
#     ActorType.SPRINGBOARD   : ('P_Gameplay.SpringBoard', 'SpringBoardHigh_layoutMesh'),
#     ActorType.STATICMESH    : ('MyPackage', ''),
# }

COLLECTION_WIDGETS = 'Widgets'
MY_PACKAGE = 'MyPackage'


# -----------------------------------------------------------------------------
# Scene Utils
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def cleanup_widgets():
    collection = bpy.context.blend_data.collections.get(COLLECTION_WIDGETS)
    if collection is not None:
        for child in collection.objects:
            if child.parent != None: continue
            bpy.data.objects.remove(child)


# -----------------------------------------------------------------------------
def new_actor(actor_type: ActorType, object_type = 'MESH', data = None):
    match(object_type):
        case 'MESH':
            obj = b3d_utils.new_object('Actor', b3d_utils.create_cube())
        case 'CURVE':
            obj = b3d_utils.new_object('Actor', b3d_utils.create_curve())
            
    obj.location = bpy.context.scene.cursor.location

    me_actor = get_actor_prop(obj)
    me_actor.type = actor_type

    if data is not None:
        b3d_utils.set_data(obj, data)

    return obj


# -----------------------------------------------------------------------------
def create_player_start() -> Mesh:
    scale = (.5, .5, -1)

    verts = [
        Vector((-0.5        * scale[0], -1 * scale[1], 0           )),
        Vector((-0.5        * scale[0],  1 * scale[1], 0           )),
        Vector(( 0.866025   * scale[0],  0           , 0           )),
        Vector((-0.5        * scale[0],  0           , 1 * scale[2])),
    ]

    faces = [
        (2, 1, 0),
        (0, 1, 3),
        (1, 2, 3),
        (0, 3, 2)
    ]

    return b3d_utils.new_mesh(verts, [], faces, 'PlayerStart')


# -----------------------------------------------------------------------------
def create_springboard() -> Object:
    small_step = b3d_utils.create_cube((.48, .96, .62))
    b3d_utils.transform(small_step, [Matrix.Translation((.48, .96, .31))])

    big_step = b3d_utils.create_cube((1.02, 1.6, 1.42))
    b3d_utils.transform(big_step, [Matrix.Translation((1.82, .8, .72))])

    return b3d_utils.join_meshes([small_step, big_step])


# -----------------------------------------------------------------------------
def create_zipline() -> Object:
    zipline = new_actor(ActorType.STATIC_MESH, 'CURVE')

    b3d_utils.set_data(zipline, b3d_utils.create_curve(3, 8, (1, 0, 0)))

    zipline.name = 'S_Zipline'
    zipline.data.bevel_depth = 0.04
    zipline.data.use_fill_caps = True

    return zipline


# -----------------------------------------------------------------------------
def create_checkpoint() -> Object:
    return b3d_utils.create_cylinder(make_faces=False)


# -----------------------------------------------------------------------------
def create_skydome():
    bpy.ops.mesh.primitive_uv_sphere_add()
    obj = bpy.context.object
    obj.name = 'Skydome'

    actor = get_actor_prop(obj)
    actor.type = ActorType.STATIC_MESH
    
    sm = actor.static_mesh
    sm.use_prefab = True

    # Remove bottom half
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    for v in bm.verts:
        if v.co.z < 0:
            bm.verts.remove(v)

    bm.to_mesh(obj.data)
    bm.free()


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def on_depsgraph_update_post(_scene:Scene, _depsgraph:Depsgraph):
    for obj in _scene.objects:
        actor = get_actor_prop(obj)
        
        match(obj.type):
            case 'LIGHT' | 'CURVE': 
                actor.user_editable = False

        match(actor.type):
            case ActorType.ZIPLINE:
                actor.zipline.update_bounds()


# -----------------------------------------------------------------------------
# Properties
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def ActorTypeProperty(_callback:Callable=None):

    def get_actor_type_items(self, _context:Context):
        return [(data.name, data.value, '') for data in ActorType]

    return EnumProperty(name='Type', 
                        items=get_actor_type_items, 
                        default=0, 
                        update=_callback)


# -----------------------------------------------------------------------------
def TrackIndexProperty(_callback:Callable=None):

    def get_track_index_items(self, _context:Context):
        return [((data.name, data.value, '')) for data in TrackIndex]

    return EnumProperty(
        items=get_track_index_items,
        name='TrackIndex',
        default=17,
        update=_callback
    )


# -----------------------------------------------------------------------------
class MaterialProperty:

    def __filter_on_package(self, _obj:Object):
        is_material = _obj.name.startswith('M_')
        return self.material_package in _obj.users_collection and is_material
    

    def get_material_path(self):
        self.material_package.name.rstrip('.')
        return self.material_package.name + '.' + self.material.name
    

    def draw_material_prop(self, _layout:UILayout):
        _layout.prop(self, 'material_package')
        _layout.prop(self, 'material')


    material_package: PointerProperty(type=bpy.types.Collection, name='Package')
    material:         PointerProperty(type=Object, name='Material', poll=__filter_on_package)


# -----------------------------------------------------------------------------
class PhysMaterialProperty:

    def __filter_on_package(self, _obj:Object):
        is_material = _obj.name.startswith('PM_')
        return self.phys_material_package in _obj.users_collection and is_material
    

    def get_phys_material_path(self):
        self.phys_material_package.name.rstrip('.')
        return self.phys_material_package.name + '.' + self.phys_material.name
    

    def draw_phys_material_prop(self, _layout:UILayout):
        _layout.prop(self, 'phys_material_package')
        _layout.prop(self, 'phys_material')


    phys_material_package: PointerProperty(type=bpy.types.Collection, name='Package')
    phys_material:         PointerProperty(type=Object, name='PhysMaterial', poll=__filter_on_package)


# -----------------------------------------------------------------------------
class MET_PG_Widget(PropertyGroup):

    obj: PointerProperty(type=Object)


# -----------------------------------------------------------------------------
class Actor:

    def init(self):
        self.clear_widgets()
        b3d_utils.link_object_to_scene(self.id_data)
        self.id_data.display_type = 'TEXTURED'
    

    def draw(self, _layout:UILayout):
        pass

    
    def clear_widgets(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()
    
    
    widgets: CollectionProperty(type=MET_PG_Widget)


# -----------------------------------------------------------------------------
# PlayerStart
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_PlayerStart(Actor, PropertyGroup):
    
    def init(self):
        super().init()

        b3d_utils.set_data(self.id_data, create_player_start())
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'Player Start'


    def draw(self, _layout:UILayout):
        _layout.prop(self, 'is_time_trial')

        if self.is_time_trial:
            _layout.prop(self, 'track_index')


    is_time_trial: BoolProperty(name='Is Time Trial')
    track_index:   TrackIndexProperty()


# -----------------------------------------------------------------------------
# Checkpoint
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Checkpoint(Actor, PropertyGroup):
    
    def init(self):
        super().init()
        b3d_utils.set_data(self.id_data, create_checkpoint())
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'TimeTrialCheckpoint'


    def draw(self, _layout:UILayout):
        b3d_utils.auto_gui_props(self, _layout)


    track_index:          TrackIndexProperty()
    order_index:          IntProperty(name='Order Index')
    custom_height:        FloatProperty(name='CustomHeight')
    custom_width_scale:   FloatProperty(name='Custom Width Scale')
    should_be_based:      BoolProperty(name='Should Be Based')
    no_intermediate_time: BoolProperty(name='No Intermediate Time')
    no_respawn:           BoolProperty(name='No Respawn')
    enabled:              BoolProperty(name='Enabled')


# -----------------------------------------------------------------------------
# StaticMesh
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_StaticMesh(Actor, MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()

        if not self.prefab:
            b3d_utils.link_object_to_scene(self.id_data, MY_PACKAGE)

        if not self.id_data.data: 
            b3d_utils.set_data(self.id_data, b3d_utils.create_cube())

        self.id_data.name = 'StaticMesh'
    
    
    def draw(self, _layout:UILayout):
        _layout.prop(self, 'use_prefab')

        if self.use_prefab:
            _layout.prop(self, 'prefab')
        else:
            _layout.prop(self, 'use_material')
            if self.use_material:
                self.draw_material_prop()
    
    def get_path(self) -> str:
        package = self.id_data.users_collection[0].name
        package.rstrip('.')

        return package + '.' + self.id_data.name

    
    def get_prefab_path(self) -> str:
        package = self.prefab.users_collection[0].name
        package.rstrip('.')

        return package + '.' + self.prefab.name


    def __on_use_prefab_update(self, _context:Context):
        if self.use_prefab:
            self.id_data.name = 'PREFAB_'
            if self.prefab:
                self.id_data.name += self.prefab.name
            b3d_utils.link_object_to_scene(self.id_data, None)
        else:
            self.id_data.name = 'StaticMesh'
            b3d_utils.link_object_to_scene(self.id_data, MY_PACKAGE)

        
    def __on_prefab_update(self, _context:Context):
        if self.prefab: 
            b3d_utils.set_data(self.id_data, self.prefab.data)
            self.id_data.name = 'PREFAB_' + self.prefab.name

        else:
            b3d_utils.set_data(self.id_data, None)
            self.id_data.name = 'StaticMesh'

    
    use_material: BoolProperty(name='Use Material', default=False)
    use_prefab:   BoolProperty(name='Use Prefab', default=False, update=__on_use_prefab_update)
    prefab:       PointerProperty(type=Object, name='Prefab', update=__on_prefab_update)


# -----------------------------------------------------------------------------
# Brush
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Brush(Actor, MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()
        b3d_utils.set_data(self.id_data, b3d_utils.create_cube())
        self.id_data.name = 'Brush'


    def draw(self, _layout:UILayout):
        self.draw_material_prop(_layout)


# -----------------------------------------------------------------------------
# Ladder
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Ladder(Actor, PropertyGroup):
    
    def init(self):
        super().init()
        scale = (1, 1, 4)

        b3d_utils.set_data(self.id_data, b3d_utils.create_cube(scale))
        self.id_data.display_type = 'WIRE'

        arrow = self.widgets.add()
        arrow.obj = b3d_utils.new_object('ArrowWidget', b3d_utils.create_arrow(scale), COLLECTION_WIDGETS, self.id_data)
        b3d_utils.set_object_selectable(arrow.obj, False)

        self.id_data.name = 'Ladder'


    def draw(self, _layout:UILayout):
        _layout.prop(self, 'is_pipe')


    def __on_is_pipe_update(self, _context:Context):
        self.id_data.name = 'LADDER'
        if self.is_pipe:
            self.id_data.name = 'PIPE'

    
    is_pipe: BoolProperty(name='Is Pipe', update=__on_is_pipe_update)


# -----------------------------------------------------------------------------
# Swing
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Swing(Actor, PropertyGroup):
    
    def init(self):
        super().init()
        self.id_data.display_type = 'WIRE'
        
        scale = Vector((2, 2, 1))

        b3d_utils.set_data(self.id_data, b3d_utils.create_cube(scale))

        m_t07_x = Matrix.Translation((.7, 0, 0))
        m_t035_x = Matrix.Translation((.2, 0, 0))
        m_r90_x = Matrix.Rotation(math.radians(90), 3, (1, 0, 0))
        m_r90_y = Matrix.Rotation(math.radians(90), 3, (0, 1, 0))
        m_mir_x = Matrix.Scale(-1, 3, (1, 0, 0))

        arrow0 = self.widgets.add()
        arrow1 = self.widgets.add()
        arrow2 = self.widgets.add()

        for arrow in self.widgets:
            s = scale * .3
            arrow.obj = b3d_utils.new_object('ArrowWidget', b3d_utils.create_arrow(s), COLLECTION_WIDGETS, self.id_data)
            b3d_utils.set_object_selectable(arrow.obj, False)

        b3d_utils.transform(arrow0.obj.data, [m_t07_x , m_r90_x])
        b3d_utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
        b3d_utils.transform(arrow2.obj.data, [m_t07_x , m_r90_x, m_mir_x]) 

        self.id_data.name = 'Swing'
    

# -----------------------------------------------------------------------------
# Zipline
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Zipline(Actor, PropertyGroup):
    
    def init(self):
        super().init()  
        
        # It would make more sense to set id_data to the curve and make the bounding box the child.
        # Unfortunately, the object type is MESH. Instead of converting to CURVE (which can conflict with other actors who expect MESH) 
        # we just make the curve a child of the bounding box.
        b3d_utils.set_data(self.id_data, b3d_utils.create_cube())  

        if self.curve:
            b3d_utils.remove_object(self.curve)

        self.curve = create_zipline()
        self.curve.location = (0, 0, 0)

        b3d_utils.set_parent(self.curve, self.id_data, False)
        b3d_utils.link_object_to_scene(self.curve, MY_PACKAGE)

        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'Zipline_BoundingBox'

        b3d_utils.set_active_object(self.id_data)

        self.update_bounds(True)

    
    def draw(self, _layout:UILayout):
        _layout.prop(self, 'curve')
        _layout.prop(self, 'auto_bb')

        if self.auto_bb:
            _layout.prop(self, 'align_bb')
            _layout.prop(self, 'bb_resolution')
            _layout.separator()
            _layout.prop(self, 'bb_scale')
            _layout.separator()
            _layout.prop(self, 'bb_offset')


    def update_bounds(self, _force=False):   
        if not self.auto_bb: 
            return

        spline = self.curve.data.splines[0]
        points = spline.points
        
        p1 = points[0].co.xyz
        p2 = points[1].co.xyz
        p3 = points[2].co.xyz

        if not _force:
            if p1 == self.c1 and p2 == self.c2 and p3 == self.c3:
                return
        
        self.c1 = p1
        self.c2 = p2
        self.c3 = p3

        verts = []
        edges = []
        segments = []; 

        def local_bounds(center:Vector, p1:Vector, p2:Vector):
            forward = (p2 - p1).normalized()
            if self.align_bb:
                forward.z = 0
            right = Vector((forward.y, -forward.x, 0)).normalized() * self.bb_scale
            up = forward.cross(right).normalized() * self.bb_scale

            center += self.bb_offset

            e1 = len(verts)
            verts.append(center + up + right)

            e2 = len(verts)
            verts.append(center + -up + right)

            e3 = len(verts)
            verts.append(center + -up - right)

            e4 = len(verts)
            verts.append(center + up - right)

            edges.append((e1, e2))
            edges.append((e2, e3))
            edges.append((e3, e4))
            edges.append((e4, e1))
            segments.append((e1, e2, e3, e4))

        length = spline.calc_length()

        v1 = (p2 - p1)
        v2 = (p2 - p3)

        handle1 = p1 + v1 * v1.length / length
        handle2 = p3 + v2 * v2.length / length

        ipoints = geometry.interpolate_bezier(p1, handle1, handle2, p3, self.bb_resolution + 1)

        for k in range(len(ipoints) - 1):
            ip1 = ipoints[k]
            ip2 = ipoints[k + 1]
            local_bounds(ip1, ip1, ip2)

        local_bounds(p3, p2, p3)
        
        faces = []
        faces.append((0, 1, 2, 3))

        for k in range(len(segments) - 1):
            s1 = segments[k]
            s2 = segments[k + 1]
            edges.append((s1[0], s2[0]))
            edges.append((s1[1], s2[1]))
            edges.append((s1[2], s2[2]))
            edges.append((s1[3], s2[3]))
            
            faces.append((s1[0], s2[0], s2[1], s1[1]))
            faces.append((s1[0], s1[3], s2[3], s2[0]))
            faces.append((s1[0], s1[3], s2[3], s2[0]))
            faces.append((s1[3], s1[2], s2[2], s2[3]))
            faces.append((s1[2], s1[1], s2[1], s2[2]))
        
        l = len(verts)
        faces.append((l-1, l-2, l-3, l-4))

        b3d_utils.set_data(self.id_data, b3d_utils.new_mesh(verts, edges, faces, self.id_data.name))


    def __force_update_bb_bounds(self, _context:Context):
        self.update_bounds(True)

    curve:    PointerProperty(type=Object, name='Curve')
    auto_bb:  BoolProperty(name='Automatic Bounding Box', default=True)
    align_bb: BoolProperty(name='Align', default=True, update=__force_update_bb_bounds)

    bb_resolution: IntProperty(name='Resolution', default=4, min=1, update=__force_update_bb_bounds)
    bb_scale:      FloatVectorProperty(name='Scale', subtype='TRANSLATION', default=(1, 1, 1), update=__force_update_bb_bounds)
    bb_offset:     FloatVectorProperty(name='Offset', subtype='TRANSLATION', update=__force_update_bb_bounds)

    c1: FloatVectorProperty(subtype='TRANSLATION')
    c2: FloatVectorProperty(subtype='TRANSLATION')
    c3: FloatVectorProperty(subtype='TRANSLATION')


# -----------------------------------------------------------------------------
# BlockingVolume
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_BlockingVolume(Actor, PhysMaterialProperty, PropertyGroup):
    def init(self):
        super().init()
        b3d_utils.set_data(self.id_data, b3d_utils.create_cube())  
        self.id_data.display_type = 'WIRE'
    

    def draw(self, _layout: UILayout):
        self.draw_phys_material_prop(_layout)


# -----------------------------------------------------------------------------
# SpringBoard
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_SpringBoard(Actor, PropertyGroup):
    
    def init(self):
        super().init()   
        b3d_utils.set_data(self.id_data, create_springboard())
        self.id_data.name = 'SpringBoard'


    def draw(self, _layout: UILayout):
        _layout.prop(self, 'is_hidden_game')


    def __on_is_hidden_game_update(self, _context:Context):
        if self.is_hidden_game:
            self.id_data.display_type = 'WIRE'
        else:
            self.id_data.display_type = 'SOLID'


    is_hidden_game: BoolProperty(name='Is Hidden In Game', update=__on_is_hidden_game_update)


# -----------------------------------------------------------------------------
# ActorProperty
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_OBJECT_PG_Actor(PropertyGroup):

    def draw(self, _layout:UILayout):
        col = _layout.column(align=True)

        if not self.user_editable:
            col.label(text=str(self.type))
            return

        col.prop(self, 'type')
        col.separator()

        match(self.type):
            case ActorType.PLAYER_START:
                self.player_start.draw(col)
            case ActorType.BRUSH:
                self.brush.draw(col)
            case ActorType.LADDER:
                self.ladder.draw(col)
            case ActorType.SWING:
                self.swing.draw(col)
            case ActorType.ZIPLINE:
                self.zipline.draw(col)
            case ActorType.SPRINGBOARD:
                self.springboard.draw(col)
            case ActorType.STATIC_MESH:
                self.static_mesh.draw(col)
            case ActorType.BLOCKING_VOLUME:
                self.blocking_volume.draw(col)
            case ActorType.CHECKPOINT:
                self.checkpoint.draw(col)

    
    def __on_type_update(self, _context:Context):
        b3d_utils.set_active_object(self.id_data)

        match(self.type):
            case ActorType.PLAYER_START:
                self.player_start.init()
            case ActorType.CHECKPOINT:
                self.checkpoint.init()
            case ActorType.STATIC_MESH:
                self.static_mesh.init()
            case ActorType.BRUSH:
                self.brush.init()
            case ActorType.LADDER:
                self.ladder.init()
            case ActorType.SWING:
                self.swing.init()
            case ActorType.ZIPLINE:
                self.zipline.init()
            case ActorType.SPRINGBOARD:
                self.springboard.init()
            case ActorType.BLOCKING_VOLUME:
                self.blocking_volume.init()

    
    type:            ActorTypeProperty(__on_type_update)
    user_editable:   BoolProperty(name='PRIVATE', default=True)

    player_start:    PointerProperty(type=MET_ACTOR_PG_PlayerStart)
    checkpoint:      PointerProperty(type=MET_ACTOR_PG_Checkpoint)
    static_mesh:     PointerProperty(type=MET_ACTOR_PG_StaticMesh)
    brush:           PointerProperty(type=MET_ACTOR_PG_Brush)
    ladder:          PointerProperty(type=MET_ACTOR_PG_Ladder)
    swing:           PointerProperty(type=MET_ACTOR_PG_Swing)
    zipline:         PointerProperty(type=MET_ACTOR_PG_Zipline)
    springboard:     PointerProperty(type=MET_ACTOR_PG_SpringBoard)
    blocking_volume: PointerProperty(type=MET_ACTOR_PG_BlockingVolume)


# -----------------------------------------------------------------------------
# Scene Utils
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def get_actor_prop(_obj:Object) -> MET_OBJECT_PG_Actor:
    return _obj.medge_actor


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def register():
    Object.medge_actor = bpy.props.PointerProperty(type=MET_OBJECT_PG_Actor)
    b3d_utils.add_callback(depsgraph_update_post, on_depsgraph_update_post)


# -----------------------------------------------------------------------------
def unregister():
    b3d_utils.remove_callback(depsgraph_update_post, on_depsgraph_update_post)
    del Object.medge_actor
