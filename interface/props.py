import bpy
from typing import Callable
from mathutils import Matrix
import math
from . import utils
from ..scene.types import ActorType

# =============================================================================
def ActorTypeProperty(callback : Callable = None):
    return bpy.props.EnumProperty(
        items=[
            (ActorType.NONE, 'None', 'None'),
            (ActorType.PLAYERSTART, 'Player Start', 'Player Start'),
            (ActorType.BRUSH, 'Brush', 'Brush'),
            (ActorType.LADDER, 'Ladder', 'TdLadderVolume'),
            (ActorType.PIPE, 'Pipe', 'TdLadderVolume'),
            (ActorType.SWING, 'Swing', 'TdSwingVolume'),
            (ActorType.ZIPLINE, 'Zipline', 'TdZiplineVolume')
        ],
        name='ActorType',
        default=ActorType.NONE,
        update=callback
    )

class ME_PG_Gizmo(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object)

# =============================================================================
class ME_OBJECT_PG_Actor(bpy.types.PropertyGroup):
    def __clear_gizmos(self):
        for gm in self.gizmos:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.gizmos.clear()

    def __set_display_type(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.BRUSH:
                obj.display_type = 'TEXTURED'
            case _:
                obj.display_type = 'WIRE'

    def __add_static_gizmos(self, obj: bpy.types.Object):
        match(self.type):
            case ActorType.LADDER:
                arrow = self.gizmos.add()
                arrow.obj = utils.add_arrow(obj.scale)
                arrow.obj.parent = obj
            case ActorType.SWING:
                m_t1_x = Matrix.Translation((1, 0, 0))
                m_r90_x = Matrix.Rotation(math.radians(90), 3, (1, 0, 0))
                m_r90_y = Matrix.Rotation(math.radians(90), 3, (0, 1, 0))
                m_mir_x = Matrix.Scale(-1, 3, (1, 0, 0))
                arrow0 = self.gizmos.add()
                arrow1 = self.gizmos.add()
                arrow2 = self.gizmos.add()
                scale = obj.scale * .5
                arrow0.obj = utils.add_arrow(scale)
                arrow1.obj = utils.add_arrow(scale)
                arrow2.obj = utils.add_arrow(scale)
                utils.transform(arrow0.obj, [m_t1_x, m_r90_x])
                utils.transform(arrow1.obj, [m_t1_x, m_r90_x, m_r90_y])
                utils.transform(arrow2.obj, [m_t1_x, m_r90_x, m_mir_x])
                arrow0.obj.parent = obj
                arrow1.obj.parent = obj
                arrow2.obj.parent = obj

    def on_type_update(self, context : bpy.types.Context):
        obj = context.active_object
        self.__clear_gizmos()
        self.__set_display_type(obj)
        self.__add_static_gizmos(obj)
        obj.name = str(self.type)

    type: ActorTypeProperty(on_type_update)
    gizmos: bpy.props.CollectionProperty(type=ME_PG_Gizmo)