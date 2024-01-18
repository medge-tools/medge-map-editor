import bpy
import bpy_extras
from ..b3d import medge_tools as medge
from ..b3d import utils
from ..t3d.scene import ActorType

# =============================================================================
class ASEExportError(Exception):
    pass

# =============================================================================
class ME_OT_ASE_Export(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Process selection before exporting to a .ase files'''
    bl_idname = 'medge_tools.ase_export'
    bl_label = 'Export ASE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.ase'

    filter_glob : bpy.props.StringProperty(
        default='*.ase',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be hilighted.
    )

    units : bpy.props.EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units'
    )

    def execute(self, context : bpy.types.Context):
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
            me_actor = medge.get_me_actor(obj)
            if me_actor is None: continue
            if me_actor.type != ActorType.STATICMESH: continue
            if me_actor.ase_export != True: continue
            obj.select_set(True)
        try:
            bpy.ops.io_scene_ase.ase_export(filepath=self.filepath, units=self.units)
        except ASEExportError as e:
            self.report({'ERROR'}, str(e))

        # Remove temp objects
        for obj in temp_objects:
            utils.remove_object(obj)
            
        return {'FINISHED'}