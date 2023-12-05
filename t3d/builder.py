import bpy
from .scene import * 
from .brush import * 

class T3DBuilderError(Exception):
    pass

class T3DBuilder:
    def build(self, context : bpy.types.Context):
        pass

