import bpy
import bmesh
from   bpy.types import Object, Collection
from   mathutils import Vector

from dataclasses import dataclass
import math

from .scene import (
    ActorType, 
    Actor, 
    Polygon, 
    Checkpoint, 
    PlayerStart, 
    StaticMesh, 
    Brush, 
    LadderVolume, 
    BlockingVolume,
    Zipline,
    DirectionalLight,
    PointLight,
    SpotLight,
    AreaLight)

from ...     import b3d_utils
from ..props import get_actor_prop


# -----------------------------------------------------------------------------
@dataclass
class T3DBuilderOptions:
    scale : int


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
# Actor Builders
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class Builder:

    def __init__(self, _options:T3DBuilderOptions, _collection_paths:CollectionPaths):
        self.mirror = Vector((1, -1, 1))
        self.options = _options
        self.collection_paths = _collection_paths


    def get_location(self, _obj:Object) -> tuple[float, float, float]:
        return _obj.matrix_world.translation * self.options.scale * self.mirror


    def get_rotation(self, _obj:Object) -> tuple[float, float, float]:
        rot = b3d_utils.get_rotation(_obj, 'X')
        # X and Y need to be swapped
        rotation = (rot.y, rot.x, rot.z)

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
                    verts.append(world_co * self.options.scale * self.mirror)
                else:
                    verts.append(v.co * obj_eval.scale * self.options.scale * self.mirror)

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
        
        t = Vector((*(self.options.scale * self.mirror), 1.0)) 
        
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
# For some reason the default rotation conversion doesn't work for lights
class LightBuilder(Builder):
    def get_rotation(self, _obj: Object) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        rot = b3d_utils.get_rotation(_obj, 'X')
        rotation = (rot.x, rot.y, rot.z - math.pi)

        return rotation


# -----------------------------------------------------------------------------
class DirectionalLightBuilder(LightBuilder):

    def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)
        light = _obj.data

        return DirectionalLight(location, rotation, light.color)


# -----------------------------------------------------------------------------
class PointLightBuilder(LightBuilder):
     
     def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)
        light = _obj.data

        return PointLight(location, rotation, light.color, light.shadow_soft_size)


# -----------------------------------------------------------------------------
class AreaLightBuilder(LightBuilder):
     
     def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)

        light = _obj.data
        scale = _obj.scale

        size_x = light.size * scale.x * self.options.scale
        size_y = light.size * scale.y * self.options.scale

        return AreaLight(location, rotation, light.color, light.shadow_soft_size, size_x, size_y)


# -----------------------------------------------------------------------------
class SpotLightBuilder(LightBuilder):
     
     def build(self, _obj:Object) -> Actor | None:
        location = self.get_location(_obj)
        rotation = self.get_rotation(_obj)
        light = _obj.data

        return SpotLight(location, rotation, light.color, light.shadow_soft_size, light.spot_size)


# -----------------------------------------------------------------------------
# T3DBuilder
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class T3DBuilder():

    def build(self, _objects:list[Object], _options:T3DBuilderOptions) -> list[Actor]:
        scene = []
        collection_paths = CollectionPaths('GenericBrowser')

        for obj in _objects:
            if(actor := self.build_actor(obj, _options, collection_paths)):
                scene.append(actor)

        return scene
    

    def build_actor(self, _obj:Object, _options:T3DBuilderOptions, _collection_paths:CollectionPaths) -> Actor | None:
        b3d_utils.set_object_mode(_obj, 'OBJECT')
        
        if _obj.type == 'LIGHT':
            match _obj.data.type:
                case 'SUN': 
                    return DirectionalLightBuilder(_options, _collection_paths).build(_obj)
                case 'POINT':
                    return PointLightBuilder(_options, _collection_paths).build(_obj)
                case 'SPOT':
                    return SpotLightBuilder(_options, _collection_paths).build(_obj)
                case 'AREA':
                    return AreaLightBuilder(_options, _collection_paths).build(_obj)

        me_actor = get_actor_prop(_obj)

        if me_actor.type == ActorType.NONE.name: return None

        match(me_actor.type):
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
    
