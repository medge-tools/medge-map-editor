import bpy
import bpy_extras
from .builder import *
from .writer import *

class T3D_OT_Exporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export scene to a .t3d file"""
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

    selected_objects : bpy.props.BoolProperty(
        name="Selected Objects",
        description="Only export selected objects",
        default=False
    )

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.prop(self, 'selected_objects')

    def execute(self, context):
        try:
            options = T3DBuilderOptions()
            options.selected_objects = self.selected_objects
            scene = T3DBuilder().build(context, options)
            T3DWriter().write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
            return {'FINISHED'}
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

classes = (
	T3D_OT_Exporter,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(T3D_OT_Exporter)