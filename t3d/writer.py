from ..scene.types import Actor
from io import TextIOWrapper

# =============================================================================
class T3DWriter:
    def __init__(self):
        self.fp : TextIOWrapper = None

    def write(self, filepath : str, scene : list[Actor] ):
        s = ''
        for a in scene:
            s += str(a)
        with open(filepath, 'w') as self.fp:
            self.fp.write('Begin Map\nBegin Level NAME=PersistentLevel\n')
            self.fp.write(s)
            self.fp.write('End Level\nBegin Surface\nEnd Surface\nEnd Map')
            
