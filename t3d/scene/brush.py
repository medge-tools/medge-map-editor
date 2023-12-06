from .types import Actor

class Point3D:
    def __init__(self, point : tuple[float, float, float] = (0, 0, 0)) -> None:
        self.X : float = point[0]
        self.Y : float = point[1]
        self.Z : float = point[2]
        self.__prefix_x : str = ""
        self.__prefix_y : str = ""
        self.__prefix_z : str = ""
    
    def __str__(self) -> str:
        x = "{:+.6f}".format(self.X)
        y = "{:+.6f}".format(self.Y)
        z = "{:+.6f}".format(self.Z)
        return f"{self.__prefix_x}{x},{self.__prefix_y}{y},{self.__prefix_z}{z}"
    
    def set_prefix(self, x : str, y : str, z : str):
        self.__prefix_x = x + '='
        self.__prefix_y = y + '='
        self.__prefix_z = z + '='

class Location(Point3D):
    def __init__(self) -> None:
        super().__init__()
        self.set_prefix('X', 'Y', 'Z')

class Rotation(Point3D):
    def __init__(self) -> None:
        super().__init__()
        self.set_prefix("Pitch", "Yaw", "Roll")

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
        self.Origin = Point3D(origin)
        self.Normal = Point3D(normal)
        self.TextureU = Point3D(u)
        self.TextureV = Point3D(v)
        self.Vertices = [Point3D(x) for x in verts]

    def __str__(self) -> str:
        texture = f"Texture={self.Texture} " if self.Texture else ""
        link = f"Link={self.Link} " if self.Link else ""
        return \
f"Begin Polygon {texture}Flags=3584 {link}\n\
\tOrigin   {self.Origin}\n\
\tNormal   {self.Normal}\n\
\tTextureU {self.TextureU}\n\
\tTextureV {self.TextureV}\n\
\tVertex   {self.Vertices[0]}\n\
\tVertex   {self.Vertices[1]}\n\
\tVertex   {self.Vertices[2]}\n\
\tVertex   {self.Vertices[3]}\n\
End Polygon\n"

class Component:
    pass

class BrushComponent(Component):
    def __init__(self, postfix : str = "Engine.Default__Brush:BrushComponent0") -> None:
        self.Postfix = postfix

    def __str__(self) -> str:
        return \
f"Begin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent'{self.Postfix}'\n\
End Object\n"

class Brush(Actor):
    __id = 0
    def __init__(self, 
                 polylist : list[Polygon],
                 actor_name : str = "Brush_",
                 brush_name : str = "Model_",
                 brush_comp_type : str = "Engine.Default__Brush:BrushComponent0") -> None:
        self.__Class = "Brush"
        self.__Archetype = "Brush\'Engine.Default__Brush\'"
        self.__CsgOper = "CSG_Add"
        self.ActorName = actor_name + str(Brush.__id)
        self.BrushName = brush_name + str(Brush.__id)
        Brush.__id += 1
        self.Components : list[Component] = [BrushComponent(brush_comp_type)]
        self.PolyList : list[Polygon] = polylist
        self.Location = Location()

    def __str__(self) -> str:
        components = ""
        for comp in self.Components:
            components += str(comp)
        polylist = ""
        link = 0
        for poly in self.PolyList:
            if not poly.Texture:
                poly.Link = link
                link += 1
            polylist += str(poly)
        return \
f"Begin Actor Class={self.__Class} Name={self.ActorName} Archetype={self.__Archetype}\n\
{components}\
CsgOper={self.__CsgOper}\n\
Begin Brush Name={self.BrushName}\n\
Begin PolyList\n\
{polylist}\
End PolyList\n\
End Brush\n\
Brush=Model'{self.BrushName}'\n\
Location=({self.Location})\n\
End Actor\n"