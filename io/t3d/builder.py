from bpy.types import Object, Context
import bmesh
from mathutils import Vector

from .scene import Polygon, Checkpoint, PlayerStart, StaticMesh, Brush, Ladder, DirectionalLight, ActorType, Actor, Zipline, Swing

from ... import b3d_utils
from ...map_editor.props import get_actor_prop


# -----------------------------------------------------------------------------
class T3DBuilderOptions:
    selected_objects : bool
    scale : int


# -----------------------------------------------------------------------------
# Actor Builders
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Builder:
    def __init__(self, _options:T3DBuilderOptions) -> None:
        self.mirror = Vector((1, -1, 1))
        self.scale = _options.scale

    # Transform to left-handed coordinate system
    def get_location_rotation(self, _obj:Object) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        rot = b3d_utils.get_rotation_mirrored_x_axis(_obj)
        location = _obj.matrix_world.translation * self.scale * self.mirror
        rotation = (rot.x, rot.y, rot.z)
        return location, rotation


    def create_polygons(self, _obj:Object) -> list[Polygon]:
        bm = bmesh.new()
        bm.from_mesh(_obj.data)

        polylist : list[Polygon] = []
        for f in bm.faces:
            verts = []
            for v in reversed(f.verts):
                verts.append(v.co * _obj.scale * self.scale * self.mirror)
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


    def build(self, _obj:Object) -> Actor | None:
        pass


# -----------------------------------------------------------------------------
class PlayerStartBuilder(Builder):
    def build(self, _obj:Object) -> Actor | None:
        player_start = get_actor_prop(_obj).player_start

        return PlayerStart(*self.get_location_rotation(_obj), player_start.is_time_trial, player_start.track_index)


# -----------------------------------------------------------------------------
class CheckpointBuilder(Builder):
    def build(self, _obj:Object) -> Actor | None:
        location, _ = self.get_location_rotation(_obj)
        checkpoint = get_actor_prop(_obj).checkpoint

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
    def build(self, _obj:Object) -> Actor | None:
        static_mesh = get_actor_prop(_obj).static_mesh
        location, rotation = self.get_location_rotation(_obj)

        if static_mesh.use_prefab:
            return StaticMesh(location, rotation, _obj.scale, static_mesh.get_prefab_path())
        
        else:
            return StaticMesh(location, rotation, _obj.scale, static_mesh.get_path())


# -----------------------------------------------------------------------------
class VolumeBuilder(Builder):
    def get_arguments(self, _obj:Object) -> tuple[list[Polygon], tuple[float, float, float], tuple[float, float, float]]:
        polylist = self.create_polygons(_obj)
        location, rotation = self.get_location_rotation(_obj)

        return polylist, location, rotation


# -----------------------------------------------------------------------------
class BrushBuilder(VolumeBuilder):
    def build(self, _obj:Object) -> Actor | None:
        polylist, location, rotation = self.get_arguments(_obj)

        for poly in polylist:
            poly.Texture = get_actor_prop(_obj).brush.get_material_path()

        return Brush(polylist, location, rotation)


# -----------------------------------------------------------------------------
class LadderBuilder(VolumeBuilder):
    def build(self, _obj:Object) -> Actor | None:
        arguments = self.get_arguments(_obj)
        ladder = get_actor_prop(_obj).ladder

        return Ladder(*arguments, ladder.is_pipe)


# -----------------------------------------------------------------------------
class SwingBuilder(VolumeBuilder):
    def build(self, _obj:Object) -> Actor | None:
        arguments = self.get_arguments(_obj)

        return Swing(*arguments)


# -----------------------------------------------------------------------------
class ZiplineBuilder(Builder):
    def build(self, _obj:Object) -> Actor | None:
        curve = get_actor_prop(_obj).zipline.curve
        
        t = Vector((*(self.scale * self.mirror), 1.0)) 
        
        mworld = curve.matrix_world
        
        points = curve.data.splines[0].points
        
        start = (mworld @ points[0].co) * t
        middle = (mworld @ points[1].co) * t
        end = (mworld @ points[2].co) * t
        
        polylist = self.create_polygons(_obj)
        
        _, rotation = self.get_location_rotation(_obj)

        return Zipline(polylist, rotation, start, middle, end)


# -----------------------------------------------------------------------------
class SpringBoardBuilder(Builder):
    def build(self, _obj:Object) -> Actor | None:
        springboard = get_actor_prop(_obj).springboard

        location, rotation = self.get_location_rotation(_obj)

        return StaticMesh(location, rotation, (1, 1, 1), 'P_Gameplay.SpringBoard.SpringBoardHigh_ColMesh', None, springboard.is_hidden_game)
   

# -----------------------------------------------------------------------------
class DirectionalLightBuilder(Builder):
    def build(self, _obj:Object) -> Actor | None:
        location, rot = self.get_location_rotation(_obj)
        # TODO: Fix export rotation
        rotation = (rot[0], rot[1] - 90, rot[2])
        light = _obj.data

        return DirectionalLight(location, rotation, light.color)


# -----------------------------------------------------------------------------
# T3DBuilder
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class T3DBuilder():
    def build_actor(self, _obj:Object, _options:T3DBuilderOptions) -> Actor | None:
        b3d_utils.set_object_mode(_obj, 'OBJECT')
        
        if _obj.type == 'LIGHT':
            match _obj.data.type:
                case 'SUN':
                    return DirectionalLightBuilder(_options).build(_obj)

        me_actor = get_actor_prop(_obj)

        if me_actor.type == ActorType.NONE: return None

        match(me_actor.type):
            case ActorType.PLAYER_START:
                return PlayerStartBuilder(_options).build(_obj)
            case ActorType.STATIC_MESH:
                return StaticMeshBuilder(_options).build(_obj)
            case ActorType.BRUSH:
                return BrushBuilder(_options).build(_obj)
            case ActorType.LADDER:
                return LadderBuilder(_options).build(_obj)
            case ActorType.SWING:
                return SwingBuilder(_options).build(_obj)
            case ActorType.ZIPLINE:
                return ZiplineBuilder(_options).build(_obj)
            case ActorType.SPRINGBOARD:
                return SpringBoardBuilder(_options).build(_obj)
            case ActorType.CHECKPOINT:
                return CheckpointBuilder(_options).build(_obj)
        
        return None


    def build(self, _context:Context, _options:T3DBuilderOptions) -> list[Actor]:
        scene = []
        objects = _context.scene.objects

        if _options.selected_objects:
            objects = _context.selected_objects

        for obj in objects:
            if(actor := self.build_actor(obj, _options)):
                scene.append(actor)

        return scene