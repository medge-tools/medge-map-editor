import math
from mathutils import Vector
from enum import Enum

EULER_TO_URU = 65536 / math.tau

# -----------------------------------------------------------------------------
# RHS needs to be exactly the same as LHS it to work in Blender
class ActorType(str, Enum):
    NONE            = 'NONE'
    PLAYER_START    = 'PLAYER_START'
    STATIC_MESH     = 'STATIC_MESH'
    BRUSH           = 'BRUSH'
    LADDER          = 'LADDER'
    SWING           = 'SWING'
    ZIPLINE         = 'ZIPLINE'
    SPRINGBOARD     = 'SPRINGBOARD'
    CHECKPOINT      = 'CHECKPOINT'


# -----------------------------------------------------------------------------
class TrackIndex(str, Enum):
    ETTS_NONE               = 'ETTS_NONE'
    ETTS_CRANES_A01         = 'ETTS_CRANES_A01'
    ETTS_CRANES_B01         = 'ETTS_CRANES_B01'
    ETTS_CRANES_B02         = 'ETTS_CRANES_B02'
    ETTS_CRANES_C01         = 'ETTS_CRANES_C01'   
    ETTS_CRANES_D01         = 'ETTS_CRANES_D01'
    ETTS_EDGE_A01           = 'ETTS_EDGE_A01'
    ETTS_STORMDRAIN_A01     = 'ETTS_STORMDRAIN_A01'
    ETTS_STORMDRAIN_A02     = 'ETTS_STORMDRAIN_A02'
    ETTS_STORMDRAIN_B01     = 'ETTS_STORMDRAIN_B01'
    ETTS_STORMDRAIN_B02     = 'ETTS_STORMDRAIN_B02'
    ETTS_STORMDRAIN_B03     = 'ETTS_STORMDRAIN_B03'
    ETTS_CONVOY_A01         = 'ETTS_CONVOY_A01'
    ETTS_CONVOY_A02         = 'ETTS_CONVOY_A02'
    ETTS_CONVOY_B01         = 'ETTS_CONVOY_B01'
    ETTS_CONVOY_B02         = 'ETTS_CONVOY_B02'
    ETTS_MALL_A01           = 'ETTS_MALL_A01'
    ETTS_TUTORIAL_A01       = 'ETTS_TUTORIAL_A01'
    ETTS_TUTORIAL_A02       = 'ETTS_TUTORIAL_A02'
    ETTS_TUTORIAL_A03       = 'ETTS_TUTORIAL_A03'
    ETTS_FACTORY_A01        = 'ETTS_FACTORY_A01'
    ETTS_SKYSCRAPER_A01     = 'ETTS_SKYSCRAPER_A01'
    ETTS_SKYSCRAPER_B01     = 'ETTS_SKYSCRAPER_B01'
    ETTS_ESCAPE_A01         = 'ETTS_ESCAPE_A01'
    ETTS_ESCAPE_B01         = 'ETTS_ESCAPE_B01'


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
class Location(Point3D):
    def __init__(self, point : tuple[float, float, float] = (0, 0, 0)) -> None:
        super().__init__(point) 
        self.set_prefix('X', 'Y', 'Z')


# -----------------------------------------------------------------------------
class Rotation(Point3D):
    def __init__(self, point : tuple[float, float, float] = (0, 0, 0)) -> None:
        rotation = Vector(point) * EULER_TO_URU
        super().__init__(rotation)
        self.set_prefix('Roll', 'Pitch', 'Yaw')
        self.set_format('{:.0f}')


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# ACTOR
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Actor:
    def __init__(self, 
                 location: tuple[float, float, float] = (0, 0, 0),
                 rotation: tuple[float, float, float] = (0, 0, 0)) -> None:
        self.Location = Location(location)
        self.Rotation = Rotation(rotation)

    def __str__(self) -> str:
        pass


# -----------------------------------------------------------------------------
class PlayerStart(Actor):
    def __init__(self, 
                 location: tuple[float, float, float] = (0, 0, 0), 
                 rotation: tuple[float, float, float] = (0, 0, 0),
                 is_time_trial: bool = False,
                 track_index: TrackIndex = TrackIndex.ETTS_TUTORIAL_A01) -> None:
        super().__init__(location, rotation)
        self.is_time_trial = is_time_trial
        self.TrackIndex = track_index

    def __str__(self) -> str:
        if self.is_time_trial: 
            return\
f'Begin Actor Class=TdTimeTrialStart Name=TdTimeTrialStart_0 Archetype=TdTimeTrialStart\'TdGame.Default__TdTimeTrialStart\'\n\
Begin Object Class=RequestedTextureResources Name=RequestedTextureResources_0 Archetype=RequestedTextureResources\'TdGame.Default__TdTimeTrialStart:PlayerStartTextureResourcesObject\'\n\
End Object\n\
TrackIndex={self.TrackIndex}\n\
Location=({self.Location})\n\
Rotation=({self.Rotation})\n\
End Actor\n'
        else:
            return \
f'Begin Actor Class=PlayerStart Name=PlayerStart_0 Archetype=PlayerStart\'Engine.Default__PlayerStart\'\n\
Location=({self.Location})\n\
Rotation=({self.Rotation})\n\
End Actor\n'


# -----------------------------------------------------------------------------
class Checkpoint(Actor):
    def __init__(self, 
                 location: tuple[float, float, float] = (0, 0, 0), 
                 track_index: TrackIndex = TrackIndex.ETTS_TUTORIAL_A01,
                 order_index: int = 0,
                 no_intermediate_time: bool = False,
                 custom_height: float = 0.0,
                 custom_width_scale: float = 0.0,
                 no_respawn: bool = False,
                 enabled: bool = True,
                 should_be_based: bool = True) -> None:
        super().__init__(location, (0, 0, 0))
        self.TrackIndex = track_index
        self.OrderIndex = order_index
        self.NoIntermediateTime = no_intermediate_time
        self.CustomHeight = custom_height
        self.CustomWidthScale = custom_width_scale
        self.NoRespawn = no_respawn
        self.Enabled = enabled
        self.ShouldBeBased = should_be_based
    
    def __str__(self) -> str:
        return \
f'Begin Actor Class=TdTimerCheckpoint Name=TdTimerCheckpoint_0 Archetype=TdTimerCheckpoint\'TdGame.Default__TdTimerCheckpoint\'\n\
BelongToTracks(0)=(TrackIndex={self.TrackIndex},OrderIndex={self.OrderIndex},bNoIntermediateTime={self.NoIntermediateTime})\n\
CustomHeight={self.CustomHeight}\n\
CustomWidthScale={self.CustomWidthScale}\n\
bNoRespawn={self.NoRespawn}\n\
bEnabled={self.Enabled}\n\
bShouldBeBased={self.ShouldBeBased}\n\
Location=({self.Location})\n\
End Actor\n'
    

# -----------------------------------------------------------------------------
class StaticMesh(Actor):
    def __init__(self, 
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float],
                 static_mesh: str,
                 material: str = '') -> None:
        super().__init__(location, rotation)
        self.StaticMesh: str = static_mesh
        self.Material: str = material
    
    def __str__(self) -> str:
        return \
f'Begin Actor Class=StaticMeshActor Name=StaticMeshActor_0 Archetype=StaticMeshActor\'Engine.Default__StaticMeshActor\'\n\
Begin Object Class=StaticMeshComponent Name=StaticMeshComponent0 Archetype=StaticMeshComponent\'Engine.Default__StaticMeshActor:StaticMeshComponent0\'\n\
StaticMesh=StaticMesh\'{self.StaticMesh}\'\n\
Materials(0)=Material\'{self.Material}\'\n\
End Object\n\
Location=({self.Location})\n\
Rotation=({self.Rotation})\n\
End Actor\n'


# -----------------------------------------------------------------------------
class Brush(Actor):
    def __init__(self, 
                 polylist : list[Polygon],
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float],
                 class_name: str = 'Brush',
                 package_name: str = 'Engine.Default__Brush',
                 csg_oper: str = 'CSG_Add') -> None:
        super().__init__(location, rotation)
        self.Package = package_name
        self.Class = class_name
        self.Archetype = class_name + '\'' + package_name + '\''
        self.CsgOper = csg_oper
        self.Settings : list[str] = []
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
        for prop in self.Settings:
            props += prop + '\n'
        return \
f'Begin Actor Class={self.Class} Name={self.Class}_0 Archetype={self.Archetype}\n\
Begin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent\'{self.Package}:BrushComponent0\'\n\
End Object\n\
CsgOper={self.CsgOper}\n\
{props}\
Begin Brush Name=Model_0\n\
Begin PolyList\n\
{polylist}\
End PolyList\n\
End Brush\n\
Brush=Model\'Model_0\'\n\
Location=({self.Location})\n\
Rotation=({self.Rotation})\n\
End Actor\n'


# -----------------------------------------------------------------------------
# VOLUMES
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Ladder(Brush):
    def __init__(self, 
                 polylist : list[Polygon],
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float],
                 is_pipe: bool = False
                 ) -> None:
        super().__init__(polylist, location, rotation,
                         'TdLadderVolume',
                         'TdGame.Default__TdLadderVolume',
                         'CSG_Active')
        if is_pipe:
            self.Settings.append('LadderType=LT_Pipe')


# -----------------------------------------------------------------------------
class Swing(Brush):
    def __init__(self, polylist: list[Polygon],
                 location: tuple[float, float, float], 
                 rotation: tuple[float, float, float]) -> None:
        super().__init__(polylist, location, rotation,
                         'TdSwingVolume',
                         'TdGame.Default__TdSwingVolume',
                         'CSG_Active')


# -----------------------------------------------------------------------------
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
        self.Settings.append(f'Start=({Location(start)})')
        self.Settings.append(f'End=({Location(end)})')
        self.Settings.append(f'Middle=({Location(middle)})')
        self.Settings.append('bHideSplineMarkers=False')
        self.Settings.append('bAllowSplineControl=True')
        self.Settings.append('OldScale=(X=1.000000,Y=1.000000,Z=1.000000)')
        self.Settings.append(f'OldLocation=({Location(start)})')

