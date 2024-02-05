import bpy
import bpy_extras

from .builder import *
from ..ase import *

# =============================================================================
class T3DWriter:
    def write(self, filepath : str, scene : list[Actor] ):
        with open(filepath, 'w') as fp:
            fp.write('Begin Map\nBegin Level NAME=PersistentLevel\n')
            for a in scene:
                fp.write(str(a))
            fp.write('End Level\nBegin Surface\nEnd Surface\nEnd Map')


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
        maxlen=255) 


    # These values are identical to the ASE Export addon
    units_scale = {
        'M': 60.352,
        'U': 1.0}


    units : bpy.props.EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units')


    selected_objects : bpy.props.BoolProperty(
        name='Selected Objects',
        description='Only export selected objects',
        default=False)
    

    export_static_meshes : bpy.props.BoolProperty(
        name='Export Static Meshes',
        description='Export static meshes',
        default=False)


    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'units')
        layout.prop(self, 'selected_objs')
        layout.prop(self, 'export_static_meshes')


    def execute(self, context : bpy.types.Context):
        # Export T3D
        try:
            options = T3DBuilderOptions()
            options.selected_objects = self.selected_objects
            us = self.units_scale[self.units]
            options.scale = Vector((us, us, us))
            scene = T3DBuilder().build(context, options)
            T3DWriter().write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))


        # Export ASE
        if self.export_static_meshes:
            bpy.ops.medge_map_editor.ase_export(filepath=self.filepath, units=self.units)


        return {'FINISHED'}