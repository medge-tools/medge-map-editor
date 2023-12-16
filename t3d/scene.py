import math
from mathutils import Vector
from enum import Enum

EULER_TO_URU = 65536 / math.tau

# =============================================================================
class ActorType(str, Enum):
    NONE        = 'NONE'
    PLAYERSTART = 'PLAYERSTART'
    BRUSH       = 'BRUSH'
    LADDER      = 'LADDER'
    PIPE        = 'PIPE'
    SWING       = 'SWING'
    ZIPLINE     = 'ZIPLINE'
    SPRINGBOARD = 'SPRINGBOARD'
    STATICMESH  = 'STATICMESH'

# =============================================================================
class Point3D(Vector):
    def __init__(self, point : tuple[float, float, float] = (0, 0, 0)) -> None:
        super().__init__() 
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.__prefix_x : str = ''
        self.__prefix_y : str = ''
        self.__prefix_z : str = ''
        self.format = '{:.6f}'

    def __str__(self) -> str:
        x = self.format.format(self.x)
        y = self.format.format(self.y)
        z = self.format.format(self.z)
        return f'{self.__prefix_x}{x},{self.__prefix_y}{y},{self.__prefix_z}{z}'
    
    def set_prefix(self, x : str, y : str, z : str):
        self.__prefix_x = x + '='
        self.__prefix_y = y + '='
        self.__prefix_z = z + '='

    def set_format(self, f : str):
        self.format = f

# =============================================================================
class Location(Point3D):
    def __init__(self, point : tuple[float, float, float] = (0, 0, 0)) -> None:
        super().__init__(point) 
        self.set_prefix('X', 'Y', 'Z')

# =============================================================================
class Rotation(Point3D):
    def __init__(self, point : tuple[float, float, float] = (0, 0, 0)) -> None:
        super().__init__(point)
        self.set_prefix('Roll', 'Pitch', 'Yaw')
        self.set_format('{:.0f}')

# =============================================================================
class Polygon:
    def __init__(
            self, 
            origin : tuple[float, float, float], 
            normal : tuple[float, float, float],
            u : tuple[float, float, float],
            v : tuple[float, float, float],
            verts : list[tuple[float, float, float]],
            texture : str = None,
            flags : int = 3585) -> None:
        self.Flags = flags
        self.Texture = texture
        self.Link : int = None
        self.__Origin = Point3D(origin)
        self.__Normal = Point3D(normal)
        self.__TextureU = Point3D(u)
        self.__TextureV = Point3D(v)
        self.__Vertices = [Point3D(x) for x in verts]

    def __str__(self) -> str:
        texture = f'Texture={self.Texture} ' if self.Texture else ''
        link = f'Link={self.Link} ' if self.Link or self.Link == 0 else ''
        verts = ''
        for v in self.__Vertices:
            verts += f'\tVertex   {v}\n'
        return \
f'Begin Polygon {texture}Flags=3584 {link}\n\
\tOrigin   {self.__Origin}\n\
\tNormal   {self.__Normal}\n\
\tTextureU {self.__TextureU}\n\
\tTextureV {self.__TextureV}\n\
{verts}\
End Polygon\n'

# =============================================================================
# ACTOR
# -----------------------------------------------------------------------------
# =============================================================================
class Actor:
    def __init__(self) -> None:
        self._Location = Location()
        self._Rotation = Rotation()

    # https://stackoverflow.com/questions/17576009/python-class-property-use-setter-but-evade-getter
    def Location(self, loc : tuple[float, float, float]):
        self._Location = Location(loc)
    Location = property(None, Location)

    def Rotation(self, euler : tuple[float, float, float]):
        self._Rotation = Rotation(Vector(euler) * EULER_TO_URU)
    Rotation = property(None, Rotation)

    def __str__(self) -> str:
        pass


# =============================================================================
class Brush(Actor):
    def __init__(self, 
                 polylist : list[Polygon],
                 actor_name : str = 'Brush',
                 brush_name : str = 'Model',
                 brush_comp_type : str = 'Engine.Default__Brush:BrushComponent0') -> None:
        super().__init__()
        self._Class = 'Brush'
        self._Archetype = 'Brush\'Engine.Default__Brush\''
        self._CsgOper = 'CSG_Add'
        self._Properties : list[str] = []
        self.ActorName = actor_name
        self.BrushName = brush_name
        self._BrushCompType = brush_comp_type
        self.PolyList : list[Polygon] = polylist

    def __str__(self) -> str:
        polylist = ''
        link = 0
        for poly in self.PolyList:
            if not poly.Texture:
                poly.Link = link
                link += 1
            polylist += str(poly)
        props = ''
        for prop in self._Properties:
            props += prop + '\n'
        return \
f'Begin Actor Class={self._Class} Name={self.ActorName}_0 Archetype={self._Archetype}\n\
Begin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent\'{self._BrushCompType}\'\n\
End Object\n\
CsgOper={self._CsgOper}\n\
{props}\
Begin Brush Name={self.BrushName}_0\n\
Begin PolyList\n\
{polylist}\
End PolyList\n\
End Brush\n\
Brush=Model\'{self.BrushName}_0\'\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
End Actor\n'

# =============================================================================
class WorldInfo(Actor):
    def __init__(self, name : str = 'WorldInfo_') -> None:
        super().__init__()
        self.Name = name

    def __str__(self) -> str:
        return \
f'Begin Actor Class=WorldInfo Name={self.Name}_0 Archetype=WorldInfo\'Engine.Default__WorldInfo\'\n\
End Actor\n'
    
# =============================================================================
class PlayerStart(Actor):
    def __init__(self, name : str = 'PlayerStart') -> None:
        super().__init__()
        self.Name = name

    def __str__(self) -> str:
        return \
f'Begin Actor Class=PlayerStart Name={self.Name}_0 Archetype=PlayerStart\'Engine.Default__PlayerStart\'\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
End Actor\n'

# =============================================================================
class StaticMesh(Actor):
    def __init__(self, 
                 static_mesh: str,
                 name : str = 'StaticMeshActor'
                 ) -> None:
        super().__init__()
        self.Name = name
        self.StaticMesh: str = static_mesh
    
    def __str__(self) -> str:
        return \
f'Begin Actor Class=StaticMeshActor Name={self.Name}_0 Archetype=StaticMeshActor\'Engine.Default__StaticMeshActor\'\n\
Begin Object Class=StaticMeshComponent Name=StaticMeshComponent0 Archetype=StaticMeshComponent\'Engine.Default__StaticMeshActor:StaticMeshComponent0\'\n\
StaticMesh=StaticMesh\'{self.StaticMesh}\'\n\
End Object\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
End Actor\n'

# =============================================================================
# VOLUMES
# -----------------------------------------------------------------------------
# =============================================================================
class Ladder(Brush):
    def __init__(self, 
                 polylist : list[Polygon],
                 actor_name : str = 'TdLadderVolume_',
                 brush_name : str = 'Model_') -> None:
        super().__init__(polylist, 
                         actor_name, 
                         brush_name, 
                         'TdGame.Default__TdLadderVolume:BrushComponent0')
        self._Class='TdLadderVolume'
        self._Archetype='TdLadderVolume\'TdGame.Default__TdLadderVolume\''
        self._CsgOper='CSG_Active'

# =============================================================================
class Pipe(Ladder):
    def __init__(self, 
                 polylist: list[Polygon], 
                 actor_name: str = 'TdLadderVolume_', 
                 brush_name: str = 'Model_') -> None:
        super().__init__(polylist, actor_name, brush_name)
        self._Properties.append('LadderType=LT_Pipe')

# =============================================================================
class Swing(Brush):
    def __init__(self, 
                 polylist: list[Polygon], 
                 actor_name: str = 'TdSwingVolume_', 
                 brush_name: str = 'Model_') -> None:
        super().__init__(polylist, actor_name, brush_name)
        self._Class='TdSwingVolume'
        self._Archetype='TdSwingVolume\'TdGame.Default__TdSwingVolume\''
        self._CsgOper='CSG_Active'