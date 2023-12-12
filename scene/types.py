from mathutils import Vector
from enum import Enum
import math

EULER_TO_URU = 65536 / math.tau

# =============================================================================
class ActorType(str, Enum):
    NONE = 'NONE'
    PLAYERSTART = 'PLAYERSTART'
    BRUSH = 'BRUSH'
    LADDER = 'LADDER'
    PIPE = 'PIPE'
    SWING = 'SWING'
    ZIPLINE = 'ZIPLINE'

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
        self.format = '{:+.6f}'

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
        self.set_format('{:+.0f}')

# =============================================================================
class Actor:
    def __init__(self) -> None:
        self._Location = Location()
        self._Rotation = Rotation()

    @property
    def Location(self):
        return self.__Location

    @Location.setter
    def Location(self, loc : tuple[float, float, float]):
        self._Location = Location(loc)

    @property
    def Rotation(self):
        return self._Rotation
    
    @Rotation.setter
    def Rotation(self, euler : tuple[float, float, float]):
        self._Rotation = Rotation(Vector(euler) * EULER_TO_URU)

    def __str__(self) -> str:
        pass

# =============================================================================
class WorldInfo(Actor):
    __id = 0
    def __init__(self, name : str = 'WorldInfo_') -> None:
        super().__init__()
        self.Name = name + str(WorldInfo.__id)
        WorldInfo.__id += 1

    def __str__(self) -> str:
        return \
f'Begin Actor Class=WorldInfo Name={self.Name} Archetype=WorldInfo\'Engine.Default__WorldInfo\'\n\
End Actor\n'
    
# =============================================================================
class PlayerStart(Actor):
    __id = 0
    def __init__(self, name : str = 'PlayerStart_') -> None:
        super().__init__()
        self.Name = name + str(PlayerStart.__id)
        PlayerStart.__id += 1

    def __str__(self) -> str:
        return \
f'Begin Actor Class=PlayerStart Name={self.Name} Archetype=PlayerStart\'Engine.Default__PlayerStart\'\n\
Begin Object Class=RequestedTextureResources Name=RequestedTextureResources_0 Archetype=RequestedTextureResources\'Engine.Default__PlayerStart:PlayerStartTextureResourcesObject\'\
End Object\n\
Begin Object Class=CylinderComponent Name=CollisionCylinder Archetype=CylinderComponent\'Engine.Default__PlayerStart:CollisionCylinder\'\n\
End Object\n\
Begin Object Class=SpriteComponent Name=Sprite Archetype=SpriteComponent\'Engine.Default__PlayerStart:Sprite\'\n\
End Object\n\
Begin Object Class=SpriteComponent Name=Sprite2 Archetype=SpriteComponent\'Engine.Default__PlayerStart:Sprite2\'\n\
End Object\n\
Begin Object Class=ArrowComponent Name=Arrow Archetype=ArrowComponent\'Engine.Default__PlayerStart:Arrow\'\n\
End Object\n\
Begin Object Class=PathRenderingComponent Name=PathRenderer Archetype=PathRenderingComponent\'Engine.Default__PlayerStart:PathRenderer\'\n\
End Object\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
Name="{self.Name}"\n\
End Actor\n'