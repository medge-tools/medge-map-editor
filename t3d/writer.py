from io import TextIOWrapper

class T3DFile:
    pass

class T3DWriter:
    def __init__(self):
        self.fp : TextIOWrapper = None
        self.indent = 0

    def write(self, filepath, t3d):
        self.indent = 0
        t3d_file = self.build_t3d_tree(t3d)
        with open(filepath, 'w') as self.fp:
            self.write_file(t3d_file); 
