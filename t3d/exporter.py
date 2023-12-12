import bpy
import bpy_extras
from .builder import *
from .writer import *

# =============================================================================
class T3D_OT_Exporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export scene to a .t3d file'''
    bl_idname = 'medge_editor.t3d_exporter'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Export T3D'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.t3d'
    filter_glob: bpy.props.StringProperty(
        default='*.t3d',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be hilighted.
    )

    scale_mult: bpy.props.IntProperty(
        name='Scale Multiplier',
        default=800
    )

    selected_objs: bpy.props.BoolProperty(
        name='Selected Objects',
        description='Only export selected objects',
        default=False
    )

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'scale_mult')
        layout.prop(self, 'selected_objs')

    def execute(self, context):
        try:
            options = T3DBuilderOptions()
            options.only_selection = self.selected_objs
            options.scale = self.scale_mult
            scene = T3DBuilder().build(context, options)
            T3DWriter().write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
            return {'FINISHED'}
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}