import bpy
import bmesh
from .scene.types import Actor 
from .scene.brush import Brush, Polygon

class T3DBuilderError(Exception):
    pass

class T3DBuilderOptions:
    selected_objects : bool

class T3DBuilder:
    def build_brush(self, obj : bpy.types.Object) -> [Brush]:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        polylist : list[Polygon] = []
        for f in bm.faces:
            verts : [tuple(float, float, float)] = []
            for v in f.verts:
                verts.append((v.co.x * 500, v.co.y * 500, v.co.z * 500))
            v0 = f.verts[0].co
            v1 = f.verts[1].co
            v3 = f.verts[2].co

            u = v0 - v1
            v = v3 - v1
            u.normalize()
            v.normalize()

            p = Polygon(verts[1], f.normal, u, v, verts)
            polylist.append(p)
        bm.free()
        return Brush(polylist)
    
    def build(self, context : bpy.types.Context, options : T3DBuilderOptions) -> list[Actor]:
        scene : list[Actor] = []
        objs = context.selectable_objects
        if options.selected_objects:
            objs = context.selected_objects
        for obj in objs:
            if obj.type != 'MESH': continue
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            brush = self.build_brush(obj)
            scene.append(brush)
        return scene


