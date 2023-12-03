import bpy
import bpy_extras
from .t3d_builder import *

class T3D_OT_Exporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = 'medge_editor.t3d_exporter'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Export T3D'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.t3d'
    filter_glob: bpy.props.StringProperty(
        default="*.t3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be hilighted.
    )

    def execute(self, context):
        try:
            t3d = ASEBuilder().build(context, options)
            ASEWriter().write(self.filepath, ase)
            self.report({'INFO'}, 'ASE exported successful')
            return {'FINISHED'}
        except ASEBuilderError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}