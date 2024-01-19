import bpy
import bmesh
from bpy.types import Object
from mathutils import Vector

from .scene import *
from ..b3d import utils
from ..b3d import medge_tools as medge


# =============================================================================
class T3DBuilderOptions:
    selected_objects : bool
    scale : int

# =============================================================================
# SCENE BUILDERS
# -----------------------------------------------------------------------------
# =============================================================================
class Builder:
    def __init__(self) -> None:
        self.mirror = Vector((1, -1, 1))
        self.scale = Vector((1, 1, 1))

    # -------------------------------------------------------------------------
    # Transform to left-handed coordinate system
    def get_location_rotation(self, obj: bpy.types.Object) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        rot = utils.get_rotation_mirrored_x_axis(obj)
        location = obj.matrix_world.translation * self.scale * self.mirror
        rotation = (rot.x, rot.y, rot.z)
        return location, rotation

    # -------------------------------------------------------------------------
    def create_polygons(self, obj: bpy.types.Object) -> list[Polygon]:
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

    # -------------------------------------------------------------------------
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        self.scale = options.scale

# =============================================================================
class PlayerStartBuilder(Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        return PlayerStart(*self.get_location_rotation(obj))

# =============================================================================
class VolumeArgs():
    def get_arguments(self, obj: bpy.types.Object):
        polylist = self.create_polygons(obj)
        location, rotation = self.get_location_rotation(obj)
        arguments = polylist, location, rotation
        return arguments

# =============================================================================
class BrushBuilder(VolumeArgs, Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        arguments = self.get_arguments(obj)
        return Brush(*arguments)

# =============================================================================
class LadderBuilder(VolumeArgs, Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        arguments = self.get_arguments(obj)
        return Ladder(*arguments)

# ================================P=============================================
class PipeBuilder(VolumeArgs, Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        arguments = self.get_arguments(obj)
        return Pipe(*arguments)

# =============================================================================
class SwingBuilder(VolumeArgs, Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        arguments = self.get_arguments(obj)
        return Swing(*arguments)

# =============================================================================
class ZiplineBuilder(Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        curve = medge.get_me_actor(obj).zipline.curve
        scale = Vector((*(self.scale * self.mirror), 1.0)) 
        mworld = curve.matrix_world
        points = curve.data.splines[0].points
        start = (mworld @ points[0].co) * scale
        middle = (mworld @ points[1].co) * scale
        end = (mworld @ points[2].co) * scale
        polylist = self.create_polygons(obj)
        _, rotation = self.get_location_rotation(obj)
        return Zipline(polylist, rotation, start, middle, end)

# =============================================================================
class SpringBoardBuilder(Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        location, rotation = self.get_location_rotation(obj)
        return StaticMesh(location, rotation, 'P_Gameplay.SpringBoard.SpringBoardHigh_ColMesh')

# =============================================================================
class StaticMeshBuilder(Builder):
    def build(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        static_mesh = medge.get_me_actor(obj).static_mesh
        location, rotation = self.get_location_rotation(obj)
        if static_mesh.use_prefab:
            prefab = static_mesh.prefab
            path = medge.get_me_actor(prefab).static_mesh.path()
            return StaticMesh(location, rotation, path)
        else:
            return StaticMesh(location, rotation, static_mesh.path())

# =============================================================================
# T3DBuilder
# -----------------------------------------------------------------------------
# =============================================================================
class T3DBuilderError(Exception):
    pass

# =============================================================================
class T3DBuilder():
    def build_actor(self, obj: bpy.types.Object, options: T3DBuilderOptions) -> Actor | None:

        me_actor = medge.get_me_actor(obj)
        
        if me_actor.type == ActorType.NONE: return None
        if not me_actor.t3d_export: return None

        utils.set_obj_mode(obj, 'OBJECT')

        actor = None
        
        match(me_actor.type):
            case ActorType.PLAYERSTART:
                actor = PlayerStartBuilder().build(obj, options)
            case ActorType.BRUSH:
                actor = BrushBuilder().build(obj, options)
            case ActorType.LADDER:
                actor = LadderBuilder().build(obj, options)
            case ActorType.PIPE:
                actor = PipeBuilder().build(obj, options)
            case ActorType.SWING:
                actor = SwingBuilder().build(obj, options)
            case ActorType.ZIPLINE:
                actor = ZiplineBuilder().build(obj, options)
            case ActorType.SPRINGBOARD:
                actor = SpringBoardBuilder().build(obj, options)
            case ActorType.STATICMESH:
                actor = StaticMeshBuilder().build(obj, options)

        return actor
    
    def build(self, context : bpy.types.Context, options : T3DBuilderOptions) -> list[Actor]:
        scene : list[Actor] = []
        objs = context.scene.objects
        if options.selected_objects:
            objs = context.selected_objects
        for obj in objs:
            if(actor := self.build_actor(obj, options)):
                scene.append(actor)
        return scene