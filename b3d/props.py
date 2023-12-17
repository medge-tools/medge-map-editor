import bpy
from typing import Callable
from mathutils import Matrix
import math
from . import utils
from ..t3d.scene import ActorType

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
class ME_PG_Gizmo(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object)

# =============================================================================

class ME_OBJECT_PG_Actor(bpy.types.PropertyGroup):
    def __clear_widget(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()

    def __set_mesh(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.SPRINGBOARD:
                utils.set_mesh(obj, utils.create_springboard())
            case ActorType.PLAYERSTART:
                utils.set_mesh(obj, utils.create_flag(self.scale))
            case _:
                utils.set_mesh(obj, utils.create_cube(self.scale))

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
                arrow.obj = utils.new_object('ARROW', utils.create_arrow(self.scale), utils.COLLECTION_WIDGET)
                arrow.obj.parent = obj
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
                utils.transform(arrow0.obj.data, [m_t07_x, m_r90_x])
                utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
                utils.transform(arrow2.obj.data, [m_t07_x, m_r90_x, m_mir_x])
                for arrow in self.widgets:
                    scale = self.scale * .3
                    arrow.obj = utils.new_object('ARROW', utils.create_arrow(scale), utils.COLLECTION_WIDGET)
                    arrow.obj.parent = obj
                    utils.set_obj_selectable(arrow.obj, False)
            case ActorType.ZIPLINE:
                path = self.widgets.add()
                path.obj = utils.new_object('CURVE', utils.create_curve(8), utils.COLLECTION_WIDGET)
                path.obj.parent = obj

    def on_type_update(self, context : bpy.types.Context):
        obj = context.active_object
        obj.scale = 1, 1, 1
        self.scale = ACTOR_DEFAULT_SCALE[self.type]
        self.__clear_widget()
        self.__set_mesh(obj)
        self.__set_display_type(obj)
        self.__add_widget(obj)
        obj.name = str(self.type)
        utils.set_active(obj)

    type: ActorTypeProperty(on_type_update)
    scale: bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0),subtype='TRANSLATION')
    widgets: bpy.props.CollectionProperty(type=ME_PG_Gizmo)