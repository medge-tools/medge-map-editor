import bpy
import bpy_extras
from ..scene.types import ActorType
from . import props

# =============================================================================
def add_mesh(self, context, type : ActorType, scale : list[bpy.types.FloatProperty], name : str = "Actor"):
    verts = [
        (-1.0 * scale.x, -1.0 * scale.y, -1.0 * scale.z),
        (-1.0 * scale.x,  1.0 * scale.y, -1.0 * scale.z),
        ( 1.0 * scale.x,  1.0 * scale.y, -1.0 * scale.z),
        ( 1.0 * scale.x, -1.0 * scale.y, -1.0 * scale.z),
        (-1.0 * scale.x, -1.0 * scale.y,  1.0 * scale.z),
        (-1.0 * scale.x,  1.0 * scale.y,  1.0 * scale.z),
        ( 1.0 * scale.x,  1.0 * scale.y,  1.0 * scale.z),
        ( 1.0 * scale.x, -1.0 * scale.y,  1.0 * scale.z),
    ]
    edges = []
    faces = [
        (0, 1, 2, 3),
        (7, 6, 5, 4),
        (4, 5, 1, 0),
        (7, 4, 0, 3),
        (6, 7, 3, 2),
        (5, 6, 2, 1),
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.me_actor.type = type
    bpy_extras.object_utils.object_data_add(context, mesh, operator=self)

# =============================================================================
class MET_OT_AddVolume(bpy.types.Operator, bpy_extras.object_utils.AddObjectHelper):
    bl_idname = 'met.add_volume'
    bl_label = 'Add Volume'
    bl_options = {'UNDO'}

    type : props.ActorTypeProperty()

    scale : bpy.props.FloatVectorProperty(
        name="Scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="Scaling",
    )

    def execute(self, context : bpy.types.Context):
        add_mesh(self, context, self.type, self.scale)
        return {'FINISHED'}
    
# =============================================================================
class MET_PT_Actor(bpy.types.Panel):
    bl_idname = 'MET_PT_Actor'
    bl_label = 'Actor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def draw(self, context : bpy.types.Context):
        # Active object properties
        obj = context.active_object
        if not obj or obj.type != 'MESH': return
        me_actor = obj.data.me_actor
        
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(me_actor, 'type')

# =============================================================================
class MET_PT_Volume(bpy.types.Panel):
    bl_idname = 'MET_PT_Volume'
    bl_label = 'Add Volume'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MEdge'

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 2

        op = row.operator(MET_OT_AddVolume.bl_idname, text="Brush")
        op.type = ActorType.BRUSH
        
        row.label(text='')
        
        row = col.row(align=True)
        row.scale_y = 2

        op = row.operator(MET_OT_AddVolume.bl_idname, text="Ladder")
        op.type = ActorType.LADDER
        
        op = row.operator(MET_OT_AddVolume.bl_idname, text="Pipe")
        op.type = ActorType.PIPE