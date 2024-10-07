import bpy
from bpy.props           import StringProperty, EnumProperty, BoolProperty, FloatVectorProperty, FloatProperty
from bpy.types           import TOPBAR_MT_file_export, Operator, Context, Collection, Panel
from bpy_extras.io_utils import ExportHelper

import os.path

from ...b3d_utils import get_selected_collection_names
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
    
    light_power_scale: FloatProperty(name='Light Power Scale', min=0.0, default=1.0, description='Scales the light power value when setting the brightness')

    add_skylight: BoolProperty(name='Add Skylight')
    skylight_location: FloatVectorProperty(name='Location', subtype='TRANSLATION', default=(0, 0, 300), description='In Unreal units')
    skylight_color: FloatVectorProperty(name='Color', subtype='COLOR', min=0.0, max=1.0, default=(1.0, 1.0, 1.0))
    skylight_brightness: FloatProperty(name='Brightness', min=0.0, default=1.0, description='In Unreal units')
    skylight_sample_factor: FloatProperty(name='Sample Factor', min=0.0, default=1.0)


    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True

        layout.prop(self, 'units')
        
        layout.separator()

        if not self.selected_objects:
            layout.prop(self, 'selected_collections')
        
        if not self.selected_collections:
            layout.prop(self, 'selected_objects')
        
        layout.prop(self, 'export_static_meshes')

        layout.separator()

        layout.prop(self, 'light_power_scale')


    def execute(self, _context: Context):
        # Export T3D
        try:
            unit_scale = self.units_scale[self.units]

            skylight_options:SkylightOptions = None

            if self.add_skylight:
                skylight_options = SkylightOptions(self.skylight_location, 
                                                   self.skylight_color, 
                                                   self.skylight_brightness,
                                                   self.skylight_sample_factor)

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
class MET_PT_SkylightSettings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = 'Add Skylight'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, _context:Context):
        sfile = _context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == 'MEDGE_MAP_EDITOR_OT_t3d_export'

    def draw_header(self, _context:Context):
        sfile = _context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, 'add_skylight', text='')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'skylight_location')
        layout.prop(operator, 'skylight_color')
        layout.prop(operator, 'skylight_brightness')
        layout.prop(operator, 'skylight_sample_factor')


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