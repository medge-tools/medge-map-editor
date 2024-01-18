import bpy
import bpy_extras
from mathutils import Matrix
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
        maxlen=255, # Max internal buffer length, longer would be hilighted.
    )

    units : bpy.props.EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units'
    )

    def execute(self, context : bpy.types.Context):
        # Apply transform to temporary copies and mirror x-axis
        temp_objs_to_export = []
        utils.select_all()
        for obj in context.selected_objects:
            me_actor = medge.get_me_actor(obj)
            if me_actor.type != ActorType.STATICMESH: continue
            if not me_actor.static_mesh.ase_export: continue
            # Convert curves to meshes
            if obj.type == 'CURVE':
                new_obj = utils.copy_object(obj)
                utils.convert_to_mesh_in_place(new_obj)
            else:
                new_obj = utils.copy_object(obj)

            utils.apply_all_transforms(new_obj)
            utils.transform(new_obj.data, [Matrix.Scale(-1, 3, (1, 0, 0))])
            temp_objs_to_export.append(new_obj)
        
        # Replace . with _ to be able to import in ME Editor
        for obj in temp_objs_to_export:
            obj.name = obj.name.replace('.', '_')
                
        # Add default material if missing; required for ASE Export
        for obj in temp_objs_to_export:
            if len(obj.data.materials) > 0: continue
            
            mat = bpy.data.materials.get('ME_Default')
            if mat is None:
                mat = bpy.data.materials.new(name='ME_Default')
            obj.data.materials.append(mat)
            obj.active_material_index = len(obj.data.materials) - 1 

        # Select objects to export
        utils.deselect_all()
        for obj in temp_objs_to_export:
            utils.select_obj(obj)

        try:
            bpy.ops.io_scene_ase.ase_export(filepath=self.filepath, units=self.units)
        except ASEExportError as e:
            self.report({'ERROR'}, str(e))

        # Remove temp objects
        for obj in reversed(temp_objs_to_export):
            utils.remove_object(obj)
            
        return {'FINISHED'}