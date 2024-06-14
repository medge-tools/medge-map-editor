import bpy
from bpy.props           import StringProperty, EnumProperty, BoolProperty
from bpy.types           import Operator, Context, TOPBAR_MT_file_export
from bpy_extras.io_utils import ExportHelper
from mathutils           import Vector

from .scene   import Actor, SkyLight
from .builder import T3DBuilder, T3DBuilderOptions

# -----------------------------------------------------------------------------
class MET_OT_T3D_Export(Operator, ExportHelper):
    '''Export scene to a .t3d file'''
    bl_idname       = 'medge_map_editor.t3d_export'
    bl_label        = 'Export T3D'
    bl_space_type   = 'PROPERTIES'
    bl_region_type  = 'WINDOW'
    filename_ext    = '.t3d'

    filter_glob: StringProperty(
        default='*.t3d',
        options={'HIDDEN'},
        maxlen=255) 


    # These values are identical to the ASE Export addon
    units_scale = {
        'M': 100.0,
        'U': 1.0}


    units: EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units')


    selected_collection: BoolProperty(
        name='Selected Collection',
        default=False
    )


    selected_objects: BoolProperty(
        name='Selected Objects',
        default=False)
    

    export_static_meshes: BoolProperty(
        name='Export Static Meshes',
        default=False)


    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'units')
        layout.prop(self, 'selected_collection')
        layout.prop(self, 'selected_objects')
        layout.prop(self, 'export_static_meshes')


    def write(self, _filepath: str, _scene: list[Actor] ):
        with open(_filepath, 'w') as f:
            f.write('Begin Map\nBegin Level NAME=PersistentLevel\n')
            f.write(str(SkyLight()))
            for a in _scene:
                f.write(str(a))
            f.write('End Level\nBegin Surface\nEnd Surface\nEnd Map')


    def execute(self, _context: Context):
        # Export T3D
        try:
            options = T3DBuilderOptions()
            options.selected_collection = self.selected_collection
            options.selected_objects = self.selected_objects

            us = self.units_scale[self.units]
            options.scale = Vector((us, us, us))

            scene = T3DBuilder().build(_context, options)

            self.write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
            
        except Exception as e:
            self.report({'ERROR'}, str(e))

        # Export ASE
        if self.export_static_meshes:
            bpy.ops.medge_map_editor.ase_export(filepath=self.filepath, units=self.units, selected_objects=self.selected_objects)

        return {'FINISHED'}
    

# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def menu_func_export(self, _context:Context):
    self.layout.operator(MET_OT_T3D_Export.bl_idname, text='MEdge T3D (.t3d)')


# -----------------------------------------------------------------------------
def register():
    TOPBAR_MT_file_export.append(menu_func_export)


# -----------------------------------------------------------------------------
def unregister():
    TOPBAR_MT_file_export.remove(menu_func_export)