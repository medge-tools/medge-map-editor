import math
from mathutils import Vector

from enum import Enum

from ... import b3d_utils


EULER_TO_URU = 65536 / math.tau


# -----------------------------------------------------------------------------
class ActorType(str, Enum):
    def __new__(cls, _value:str):
        obj = str.__new__(cls, _value)
        obj._value_ = _value
        obj.label = _value
    
        return obj


    NONE            = 'None'
    BRUSH           = 'Brush'
    STATIC_MESH     = 'StaticMesh'
    LADDER_VOLUME   = 'Ladder'
    SWING_VOLUME    = 'Swing'
    ZIPLINE         = 'Zipline'
    BLOCKING_VOLUME = 'BlockingVolume'
    TRIGGER_VOLUME  = 'TriggerVolume'
    KILL_VOLUME     = 'KillVolume'
    PLAYER_START    = 'PlayerStart'
    CHECKPOINT      = 'Checkpoint'


# -----------------------------------------------------------------------------
class TrackIndex(str, Enum):
    ETTS_NONE          = 'ETTS_NONE'
    ETTS_CRANESA01     = 'ETTS_CRANESA01'
    ETTS_CRANESB01     = 'ETTS_CRANESB01'
    ETTS_CRANESB02     = 'ETTS_CRANESB02'
    ETTS_CRANESC01     = 'ETTS_CRANESC01'   
    ETTS_CRANESD01     = 'ETTS_CRANESD01'
    ETTS_EDGEA01       = 'ETTS_EDGEA01'
    ETTS_STORMDRAINA01 = 'ETTS_STORMDRAINA01'
    ETTS_STORMDRAINA02 = 'ETTS_STORMDRAINA02'
    ETTS_STORMDRAINB01 = 'ETTS_STORMDRAINB01'
    ETTS_STORMDRAINB02 = 'ETTS_STORMDRAINB02'
    ETTS_STORMDRAINB03 = 'ETTS_STORMDRAINB03'
    ETTS_CONVOYA01     = 'ETTS_CONVOYA01'
    ETTS_CONVOYA02     = 'ETTS_CONVOYA02'
    ETTS_CONVOYB01     = 'ETTS_CONVOYB01'
    ETTS_CONVOYB02     = 'ETTS_CONVOYB02'
    ETTS_MALLA01       = 'ETTS_MALLA01'
    ETTS_TUTORIALA01   = 'ETTS_TUTORIALA01'
    ETTS_TUTORIALA02   = 'ETTS_TUTORIALA02'
    ETTS_TUTORIALA03   = 'ETTS_TUTORIALA03'
    ETTS_FACTORYA01    = 'ETTS_FACTORYA01'
    ETTS_SKYSCRAPERA01 = 'ETTS_SKYSCRAPERA01'
    ETTS_SKYSCRAPERB01 = 'ETTS_SKYSCRAPERB01'
    ETTS_ESCAPEA01     = 'ETTS_ESCAPEA01'
    ETTS_ESCAPEB01     = 'ETTS_ESCAPEB01'


# -----------------------------------------------------------------------------
class Point3D(Vector):
    def __init__(self, _point=(0, 0, 0)):
        super().__init__() 
        self.x = _point[0]
        self.y = _point[1]
        self.z = _point[2]

        self.__prefix_x = ''
        self.__prefix_y = ''
        self.__prefix_z = ''

        self.format = '{:.6f}'

    def __str__(self) -> str:
        x = self.format.format(self.x)
        y = self.format.format(self.y)
        z = self.format.format(self.z)

        return f'{self.__prefix_x}{x},{self.__prefix_y}{y},{self.__prefix_z}{z}'
    
    def set_prefix(self, _x:str, _y:str, _z:str):
        self.__prefix_x = _x + '='
        self.__prefix_y = _y + '='
        self.__prefix_z = _z + '='

    def set_format(self, _f:str):
        self.format = _f


# -----------------------------------------------------------------------------
class Location(Point3D):
    def __init__(self, _point=(0, 0, 0)):
        super().__init__(_point) 
        self.set_prefix('X', 'Y', 'Z')


# -----------------------------------------------------------------------------
class Rotation(Point3D):
    def __init__(self, _point=(0, 0, 0)):
        rotation = Vector(_point) * EULER_TO_URU
        super().__init__(rotation)
        self.set_prefix('Pitch', 'Roll', 'Yaw')
        self.set_format('{:.0f}')


# -----------------------------------------------------------------------------
class Color(Point3D):
    def __init__(self, _point=(0, 0, 0)):
        super().__init__(_point)
        self.x = b3d_utils.map_range(self.x, 0, 1, 0, 255)
        self.y = b3d_utils.map_range(self.y, 0, 1, 0, 255)
        self.z = b3d_utils.map_range(self.z, 0, 1, 0, 255)
        self.set_prefix('R', 'G', 'B')
        self.set_format('{:.0f}')


# -----------------------------------------------------------------------------
class Polygon:
    def __init__(
            self, 
            _origin: tuple[float, float, float], 
            _normal: tuple[float, float, float],
            _u:      tuple[float, float, float],
            _v:      tuple[float, float, float],
            _verts:  list[tuple[float, float, float]],
            _texture:str=None,
            _flags=  3585):
        
        self.Flags      = _flags
        self.Texture    = _texture
        self.Link : int = None
        self.__Origin   = Point3D(_origin)
        self.__Normal   = Point3D(_normal)
        self.__TextureU = Point3D(_u)
        self.__TextureV = Point3D(_v)
        self.__Vertices = [Point3D(x) for x in _verts]


    def __str__(self) -> str:
        texture = f'Texture={self.Texture} ' if self.Texture else ''
        link    = f'Link={self.Link} '       if self.Link or self.Link == 0 else ''
        verts   = ''

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
# Actor
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Actor:
    def __init__(self, 
                 _location=(0, 0, 0),
                 _rotation=(0, 0, 0),
                 _scale   =(1, 1, 1)):
        self.Location    = Location(_location)
        self.Rotation    = Rotation(_rotation)
        self.DrawScale3D = Location(_scale)

    def __str__(self) -> str:
        pass


# -----------------------------------------------------------------------------
class Brush(Actor):
    def __init__(self, 
                 _polylist:list[Polygon],
                 _location:tuple[float, float, float], 
                 _rotation:tuple[float, float, float],
                 _class_name  ='Brush',
                 _package_name='Engine.Default__Brush',
                 _csg_oper    ='CSG_Active'):
        super().__init__(_location, _rotation)
        self.Package                   = _package_name
        self.Class                     = _class_name
        self.Archetype                 = _class_name + '\'' + _package_name + '\''
        self.CsgOper                   = _csg_oper
        self.ObjectSettings: list[str] = []
        self.ActorSettings: list[str]  = []
        self.PolyList: list[Polygon]   = _polylist


    def __str__(self) -> str:
        polylist = ''
        link = 0

        for poly in self.PolyList:
            if not poly.Texture:
                poly.Link = link
                link += 1
            polylist += str(poly)

        object_settings = ''

        for s in self.ObjectSettings:
            object_settings += s + '\n'


        actor_settings = ''

        for s in self.ActorSettings:
            actor_settings += s + '\n'

        return \
f'Begin Actor Class={self.Class} Name={self.Class}_0 Archetype={self.Archetype}\n\
\tBegin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent\'{self.Package}:BrushComponent0\'\n\
{object_settings}\
\tEnd Object\n\
\tBegin Brush Name=Model_0\n\
\t\tBegin PolyList\n\
\t\t\t{polylist}\
\t\tEnd PolyList\n\
\tEnd Brush\n\
\tBrush=Model\'Model_0\'\n\
\tCsgOper={self.CsgOper}\n\
{actor_settings}\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
End Actor\n'


# -----------------------------------------------------------------------------
class StaticMesh(Actor):
    def __init__(self, 
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _scale:    tuple[float, float, float],
                 _static_mesh: str,
                 _material='',
                 _hidden_game=False):
        super().__init__(_location, _rotation, _scale)
        self.StaticMesh = _static_mesh
        self.Material   = _material
        self.HiddenGame = _hidden_game
    

    def __str__(self) -> str:
        return \
f'Begin Actor Class=StaticMeshActor Name=StaticMeshActor_0 Archetype=StaticMeshActor\'Engine.Default__StaticMeshActor\'\n\
\tBegin Object Class=StaticMeshComponent Name=StaticMeshComponent0 Archetype=StaticMeshComponent\'Engine.Default__StaticMeshActor:StaticMeshComponent0\'\n\
\t\tStaticMesh=StaticMesh\'{self.StaticMesh}\'\n\
\t\tHiddenGame={self.HiddenGame}\n\
\t\tMaterials(0)=Material\'{self.Material}\'\n\
\tEnd Object\n\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
\tDrawScale3D=({self.DrawScale3D})\n\
End Actor\n'
    

# -----------------------------------------------------------------------------
class PlayerStart(Actor):
    def __init__(self, 
                 _location     =(0, 0, 0), 
                 _rotation     =(0, 0, 0),
                 _is_time_trial=False,
                 _track_index  =TrackIndex.ETTS_TUTORIALA01):
        super().__init__(_location, _rotation)
        self.is_time_trial = _is_time_trial
        self.TrackIndex    = _track_index


    def __str__(self) -> str:
        if self.is_time_trial: 
            return\
f'Begin Actor Class=TdTimeTrialStart Name=TdTimeTrialStart_0 Archetype=TdTimeTrialStart\'TdGame.Default__TdTimeTrialStart\'\n\
\tBegin Object Class=RequestedTextureResources Name=RequestedTextureResources_0 Archetype=RequestedTextureResources\'TdGame.Default__TdTimeTrialStart:PlayerStartTextureResourcesObject\'\n\
\tEnd Object\n\
\tTrackIndex={self.TrackIndex}\n\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
\tEnd Actor\n'
        else:
            return \
f'Begin Actor Class=PlayerStart Name=PlayerStart_0 Archetype=PlayerStart\'Engine.Default__PlayerStart\'\n\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
End Actor\n'


# -----------------------------------------------------------------------------
class Checkpoint(Actor):
    def __init__(self, 
                 _location            =(0, 0, 0), 
                 _track_index         =TrackIndex.ETTS_TUTORIALA01,
                 _order_index         =0,
                 _no_intermediate_time=False,
                 _custom_height       =0.0,
                 _custom_width_scale  =0.0,
                 _no_respawn          =False,
                 _enabled             =True,
                 _should_be_based     =True):
        
        super().__init__(_location, (0, 0, 0))
        self.TrackIndex         = _track_index
        self.OrderIndex         = _order_index
        self.NoIntermediateTime = _no_intermediate_time
        self.CustomHeight       = _custom_height
        self.CustomWidthScale   = _custom_width_scale
        self.NoRespawn          = _no_respawn
        self.Enabled            = _enabled
        self.ShouldBeBased      = _should_be_based
    
    
    def __str__(self) -> str:
        return \
f'Begin Actor Class=TdTimerCheckpoint Name=TdTimerCheckpoint_0 Archetype=TdTimerCheckpoint\'TdGame.Default__TdTimerCheckpoint\'\n\
\tBelongToTracks(0)=(TrackIndex={self.TrackIndex},OrderIndex={self.OrderIndex},bNoIntermediateTime={self.NoIntermediateTime})\n\
\tCustomHeight={self.CustomHeight}\n\
\tCustomWidthScale={self.CustomWidthScale}\n\
\tbNoRespawn={self.NoRespawn}\n\
\tbEnabled={self.Enabled}\n\
\tbShouldBeBased={self.ShouldBeBased}\n\
\tLocation=({self.Location})\n\
End Actor\n'


# -----------------------------------------------------------------------------
# Volumes
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class LadderVolume(Brush):
    def __init__(self, 
                 _polylist: list[Polygon],
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _is_pipe=False
                 ):
        super().__init__(_polylist, _location, _rotation,
                         'TdLadderVolume',
                         'TdGame.Default__TdLadderVolume')
        
        if _is_pipe:
            self.ActorSettings.append('LadderType=LT_Pipe')


# -----------------------------------------------------------------------------
class Zipline(Brush):
    def __init__(self, 
                 _polylist: list[Polygon],
                 _rotation: tuple[float, float, float],
                 _start:    tuple[float, float, float],
                 _middle:   tuple[float, float, float],
                 _end:      tuple[float, float, float]):
        super().__init__(_polylist, _start, _rotation,
                         'TdZiplineVolume',
                         'TdGame.Default__TdZiplineVolume')
        
        self.ActorSettings.append(f'Start=({Location(_start)})')
        self.ActorSettings.append(f'End=({Location(_end)})')
        self.ActorSettings.append(f'Middle=({Location(_middle)})')
        self.ActorSettings.append('bHideSplineMarkers=False')
        self.ActorSettings.append('bAllowSplineControl=True')
        self.ActorSettings.append('OldScale=(X=1.000000,Y=1.000000,Z=1.000000)')
        self.ActorSettings.append(f'OldLocation=({Location(_start)})')


# -----------------------------------------------------------------------------
class BlockingVolume(Brush):
    def __init__(self, 
                 _polylist: list[Polygon], 
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _phys_material:str=None):
        super().__init__(_polylist, _location, _rotation, 
                         'BlockingVolume', 
                         'Engine.Default__BlockingVolume')
        
        if _phys_material:
            self.ObjectSettings.append(f'PhysMaterialOverride=PhysicalMaterial\'{_phys_material}\'')


# -----------------------------------------------------------------------------
# Lights
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class SkyLight(Actor):
    def __str__(self) -> str:
        return \
f'Begin Actor Class=SkyLight Name=SkyLight_0 Archetype=SkyLight\'Engine.Default__SkyLight\'\n\
Begin Object Class=SkyLightComponent Name=SkyLightComponent0 Archetype=SkyLightComponent\'Engine.Default__SkyLight:SkyLightComponent0\'\n\
End Object\n\
Location=(X=0.000000,Y=0.000000,Z=300.000000)\n\
DrawScale=3.000000\n\
End Actor\n'        


# -----------------------------------------------------------------------------
class DirectionalLight(Actor):
    def __init__(self,
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _color:    tuple[int, int, int]):
        super().__init__(_location, _rotation)
        self.Color = Color(_color)

    def __str__(self) -> str:
        return \
f'Begin Actor Class=DirectionalLight Name=DirectionalLight_0 Archetype=DirectionalLight\'Engine.Default__DirectionalLight\'\n\
\tBegin Object Class=DirectionalLightComponent Name=DirectionalLightComponent0 Archetype=DirectionalLightComponent\'Engine.Default__DirectionalLight:DirectionalLightComponent0\'\n\
\t\tLightColor=({self.Color},A=0)\n\
\tEnd Object\n\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
End Actor\n'
    

# -----------------------------------------------------------------------------
class PointLight(Actor):
    def __init__(self,
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _color:    tuple[int, int, int],
                 _radius:   float):
        super().__init__(_location, _rotation)
        self.Color = Color(_color)
        self.Radius = _radius

    def __str__(self) -> str:
        return \
f'Begin Actor Class=PointLight Name=PointLight_0 Archetype=PointLight\'Engine.Default__PointLight\'\n\
\tBegin Object Class=PointLightComponent Name=PointLightComponent0 Archetype=PointLightComponent\'Engine.Default__PointLight:PointLightComponent0\'\n\
\t\tRadius={self.Radius}\n\
\t\tLightColor=({self.Color},A=0)\n\
\tEnd Object\n\
\tLocation=({self.Location})\n\
End Actor\n'
    

# -----------------------------------------------------------------------------
class AreaLight(Actor):
    def __init__(self,
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _color:    tuple[int, int, int],
                 _radius:   float,
                 _size_x:   float,
                 _size_z:   float):
        super().__init__(_location, _rotation)
        self.Color = Color(_color)
        self.Radius = _radius
        self.SizeX = _size_x
        self.SizeZ = _size_z

    def __str__(self) -> str:
        return \
f'Begin Actor Class=TdAreaLight Name=TdAreaLight_0 Archetype=TdAreaLight\'TdGame.Default__TdAreaLight\'\n\
\tBegin Object Class=PointLightComponent Name=PointLightComponent0 Archetype=PointLightComponent\'TdGame.Default__TdAreaLight:PointLightComponent0\'\n\
\t\tRadius={self.Radius}\n\
\t\tLightColor=({self.Color},A=0)\n\
\tEnd Object\n\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
\tDrawScale3D=(X={self.SizeX},Y=1.000000,Z={self.SizeZ})\n\
End Actor\n'


# -----------------------------------------------------------------------------
class SpotLight(Actor):
    def __init__(self,
                 _location: tuple[float, float, float], 
                 _rotation: tuple[float, float, float],
                 _color:    tuple[int, int, int],
                 _radius:   float,
                 _angle:    float):
        super().__init__(_location, _rotation)
        self.Color = Color(_color)
        self.Radius = _radius
        self.Angle = _angle

    def __str__(self) -> str:
        return \
f'Begin Actor Class=SpotLight Name=SpotLight_0 Archetype=SpotLight\'Engine.Default__SpotLight\'\n\
\tBegin Object Class=SpotLightComponent Name=SpotLightComponent0 Archetype=SpotLightComponent\'Engine.Default__SpotLight:SpotLightComponent0\'\n\
\t\tOuterConeAngle={self.Angle}\n\
\t\tRadius={self.Radius}\n\
\t\tLightColor=({self.Color},A=0)\n\
\tEnd Object\n\
\tLocation=({self.Location})\n\
\tRotation=({self.Rotation})\n\
End Actor\n'