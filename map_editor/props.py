import bpy
from bpy.props import *
from bpy.types import Object, PropertyGroup, Context, UILayout
from typing import Callable
from mathutils import Matrix

import math

from ..io.t3d.scene import ActorType, TrackIndex
from . import b3d_utils
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


# =============================================================================
class MET_MaterialProperty():
    def __filter_on_package(self, obj: Object):
        is_material = obj.name.startswith('M_')
        return self.material_package in obj.users_collection and is_material
    
    def get_material_path(self):
        self.material_package.name.rstrip('.')
        return self.material_package.name + '.' + self.material.name
    
    material_package: PointerProperty(type=bpy.types.Collection, name='Package')
    material: PointerProperty(type=Object, name='Material', poll=__filter_on_package)


# =============================================================================
class MET_PG_Widget(PropertyGroup):
    obj : PointerProperty(type=Object)


# =============================================================================
# ACTORS
# -----------------------------------------------------------------------------
# =============================================================================
class MET_ActorProperty():
    
    def __clear_widgets(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()
    
    def init(self):
        self.__clear_widgets()
        b3d_utils.link_to_scene(self.id_data)
        self.scale = (1, 1, 1)
        self.id_data.display_type = 'TEXTURED'
    
    def draw(self, layout: UILayout):
        pass

    
    widgets: CollectionProperty(type=MET_PG_Widget)
    scale: FloatVectorProperty(default=(1.0, 1.0, 1.0), subtype='TRANSLATION')


# =============================================================================
class MET_ACTOR_PG_PlayerStart(MET_ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        self.scale = (.5, .5, -1)
        b3d_utils.set_mesh(self.id_data, scene.create_player_start(self.scale))
        self.id_data.display_type = 'WIRE'

    def draw(self, layout: UILayout):
        layout.prop(self, 'is_time_trial')
        if self.is_time_trial:
            layout.prop(self, 'track_index')

    is_time_trial: BoolProperty(name='Is Time Trial')
    track_index: TrackIndexProperty()


# =============================================================================
class MET_ACTOR_PG_TimeTrial_Checkpoint(MET_ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        b3d_utils.set_mesh(self.id_data, scene.create_checkpoint())
        self.id_data.display_type = 'WIRE'

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


# =============================================================================
class MET_ACTOR_PG_StaticMesh(MET_ActorProperty, MET_MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()
        if self.id_data.type == 'MESH':
            b3d_utils.link_to_scene(self.id_data, scene.DEFAULT_PACKAGE)
            if self.id_data.data: return
            b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube())
    
    
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


# =============================================================================
class MET_ACTOR_PG_Brush(MET_ActorProperty, MET_MaterialProperty, PropertyGroup):
    
    def init(self):
        super().init()
        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube(self.scale))

    def draw(self, layout: UILayout):
        layout.prop(self, 'material_package')
        layout.prop(self, 'material')


# =============================================================================
class MET_ACTOR_PG_Ladder(MET_ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        self.scale = (.5, .5, 2)
        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube(self.scale))
        self.id_data.display_type = 'WIRE'
        arrow = self.widgets.add()
        arrow.obj = b3d_utils.new_object('ARROW', b3d_utils.create_arrow(self.scale), scene.COLLECTION_WIDGETS, self.id_data)
        b3d_utils.set_obj_selectable(arrow.obj, False)

    def draw(self, layout: UILayout):
        layout.prop(self, 'is_pipe')


    def __on_is_pipe_update(self, context: Context):
        self.id_data.name = 'LADDER'
        if self.is_pipe:
            self.id_data.name = 'PIPE'

    
    is_pipe: BoolProperty(name='Is Pipe', update=__on_is_pipe_update)


# =============================================================================
class MET_ACTOR_PG_Swing(MET_ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()
        
        self.scale = (1, 1, .5)

        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube(self.scale))

        self.id_data.display_type = 'WIRE'

        m_t07_x = Matrix.Translation((.7, 0, 0))
        m_t035_x = Matrix.Translation((.2, 0, 0))
        m_r90_x = Matrix.Rotation(math.radians(90), 3, (1, 0, 0))
        m_r90_y = Matrix.Rotation(math.radians(90), 3, (0, 1, 0))
        m_mir_x = Matrix.Scale(-1, 3, (1, 0, 0))
        arrow0 = self.widgets.add()
        arrow1 = self.widgets.add()
        arrow2 = self.widgets.add()
        for arrow in self.widgets:
            scale = self.scale * .3
            arrow.obj = b3d_utils.new_object('ARROW', b3d_utils.create_arrow(scale), scene.COLLECTION_WIDGETS, self.id_data)
            b3d_utils.set_obj_selectable(arrow.obj, False)
        b3d_utils.transform(arrow0.obj.data, [m_t07_x , m_r90_x])
        b3d_utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
        b3d_utils.transform(arrow2.obj.data, [m_t07_x , m_r90_x, m_mir_x]) 
    
# =============================================================================
class MET_ACTOR_PG_Zipline(MET_ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()  
        b3d_utils.set_mesh(self.id_data, b3d_utils.create_cube())      
        self.curve = scene.create_zipline()
        self.curve.location = self.id_data.location
        b3d_utils.set_parent(self.curve, self.id_data)
        b3d_utils.link_to_scene(self.curve, scene.DEFAULT_PACKAGE)
        self.id_data.display_type = 'WIRE'

    
    def draw(self, layout: UILayout):
        layout.column(align=True)
        layout.prop(self, 'curve')


    curve: PointerProperty(type=Object, name='Curve')


# =============================================================================
class MET_ACTOR_PG_SpringBoard(MET_ActorProperty, PropertyGroup):
    
    def init(self):
        super().init()   
        b3d_utils.set_mesh(self.id_data, scene.create_springboard())


# =============================================================================
# 
# -----------------------------------------------------------------------------
# =============================================================================
class ME_OBJECT_PG_Actor(PropertyGroup):
    def draw(self, layout: UILayout):
        col = layout.column(align=True)
        col.prop(self, 'type')

        col = layout.column(align=True)
        match(self.type):
            case ActorType.NONE:
                b3d_utils.link_to_scene(self.id_data)
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
                self.tt_checkpoint.draw(col)

    
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
                self.tt_checkpoint.init()

    
    type: ActorTypeProperty(__on_type_update)

    player_start: PointerProperty(type=MET_ACTOR_PG_PlayerStart)
    static_mesh: PointerProperty(type=MET_ACTOR_PG_StaticMesh)
    brush: PointerProperty(type=MET_ACTOR_PG_Brush)
    ladder: PointerProperty(type=MET_ACTOR_PG_Ladder)
    swing: PointerProperty(type=MET_ACTOR_PG_Swing)
    zipline: PointerProperty(type=MET_ACTOR_PG_Zipline)
    springboard: PointerProperty(type=MET_ACTOR_PG_SpringBoard)
    tt_checkpoint: PointerProperty(type=MET_ACTOR_PG_TimeTrial_Checkpoint)



