import bpy
import math
from typing import Callable
from mathutils import Matrix
from ..t3d.scene import ActorType
from . import utils
from . import creator

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
    ActorType.PLAYERSTART   : ('', ''),
    ActorType.BRUSH         : ('', ''),
    ActorType.LADDER        : ('P_Generic.Ladders', 'S_LadderSystem_01b'),
    ActorType.PIPE          : ('P_Pipes.PipeSystem_03', 'S_PipeSystem_03h'),
    ActorType.SWING         : ('P_RunnerObjects.SwingPole_01', 'S_SwingPole_01c'),
    ActorType.ZIPLINE       : ('', ''),
    ActorType.SPRINGBOARD   : ('P_Gameplay.SpringBoard', 'SpringBoardHigh_ColMesh'),
    ActorType.STATICMESH    : ('', ''),
}

# =============================================================================
class ME_PG_Gizmo(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object)

# =============================================================================
class ME_OBJECT_PG_Actor(bpy.types.PropertyGroup):
    def __clear_widget(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()

    def __set_default_static_mesh(self):
        self.static_mesh_package, self.static_mesh_name = ACTOR_DEFAULT_STATIC_MESH[self.type]
        self.enable_static_mesh = False
        if(self.static_mesh_package and self.static_mesh_name): 
            self.enable_static_mesh = True

    def __set_mesh(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.SPRINGBOARD:
                utils.set_mesh(obj, creator.create_springboard())
            case ActorType.PLAYERSTART:
                utils.set_mesh(obj, creator.create_flag(self.scale))
            case _:
                utils.set_mesh(obj, creator.create_cube(self.scale))

    def __set_display_type(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.BRUSH | ActorType.SPRINGBOARD:
                obj.display_type = 'TEXTURED'
            case _:
                obj.display_type = 'WIRE'

    def __add_widget(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.LADDER | ActorType.PIPE:
                arrow = self.widgets.add()
                arrow.obj = utils.new_object('ARROW', creator.create_arrow(self.scale), utils.COLLECTION_WIDGET, obj)
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
                    arrow.obj = utils.new_object('ARROW', creator.create_arrow(scale), utils.COLLECTION_WIDGET, obj)
                    utils.set_obj_selectable(arrow.obj, False)
                utils.transform(arrow0.obj.data, [m_t07_x, m_r90_x])
                utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
                utils.transform(arrow2.obj.data, [m_t07_x, m_r90_x, m_mir_x])
            case ActorType.ZIPLINE:
                path = self.widgets.add()
                path.obj = utils.new_object('CURVE', creator.create_curve(8), utils.COLLECTION_WIDGET, obj)

    def __on_type_update(self, context : bpy.types.Context):
        obj = context.active_object
        obj.scale = 1, 1, 1
        self.scale = ACTOR_DEFAULT_SCALE[self.type]
        self.__clear_widget()
        self.__set_default_static_mesh()
        self.__set_mesh(obj)
        self.__set_display_type(obj)
        self.__add_widget(obj)
        obj.name = str(self.type)
        utils.set_active(obj)

    def add_static_mesh(self, context : bpy.types.Context):
        prefab = self.static_mesh_prefab
        if(not prefab): return False
        parent = context.active_object
        obj = creator.new_actor(ActorType.STATICMESH)
        utils.set_mesh(obj, prefab.data)
        obj.parent = parent
        me_actor = utils.get_me_actor(obj)
        me_actor.copy_static_mesh(utils.get_me_actor(parent))
        return True
    
    def copy_static_mesh(self, actor : 'ME_OBJECT_PG_Actor'):
        self.enable_static_mesh = True
        self.static_mesh_package = actor.static_mesh_package
        self.static_mesh_name = actor.static_mesh_name

    type: ActorTypeProperty(__on_type_update)
    scale: bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), subtype='TRANSLATION')
    widgets: bpy.props.CollectionProperty(type=ME_PG_Gizmo)
    enable_static_mesh: bpy.props.BoolProperty(name="Enable Static Mesh", default=False)
    static_mesh_package: bpy.props.StringProperty(name="Package")
    static_mesh_name: bpy.props.StringProperty(name="Name")
    static_mesh_prefab: bpy.props.PointerProperty(type=bpy.types.Object, name="Placeholder")
    enable_material: bpy.props.BoolProperty(name="Enable Material", default=False, )
    material_package: bpy.props.StringProperty(name="Package")
    material_name: bpy.props.StringProperty(name="Name")