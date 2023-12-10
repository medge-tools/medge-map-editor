import bpy
from typing import Callable
from ..scene.types import ActorType

# =============================================================================
def ActorTypeProperty(func : Callable = None):
    return bpy.props.EnumProperty(
        items=[
            (ActorType.BRUSH, 'Brush', 'Brush'),
            (ActorType.LADDER, 'Ladder', 'TdLadderVolume'),
            (ActorType.PIPE, 'Pipe', 'TdLadderVolume'),
            (ActorType.SWING, 'Swing', 'TdSwingVolume')
        ],
        name='ActorType',
        default=ActorType.BRUSH,
        update=func
    )

# =============================================================================
class MET_PG_MESH_Actor(bpy.types.PropertyGroup):
    def switch_gizmo(self, context):
        pass

    type : ActorTypeProperty(switch_gizmo)