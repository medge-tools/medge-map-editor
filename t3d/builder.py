import bpy
import bmesh
from mathutils import Vector, Matrix

from ..interface import utils
from ..scene.types import * 
from ..scene.brush import *
from ..scene.volumes import *

# =============================================================================
class T3DBuilderError(Exception):
    pass

# =============================================================================
class T3DBuilderOptions:
    only_selection : bool
    scale : int

# =============================================================================
class T3DBuilder:
    def create_brush(self,
                     obj: bpy.types.Object, 
                     polylist: list[Polygon]) -> Brush:
        type: ActorType = utils.get_me_actor(obj).type
        match(type):
            case ActorType.LADDER:
                brush = Ladder(polylist)
            case ActorType.PIPE:
                brush = Pipe(polylist)
            case ActorType.SWING:
                brush = Swing(polylist)
            case _:
                brush = Brush(polylist)
        return brush

    def build_brush(self, object : bpy.types.Object, options : T3DBuilderOptions) -> Brush | None:
        # Transform to left-handed coordinate system by mirroring along the y-axis
        # Mirror the location and vertices
        if utils.get_me_actor(object).type == ActorType.NONE: 
            return None
        scale = Vector((options.scale, options.scale, options.scale))
        mirror = Vector((1, -1, 1))
        
        utils.set_obj_mode(object, 'OBJECT')
        obj = utils.deepcopy(object)
        obj.location *= mirror
        utils.mirror_quaternion_x_axis(obj)

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        polylist : list[Polygon] = []
        for f in bm.faces:
            verts = []
            for v in reversed(f.verts):
                verts.append(v.co * obj.scale * scale * mirror)
            v0 = f.verts[0].co
            v1 = f.verts[1].co
            
            u = v1 - v0
            u.normalize()
            n = f.normal
            v = n.cross(u)

            p = Polygon(verts[0], n, u, v, verts)
            polylist.append(p)
        bm.free()

        # Build Brush
        brush = self.create_brush(obj, polylist)
        brush.Location = obj.location * scale
        euler = Vector(obj.rotation_euler)
        brush.Rotation = (euler.x, euler.y, euler.z)
        return brush
    
    def build(self, context : bpy.types.Context, options : T3DBuilderOptions) -> list[Actor]:
        scene : list[Actor] = []
        objs = context.selectable_objects
        if options.only_selection:
            objs = context.selected_objects
        for obj in objs:
            if(brush := self.build_brush(obj, options)):
                scene.append(brush)
        return scene