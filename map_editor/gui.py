import bpy
from bpy.types import Panel, Context, UILayout, Menu

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
class MET_PT_ActiveActor(MapEditorMainPanel, Panel):
    bl_parent_id = MET_PT_MapEditorMainPanel.bl_idname
    bl_label = 'Selected'


    def draw(self, _context:Context):
        obj = _context.active_object

        if not obj: return
        
        me_actor = get_actor_prop(obj)

        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        me_actor.draw(layout)


# -----------------------------------------------------------------------------
class MET_PT_Actors(MapEditorMainPanel, Panel):
    bl_parent_id = MET_PT_MapEditorMainPanel.bl_idname
    bl_label = 'Actors'


    def create_row(self, _layout:UILayout):
        row = _layout.row(align=True)
        row.scale_y = 2

        return row


    def row_actor(self, 
                  _layout:UILayout, 
                  _types:tuple[ActorType, ...]):
        row = self.create_row(_layout)

        for type in _types:
            if type == ActorType.NONE:
                row.label(text='')
                continue                

            op = row.operator(MET_OT_AddActor.bl_idname, text=type.label)
            op.type = type.name
        
        return row


    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        
        col = layout.column(align=True)

        self.row_actor(col, (ActorType.BRUSH, ActorType.PLAYER_START))
        self.row_actor(col, (ActorType.LADDER_VOLUME, ActorType.SWING_VOLUME))
        self.row_actor(col, (ActorType.SPRINGBOARD, ActorType.STATIC_MESH))
        self.row_actor(col, (ActorType.ZIPLINE, ActorType.BLOCKING_VOLUME))
        self.row_actor(col, (ActorType.TRIGGER_VOLUME, ActorType.KILL_VOLUME))

        row = self.row_actor(col, (ActorType.CHECKPOINT, ))
        row.operator(MET_OT_AddSkydome.bl_idname, text='Skydome')
        
        col.separator()
        row = col.row(align=True)
        row.operator(MET_OT_CleanupWidgets.bl_idname, text='Cleanup Widgets')


# -----------------------------------------------------------------------------
class VIEW3D_MT_PIE_medge_actors(Menu):
    bl_label = 'MEdge Actors'

    
    def add_operators(self, _layout:UILayout, _types:tuple[ActorType, ...]):
        col = _layout.column(align=True)

        for type in _types:
            op = col.operator(MET_OT_AddActor.bl_idname, text=type.label)
            op.type = type.name

        return col


    def draw(self, _context:Context):
        pie = self.layout.menu_pie()

        self.add_operators(pie, (ActorType.BRUSH, ActorType.STATIC_MESH))
        self.add_operators(pie, (ActorType.LADDER_VOLUME, ActorType.SWING_VOLUME, ActorType.SPRINGBOARD, ActorType.ZIPLINE))
        self.add_operators(pie, (ActorType.PLAYER_START, ActorType.CHECKPOINT))
        self.add_operators(pie, (ActorType.BLOCKING_VOLUME, ActorType.KILL_VOLUME, ActorType.TRIGGER_VOLUME))

        col = pie.column(align=True)
        col.operator(MET_OT_AddSkydome.bl_idname, text='Skydome')


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
addon_keymaps = []


# -----------------------------------------------------------------------------
def register():
    global addon_keymaps

    window_manager = bpy.context.window_manager
    
    if window_manager.keyconfigs.addon:

        keymap = window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        keymap_item = keymap.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS', ctrl=True, shift=True)
        keymap_item.properties.name = 'VIEW3D_MT_PIE_medge_actors'

        # save the key map to deregister later
        addon_keymaps.append((keymap, keymap_item))


# -----------------------------------------------------------------------------
def unregister():
    global addon_keymaps

    window_manager = bpy.context.window_manager

    if window_manager and window_manager.keyconfigs and window_manager.keyconfigs.addon:
        
        for keymap, keymap_item in addon_keymaps:
            keymap.keymap_items.remove(keymap_item)

    addon_keymaps.clear()