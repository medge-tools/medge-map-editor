from .scene import Actor
from io import TextIOWrapper

# =============================================================================
class T3DWriter:
    def __init__(self):
        self.fp : TextIOWrapper = None

    def write(self, filepath : str, scene : list[Actor] ):
        with open(filepath, 'w') as self.fp:
            self.fp.write('Begin Map\nBegin Level NAME=PersistentLevel\n')
            for a in scene:
                self.fp.write(str(a))
            self.fp.write('End Level\nBegin Surface\nEnd Surface\nEnd Map')
            
