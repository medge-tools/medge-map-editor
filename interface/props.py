import bpy
from typing import Callable

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
            (ActorType.SWING, 'Swing', 'TdSwingVolume')
        ],
        name='ActorType',
        default=ActorType.NONE,
        update=callback
    )

class ME_PG_Gizmo(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object)

# =============================================================================
class ME_OBJECT_PG_Actor(bpy.types.PropertyGroup):
    def switch_gizmo(self, context : bpy.types.Context):
        obj = context.active_object
        self.clear_gizmos()

        # Set display type
        match(self.type):
            case ActorType.BRUSH:
                obj.display_type = 'TEXTURED'
            case _:
                obj.display_type = 'WIRE'
        
        # Add static gizmos
        match(self.type):
            case ActorType.LADDER:
                gm = self.gizmos.add()
                gm.obj = utils.add_arrow(obj.scale)
                gm.obj.parent = obj

    def clear_gizmos(self):
        for gm in self.gizmos:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.gizmos.clear()

    type: ActorTypeProperty(switch_gizmo)
    gizmos: bpy.props.CollectionProperty(type=ME_PG_Gizmo)