import bpy
from bpy.props        import EnumProperty, PointerProperty, CollectionProperty, BoolProperty, IntProperty, FloatVectorProperty, FloatProperty, StringProperty
from bpy.types        import Scene, Depsgraph, Object, Mesh, ID, PropertyGroup, Context, UILayout
from bpy.app.handlers import depsgraph_update_post
from mathutils        import Vector, Matrix

import math
from typing    import Callable
from mathutils import Matrix, Vector

from ..         import b3d_utils
from .t3d.scene import ActorType, TrackIndex

COLLECTION_WIDGETS = 'Widgets'


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
def new_actor(_actor_type:ActorType, _data:ID=None):

    if _data:
        obj = b3d_utils.new_object(_data, _actor_type.label)
    else:
        obj = b3d_utils.new_object(b3d_utils.create_cube(), _actor_type.label)


    me_actor = get_actor_prop(obj)
    me_actor.actor_type = _actor_type.name

    return obj


# -----------------------------------------------------------------------------
# Properties
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def ActorTypeEnumProperty(_callback:Callable=None):
    def get_actor_type_items(self, _context:Context):
        return [(data.name, data.label, '') for data in ActorType]

    return EnumProperty(name='Actor Type', 
                        items=get_actor_type_items, 
                        default=0, 
                        update=_callback)


# -----------------------------------------------------------------------------
def TrackIndexEnumProperty(_callback:Callable=None):
    def get_track_index_items(self, _context:Context):
        return [((data.name, data.value, '')) for data in TrackIndex]

    return EnumProperty(
        items=get_track_index_items,
        name='TrackIndex',
        default=17,
        update=_callback
    )


# -----------------------------------------------------------------------------
# We cannot make this a PropertyGroup and add it as a PointerProperty to actors,
# otherwise we will get a stackoverflow.
# I think it's because of to many nested PointerProperties
class MaterialProperty:

    def __filter_on_package(self, _obj:Object):
        if _obj:
            if self.material_filter:
                valid = self.material_filter_collection in _obj.users_collection
                
                if (prefix := self.material_filter_prefix):
                    valid = valid and _obj.name.startswith(prefix)

                return valid
        
        return True
    

    def draw_material(self, _layout:UILayout):
        _layout.prop(self, 'material_filter')

        if self.material_filter:
            _layout.prop(self, 'material_filter_collection')
            _layout.prop(self, 'material_filter_prefix')
        
        _layout.prop(self, 'material')


    material_filter:            BoolProperty(name='Filter')
    material_filter_collection: PointerProperty(type=bpy.types.Collection, name='Collection')
    material_filter_prefix:     StringProperty(name='Prefix')
    material:                   PointerProperty(type=Object, name='Material', update=__filter_on_package)


# -----------------------------------------------------------------------------
# We cannot make this a PropertyGroup and add it as a PointerProperty to actors,
# otherwise we will get a stackoverflow. 
# I think it's because of to many nested PointerProperties
class PhysMaterialProperty:

    def __filter_on_package(self, _obj:Object):
        if _obj:
            if self.phys_material_filter:
                valid = self.phys_material_filter_collection in _obj.users_collection
                
                if (prefix := self.phys_material_filter_prefix):
                    valid = valid and _obj.name.startswith(prefix)

                return valid
        
        return True
    

    def draw_phys_material(self, _layout:UILayout):
        _layout.prop(self, 'phys_material_filter')

        if self.phys_material_filter:
            _layout.prop(self, 'phys_material_filter_collection')
            _layout.prop(self, 'phys_material_filter_prefix')
        
        _layout.prop(self, 'phys_material')


    phys_material_filter:            BoolProperty(name='Filter')
    phys_material_filter_collection: PointerProperty(type=bpy.types.Collection, name='Collection')
    phys_material_filter_prefix:     StringProperty(name='Prefix')
    phys_material:                   PointerProperty(type=Object, name='PhysMaterial', update=__filter_on_package)


# -----------------------------------------------------------------------------
class MET_PG_Widget(PropertyGroup):

    obj: PointerProperty(type=Object)


# -----------------------------------------------------------------------------
class Actor:

    def init(self):
        self.clear_widgets()
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
# Brush
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Brush(Actor, MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()
        
        if self.id_data.type != 'MESH':
            b3d_utils.set_data(self.id_data, b3d_utils.create_cube())
        
        self.id_data.name = 'Brush'


    def draw(self, _layout:UILayout):
        self.draw_material(_layout)


# -----------------------------------------------------------------------------
# StaticMesh
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_StaticMesh(Actor, MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()

        if not self.id_data.data: 
            b3d_utils.set_data(self.id_data, b3d_utils.create_cube())

    
    def draw(self, _layout:UILayout):
        b3d_utils.draw_box(_layout, 'Do not apply any transforms, these values are needed for export')   
        _layout.separator()

        _layout.prop(self, 'is_hidden_game')

        if not self.is_hidden_game:
            self.draw_material(_layout)
        
        _layout.prop(self, 'use_prefab')
        if self.use_prefab:
            _layout.prop(self, 'prefab')
    
    
    def __update_name(self, _context:Context):
        if self.use_prefab:
            self.id_data.name = 'PREFAB_'

            if self.prefab:
                self.id_data.name += self.prefab.name

        else:
            self.id_data.name = 'SM_'


    def __on_is_hidden_game_update(self, _context:Context):
        if self.is_hidden_game:
            self.id_data.display_type = 'WIRE'
        else:
            self.id_data.display_type = 'SOLID'

        
    def __on_prefab_update(self, _context:Context):
        if self.prefab: 
            if self.prefab.type == 'MESH': 
                b3d_utils.set_data(self.id_data, self.prefab.data)
            self.__update_name(_context)
        else:
            b3d_utils.set_data(self.id_data, None)

    
    is_hidden_game: BoolProperty(name='Is Hidden In Game', update=__on_is_hidden_game_update)
    use_prefab:     BoolProperty(name='Use Prefab', update=__update_name)
    prefab:         PointerProperty(type=Object, name='Prefab', update=__on_prefab_update)


# -----------------------------------------------------------------------------
# Ladder
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_LadderVolume(Actor, PropertyGroup):
    
    def init(self):
        super().init()

        scale = 1, 1, 6
        volume = b3d_utils.create_cube(scale)
        b3d_utils.transform(volume, [Matrix.Translation((0, 0, 3))])

        b3d_utils.set_data(self.id_data, volume)

        self.id_data.display_type = 'WIRE'

        arrow = self.widgets.add()
        arrow.obj = b3d_utils.new_object(b3d_utils.create_arrow(scale), 'ArrowWidget', COLLECTION_WIDGETS, self.id_data, False)
        arrow.obj.location = 0, 0, 5
        b3d_utils.set_object_selectable(arrow.obj, False)

        self.id_data.name = 'LadderVolume'


    def draw(self, _layout:UILayout):
        b3d_utils.draw_box(_layout, 'Do not apply any transforms, these values are needed for export') 
        _layout.separator()
        _layout.prop(self, 'is_pipe')


    def create(self):
        verts = []


    def __on_is_pipe_update(self, _context:Context):
        self.id_data.name = 'LadderVolume'

        if self.is_pipe:
            self.id_data.name = 'PipeVolume'

    
    is_pipe: BoolProperty(name='Is Pipe', update=__on_is_pipe_update)


# -----------------------------------------------------------------------------
# Swing
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_SwingVolume(Actor, PropertyGroup):
    
    def init(self):
        super().init()

        self.id_data.display_type = 'WIRE'
        
        scale = Vector((2, 2, 1))
        b3d_utils.set_data(self.id_data, b3d_utils.create_cube(scale))

        arrow0 = self.widgets.add()
        arrow1 = self.widgets.add()
        arrow2 = self.widgets.add()

        for arrow in self.widgets:
            s = scale * .3
            arrow.obj = b3d_utils.new_object(b3d_utils.create_arrow(s), 'ArrowWidget', COLLECTION_WIDGETS, self.id_data, False)
            arrow.obj.location = 0, 0, 0
            b3d_utils.set_object_selectable(arrow.obj, False)

        m_t07_x  = Matrix.Translation((.7, 0, 0))
        m_t035_x = Matrix.Translation((.2, 0, 0))
        m_r90_x  = Matrix.Rotation(math.radians(90), 3, (1, 0, 0))
        m_r90_y  = Matrix.Rotation(math.radians(90), 3, (0, 1, 0))
        m_mir_x  = Matrix.Scale(-1, 3, (1, 0, 0))

        b3d_utils.transform(arrow0.obj.data, [m_t07_x , m_r90_x])
        b3d_utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
        b3d_utils.transform(arrow2.obj.data, [m_t07_x , m_r90_x, m_mir_x]) 

        self.id_data.name = 'Swing'


    def draw(self, _layout: UILayout):
        b3d_utils.draw_box(_layout, 'Do not apply any transforms, these values are needed for export')     


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

        self.curve = self.create_zipline()
        self.curve.location = 0, 0, 0

        b3d_utils.set_parent(self.curve, self.id_data, False)

        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'Zipline_BoundingBox'

        b3d_utils.set_active_object(self.id_data)

        self.update_bounds(True)

    
    def draw(self, _layout:UILayout):
        _layout.prop(self, 'curve')

        _layout.separator()
        _layout.prop(self, 'auto_bb')

        if self.auto_bb:
            _layout.prop(self, 'align_bb')
            _layout.prop(self, 'bb_resolution')
            _layout.separator()
            _layout.prop(self, 'bb_scale')
            _layout.separator()
            _layout.prop(self, 'bb_offset')


    def create_zipline(self) -> Object:
        curve, path = b3d_utils.create_curve()

        for k, p in enumerate(path.points):
            v = Vector((8, 0, 0)) * k
            p.co = (*v, 1)

        zipline = new_actor(ActorType.STATIC_MESH, curve)

        zipline.name = 'S_Zipline'
        zipline.data.bevel_depth = 0.04
        zipline.data.use_fill_caps = True

        return zipline


    def update_bounds(self, _force=False):   
        if not self.auto_bb: 
            return

        curve_data = self.curve.data

        nurbs = curve_data.splines[0]
        points = nurbs.points
        
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

            if self.align_z:
                forward.z = 0

            right = Vector((forward.y, -forward.x, 0)).normalized() * self.bb_scale
            up = forward.cross(right).normalized() * self.bb_scale

            center += self.bb_offset

            e1 = len(verts)
            verts.append(center + up + right)

            e2 = len(verts)
            verts.append(center - up + right)

            e3 = len(verts)
            verts.append(center - up - right)

            e4 = len(verts)
            verts.append(center + up - right)

            edges.append((e1, e2))
            edges.append((e2, e3))
            edges.append((e3, e4))
            edges.append((e4, e1))
            
            segments.append((e1, e2, e3, e4))

        # Interpolate points
        stride = 3
        ipoints = b3d_utils.interpolate_nurbs(nurbs, curve_data.resolution_u, stride)

        for k in range(0, len(ipoints) - stride, stride + self.bb_resolution * 3):
            ip1 = Vector((ipoints[k + 0], ipoints[k + 1], ipoints[k + 2]))
            ip2 = Vector((ipoints[k + 3], ipoints[k + 4], ipoints[k + 5]))
            local_bounds(ip1, ip1, ip2)

        local_bounds(p3, p2, p3)
        
        # Create mesh bounds
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
        

    curve:         PointerProperty(type=Object, name='Curve')
    auto_bb:       BoolProperty(name='Automatic Bounding Box', default=True)
    align_z:       BoolProperty(name='Align Z', update=__force_update_bb_bounds)

    bb_resolution: IntProperty(name='Resolution', default=5, min=0, update=__force_update_bb_bounds)
    bb_scale:      FloatVectorProperty(name='Scale', subtype='TRANSLATION', default=(1, 1, 1), update=__force_update_bb_bounds)
    bb_offset:     FloatVectorProperty(name='Offset', subtype='TRANSLATION', update=__force_update_bb_bounds)

    c1:            FloatVectorProperty(name='PRIVATE', subtype='TRANSLATION')
    c2:            FloatVectorProperty(name='PRIVATE', subtype='TRANSLATION')
    c3:            FloatVectorProperty(name='PRIVATE', subtype='TRANSLATION')


# -----------------------------------------------------------------------------
# BlockingVolume
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_BlockingVolume(Actor, PhysMaterialProperty, PropertyGroup):

    def init(self):
        super().init()

        if self.id_data.type != 'MESH':
            b3d_utils.set_data(self.id_data, b3d_utils.create_cube())  

        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'BlockingVolume'
    

    def draw(self, _layout: UILayout):
        self.draw_phys_material(_layout)


# -----------------------------------------------------------------------------
# TriggerVolume
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_TriggerVolume(Actor, PropertyGroup):

    def init(self):
        super().init()
        
        if self.id_data.type != 'MESH':
            b3d_utils.set_data(self.id_data, b3d_utils.create_cube())  

        self.id_data.display_type = 'WIRE'


# -----------------------------------------------------------------------------
# PlayerStart
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_PlayerStart(Actor, PropertyGroup):
    
    def init(self):
        super().init()

        b3d_utils.set_data(self.id_data, self.create())
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'PlayerStart'


    def draw(self, _layout:UILayout):
        b3d_utils.draw_box(_layout, 'Do not apply any transforms, these values are needed for export') 
        _layout.separator()

        _layout.prop(self, 'is_time_trial')

        if self.is_time_trial:
            _layout.prop(self, 'track_index')


    def create(self):
        scale = (.5, .5, 1)

        # The origin will be at the bottom, but when we export we add +1 to the z value
        verts = [
            Vector((0        * scale[0], -1 * scale[1], 1 * scale[2])),
            Vector((0        * scale[0],  1 * scale[1], 1 * scale[2])),
            Vector((1.366025 * scale[0],  0           , 1 * scale[2])),
            Vector((0        * scale[0],  0           , 0 * scale[2])),
        ]

        faces = [
            (2, 1, 0),
            (0, 1, 3),
            (1, 2, 3),
            (0, 3, 2)
        ]

        return b3d_utils.new_mesh(verts, [], faces, 'PlayerStart')


    is_time_trial: BoolProperty(name='Is Time Trial')
    track_index:   TrackIndexEnumProperty()


# -----------------------------------------------------------------------------
# Checkpoint
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Checkpoint(Actor, PropertyGroup):
    
    def init(self):
        super().init()

        b3d_utils.set_data(self.id_data, self.create())
        
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'TimeTrialCheckpoint_0'


    def draw(self, _layout:UILayout):
        b3d_utils.auto_gui_props(self, _layout)

    
    def create(self) -> Mesh:
        height = 30

        verts = [ 
            (-1, -1, 0), (-1, 1, 0), (1, 1, 0), (1, -1, 0), 
            (0, 0, 0),
            (0, 0, height), (-.5, -.5, height), (-.5, .5, height), (.5, .5, height), (.5, -.5, height), 
        ]

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
        ]

        return b3d_utils.new_mesh(verts, edges, [], 'Checkpoint')


    def __on_order_index_update(self, _context:Context):
        self.id_data.name = 'TimeTrialCheckpoint_' + self.order_index


    track_index:          TrackIndexEnumProperty()
    order_index:          IntProperty(name='Order Index', update=__on_order_index_update)
    custom_height:        FloatProperty(name='CustomHeight')
    custom_width_scale:   FloatProperty(name='Custom Width Scale')
    should_be_based:      BoolProperty(name='Should Be Based')
    no_intermediate_time: BoolProperty(name='No Intermediate Time')
    no_respawn:           BoolProperty(name='No Respawn')
    enabled:              BoolProperty(name='Enabled', default=True)


# -----------------------------------------------------------------------------
# Lights
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class BakerSettings:
    
    def draw(self, _layout:UILayout):
        _layout.prop(self, 'sample_factor')

    sample_factor: FloatProperty(name='Sample Factor', min=0, default=1.0)


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_PointLight(BakerSettings, PropertyGroup):
    pass

# -----------------------------------------------------------------------------
class MET_ACTOR_PG_DirectionalLight(BakerSettings, PropertyGroup):
    pass

# -----------------------------------------------------------------------------
class MET_ACTOR_PG_SpotLight(BakerSettings, PropertyGroup):
    pass

# -----------------------------------------------------------------------------
class MET_ACTOR_PG_AreaLight(BakerSettings, PropertyGroup):

    def draw(self, _layout: UILayout):
        super().draw(_layout)
        b3d_utils.auto_gui_props(self, _layout)

    is_window_light: BoolProperty(name='Is Window Light')
    window_light_angle: FloatProperty(name='Window Light Angle')


# -----------------------------------------------------------------------------
# ActorProperty
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_OBJECT_PG_Actor(PropertyGroup):

    def draw(self, _layout:UILayout):
        col = _layout.column(align=True)

        if self.id_data.type == 'MESH':
            col.prop(self, 'actor_type')
        col.separator()

        match(self.actor_type):
            case ActorType.BRUSH.name:
                self.brush.draw(col)
            case ActorType.STATIC_MESH.name:
                self.static_mesh.draw(col)
            case ActorType.LADDER_VOLUME.name:
                self.ladder.draw(col)
            case ActorType.SWING_VOLUME.name:
                self.swing.draw(col)
            case ActorType.ZIPLINE.name:
                self.zipline.draw(col)
            case ActorType.BLOCKING_VOLUME.name:
                self.blocking_volume.draw(col)
            case ActorType.TRIGGER_VOLUME.name | ActorType.KILL_VOLUME.name:
                self.trigger_volume.draw(col)
            case ActorType.PLAYER_START.name:
                self.player_start.draw(col)
            case ActorType.CHECKPOINT.name:
                self.checkpoint.draw(col)
        
        if not self.id_data or self.id_data.type != 'LIGHT':
            col.label(text='No Settings')
            return

        match self.id_data.data.type:
            case 'POINT':
                self.point_light.draw(col)
            case 'SUN':
                self.directional_light.draw(col)
            case 'SPOT':
                self.spot_light.draw(col)
            case 'AREA':
                self.area_light.draw(col)
            

    def __on_type_update(self, _context:Context):
        b3d_utils.set_active_object(self.id_data)

        match(self.actor_type):
            case ActorType.BRUSH.name:
                self.brush.init()
            case ActorType.STATIC_MESH.name:
                self.static_mesh.init()
            case ActorType.LADDER_VOLUME.name:
                self.ladder.init()
            case ActorType.SWING_VOLUME.name:
                self.swing.init()
            case ActorType.ZIPLINE.name:
                self.zipline.init()
            case ActorType.BLOCKING_VOLUME.name:
                self.blocking_volume.init()
            case ActorType.TRIGGER_VOLUME.name | ActorType.KILL_VOLUME.name:
                self.trigger_volume.init()
            case ActorType.PLAYER_START.name:
                self.player_start.init()
            case ActorType.CHECKPOINT.name:
                self.checkpoint.init()
        
        if not self.id_data: return
        if self.id_data.type != 'LIGHT': return

        match self.id_data.data.type:
            case 'POINT':
                self.point_light.init()
            case 'SUN':
                self.directional_light.init()
            case 'SPOT':
                self.spot_light.init()
            case 'AREA':
                self.area_light.init()
    

    def get_brush(self) -> MET_ACTOR_PG_Brush:
        return self.brush
    
    def get_static_mesh(self) -> MET_ACTOR_PG_StaticMesh:
        return self.static_mesh
    
    def get_ladder(self) -> MET_ACTOR_PG_LadderVolume:
        return self.ladder
    
    def get_swing(self) -> MET_ACTOR_PG_SwingVolume:
        return self.swing
    
    def get_zipline(self) -> MET_ACTOR_PG_Zipline:
        return self.zipline
    
    def get_blocking_volume(self) -> MET_ACTOR_PG_BlockingVolume:
        return self.blocking_volume
    
    def get_trigger_volume(self) -> MET_ACTOR_PG_TriggerVolume:
        return self.trigger_volume
    
    def get_player_start(self) -> MET_ACTOR_PG_PlayerStart:
        return self.player_start
    
    def get_checkpoint(self) -> MET_ACTOR_PG_Checkpoint:
        return self.checkpoint

    def get_point_light(self) -> MET_ACTOR_PG_PointLight:
        return self.point_light

    def get_directional_light(self) -> MET_ACTOR_PG_DirectionalLight:
        return self.directional_light

    def get_spot_light(self) -> MET_ACTOR_PG_SpotLight:
        return self.spot_light

    def get_area_light(self) -> MET_ACTOR_PG_AreaLight:
        return self.area_light

    actor_type:      ActorTypeEnumProperty(__on_type_update)

    brush:           PointerProperty(type=MET_ACTOR_PG_Brush)
    static_mesh:     PointerProperty(type=MET_ACTOR_PG_StaticMesh)
    ladder:          PointerProperty(type=MET_ACTOR_PG_LadderVolume)
    swing:           PointerProperty(type=MET_ACTOR_PG_SwingVolume)
    zipline:         PointerProperty(type=MET_ACTOR_PG_Zipline)
    blocking_volume: PointerProperty(type=MET_ACTOR_PG_BlockingVolume)
    trigger_volume:  PointerProperty(type=MET_ACTOR_PG_TriggerVolume)
    player_start:    PointerProperty(type=MET_ACTOR_PG_PlayerStart)
    checkpoint:      PointerProperty(type=MET_ACTOR_PG_Checkpoint)

    point_light:       PointerProperty(type=MET_ACTOR_PG_PointLight)
    directional_light: PointerProperty(type=MET_ACTOR_PG_DirectionalLight)
    spot_light:        PointerProperty(type=MET_ACTOR_PG_SpotLight)
    area_light:        PointerProperty(type=MET_ACTOR_PG_AreaLight)


# -----------------------------------------------------------------------------
# Scene Utils
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def get_actor_prop(_obj:Object) -> MET_OBJECT_PG_Actor:
    return _obj.medge_actor


# -----------------------------------------------------------------------------
def on_depsgraph_update_post(_scene:Scene, _depsgraph:Depsgraph):
    for obj in _scene.objects:
        actor = get_actor_prop(obj)

        match(actor.actor_type):
            case ActorType.ZIPLINE.name:
                actor.zipline.update_bounds()


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
    
    if hasattr(Object, 'medge_actor'): del Object.medge_actor
