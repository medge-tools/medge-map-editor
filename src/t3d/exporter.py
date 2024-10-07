import bpy
from bpy.props           import StringProperty, EnumProperty, BoolProperty, FloatVectorProperty, FloatProperty
from bpy.types           import TOPBAR_MT_file_export, Operator, Context, Collection
from bpy_extras.io_utils import ExportHelper

import os.path

from ...b3d_utils import get_selected_collection_names
from .scene       import Actor
from .builder     import T3DBuilder, T3DBuilderOptions, SkylightOptions


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


    units_scale = {
        'M': 100.0,
        'U': 1.0}


    units: EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units')


    selected_collections: BoolProperty(name='Selected Collections')

    selected_objects: BoolProperty(name='Selected Objects')
    
    export_static_meshes: BoolProperty(name='Export StaticMeshes')
    
    add_skylight: BoolProperty(name='Add Skylight')
    skylight_location: FloatVectorProperty(name='Location', subtype='TRANSLATION', default=(0, 0, 300), description='In Unreal units')
    skylight_color: FloatVectorProperty(name='Color', subtype='COLOR', min=0.0, max=1.0, default=(1.0, 1.0, 1.0))
    skylight_brightness: FloatProperty(name='Brightness', min=0.0, description='In Unreal units')

    light_power_scale: FloatProperty(name='Light Power Scale', min=0.0, default=1.0, description='Scales the light power value when setting the brightness')

    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        col = layout.column(align=True)

        col.prop(self, 'units')
        
        col.separator()

        if not self.selected_objects:
            col.prop(self, 'selected_collections')
        
        if not self.selected_collections:
            col.prop(self, 'selected_objects')
        
        col.prop(self, 'export_static_meshes')

        col.separator()

        col.prop(self, 'add_skylight')

        if self.add_skylight:
            col.prop(self, 'skylight_location')
            col.prop(self, 'skylight_color')
            col.prop(self, 'skylight_brightness')

        col.separator()

        col.prop(self, 'light_power_scale')


    def execute(self, _context: Context):
        # Export T3D
        try:
            unit_scale = self.units_scale[self.units]

            skylight_options:SkylightOptions = None

            if self.add_skylight:
                skylight_options = SkylightOptions(self.skylight_location, 
                                                   self.skylight_color, 
                                                   self.skylight_brightness)

            options = T3DBuilderOptions(unit_scale, 
                                        skylight_options, 
                                        self.light_power_scale)

            if self.selected_collections:
                for name in get_selected_collection_names():
                    coll:Collection = bpy.data.collections.get(name)
                    dir = os.path.dirname(self.filepath)
                    
                    t3d = T3DBuilder()
                    t3d.build(coll.all_objects, options)
                    t3d.write(f'{dir}\\{coll.name}.t3d')

            else:
                objects = _context.scene.objects
                
                if self.selected_objects:
                    objects = _context.selected_objects

                t3d = T3DBuilder()
                t3d.build(objects, options)
                t3d.write(self.filepath)

            self.report({'INFO'}, 'T3D exported successful')

        except Exception as e:
            self.report({'ERROR'}, str(e))

        # Export ASE
        if self.export_static_meshes:
            bpy.ops.medge_map_editor.ase_export(filepath=self.filepath, 
                                                units=self.units, 
                                                selected_collection=self.selected_collections,
                                                selected_objects=self.selected_objects)

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