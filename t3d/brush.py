class Point3D:
    def __init__(self, 
                 x : float = 0,
                 y : float = 0,
                 z : float = 0) -> None:
        self.X : float = x
        self.Y : float = y
        self.Z : float = z
        self.__prefix_x : str = ""
        self.__prefix_y : str = ""
        self.__prefix_z : str = ""
    
    def __str__(self) -> str:
        xs = "-" if self.X < 0 else "+"
        ys = "-" if self.Y < 0 else "+"
        zs = "-" if self.Z < 0 else "+"
        return f"{self.__prefix_x}{xs}{self.X},{self.__prefix_y}{ys}{self.Y},{self.__prefix_z}{zs}{self.Z}"
    
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
            origin : Point3D, 
            normal : Point3D,
            u : Point3D,
            v : Point3D,
            verts : list[Point3D],
            texture : str = None,
            flags : int = 3585,
            link : int = -1) -> None:
        self.Flags = flags
        self.Texture = texture
        self.Link = link
        self.Origin = origin
        self.Normal = normal
        self.TextureU = u
        self.TextureV = v
        self.Vertices = verts

    def __str__(self) -> str:
        texture = f"Texture={self.Texture}" if self.Texture else ""
        link = f"Link={self.Link}" if self.Link else ""
        return \
        f"Begin Polygon {texture} Flags=3584 {link}\n\
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
        return f"Begin Object Class=BrushComponent Name=BrushComponent0 Archetype=BrushComponent'{self.Postfix}'\n\
        End Object\n"

class Brush:
    __id = 0
    def __init__(self, 
                 actor_name : str = "Brush_",
                 brush_name : str = "Model_",
                 brushcomp_postfix : str = "Engine.Default__Brush:BrushComponent0") -> None:
        self.__Class = "Brush"
        self.__Archetype = "Brush\'Engine.Default__Brush\'"
        self.ActorName = actor_name + str(Brush.__id)
        self.BrushName = brush_name + str(Brush.__id)
        Brush.__id += 1
        self.Components : list[Component] = [BrushComponent(brushcomp_postfix)]
        self.PolyList : list[Polygon] = []
        self.Location = Location()

    def __str__(self) -> str:
        components = ""
        for comp in self.Components:
            components += str(comp)
        polylist = ""
        for poly in self.PolyList:
            polylist += str(poly)
        return \
        f"Begin Actor Class={self.__Class} Name={self.ActorName} Archetype={self.__Archetype}\n\
        {components}\
        \tCsgOper=CSG_Add\n\
        \tBegin Brush Name={self.BrushName}\n\
        \t\tBegin PolyList\n\
        {polylist}\
        \t\tEnd PolyList\n\
        \tEnd Brush\n\
        \tBrush=Model'{self.BrushName}'\n\
        Location=({self.Location})\n\
        End Actor\n"