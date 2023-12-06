class Actor:
    def __str__(self) -> str:
        pass

class WorldInfo(Actor):
    __id = 0
    def __init__(self, name : str = "WorldInfo_") -> None:
        self.Name = name + str(WorldInfo.__id)
        WorldInfo.__id += 1

    def __str__(self) -> str:
        return \
f"Begin Actor Class=WorldInfo Name={self.Name} Archetype=WorldInfo'Engine.Default__WorldInfo'\n\
End Actor\n"