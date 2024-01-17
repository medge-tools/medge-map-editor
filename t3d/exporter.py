import bpy
import bpy_extras
from .builder import *
from .writer import *
from ..b3d import medge_tools as medge

# =============================================================================
class ME_OT_Exporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export scene to a .t3d file'''
    bl_idname = 'medge_editor.t3d_exporter'
    bl_label = 'Export T3D'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.t3d'

    filter_glob : bpy.props.StringProperty(
        default='*.t3d',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be hilighted.
    )

    units : bpy.props.EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units'
    )

    units_scale = {
        'M': 60.352,
        'U': 1.0
    }

    selected_objs : bpy.props.BoolProperty(
        name='Selected Objects',
        description='Only export selected objects',
        default=False
    )

    ase_export : bpy.props.BoolProperty(
        name='Export ASE',
        description='Export static meshes',
        default=True
    )

    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'units')
        layout.prop(self, 'selected_objs')
        layout.prop(self, 'ase_export')

    def execute(self, context : bpy.types.Context):
        self.__t3d_export(context)
        self.__ase_export(context)
        return {'FINISHED'}
        
    def __t3d_export(self, context : bpy.types.Context):
        try:
            options = T3DBuilderOptions()
            options.only_selection = self.selected_objs
            options.scale = self.units_scale[self.units]
            scene = T3DBuilder().build(context, options)
            T3DWriter().write(self.filepath, scene)
            self.report({'INFO'}, 'T3D exported successful')
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))
        
    def __ase_export(self, context : bpy.types.Context):
        temp_objects = []
        
        # Convert curves to meshes
        for obj in context.selectable_objects:
            if obj.type == 'CURVE':
                new_obj = medge.curve_to_mesh(obj)
                temp_objects.append(new_obj)
        
        # Replace . with _
        for obj in context.selectable_objects:
            obj.name = obj.name.replace('.', '_')
                
        # Add default material if missing
        for obj in context.selectable_objects:
            if len(obj.data.materials) > 0: continue
            mat = bpy.data.materials.get('ME_Default')
            if mat is None:
                mat = bpy.data.materials.new(name='ME_Default')
            obj.data.materials.append(mat)
            obj.active_material_index = len(obj.data.materials) - 1 

        # Select all ActorType.STATICMESH with export_ase == TRUE
        utils.deselect_all()
        for obj in context.selectable_objects:
            me_actor = utils.get_me_actor(obj)
            if me_actor is None: continue
            if me_actor.type != ActorType.STATICMESH: continue
            if me_actor.ase_export != True: continue
            obj.select_set(True)
        try:
            bpy.ops.io_scene_ase.ase_export(filepath=self.filepath, units=self.units)
        except T3DBuilderError as e:
            self.report({'ERROR'}, str(e))

        # Remove temp objects
        # for obj in temp_objects:
        #     utils.remove_object(obj)