import bpy
from . import utils
from . import props

# =============================================================================
class ME_OT_AddActor(bpy.types.Operator):
    bl_idname = 'met.add_actor'
    bl_label = 'Add Actor'
    bl_options = {'UNDO'}

    type: props.ActorTypeProperty()

    scale: bpy.props.FloatVectorProperty(
        name="Scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="Scaling"
    )

    def execute(self, context : bpy.types.Context):
        utils.add_brush(self.type, self.scale, self.type)
        return {'FINISHED'}
    
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
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        me_actor = utils.get_me_actor(obj)
        layout.prop(me_actor, 'type')

# =============================================================================
class ME_OT_CleanupGizmos(bpy.types.Operator):
    bl_idname = 'met.cleanup_gizmos'
    bl_label = 'Cleanup Gizmos'
    bl_options = {'UNDO'}

    def execute(self, context: bpy.types.Context):
        utils.cleanup_gizmos()
        return {'FINISHED'}
