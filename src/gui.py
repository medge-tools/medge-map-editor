import bpy
from bpy.types import Panel, Context, UILayout, Menu

from .t3d.scene import ActorType
from .ops       import MET_OT_add_actor, MET_OT_cleanup_widgets, MET_OT_add_skydome, MET_OT_add_springboard
from .props     import get_actor_prop


# -----------------------------------------------------------------------------
class MEdgeToolsPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge Tools'


# -----------------------------------------------------------------------------
class MET_PT_map_editor(MEdgeToolsPanel, Panel):
    bl_idname = 'MET_PT_map_editor'
    bl_label = 'Map Editor'
    

    def draw(self, _context:Context):
        pass


# -----------------------------------------------------------------------------
class MET_PT_selected_actor(MEdgeToolsPanel, Panel):
    bl_parent_id = MET_PT_map_editor.bl_idname
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
class MET_PT_actors(MEdgeToolsPanel, Panel):
    bl_parent_id = MET_PT_map_editor.bl_idname
    bl_label = 'Actors'


    def create_row(self, _layout:UILayout):
        row = _layout.row(align=True)
        row.scale_y = 2
        
        return row


    def add_actor(self, _layout:UILayout, _type:ActorType):
        op = _layout.operator(MET_OT_add_actor.bl_idname, text=_type.label)
        op.type = _type.name


    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        
        col = layout.column(align=True)

        row = self.create_row(col)
        self.add_actor(row, ActorType.BRUSH)
        self.add_actor(row, ActorType.STATIC_MESH)
        
        row = self.create_row(col)
        self.add_actor(row, ActorType.LADDER_VOLUME)
        self.add_actor(row, ActorType.SWING_VOLUME)

        row = self.create_row(col)
        row.operator(MET_OT_add_springboard.bl_idname, text='Springboard')
        self.add_actor(row, ActorType.ZIPLINE)

        row = self.create_row(col)
        self.add_actor(row, ActorType.BLOCKING_VOLUME)
        self.add_actor(row, ActorType.TRIGGER_VOLUME)

        row = self.create_row(col)
        self.add_actor(row, ActorType.KILL_VOLUME)
        row.operator(MET_OT_add_skydome.bl_idname, text='Skydome')

        row = self.create_row(col)
        self.add_actor(row, ActorType.PLAYER_START)
        self.add_actor(row, ActorType.CHECKPOINT)

        col.separator()
        row = col.row(align=True)
        row.operator(MET_OT_cleanup_widgets.bl_idname, text='Cleanup Widgets')


# -----------------------------------------------------------------------------
class MET_PT_measurements(MEdgeToolsPanel, Panel):
    bl_parent_id = MET_PT_map_editor.bl_idname
    bl_label = 'Measurements'


    def draw(self, _context:Context):
        layout = self.layout

        row  =layout.row()
        col1 = row.column()
        col2 = row.column()

        col1.label(text='Player Height')
        col2.label(text='1.92m')
        col1.label(text='Max Height')
        col2.label(text='11m')
        col1.label(text='Min Crouch')
        col2.label(text='1.5m')


# -----------------------------------------------------------------------------
class VIEW3D_MT_PIE_medge_actors(Menu):
    bl_label = 'MEdge Actors'

    
    def add_operators(self, _layout:UILayout, _types:tuple[ActorType, ...]):
        col = _layout.column(align=True)

        for type in _types:
            op = col.operator(MET_OT_add_actor.bl_idname, text=type.label)
            op.type = type.name

        return col


    def draw(self, _context:Context):
        pie = self.layout.menu_pie()

        self.add_operators(pie, (ActorType.BRUSH, ActorType.STATIC_MESH))
        
        col = self.add_operators(pie, (ActorType.LADDER_VOLUME, ActorType.SWING_VOLUME, ActorType.ZIPLINE))
        col.operator(MET_OT_add_springboard.bl_idname, text='Springboard')

        self.add_operators(pie, (ActorType.PLAYER_START, ActorType.CHECKPOINT))
        self.add_operators(pie, (ActorType.BLOCKING_VOLUME, ActorType.KILL_VOLUME, ActorType.TRIGGER_VOLUME))

        col = pie.column(align=True)
        col.operator(MET_OT_add_skydome.bl_idname, text='Skydome')


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