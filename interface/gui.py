import bpy
import bmesh
from mathutils import Vector
from . import props
from . import utils
from ..scene.types import ActorType
from ..scene.brush import Polygon

# =============================================================================
class ME_OT_Test(bpy.types.Operator):
    bl_idname = 'met.test'
    bl_label = 'Test'
    bl_options = {'UNDO'}

    def execute(self, context : bpy.types.Context):
        obj = context.object

        # Transform to left-handed coordinate system
        # utils.mirror_quaternion_x_axis(obj)
        scale = Vector((10, 10, 10))
        mirror = Vector((1, 1, -1))

        # Transform to left-handed coordinate system
        utils.mirror_quaternion_x_axis(obj)
        obj.location *= mirror
        # utils.apply_scale(obj)

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        for v in bm.verts:
            v.co *= mirror

        bm.to_mesh(obj.data)
        bm.free()

        return {'FINISHED'}

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
        # Active object properties
        obj = context.active_object
        if not obj or obj.type != 'MESH': return
        me_actor = utils.get_me_actor(obj)
        
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(me_actor, 'type')

# =============================================================================
class ME_PT_Volume(bpy.types.Panel):
    bl_idname = 'MET_PT_volume'
    bl_label = 'Add Volume'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        scale_y = 2
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = scale_y

        op = row.operator(ME_OT_AddActor.bl_idname, text='Brush')
        op.type = ActorType.BRUSH
        op = row.operator(ME_OT_AddActor.bl_idname, text='PlayerStart')
        op.type = ActorType.PLAYERSTART
        
        row = col.row(align=True)
        row.scale_y = scale_y

        op = row.operator(ME_OT_AddActor.bl_idname, text='Ladder')
        op.type = ActorType.LADDER
        op.scale = (.05, .05, 1)
        op = row.operator(ME_OT_AddActor.bl_idname, text='Pipe')
        op.type = ActorType.PIPE
        op.scale = (.05, .05, 1)
        
        row = col.row(align=True)
        row.scale_y = scale_y

        op = row.operator(ME_OT_Test.bl_idname, text='Test')