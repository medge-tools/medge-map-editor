import bpy
import bpy_extras
from .builder import *
from .writer import *
from ..ase import *

# =============================================================================
class ME_OT_T3D_Export(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export scene to a .t3d file'''
    bl_idname = 'medge_tools.t3d_export'
    bl_label = 'Export T3D'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.t3d'

    filter_glob : bpy.props.StringProperty(
        default='*.t3d',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be hilighted.
    )

    # These values are identical to the ASE Export addon
    units_scale = {
        'M': 60.352,
        'U': 1.0
    }

    units : bpy.props.EnumProperty(
        default='M',
        items=(('M', 'Meters', f'1 Blender unit is {units_scale["M"]} Unreal units'),
               ('U', 'Unreal', f'1 Blender unit is {units_scale["U"]} Unreal units')),
        name='Units'
    )

    selected_objects : bpy.props.BoolProperty(
        name='Selected Objects',
        description='Only export selected objects',
        default=False
    )

    ase_export : bpy.props.BoolProperty(
        name='Export ASE',
        description='Export static meshes',
        default=False
    )

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'units')
        layout.prop(self, 'selected_objs')
        layout.prop(self, 'ase_export')

    def execute(self, context : bpy.types.Context):
        # Export T3D
        try:
            options = T3DBuilderOptions()
            options.selected_objects = self.selected_objects
            s = self.units_scale[self.units]
            options.scale = Vector((s, s, s))
            scene = T3DBuilder().build(context, options)
            T3DWriter().write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))

        # Export ASE
        if self.ase_export:
            bpy.ops.medge_map_editor.ase_export(filepath=self.filepath, units=self.units)

        return {'FINISHED'}