import bpy
from .ops import *
from ..t3d.scene import ActorType
from . import medge_tools as medge

# =============================================================================
class ME_PT_GenericBrowser(bpy.types.Panel):
    bl_idname = 'MET_PT_GenericBrowser'
    bl_label = 'Generic Browser'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def draw(self, context: bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text='Packages')
        row = layout.row(align=True)
        row.template_list('ME_UL_GenericList', 'packages', browser, 'packages', browser, 'active_idx', rows=4)
        col = row.column(align=True)
        col.operator(ME_OT_AddPackage.bl_idname, icon='ADD', text='')
        col.operator(ME_OT_RemovePackage.bl_idname, icon='REMOVE', text='')
        col.operator(ME_OT_MovePackage.bl_idname, icon='TRIA_UP', text='').direction = 'UP'
        col.operator(ME_OT_MovePackage.bl_idname, icon='TRIA_DOWN', text='').direction = 'DOWN'
        
        package = browser.get_active_package()

        if package:
            col = layout.column(align=True)
            col.prop(package, 'name')

            layout.label(text='Resources')
            row = layout.row(align=True)
            row.template_list('ME_UL_GenericList', 'resources', package, 'resources', package, 'active_idx', rows=4)
            col = row.column(align=True)
            col.operator(ME_OT_AddResource.bl_idname, icon='ADD', text='')
            col.operator(ME_OT_RemoveResource.bl_idname, icon='REMOVE', text='')
            col.operator(ME_OT_MoveResource.bl_idname, icon='TRIA_UP', text='').direction = 'UP'
            col.operator(ME_OT_MoveResource.bl_idname, icon='TRIA_DOWN', text='').direction = 'DOWN'
            
            resource = package.get_active_resource()

            if resource:
                col = layout.column(align=True)
                col.prop(resource, 'name')


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
        col.prop(me_actor, 't3d_export')

        if me_actor.type == ActorType.NONE: return

        match(me_actor.type):
            case ActorType.PLAYERSTART:
                actor = me_actor.player_start
            case ActorType.BRUSH:
                actor = me_actor.brush
            case ActorType.LADDER:
                actor = me_actor.ladder
            case ActorType.PIPE:
                actor = me_actor.pipe
            case ActorType.SWING:
                actor = me_actor.swing
            case ActorType.ZIPLINE:
                actor = me_actor.zipline
            case ActorType.SPRINGBOARD:
                actor = me_actor.springboard
            case ActorType.STATICMESH:
                actor = me_actor.static_mesh

        actor.draw(layout)

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
        for actor in types:
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
        row.operator(ME_OT_CleanupWidgets.bl_idname, text='CLEANUP WIDGETS')