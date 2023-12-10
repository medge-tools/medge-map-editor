from mathutils import Vector
from enum import Enum
import math

EULER_TO_URU = 65536 / math.tau

# =============================================================================
class ActorType(str, Enum):
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
        self.set_prefix('Pitch', 'Roll', 'Yaw')
        self.set_format('{:+.0f}')

# =============================================================================
class Actor:
    def __str__(self) -> str:
        pass

# =============================================================================
class WorldInfo(Actor):
    __id = 0
    def __init__(self, name : str = 'WorldInfo_') -> None:
        self.Name = name + str(WorldInfo.__id)
        WorldInfo.__id += 1

    def __str__(self) -> str:
        return \
f'Begin Actor Class=WorldInfo Name={self.Name} Archetype=WorldInfo\'Engine.Default__WorldInfo\'\n\
End Actor\n'