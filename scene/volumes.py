from .brush import *

# =============================================================================
class ArrowComponent(Component):
    def __str__(self) -> str:
        return \
'Begin Object Class=ArrowComponent Name=WallDir Archetype=ArrowComponent\'TdGame.Default__TdLadderVolume:WallDir\'\n\
End Object\n'

# =============================================================================
class TdMoveVolumeRenderComponent(Component): 
    def __str__(self) -> str:
        return \
'Begin Object Class=TdMoveVolumeRenderComponent Name=MovementMesh ObjName=TdMoveVolumeRenderComponent_0 Archetype=TdMoveVolumeRenderComponent\'TdGame.Default__TdLadderVolume:MovementMesh\'\n\
End Object\n'

# =============================================================================
class Ladder(Brush):
    def __init__(self, 
                 polylist : list[Polygon],
                 actor_name : str = 'TdLadderVolume_',
                 brush_name : str = 'Model_') -> None:
        super().__init__(polylist, actor_name, brush_name, 'TdGame.Default__TdLadderVolume:BrushComponent0')
        self._Class='TdLadderVolume'
        self._Archetype='TdLadderVolume\'TdGame.Default__TdLadderVolume\''
        self._CsgOper='CSG_Active'
        self._Components.append(ArrowComponent())
        self._Components.append(TdMoveVolumeRenderComponent())
