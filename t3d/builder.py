import bpy
import bmesh
from mathutils import Vector
from ..scene.types import Actor 
from ..scene.brush import *
from ..scene.volumes import *
from ..scene.types import ActorType

# =============================================================================
class T3DBuilderError(Exception):
    pass

# =============================================================================
class T3DBuilderOptions:
    selected_objs : bool
    scale_mult : int

# =============================================================================
class T3DBuilder:
    def build_brush(self, obj : bpy.types.Object, options : T3DBuilderOptions) -> [Brush]:
        m = options.scale_mult
        mult = Vector((m, m, m))
        # Build Polygons
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        polylist : list[Polygon] = []
        for f in bm.faces:
            verts = []
            for v in f.verts:
                verts.append(v.co * mult)
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
        type : ActorType = obj.data.me_actor.type
        match(type):
            case ActorType.BRUSH:
                brush = Brush(polylist)
            case ActorType.LADDER:
                brush = Ladder(polylist)
        brush.Location = obj.location * mult
        euler = obj.rotation_euler
        brush.Rotation = (euler.x, euler.y, euler.z)
        return brush
    
    def build(self, context : bpy.types.Context, options : T3DBuilderOptions) -> list[Actor]:
        scene : list[Actor] = []
        objs = context.selectable_objects
        if options.selected_objs:
            objs = context.selected_objects
        for obj in objs:
            if obj.type != 'MESH': continue
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            brush = self.build_brush(obj, options)
            scene.append(brush)
        return scene


