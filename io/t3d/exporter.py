import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from .builder import *
from ..ase import *


# -----------------------------------------------------------------------------
class MET_OT_T3D_Export(Operator, ExportHelper):
    '''Export scene to a .t3d file'''
    bl_idname       = 'medge_map_editor.t3d_export'
    bl_label        = 'Export T3D'
    bl_space_type   = 'PROPERTIES'
    bl_region_type  = 'WINDOW'
    filename_ext    = '.t3d'

    filter_glob : bpy.props.StringProperty(
        default='*.t3d',
        options={'HIDDEN'},
        maxlen=255) 


    # These values are identical to the ASE Export addon
    units_scale = {
        'M': 100.0,
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
        layout.prop(self, 'selected_objects')
        layout.prop(self, 'export_static_meshes')


    def write(self, filepath : str, scene : list[Actor] ):
        with open(filepath, 'w') as f:
            f.write('Begin Map\nBegin Level NAME=PersistentLevel\n')
            f.write(str(SkyLight()))
            for a in scene:
                f.write(str(a))
            f.write('End Level\nBegin Surface\nEnd Surface\nEnd Map')


    def execute(self, context : bpy.types.Context):
        # Export T3D
        try:
            options = T3DBuilderOptions()
            options.selected_objects = self.selected_objects
            us = self.units_scale[self.units]
            options.scale = Vector((us, us, us))
            scene = T3DBuilder().build(context, options)
            self.write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
        except Exception as e:
            self.report({'ERROR'}, str(e))


        # Export ASE
        if self.export_static_meshes:
            bpy.ops.medge_map_editor.ase_export(filepath=self.filepath, units=self.units)


        return {'FINISHED'}
    

# -----------------------------------------------------------------------------
# REGISTRATION
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def menu_func_export(self, context):
    self.layout.operator(MET_OT_T3D_Export.bl_idname, text='MEdge T3D (.t3d)')


# -----------------------------------------------------------------------------
def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


# -----------------------------------------------------------------------------
def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)