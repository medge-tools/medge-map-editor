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
    def __init__(self, 
                 location: tuple[float, float, float] = (0, 0, 0),
                 rotation: tuple[float, float, float] = (0, 0, 0)) -> None:
        self._Location = Location(location)
        self._Rotation = Rotation(rotation)

    def __str__(self) -> str:
        pass

# =============================================================================
class WorldInfo(Actor):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return \
f'Begin Actor Class=WorldInfo Name=WorldInfo_0 Archetype=WorldInfo\'Engine.Default__WorldInfo\'\n\
End Actor\n'
    
# =============================================================================
class PlayerStart(Actor):
    def __init__(self, 
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float]) -> None:
        super().__init__(location, rotation)

    def __str__(self) -> str:
        return \
f'Begin Actor Class=PlayerStart Name=PlayerStart_0 Archetype=PlayerStart\'Engine.Default__PlayerStart\'\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
End Actor\n'

# =============================================================================
class StaticMesh(Actor):
    def __init__(self, 
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float],
                 static_mesh: str) -> None:
        super().__init__(location, rotation)
        self.StaticMesh: str = static_mesh
    
    def __str__(self) -> str:
        return \
f'Begin Actor Class=StaticMeshActor Name=StaticMeshActor_0 Archetype=StaticMeshActor\'Engine.Default__StaticMeshActor\'\n\
Begin Object Class=StaticMeshComponent Name=StaticMeshComponent0 Archetype=StaticMeshComponent\'Engine.Default__StaticMeshActor:StaticMeshComponent0\'\n\
StaticMesh=StaticMesh\'{self.StaticMesh}\'\n\
End Object\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
End Actor\n'

# =============================================================================
class Brush(Actor):
    def __init__(self, 
                 polylist : list[Polygon],
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float],
                 class_name: str = 'Brush',
                 package_name: str = 'Engine.Default__Brush',
                 csg_oper: str = 'CSG_Add') -> None:
        super().__init__(location, rotation)
        self._Package = package_name
        self._Class = class_name
        self._Archetype = class_name + '\'' + package_name + '\''
        self._CsgOper = csg_oper
        self._Settings : list[str] = []
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
        for prop in self._Settings:
            props += prop + '\n'
        return \
f'Begin Actor Class={self._Class} Name={self._Class}_0 Archetype={self._Archetype}\n\
Begin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent\'{self._Package}:BrushComponent0\'\n\
End Object\n\
CsgOper={self._CsgOper}\n\
{props}\
Begin Brush Name=Model_0\n\
Begin PolyList\n\
{polylist}\
End PolyList\n\
End Brush\n\
Brush=Model\'Model_0\'\n\
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
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float]
                 ) -> None:
        super().__init__(polylist, location, rotation,
                         'TdLadderVolume',
                         'TdGame.Default__TdLadderVolume',
                         'CSG_Active')

# =============================================================================
class Pipe(Ladder):
    def __init__(self, polylist: list[Polygon],
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float]) -> None:
        super().__init__(polylist, location, rotation)
        self._Settings.append('LadderType=LT_Pipe')

# =============================================================================
class Swing(Brush):
    def __init__(self, polylist: list[Polygon],
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float]) -> None:
        super().__init__(polylist, location, rotation,
                         'TdSwingVolume',
                         'TdGame.Default__TdSwingVolume',
                         'CSG_Active')

# =============================================================================
class Zipline(Brush):
    def __init__(self, 
                 polylist: list[Polygon],
                 rotation: tuple[float, float, float],
                 start: tuple[float, float, float],
                 middle: tuple[float, float, float],
                 end: tuple[float, float, float]) -> None:
        super().__init__(polylist, start, rotation,
                         'TdZiplineVolume',
                         'TdGame.Default__TdZiplineVolume',
                         'CSG_Active')
        self._Settings.append(f'Start=({Location(start)})')
        self._Settings.append(f'End=({Location(end)})')
        self._Settings.append(f'Middle=({Location(middle)})')
        self._Settings.append('bHideSplineMarkers=False')
        self._Settings.append('bAllowSplineControl=True')
        self._Settings.append('OldScale=(X=1.000000,Y=1.000000,Z=1.000000)')
        self._Settings.append(f'OldLocation=({Location(start)})')