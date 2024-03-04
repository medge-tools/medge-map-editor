import bpy
from bpy.props import *
from bpy.types import Object, PropertyGroup, Context, UILayout
from typing import Callable
from mathutils import Matrix, Vector, geometry

import math

from ..io.t3d.scene import ActorType, TrackIndex
from .. import b3d_utils
from . import scene_utils as scene

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

def ActorTypeProperty(callback: Callable = None):
    def get_actor_type_items(self, context: Context):
        return [(data.name, data.value, '') for data in ActorType]

    return EnumProperty(name='Type', 
                        items=get_actor_type_items, 
                        default=0, 
                        update=callback)

def TrackIndexProperty(callback: Callable = None):
    def get_track_index_items(self, context: Context):
        return [((data.name, data.value, '')) for data in TrackIndex]

    return EnumProperty(
        items=get_track_index_items,
        name='TrackIndex',
        default=17,
        update=callback
    )


# -----------------------------------------------------------------------------
class MaterialProperty():
    def __filter_on_package(self, obj: Object):
        is_material = obj.name.startswith('M_')
        return self.material_package in obj.users_collection and is_material
    
    def get_material_path(self):
        self.material_package.name.rstrip('.')
        return self.material_package.name + '.' + self.material.name
    
    material_package: PointerProperty(type=bpy.types.Collection, name='Package')
    material: PointerProperty(type=Object, name='Material', poll=__filter_on_package)


# -----------------------------------------------------------------------------
class MET_PG_Widget(PropertyGroup):
    obj : PointerProperty(type=Object)


# -----------------------------------------------------------------------------
# ACTORS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class ActorProperty():

    def init(self):
        self.clear_widgets()
        b3d_utils.link_to_scene(self.id_data)
        self.id_data.display_type = 'TEXTURED'
    

    def draw(self, layout: UILayout):
        pass

    
    def clear_widgets(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()
    
    
    widgets: CollectionProperty(type=MET_PG_Widget)


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_PlayerStart(ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        scale = (.5, .5, -1)
        b3d_utils.set_mesh(self.id_data, scene.create_player_start(scale))
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'Player Start'


    def draw(self, layout: UILayout):
        layout.prop(self, 'is_time_trial')
        if self.is_time_trial:
            layout.prop(self, 'track_index')


    is_time_trial: BoolProperty(name='Is Time Trial')
    track_index: TrackIndexProperty()


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_StaticMesh(ActorProperty, MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()
        if self.id_data.type == 'MESH':
            b3d_utils.link_to_scene(self.id_data, scene.DEFAULT_PACKAGE)
            if self.id_data.data: return
            b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube())
        self.id_data.name = 'Static Mesh'
    
    
    def draw(self, layout: UILayout):
        layout.prop(self, 'use_prefab')

        if self.use_prefab:
            layout.prop(self, 'prefab')
        else:
            layout.prop(self, 'use_material')
            if self.use_material:
                layout = layout.column(align=True)
                layout.label(text='Material')
                layout.prop(self, 'material_package')
                layout.prop(self, 'material')

    
    def get_path(self) -> str:
        package = self.id_data.users_collection[0].name
        package.rstrip('.')
        return package + '.' + self.id_data.name

    
    def get_prefab_path(self) -> str:
        package = self.prefab.users_collection[0].name
        package.rstrip('.')
        return package + '.' + self.prefab.name

    
    def __on_use_prefab_update(self, context: Context):
        if self.use_prefab:
            self.ase_export = False

    
    def __on_prefab_update(self, context: Context):
        prefab = self.prefab
        if not prefab: 
            self.set_mesh(self.id_data)
            return
        b3d_utils.set_mesh(self.id_data, prefab.data)
        self.id_data.name = prefab.name + '_PREFAB'

    
    use_material: BoolProperty(name='Use Material', default=False)
    use_prefab: BoolProperty(name='Use Prefab', default=False, update=__on_use_prefab_update)
    prefab: PointerProperty(type=Object, name='Prefab', update=__on_prefab_update)


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Brush(ActorProperty, MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()
        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube())
        self.id_data.name = 'Brush'

    def draw(self, layout: UILayout):
        layout.prop(self, 'material_package')
        layout.prop(self, 'material')


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Ladder(ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        scale = (.5, .5, 2)
        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube(scale))
        self.id_data.display_type = 'WIRE'
        arrow = self.widgets.add()
        arrow.obj = b3d_utils.new_object('ARROW', b3d_utils.create_arrow(scale), scene.COLLECTION_WIDGETS, self.id_data)
        b3d_utils.set_object_selectable(arrow.obj, False)
        self.id_data.name = 'Ladder'


    def draw(self, layout: UILayout):
        layout.prop(self, 'is_pipe')


    def __on_is_pipe_update(self, context: Context):
        self.id_data.name = 'LADDER'
        if self.is_pipe:
            self.id_data.name = 'PIPE'

    
    is_pipe: BoolProperty(name='Is Pipe', update=__on_is_pipe_update)


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Swing(ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        self.id_data.display_type = 'WIRE'
        
        scale = Vector((1, 1, .5))

        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube(scale))

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
            arrow.obj = b3d_utils.new_object('ARROW', b3d_utils.create_arrow(s), scene.COLLECTION_WIDGETS, self.id_data)
            b3d_utils.set_object_selectable(arrow.obj, False)
        b3d_utils.transform(arrow0.obj.data, [m_t07_x , m_r90_x])
        b3d_utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
        b3d_utils.transform(arrow2.obj.data, [m_t07_x , m_r90_x, m_mir_x]) 
        self.id_data.name = 'Swing'
    
# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Zipline(ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()  
        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube())  

        if self.curve:
            b3d_utils.remove_object(self.curve)

        self.curve = scene.create_zipline()
        self.curve.location = self.id_data.location
        b3d_utils.set_parent(self.curve, self.id_data)
        b3d_utils.link_to_scene(self.curve, scene.DEFAULT_PACKAGE)
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'Zipline'
        b3d_utils.set_active(self.id_data)
        self.update_bounds(True)

    
    def draw(self, layout: UILayout):
        layout.prop(self, 'curve')
        layout.prop(self, 'auto_bb')
        layout.separator()

        if self.auto_bb:
            layout.prop(self, 'align_bb')
            layout.prop(self, 'bb_resolution')
            layout.separator()
            layout.prop(self, 'bb_scale')
            layout.separator()
            layout.prop(self, 'bb_offset')


    def update_bounds(self, force=False):   
        if not self.auto_bb: 
            return

        spline = self.curve.data.splines[0]
        points = spline.points
        
        p1 = points[0].co.xyz
        p2 = points[1].co.xyz
        p3 = points[2].co.xyz

        if not force:
            if p1 == self.c1 and p2 == self.c2 and p3 == self.c3:
                return
        
        self.c1 = p1; self.c2 = p2; self.c3 = p3

        verts = []; edges = []; segments = []; 

        def local_bounds(center, p1, p2):
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
            verts.append(center + -up + -right)

            e4 = len(verts)
            verts.append(center + up + -right)

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

        b3d_utils.set_mesh(self.id_data, b3d_utils.create_mesh(verts, edges, faces, self.id_data.name))


    def __force_update_bb_bounds(self, context):
        self.update_bounds(True)

    curve: PointerProperty(type=Object, name='Curve')
    auto_bb: BoolProperty(name='Automatic Bounding Box', default=True)
    align_bb: BoolProperty(name='Align', default=True, update=__force_update_bb_bounds)

    bb_resolution: IntProperty(name='Resolution', default=4, min=1, update=__force_update_bb_bounds)
    bb_scale: FloatVectorProperty(name='Scale', subtype='TRANSLATION', default=(1, 1, 1), update=__force_update_bb_bounds)
    bb_offset: FloatVectorProperty(name='Offset', subtype='TRANSLATION', update=__force_update_bb_bounds)

    c1: FloatVectorProperty(subtype='TRANSLATION')
    c2: FloatVectorProperty(subtype='TRANSLATION')
    c3: FloatVectorProperty(subtype='TRANSLATION')


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_SpringBoard(ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()   
        b3d_utils.set_mesh(self.id_data, scene.create_springboard())
        self.id_data.name = 'Spring Board'


# -----------------------------------------------------------------------------
class MET_ACTOR_PG_Checkpoint(ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        b3d_utils.set_mesh(self.id_data, scene.create_checkpoint())
        self.id_data.display_type = 'WIRE'
        self.id_data.name = 'Time Trial Checkpoint'

    def draw(self, layout: UILayout):
        b3d_utils.auto_gui_properties(self, layout)


    track_index: TrackIndexProperty()
    order_index: IntProperty(name='Order Index')
    custom_height: FloatProperty(name='CustomHeight')
    custom_width_scale: FloatProperty(name='Custom Width Scale')
    should_be_based: BoolProperty(name='Should Be Based')
    no_intermediate_time: BoolProperty(name='No Intermediate Time')
    no_respawn: BoolProperty(name='No Respawn')
    enabled: BoolProperty(name='Enabled')


# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class MET_OBJECT_PG_Actor(PropertyGroup):
    def draw(self, layout: UILayout):
        col = layout.column(align=True)
        if not self.user_editable:
            col.label(text=str(self.type))
            return

        col.prop(self, 'type')

        col = layout.column(align=True)
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
            case ActorType.CHECKPOINT:
                self.checkpoint.draw(col)

    
    def __on_type_update(self, context: Context):
        b3d_utils.set_active(self.id_data)

        match(self.type):
            case ActorType.PLAYER_START:
                self.player_start.init()
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
            case ActorType.CHECKPOINT:
                self.checkpoint.init()

    
    type: ActorTypeProperty(__on_type_update)
    user_editable: BoolProperty(default=True)

    player_start: PointerProperty(type=MET_ACTOR_PG_PlayerStart)
    static_mesh: PointerProperty(type=MET_ACTOR_PG_StaticMesh)
    brush: PointerProperty(type=MET_ACTOR_PG_Brush)
    ladder: PointerProperty(type=MET_ACTOR_PG_Ladder)
    swing: PointerProperty(type=MET_ACTOR_PG_Swing)
    zipline: PointerProperty(type=MET_ACTOR_PG_Zipline)
    springboard: PointerProperty(type=MET_ACTOR_PG_SpringBoard)
    checkpoint: PointerProperty(type=MET_ACTOR_PG_Checkpoint)



