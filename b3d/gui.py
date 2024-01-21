import bpy
from .ops import *
from ..t3d.scene import ActorType
from . import medge_tools as medge

# =============================================================================
class ME_PT_Actor(bpy.types.Panel):
    bl_idname = 'MET_PT_actor'
    bl_label = 'Actor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def draw(self, context : bpy.types.Context):
        obj = context.active_object
        if not obj: return
        
        me_actor = medge.get_me_actor(obj)

        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        col = layout.column(align=True)
        col.prop(me_actor, 'type')

        if me_actor.type == ActorType.NONE: return

        match(me_actor.type):
            case ActorType.PLAYERSTART:
                actor = me_actor.player_start
            case ActorType.BRUSH:
                actor = me_actor.brush
            case ActorType.LADDER:
                actor = me_actor.ladder
            case ActorType.SWING:
                actor = me_actor.swing
            case ActorType.ZIPLINE:
                actor = me_actor.zipline
            case ActorType.SPRINGBOARD:
                actor = me_actor.springboard
            case ActorType.STATICMESH:
                actor = me_actor.static_mesh

        col = layout.column(align=True)
        actor.draw(context, col)

# =============================================================================
class ME_PT_Volume(bpy.types.Panel):
    bl_idname = 'MET_PT_volume'
    bl_label = 'Add Actor'
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
        for type in types:
            if type == ActorType.NONE:
                row.label(text='')
                continue
            op = row.operator(ME_OT_AddActor.bl_idname, text=type)
            op.type = type

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        col = layout.column(align=True)

        self.row_actor(col, (ActorType.BRUSH, ActorType.PLAYERSTART))
        self.row_actor(col, (ActorType.LADDER, ActorType.SWING))
        self.row_actor(col, (ActorType.SPRINGBOARD, ActorType.STATICMESH))
        self.row_actor(col, (ActorType.ZIPLINE, ActorType.NONE))
        
        row = self.create_row(col)
        row.operator(ME_OT_CleanupWidgets.bl_idname, text='Cleanup Widgets')