import bpy
from bpy.types import Object, Light
import bmesh
from mathutils import Vector

from .scene import *
from ... import b3d_utils
from ...map_editor import scene_utils as scene


# -----------------------------------------------------------------------------
class T3DBuilderOptions:
    selected_objects : bool
    scale : int


# -----------------------------------------------------------------------------
# SCENE BUILDERS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Builder:
    def __init__(self) -> None:
        self.mirror = Vector((1, -1, 1))
        self.scale = Vector((1, 1, 1))


    # Transform to left-handed coordinate system
    def get_location_rotation(self, obj: Object) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        rot = b3d_utils.get_rotation_mirrored_x_axis(obj)
        location = obj.matrix_world.translation * self.scale * self.mirror
        rotation = (rot.x, rot.y, rot.z)
        return location, rotation


    def create_polygons(self, obj: Object) -> list[Polygon]:
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


    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        self.scale = options.scale


# -----------------------------------------------------------------------------
class PlayerStartBuilder(Builder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        player_start = scene.get_actor(obj).player_start
        return PlayerStart(*self.get_location_rotation(obj), player_start.is_time_trial, player_start.track_index)


# -----------------------------------------------------------------------------
class CheckpointBuilder(Builder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        location, _ = self.get_location_rotation(obj)
        checkpoint = scene.get_actor(obj).checkpoint
        return Checkpoint(location, 
                            checkpoint.track_index,
                            checkpoint.order_index,
                            checkpoint.no_intermediate_time,
                            checkpoint.custom_height,
                            checkpoint.custom_width_scale,
                            checkpoint.no_respawn,
                            checkpoint.enabled, 
                            checkpoint.should_be_based)


# -----------------------------------------------------------------------------
class StaticMeshBuilder(Builder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        static_mesh = scene.get_actor(obj).static_mesh
        location, rotation = self.get_location_rotation(obj)
        if static_mesh.use_prefab:
            return StaticMesh(location, rotation, obj.scale, static_mesh.get_prefab_path())
        else:
            location = (0.0, 0.0, 0.0)
            return StaticMesh(location, rotation, obj.scale, static_mesh.get_path())


# -----------------------------------------------------------------------------
class VolumeBuilder(Builder):
    def get_arguments(self, obj: Object) -> tuple[list[Polygon], tuple[float, float, float], tuple[float, float, float]]:
        polylist = self.create_polygons(obj)
        location, rotation = self.get_location_rotation(obj)
        return polylist, location, rotation


# -----------------------------------------------------------------------------
class BrushBuilder(VolumeBuilder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        polylist, location, rotation = self.get_arguments(obj)
        for poly in polylist:
            poly.Texture = scene.get_actor(obj).brush.get_material_path()

        return Brush(polylist, location, rotation)


# -----------------------------------------------------------------------------
class LadderBuilder(VolumeBuilder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        arguments = self.get_arguments(obj)
        ladder = scene.get_actor(obj).ladder
        return Ladder(*arguments, ladder.is_pipe)


# -----------------------------------------------------------------------------
class SwingBuilder(VolumeBuilder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        arguments = self.get_arguments(obj)
        return Swing(*arguments)


# -----------------------------------------------------------------------------
class ZiplineBuilder(Builder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        curve = scene.get_actor(obj).zipline.curve
        t = Vector((*(self.scale * self.mirror), 1.0)) 
        mworld = curve.matrix_world
        points = curve.data.splines[0].points
        start = (mworld @ points[0].co) * t
        middle = (mworld @ points[1].co) * t
        end = (mworld @ points[2].co) * t
        polylist = self.create_polygons(obj)
        _, rotation = self.get_location_rotation(obj)
        return Zipline(polylist, rotation, start, middle, end)


# -----------------------------------------------------------------------------
class SpringBoardBuilder(Builder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        location, rotation = self.get_location_rotation(obj)
        return StaticMesh(location, rotation, (1, 1, 1), 'P_Gameplay.SpringBoard.SpringBoardHigh_ColMesh')
   

# -----------------------------------------------------------------------------
class DirectionalLightBuilder(Builder):
    def build(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        super().build(obj, options)
        location, rot = self.get_location_rotation(obj)
        # TODO: Fix export rotation
        rotation = (rot[0], rot[1] - 90, rot[2])
        light = obj.data
        return DirectionalLight(location, rotation, light.color)

# -----------------------------------------------------------------------------
# T3DBuilder
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class T3DBuilder():
    def build_actor(self, obj: Object, options: T3DBuilderOptions) -> Actor | None:
        b3d_utils.set_object_mode(obj, 'OBJECT')
        
        if obj.type == 'LIGHT':
            match obj.data.type:
                case 'SUN':
                    return DirectionalLightBuilder().build(obj, options)


        me_actor = scene.get_actor(obj)
        if me_actor.type == ActorType.NONE: return None

        match(me_actor.type):
            case ActorType.PLAYER_START:
                return PlayerStartBuilder().build(obj, options)
            case ActorType.STATIC_MESH:
                return StaticMeshBuilder().build(obj, options)
            case ActorType.BRUSH:
                return BrushBuilder().build(obj, options)
            case ActorType.LADDER:
                return LadderBuilder().build(obj, options)
            case ActorType.SWING:
                return SwingBuilder().build(obj, options)
            case ActorType.ZIPLINE:
                return ZiplineBuilder().build(obj, options)
            case ActorType.SPRINGBOARD:
                return SpringBoardBuilder().build(obj, options)
            case ActorType.CHECKPOINT:
                return CheckpointBuilder().build(obj, options)
        
        return None


    def build(self, context : bpy.types.Context, options : T3DBuilderOptions) -> list[Actor]:
        scene = []
        objs = context.scene.objects
        if options.selected_objects:
            objs = context.selected_objects
        for obj in objs:
            if(actor := self.build_actor(obj, options)):
                scene.append(actor)
        return scene