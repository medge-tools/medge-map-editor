from enum import Enum

class strdq(str):
    """
    Returns string inside double quotations.
    >>> t = strdq("hello")
    >>> print(t)
    "hello" 
    """
    def __new__(cls, value : str):
        return super().__new__(cls, f"\"{value}\"")

class strsq(str):
    """
    Returns string inside single quotations.
    >>> t = strdq("hello")
    >>> print(t)
    'hello'
    """
    def __new__(cls, value : str):
        return super().__new__(cls, f"\'{value}\'")

class Actor:
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