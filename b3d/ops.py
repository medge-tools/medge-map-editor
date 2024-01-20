import bpy
from bpy.types import Operator
from . import props
from . import medge_tools as medge

# =============================================================================
# ACTOR
# -----------------------------------------------------------------------------
# =============================================================================
class ME_OT_AddActor(Operator):
    bl_idname = 'medge_tools.add_actor'
    bl_label = 'Add Actor'
    bl_options = {'UNDO'}

    type: props.ActorTypeProperty()

    def execute(self, context : bpy.types.Context):
        medge.new_actor(self.type)
        return {'FINISHED'}

# =============================================================================
# HELPERS
# -----------------------------------------------------------------------------
# =============================================================================
class ME_OT_CleanupWidgets(Operator):
    bl_idname = 'medge_tools.cleanup_gizmos'
    bl_label = 'Cleanup Gizmos'
    bl_options = {'UNDO'}

    def execute(self, context: bpy.types.Context):
        medge.cleanup_widgets()
        return {'FINISHED'}

# =============================================================================
# GENERIC BROWSER
# -----------------------------------------------------------------------------
# =============================================================================
# PACKAGE
# =============================================================================
class ME_OT_AddPackage(Operator):
    bl_idname = 'medge_tools.add_package'
    bl_label = 'Add Package'
    bl_options = {'UNDO'}
    
    def execute(self, context : bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        browser.add_package()
        return {'FINISHED'}

# =============================================================================
class ME_OT_RemovePackage(Operator):
    bl_idname = 'medge_tools.remove_package'
    bl_label = 'Remove Package'
    bl_options = {'UNDO'}
    
    def execute(self, context : bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        browser.remove_active_package()
        return {'FINISHED'}

class ME_OT_MovePackage(Operator):
    bl_idname = 'medge_tools.move_package'
    bl_label = 'Move Package'
    bl_options = {'UNDO'}
    
    direction: bpy.props.EnumProperty(items=(
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ))

    def execute(self, context : bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        new_idx = browser.active_idx
        new_idx += (-1 if self.direction == 'UP' else 1)
        browser.packages.move(new_idx, browser.active_idx)
        browser.active_idx = max(0, min(new_idx, len(browser.packages) - 1))
        return {'FINISHED'}

# =============================================================================
# RESOURCE
# =============================================================================
class ME_OT_AddResource(Operator):
    bl_idname = 'medge_tools.add_resource'
    bl_label = 'Add Resource'
    bl_options = {'UNDO'}
    
    def execute(self, context : bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        package = browser.get_active_package()
        package.add_resource()
        return {'FINISHED'}

# =============================================================================
class ME_OT_RemoveResource(Operator):
    bl_idname = 'medge_tools.remove_resource'
    bl_label = 'Remove Resource'
    bl_options = {'UNDO'}
    
    def execute(self, context : bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        package = browser.get_active_package()
        package.remove_active_resource()
        return {'FINISHED'}
    
# =============================================================================
class ME_OT_MoveResource(Operator):
    bl_idname = 'medge_tools.move_resource'
    bl_label = 'Move Resource'
    bl_options = {'UNDO'}
    
    direction: bpy.props.EnumProperty(items=(
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ))

    def execute(self, context : bpy.types.Context):
        browser = medge.get_me_browser(context.scene)
        package = browser.get_active_package()
        new_idx = package.active_idx
        new_idx += (-1 if self.direction == 'UP' else 1)
        package.resources.move(new_idx, package.active_idx)
        package.active_idx = max(0, min(new_idx, len(package.resources) - 1))
        return {'FINISHED'}