import bpy
import bmesh
from mathutils import Vector
from ..b3d import utils
from ..b3d import medge_tools as medge
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

    # Transform to left-handed coordinate system
    def __get_location_rotation(self, obj: bpy.types.Object) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        rot = utils.get_rotation_mirrored_x_axis(obj)
        location = obj.matrix_world.translation * self.scale * self.mirror
        rotation = (rot.x, rot.y, rot.z)
        return location, rotation

    def __create_polygons(self, obj: bpy.types.Object) -> list[Polygon]:
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
        return polylist

    def __build_brush(self, obj : bpy.types.Object) -> Brush:
        polylist = self.__create_polygons(obj)
        type: ActorType = medge.get_me_actor(obj).type
        location, rotation = self.__get_location_rotation(obj)
        arguments = polylist, location, rotation
        match(type):
            case ActorType.LADDER:
                brush = Ladder(*arguments)
            case ActorType.PIPE:
                brush = Pipe(*arguments)
            case ActorType.SWING:
                brush = Swing(*arguments)
            case ActorType.BRUSH:
                brush = Brush(*arguments)
        return brush

    def __build_zipline(self, obj: bpy.types.Object) -> Actor:
        for child in obj.children:
            if child.type == 'CURVE':
                scale = Vector((*self.scale, 1.0))
                mworld = child.matrix_world
                points = child.data.splines[0].points
                start = (mworld @ points[0].co) * scale
                middle = (mworld @ points[1].co) * scale
                end = (mworld @ points[2].co) * scale
                polylist = self.__create_polygons(obj)
                _, rotation = self.__get_location_rotation(obj)
                return Zipline(polylist, rotation, start, middle, end)

    def __build_static_mesh(self, obj: bpy.types.Object) -> Actor:
        me_actor = medge.get_me_actor(obj)
        location, rotation = self.__get_location_rotation(obj)
        if me_actor.use_prefab:
            prefab = me_actor.prefab
            ma = medge.get_me_actor(prefab)
            print(ma.get_static_mesh())
            return StaticMesh(location, rotation, ma.get_static_mesh())
        else:
            print('else ' + me_actor.get_static_mesh())
            return StaticMesh(location, rotation, me_actor.get_static_mesh())
        
    def __build_actor(self, obj : bpy.types.Object) -> Actor | None:
        if obj.type != 'MESH': return None

        me_actor = medge.get_me_actor(obj)
        if me_actor.type == ActorType.NONE: return None
        if not me_actor.t3d_export: return None

        utils.set_obj_mode(obj, 'OBJECT')
        
        match(me_actor.type):
            case ActorType.PLAYERSTART:
                actor = PlayerStart(*self.__get_location_rotation(obj))
            case ActorType.STATICMESH:
                actor = self.__build_static_mesh(obj)
            case ActorType.SPRINGBOARD:
                location, rotation = self.__get_location_rotation(obj)
                actor = StaticMesh(location, rotation, 'P_Gameplay.SpringBoard.SpringBoardHigh_ColMesh')
            case ActorType.ZIPLINE:
                actor = self.__build_zipline(obj)
            case _:
                actor = self.__build_brush(obj)
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