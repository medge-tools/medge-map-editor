import bpy
import bmesh
from mathutils import Vector
from ..b3d import utils
from .scene import *

# =============================================================================
class T3DBuilderError(Exception):
    pass

# =============================================================================
class T3DBuilderOptions:
    only_selection : bool
    scale : int

# =============================================================================
class T3DBuilder:
    def __init__(self) -> None:
        self.mirror = Vector((1, -1, 1))
        self.scale = (1, 1, 1)

    def __create_brush(self,
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
            case ActorType.BRUSH:
                brush = Brush(polylist)
        return brush

    def __build_brush(self, obj : bpy.types.Object) -> Brush:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        polylist : list[Polygon] = []
        for f in bm.faces:
            verts = []
            for v in reversed(f.verts):
                verts.append(v.co * obj.scale * self.scale * self.mirror)
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
        return self.__create_brush(obj, polylist)

    # Transform to left-handed coordinate system
    def __build_actor(self, obj : bpy.types.Object) -> Actor | None:
        actor_type = utils.get_me_actor(obj).type
        if actor_type == ActorType.NONE: 
            return None
        utils.set_obj_mode(obj, 'OBJECT')
        
        match(actor_type):
            case ActorType.PLAYERSTART:
                actor = PlayerStart()
            case ActorType.SPRINGBOARD:
                actor = StaticMesh(static_mesh='P_Gameplay.SpringBoard.SpringBoardHigh_ColMesh')
            case _:
                actor = self.__build_brush(obj)
        
        rot = utils.get_rotation_mirrored_x_axis(obj)
        actor.Location = obj.location * self.scale * self.mirror
        actor.Rotation = (rot.x, rot.y, rot.z)
        return actor
    
    def build(self, context : bpy.types.Context, options : T3DBuilderOptions) -> list[Actor]:
        scene : list[Actor] = []
        objs = context.selectable_objects
        self.scale = Vector((options.scale, options.scale, options.scale))
        if options.only_selection:
            objs = context.selected_objects
        for obj in objs:
            if(actor := self.__build_actor(obj)):
                scene.append(actor)
        return scene