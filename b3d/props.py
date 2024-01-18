import bpy
import math
from typing import Callable
from mathutils import Matrix
from ..t3d.scene import ActorType
from . import utils
from . import medge_tools as medge

# =============================================================================
def ActorTypeProperty(callback : Callable = None):
    return bpy.props.EnumProperty(
        items=[
            (ActorType.NONE, 'None', 'None'),
            (ActorType.PLAYERSTART, 'PlayerStart', 'PlayerStart'),
            (ActorType.BRUSH, 'Brush', 'Brush'),
            (ActorType.LADDER, 'Ladder', 'TdLadderVolume'),
            (ActorType.PIPE, 'Pipe', 'TdLadderVolume'),
            (ActorType.SWING, 'Swing', 'TdSwingVolume'),
            (ActorType.ZIPLINE, 'Zipline', 'TdZiplineVolume'),
            (ActorType.SPRINGBOARD, 'Springboard', 'P_Gameplay.SpringBoardHigh_ColMesh'),
            (ActorType.STATICMESH, 'StaticMesh', 'StaticMeshActor')
        ],
        name='ActorType',
        default=ActorType.NONE,
        update=callback
    )
# =============================================================================
ACTOR_DEFAULT_SCALE = {
    ActorType.PLAYERSTART   : (.5, .5, -1),
    ActorType.BRUSH         : (1, 1, 1),
    ActorType.LADDER        : (.5, .5, 2), 
    ActorType.PIPE          : (.5, .5, 2),
    ActorType.SWING         : (1, 1, .5),
    ActorType.ZIPLINE       : (1, 1, 1),
    ActorType.SPRINGBOARD   : (1, 1, 1),
    ActorType.STATICMESH    : (1, 1, 1)
}

# =============================================================================
ACTOR_DEFAULT_STATIC_MESH = {
    ActorType.PLAYERSTART   : ('MyPackage', ''),
    ActorType.BRUSH         : ('MyPackage', ''),
    ActorType.LADDER        : ('P_Generic.Ladders', 'S_LadderSystem_01b'),
    ActorType.PIPE          : ('P_Pipes.PipeSystem_03', 'S_PipeSystem_03h'),
    ActorType.SWING         : ('P_RunnerObjects.SwingPole_01', 'S_SwingPole_01c'),
    ActorType.ZIPLINE       : ('MyPackage', ''),
    ActorType.SPRINGBOARD   : ('P_Gameplay.SpringBoard', 'SpringBoardHigh_ColMesh'),
    ActorType.STATICMESH    : ('MyPackage', ''),
}

# =============================================================================
class ME_PG_Gizmo(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object)

# =============================================================================
class ME_OBJECT_PG_Actor(bpy.types.PropertyGroup):
    def __reset(self):
        self.scale = ACTOR_DEFAULT_SCALE[self.type]
        self.ase_export = False
    
    def __clear_widgets(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()

    def __set_mesh(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.SPRINGBOARD:
                utils.set_mesh(obj, medge.create_springboard())
            case ActorType.PLAYERSTART:
                utils.set_mesh(obj, medge.create_flag(self.scale))
            case ActorType.ZIPLINE:
                # Creat volume
                utils.set_mesh(obj, medge.create_cube(self.scale)) 
                # Create zipline
                path = medge.new_actor(ActorType.STATICMESH, 'CURVE')
                path.parent = obj
                path.location = 0, 0, 0
                utils.set_mesh(path, medge.create_curve(step=8))
                me_actor = medge.get_me_actor(path)
                me_actor.static_mesh_name = 'Zipline'
                me_actor.ase_export = True
                path.data.bevel_depth = 0.04
            case _:
                if obj.data: return
                if obj.type == 'MESH':
                    utils.set_mesh(obj, medge.create_cube(self.scale))

    def __set_display_type(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.BRUSH | ActorType.SPRINGBOARD | ActorType.STATICMESH:
                obj.display_type = 'TEXTURED'
            case _:
                obj.display_type = 'WIRE'

    def __add_widget(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.LADDER | ActorType.PIPE:
                arrow = self.widgets.add()
                arrow.obj = utils.new_object('ARROW', medge.create_arrow(self.scale), utils.COLLECTION_WIDGET, obj)
                utils.set_obj_selectable(arrow.obj, False)
            case ActorType.SWING:
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
                    arrow.obj = utils.new_object('ARROW', medge.create_arrow(scale), utils.COLLECTION_WIDGET, obj)
                    utils.set_obj_selectable(arrow.obj, False)
                utils.transform(arrow0.obj.data, [m_t07_x , m_r90_x])
                utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
                utils.transform(arrow2.obj.data, [m_t07_x , m_r90_x, m_mir_x])                

    def __on_type_update(self, context: bpy.types.Context):
        obj = context.active_object
        self.__reset()
        self.__clear_widgets()
        self.__set_mesh(obj)
        self.__set_display_type(obj)
        self.__add_widget(obj)
        obj.name = str(self.type)
        utils.set_active(obj)
        self.parent = obj

    def __on_static_mesh_name_update(self, context: bpy.types.Context):
        if self.static_mesh_use_prefab: return
        if context.active_object != self.parent: return
        obj = context.active_object
        if obj.name != self.static_mesh_name:
            obj.name = self.static_mesh_name
        # obj.name might be changed by Blender; we update self.static_mesh_name in utils.on_depsgraph_update

    def __on_static_mesh_prefab_update(self, context: bpy.types.Context):
        obj = context.active_object
        prefab = self.static_mesh_prefab
        if not prefab: return
        utils.set_mesh(obj, prefab.data)
        me_actor = medge.get_me_actor(prefab)
        package = me_actor.static_mesh_package
        name = me_actor.static_mesh_name
        if not package or not name:
            self.report({'WARNING'}, 'Prefab has no package data')

    def __on_static_mesh_package_update(self, context : bpy.types.Context):
        self.static_mesh_package.rstrip('.')

    def get_static_mesh(self) -> str:
        return self.static_mesh_package + '.' + self.static_mesh_name

    type : ActorTypeProperty(__on_type_update)
    scale : bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), subtype='TRANSLATION')
    widgets : bpy.props.CollectionProperty(type=ME_PG_Gizmo)
    parent : bpy.props.PointerProperty(type=bpy.types.Object)
    static_mesh_package : bpy.props.StringProperty(name='Package', update=__on_static_mesh_package_update)
    static_mesh_name : bpy.props.StringProperty(name='Name', update=__on_static_mesh_name_update)
    static_mesh_use_prefab : bpy.props.BoolProperty(name='Use Prefab', default=False)
    static_mesh_prefab : bpy.props.PointerProperty(type=bpy.types.Object, name='Prefab', update=__on_static_mesh_prefab_update)
    enable_material : bpy.props.BoolProperty(name='Enable Material', default=False, )
    material_package : bpy.props.StringProperty(name='Package')
    material_name : bpy.props.StringProperty(name='Name')
    ase_export : bpy.props.BoolProperty(name='Export ASE', default=False, description='Mesh will be export as .ase file.')

# =============================================================================
def copy_me_actor(src : ME_OBJECT_PG_Actor, dest : ME_OBJECT_PG_Actor):
    dest.scale                  = src.scale
    dest.static_mesh_package    = src.static_mesh_package
    dest.static_mesh_name       = src.static_mesh_name
    dest.enable_material        = src.enable_material
    dest.material_package       = src.material_package
    dest.material_name          = src.material_name
    dest.ase_export             = src.ase_export

# =============================================================================
def on_depsgraph_update_post_sync_static_mesh_name(scene : bpy.types.Scene, depsgraph : bpy.types.Depsgraph):
    for obj in scene.objects:
        me_actor = medge.get_me_actor(obj)
        if me_actor is None: continue
        if me_actor.static_mesh_name != obj.name:
            me_actor.static_mesh_name = obj.name