import bpy
import bmesh
from   bpy.types import (
    Object, Collection, 
    PointLight as BL_PointLight, 
    SunLight as BL_SunLight, 
    SpotLight as BL_SpotLight, 
    AreaLight as BL_AreaLight)
from   mathutils import Vector, Euler

from dataclasses import dataclass
import math
from math import atan2, hypot

from .scene import (
    ActorType, 
    BakerSettings,
    Actor, 
    Polygon, 
    Checkpoint, 
    PlayerStart, 
    StaticMesh, 
    Brush, 
    LadderVolume, 
    BlockingVolume,
    Zipline,
    SkyLight,
    DirectionalLight,
    PointLight,
    SpotLight,
    AreaLight)

from ...     import b3d_utils
from ..props import get_actor_prop


# -----------------------------------------------------------------------------
@dataclass
class SkylightOptions:
    location : tuple[float, float, float]
    color : tuple[float, float, float, float]
    brightness : float
    sample_factor : float


# -----------------------------------------------------------------------------
@dataclass
class T3DBuilderOptions:
    unit_scale : int
    skylight_options : SkylightOptions | None # If not None, add skylight
    light_power_scale : float # Scales the energy when setting brightness
    window_light_angle_scale : float # Scale the energy when setting window light angle


# -----------------------------------------------------------------------------
class CollectionPaths:

    def __init__(self, _collection_root:str):
        self.paths = {} # Dictionary of (object name, collection path)
        root = bpy.data.collections.get(_collection_root)
        
        if root:
            self.build_hierarchy(root)
        else:
            print(f'Collection does not exists: {_collection_root}')


    def __getitem__(self, key:str):
        if key in self.paths: return self.paths[key]
        return ''


    def build_hierarchy(self, _collection:Collection, _path=''):
        for obj in _collection.objects:
            self.paths[obj.name] = _path

        for child in _collection.children:
            self.build_hierarchy(child, _path + child.name + '.')


# -----------------------------------------------------------------------------
def get_rotation_mirrored(_obj:Object) -> Euler:
    q = _obj.matrix_world.to_quaternion()
    q.x *= -1
    q.w *= -1

    return q.to_euler()


# -----------------------------------------------------------------------------
# Actor Builders
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Builder:

    def __init__(self, _options:T3DBuilderOptions, _collection_paths:CollectionPaths):
        self.mirror = Vector((1, -1, 1))
        self.options = _options
        self.collection_paths = _collection_paths


    def get_location(self, _obj:Object) -> tuple[float, float, float]:
        return _obj.matrix_world.translation * self.options.unit_scale * self.mirror


    def get_rotation(self, _obj:Object) -> tuple[float, float, float]:
        r = get_rotation_mirrored(_obj)
        # X and Y need to be swapped
        rotation = (r.y, r.x, r.z)

        return rotation


    def create_polygons(self, _obj:Object, _apply_transforms=False) -> list[Polygon]:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = _obj.evaluated_get(depsgraph)

        bm = bmesh.new()
        bm.from_mesh(obj_eval.data)

        polylist : list[Polygon] = []

        for f in bm.faces:
            verts = []

            for v in reversed(f.verts):
                if _apply_transforms:
                    world_co = obj_eval.matrix_world @ v.co
                    verts.append(world_co * self.options.unit_scale * self.mirror)
                else:
                    verts.append(v.co * obj_eval.scale * self.options.unit_scale * self.mirror)

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
        raise Exception('Method should be overridden')


# -----------------------------------------------------------------------------
class PlayerStartBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        player_start = get_actor_prop(_obj).player_start
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)
        
        location.z += 1

        return PlayerStart(location, rotation, player_start.is_time_trial, player_start.track_index)


# -----------------------------------------------------------------------------
class CheckpointBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        checkpoint = get_actor_prop(_obj).get_checkpoint()

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
        static_mesh = get_actor_prop(_obj).get_static_mesh()
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        if static_mesh.use_prefab:
            if (prefab := static_mesh.prefab):
                name = prefab.name
                path = self.collection_paths[name]

                return StaticMesh(location, rotation, _obj.scale, path + name, static_mesh.is_hidden_game)
            
            else:
                print(f'Object {_obj.name} uses prefab, but has not prefab selected')
        
        else:
            name = _obj.name
            path = self.collection_paths[name]
            
            return StaticMesh(location, rotation, _obj.scale, path + name, static_mesh.is_hidden_game)


# -----------------------------------------------------------------------------
class ZiplineBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        curve = get_actor_prop(_obj).get_zipline().curve
        
        t = Vector((*(self.options.unit_scale * self.mirror), 1.0)) 
        
        mworld = curve.matrix_world
        
        points = curve.data.splines[0].points
        
        start = (mworld @ points[0].co) * t
        middle = (mworld @ points[1].co) * t
        end = (mworld @ points[2].co) * t
        
        polylist = self.create_polygons(_obj)
        
        rotation = self.get_rotation(_obj)

        return Zipline(polylist, rotation, start, middle, end)


# -----------------------------------------------------------------------------
class BrushBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        polylist = self.create_polygons(_obj, True)

        material = get_actor_prop(_obj).get_brush().material

        if material:
            for poly in polylist:
                name = material.name
                poly.Texture = self.collection_paths[name] + name

        return Brush(polylist, (0, 0, 0), (0, 0, 0), _csg_oper='CSG_Add')


# -----------------------------------------------------------------------------
class LadderVolumeBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        polylist = self.create_polygons(_obj)
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        ladder = get_actor_prop(_obj).get_ladder()

        return LadderVolume(polylist, location, rotation, ladder.is_pipe)


# -----------------------------------------------------------------------------
class SwingVolumeBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        polylist = self.create_polygons(_obj)
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        return Brush(polylist, location, rotation, 
                     'TdSwingVolume',
                     'TdGame.Default__TdSwingVolume')


# -----------------------------------------------------------------------------
class BlockingVolumeBuilder(Builder):

    def build(self, _obj:Object) -> Actor | None:
        polylist = self.create_polygons(_obj)
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        blocking_volume = get_actor_prop(_obj).get_blocking_volume()

        path = ''

        if (material := blocking_volume.phys_material):
            name = material.name
            path = self.collection_paths[name] + name

        return BlockingVolume(polylist, location, rotation, path)
    

# -----------------------------------------------------------------------------
class TriggerVolumeBuilder(Builder):
    
    def build(self, _obj:Object) -> Actor | None:
        polylist = self.create_polygons(_obj)
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        return Brush(polylist, location, rotation, 
                     'TdTriggerVolume',
                     'TdGame.Default__TdTriggerVolume')
    

# -----------------------------------------------------------------------------
class KillVolumeBuilder(Builder):
    
    def build(self, _obj:Object) -> Actor | None:
        polylist = self.create_polygons(_obj)
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        return Brush(polylist, location, rotation, 
                     'TdKillVolume',
                     'TdGame.Default__TdKillVolume')


# -----------------------------------------------------------------------------
# Lights
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# In UnrealEd the default direction of every light is not the same. 

class EulerLightBuilder(Builder):

    def get_rotation(self, _obj: Object) -> tuple[float, float, float]:
        direction = Vector((0, 0, -1))
        
        rotation = _obj.matrix_world.to_quaternion()
        direction.rotate(rotation)
        
        x = direction.x
        y = direction.y
        z = direction.z

        # Align 
        pitch = atan2(hypot(x, y), -z)
        yaw = atan2(x, -y) + math.pi / 2
        
        # Mirror on y-axis, because it gets mirrored in UnrealEd
        y_axis = Vector((0, -1, 0))
        a = y_axis.angle(direction)

        return pitch - math.pi / 2, 0, yaw - a * 2


# -----------------------------------------------------------------------------
class PointLightBuilder(Builder):
     
    def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        light:BL_PointLight = _obj.data

        pl = get_actor_prop(_obj).get_point_light()

        return PointLight(location, 
                          light.color, 
                          light.energy * self.options.light_power_scale,
                          light.shadow_soft_size * self.options.unit_scale, 
                          light.cutoff_distance,
                          pl.sample_factor)
    

# -----------------------------------------------------------------------------
class DirectionalLightBuilder(EulerLightBuilder):
    
    def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)
        light:BL_SunLight = _obj.data

        dl = get_actor_prop(_obj).get_directional_light()

        return DirectionalLight(location, 
                                rotation, 
                                light.color,
                                light.energy, # SunLight energy is already normalized
                                dl.sample_factor)


# -----------------------------------------------------------------------------
class SpotLightBuilder(EulerLightBuilder):
     
    def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)
        light: BL_SpotLight = _obj.data

        sl = get_actor_prop(_obj).get_spot_light()

        return SpotLight(location, 
                         rotation, 
                         light.color, 
                         light.energy * self.options.light_power_scale,
                         light.shadow_soft_size, 
                         light.spot_size,
                         light.cutoff_distance,
                         sl.sample_factor)


# -----------------------------------------------------------------------------
class AreaLightBuilder(Builder):

    def get_rotation(self, _obj: Object) -> tuple[float, float, float]:
        r = get_rotation_mirrored(_obj)
        # X and Y need to be swapped
        rotation = (r.y, r.x - math.pi / 2, r.z)

        return rotation
        
    def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        light = _obj.data
        scale = _obj.scale

        size_x = light.size * scale.x * self.options.unit_scale
        size_y = light.size * scale.y * self.options.unit_scale

        al = get_actor_prop(_obj).get_area_light()

        return AreaLight(location, 
                         rotation, 
                         light.color, 
                         light.energy * self.options.light_power_scale,
                         light.shadow_soft_size, 
                         size_x, 
                         size_y,
                         light.cutoff_distance * self.options.unit_scale,
                         al.sample_factor,
                         al.is_window_light,
                         light.energy * self.options.window_light_angle_scale)


# -----------------------------------------------------------------------------
# T3DBuilder
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class T3DBuilder:

    def __init__(self) -> None:
        self.scene:list[Actor] = []


    def build(self, _objects:list[Object], _options:T3DBuilderOptions) -> list[Actor]:
        collection_paths = CollectionPaths('GenericBrowser')

        if (so := _options.skylight_options):
            self.scene.append(SkyLight(so.location, so.color, so.brightness, so.sample_factor))

        for obj in _objects:
            if(actor := self.build_actor(obj, _options, collection_paths)):
                self.scene.append(actor)

        return self.scene    


    def build_actor(self, _obj:Object, _options:T3DBuilderOptions, _collection_paths:CollectionPaths) -> Actor | None:
        b3d_utils.set_object_mode(_obj, 'OBJECT')
        
        if _obj.type == 'LIGHT':
            match _obj.data.type:
                case 'POINT':
                    return PointLightBuilder(_options, _collection_paths).build(_obj)
                case 'SUN': 
                    return DirectionalLightBuilder(_options, _collection_paths).build(_obj)
                case 'SPOT':
                    return SpotLightBuilder(_options, _collection_paths).build(_obj)
                case 'AREA':
                    return AreaLightBuilder(_options, _collection_paths).build(_obj)

        me_actor = get_actor_prop(_obj)

        if me_actor.actor_type == ActorType.NONE.name: return None

        match(me_actor.actor_type):
            case ActorType.PLAYER_START.name:
                return PlayerStartBuilder(_options, _collection_paths).build(_obj)
            case ActorType.CHECKPOINT.name:
                return CheckpointBuilder(_options, _collection_paths).build(_obj)
            case ActorType.STATIC_MESH.name:
                return StaticMeshBuilder(_options, _collection_paths).build(_obj)
            case ActorType.ZIPLINE.name:
                return ZiplineBuilder(_options, _collection_paths).build(_obj)
            case ActorType.BRUSH.name:
                return BrushBuilder(_options, _collection_paths).build(_obj)
            case ActorType.LADDER_VOLUME.name:
                return LadderVolumeBuilder(_options, _collection_paths).build(_obj)
            case ActorType.SWING_VOLUME.name:
                return SwingVolumeBuilder(_options, _collection_paths).build(_obj)
            case ActorType.BLOCKING_VOLUME.name:
                return BlockingVolumeBuilder(_options, _collection_paths).build(_obj)
            case ActorType.TRIGGER_VOLUME.name:
                return TriggerVolumeBuilder(_options, _collection_paths).build(_obj)
            case ActorType.KILL_VOLUME.name:
                return KillVolumeBuilder(_options, _collection_paths).build(_obj)
        
        return None
    

    def write(self, _filepath: str):
        with open(_filepath, 'w') as f:
            f.write('Begin Map\nBegin Level NAME=PersistentLevel\n')
            for actor in self.scene:
                f.write(str(actor))
            f.write('End Level\nBegin Surface\nEnd Surface\nEnd Map')