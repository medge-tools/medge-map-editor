import bpy
from ..scene.types import ActorType
from .ops import *

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
                types: tuple[ActorType, ...],
                scales: tuple[tuple[float, float, float], ...]):
        row = self.create_row(layout)
        for k, actor in enumerate(types):
            if actor == ActorType.NONE:
                row.label(text='')
                continue
            op = row.operator(ME_OT_AddActor.bl_idname, text=actor)
            op.type = actor
            if scales != None:
                op.scale = scales[k]

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        col = layout.column(align=True)

        self.row_actor(col, 
                       (ActorType.BRUSH, ActorType.PLAYERSTART),
                       ((1, 1, 1), (.1, 1, 1)))
        self.row_actor(col, 
                       (ActorType.LADDER, ActorType.PIPE), 
                       ((.05, .05, .3), (.05, .05, .3)))
        self.row_actor(col,
                       (ActorType.SWING, ActorType.ZIPLINE),
                       ((.05, .05, .03), (1, 1, 1)))
        
        row = self.create_row(col)
        row.operator(ME_OT_CleanupGizmos.bl_idname, text='CLEANUP GIZMOS')