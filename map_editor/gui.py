from bpy.types import Panel, Context, UILayout

from ..io.t3d.scene import ActorType
from .ops           import MET_OT_AddActor, MET_OT_AddSkydome, MET_OT_CleanupWidgets
from .props         import get_actor_prop


# -----------------------------------------------------------------------------
class MapEditorMainPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge Tools'


# -----------------------------------------------------------------------------
class MET_PT_MapEditorMainPanel(MapEditorMainPanel, Panel):
    bl_idname = 'MET_PT_MapEditorMainPanel'
    bl_label = 'Map Editor'
    
    def draw(self, _context:Context):
        pass


# -----------------------------------------------------------------------------
class MET_PT_Actor(MapEditorMainPanel, Panel):
    bl_parent_id = MET_PT_MapEditorMainPanel.bl_idname
    bl_label = 'Active Actor'

    def draw(self, _context:Context):
        obj = _context.active_object

        if not obj: return
        
        me_actor = get_actor_prop(obj)

        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        me_actor.draw(layout)

# -----------------------------------------------------------------------------
class MET_PT_Volume(MapEditorMainPanel, Panel):
    bl_parent_id = MET_PT_MapEditorMainPanel.bl_idname
    bl_label = 'Scene'


    def create_row(self, _layout:UILayout):
        row = _layout.row(align=True)
        row.scale_y = 2
        return row


    def row_actor(self, 
                  _layout:UILayout, 
                  _types:tuple[ActorType, ...],
                  _names:tuple[str, ...]):
        row = self.create_row(_layout)

        for k, type in enumerate(_types):
            if type == ActorType.NONE:
                row.label(text='')
                continue                

            op = row.operator(MET_OT_AddActor.bl_idname, text=_names[k])
            op.type = type


    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        
        col = layout.column(align=True)

        self.row_actor(col, (ActorType.BRUSH, ActorType.PLAYER_START), ('Brush', 'PlayerStart'))
        self.row_actor(col, (ActorType.LADDER, ActorType.SWING), ('Ladder', 'Swing'))
        self.row_actor(col, (ActorType.SPRINGBOARD, ActorType.STATIC_MESH), ('SpringBoard', 'StaticMesh'))
        self.row_actor(col, (ActorType.ZIPLINE, ActorType.CHECKPOINT), ('Zipline', 'Checkpoint'))
        row = self.create_row(col)
        row.operator(MET_OT_AddSkydome.bl_idname, text='Skydome')
        row.label(text='')
        
        col.separator()
        row = col.row(align=True)
        row.operator(MET_OT_CleanupWidgets.bl_idname, text='Cleanup Widgets')