from .types import *

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
class Component:
    pass

# =============================================================================
class BrushComponent(Component):
    def __init__(self, postfix : str = 'Engine.Default__Brush:BrushComponent0') -> None:
        self.Postfix = postfix

    def __str__(self) -> str:
        return \
f'Begin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent\'{self.Postfix}\'\n\
End Object\n'

# =============================================================================
class Brush(Actor):
    __id = 0
    def __init__(self, 
                 polylist : list[Polygon],
                 actor_name : str = 'Brush_',
                 brush_name : str = 'Model_',
                 brush_comp_type : str = 'Engine.Default__Brush:BrushComponent0') -> None:
        super().__init__()
        self._Class = 'Brush'
        self._Archetype = 'Brush\'Engine.Default__Brush\''
        self._CsgOper = 'CSG_Add'
        self._Properties : list[str] = []
        self.ActorName = actor_name + str(Brush.__id)
        self.BrushName = brush_name + str(Brush.__id)
        Brush.__id += 1
        self._Components : list[Component] = [BrushComponent(brush_comp_type)]
        self.PolyList : list[Polygon] = polylist

    def __str__(self) -> str:
        components = ''
        for comp in self._Components:
            components += str(comp)
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
f'Begin Actor Class={self._Class} Name={self.ActorName} Archetype={self._Archetype}\n\
{components}\
CsgOper={self._CsgOper}\n\
{props}\
Begin Brush Name={self.BrushName}\n\
Begin PolyList\n\
{polylist}\
End PolyList\n\
End Brush\n\
Brush=Model\'{self.BrushName}\'\n\
Location=({self._Location})\n\
Rotation=({self._Rotation})\n\
End Actor\n'