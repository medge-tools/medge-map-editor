import bpy
from .ops import *
from ..t3d.scene import ActorType

# =============================================================================
class ME_PT_Actor(bpy.types.Panel):
    bl_idname = 'MET_PT_actor'
    bl_label = 'Actor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def draw(self, context : bpy.types.Context):
        obj = context.active_object
        if not obj or obj.type != 'MESH': return
        
        me_actor = utils.get_me_actor(obj)
        if me_actor.type == ActorType.NONE: return

        layout = self.layout
        col = layout.column(align=True)
        col.use_property_decorate = False
        col.use_property_split = True

        col.prop(me_actor, 'type')
        col.prop(me_actor, 'enable_static_mesh')
        col.prop(me_actor, 'enable_material')

        if(me_actor.enable_static_mesh):
            col = layout.column(align=True)
            col.label(text='Static Mesh')
            col.prop(me_actor, 'static_mesh_package')
            col.prop(me_actor, 'static_mesh_name')
            col.prop(me_actor, 'static_mesh_prefab')
            col = layout.column(align=True)
            col.operator(ME_OT_AddPlaceholder.bl_idname)

        if(me_actor.enable_material):
            col = layout.column(align=True)
            col.label(text='Material')
            col.prop(me_actor, 'material_package')
            col.prop(me_actor, 'material_name')

# =============================================================================
class ME_PT_Volume(bpy.types.Panel):
    bl_idname = 'MET_PT_volume'
    bl_label = 'Add Volume'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def create_row(self, layout: bpy.types.UILayout) -> bpy.types.UILayout:
        row = layout.row(align=True)
        row.scale_y = 2
        return row

    def row_actor(self, 
                layout: bpy.types.UILayout, 
                types: tuple[ActorType, ...]):
        row = self.create_row(layout)
        for k, actor in enumerate(types):
            if actor == ActorType.NONE:
                row.label(text='')
                continue
            op = row.operator(ME_OT_AddActor.bl_idname, text=actor)
            op.type = actor

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        col = layout.column(align=True)

        self.row_actor(col, (ActorType.BRUSH, ActorType.PLAYERSTART))
        self.row_actor(col, (ActorType.LADDER, ActorType.PIPE))
        self.row_actor(col, (ActorType.SWING, ActorType.ZIPLINE))
        self.row_actor(col, (ActorType.SPRINGBOARD, ActorType.STATICMESH))
        
        row = self.create_row(col)
        row.operator(ME_OT_CleanupGizmos.bl_idname, text='CLEANUP GIZMOS')