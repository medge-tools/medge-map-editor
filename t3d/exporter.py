import bpy
import bpy_extras
from t3d.builder import *
from t3d.writer import *

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
            t3d = T3DBuilder().build(context)
            T3DWriter().write(self.filepath, t3d)
            self.report({'INFO'}, 'T3D exported successful')
            return {'FINISHED'}
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}