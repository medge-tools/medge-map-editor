import bpy
from .ops import *
from ..io.t3d.scene import ActorType
from . import scene_utils as scene

# -----------------------------------------------------------------------------
class MET_PT_Actor(bpy.types.Panel):
    bl_idname = 'MET_PT_actor'
    bl_label = 'Actor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge Tools'

    def draw(self, context : bpy.types.Context):
        obj = context.active_object
        if not obj: return
        
        me_actor = scene.get_actor(obj)

        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        me_actor.draw(layout)

# -----------------------------------------------------------------------------
class MET_PT_Volume(bpy.types.Panel):
    bl_idname = 'MET_PT_volume'
    bl_label = 'Map Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge Tools'

    def create_row(self, layout: bpy.types.UILayout):
        row = layout.row(align=True)
        row.scale_y = 2
        return row

    def row_actor(self, 
                layout: bpy.types.UILayout, 
                types: tuple[ActorType, ...],
                names: tuple[str, ...]):
        row = self.create_row(layout)
        for k, type in enumerate(types):
            if type == ActorType.NONE:
                row.label(text='')
                continue                
            op = row.operator(MET_OT_AddActor.bl_idname, text=names[k])
            op.type = type

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        col = layout.column(align=True)

        self.row_actor(col, (ActorType.BRUSH, ActorType.PLAYER_START), ('Brush', 'Player Start'))
        self.row_actor(col, (ActorType.LADDER, ActorType.SWING), ('Ladder', 'Swing'))
        self.row_actor(col, (ActorType.SPRINGBOARD, ActorType.STATIC_MESH), ('Springboard', 'Static Mesh'))
        self.row_actor(col, (ActorType.ZIPLINE, ActorType.CHECKPOINT), ('Zipline', 'Checkpoint'))
        row = self.create_row(col)
        row.operator(MET_OT_AddSkydome.bl_idname, text='Skydome')
        row.label(text='')
        
        row = self.create_row(col)
        row.operator(MET_OT_CleanupWidgets.bl_idname, text='Cleanup Widgets')