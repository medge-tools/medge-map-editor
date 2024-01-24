import bpy
from bpy.props import *
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
    bl_idname = 'medge_map_editor.ase_export'
    bl_label = 'Export ASE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.ase'

    filter_glob: StringProperty(
        default='*.ase',
        options={'HIDDEN'},
        maxlen=255) # Max internal buffer length, longer would be hilighted.


    combine_meshes: BoolProperty(
        default=False,
        name='Combine Meshes')


    units: EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units')


    def draw(self, context : bpy.types.Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'units')
        layout.prop(self, 'combine_meshes')


    def execute(self, context : bpy.types.Context):
        # Apply transform to temporary copies and mirror x-axis
        temp_objs_to_export = []
        # To convert curves to mesh we create a new mesh to keep the curve intact.
        # But the new mesh needs the name of the original mesh, because the original name is what is written to .t3d.
        # Therefore, swap the names before export and swap back after.
        orig_obj_names = []
        for obj in context.scene.objects:

            me_actor = medge.get_me_actor(obj)
            if me_actor.type != ActorType.STATIC_MESH: continue
            if me_actor.static_mesh.use_prefab: continue

            # Convert to mesh
            if obj.type == 'CURVE':
                new_obj = utils.copy_object(obj)
                utils.convert_to_mesh_in_place(new_obj)
            else:
                new_obj = utils.copy_object(obj)
            
            utils.apply_all_transforms(new_obj)
            # Mirror x, y because the ASE exporter rotates the models 180 degrees around z
            utils.transform(new_obj.data, [Matrix.Scale(-1, 3, (1, 0, 0))])
            utils.transform(new_obj.data, [Matrix.Scale(-1, 3, (0, 1, 0))])
            temp_objs_to_export.append(new_obj)
            orig_obj_names.append((obj, obj.name))
            self.__swap_names(obj, new_obj)
                

        self.__check_material(temp_objs_to_export)
        self.__format_names(temp_objs_to_export)


        # Select objects to export
        utils.deselect_all()
        for obj in temp_objs_to_export:
            utils.select_obj(obj)


        try:
            bpy.ops.io_scene_ase.ase_export(filepath=self.filepath, units=self.units, combine_meshes=self.combine_meshes)
            self.report({'INFO'}, 'ASE exported successful')
        except ASEExportError as e:
            self.report({'ERROR'}, str(e))


        # Restore original names
        for obj, name in orig_obj_names:
            obj.name = name

        # Remove temp objects
        for obj in temp_objs_to_export:
            utils.remove_object(obj)

            
        return {'FINISHED'}
    
    # -------------------------------------------------------------------------
    # Add default material if missing; required for ASE Export
    def __check_material(self, objects : list[bpy.types.Object]):
        for obj in objects:
            if len(obj.data.materials) > 0: continue
            
            mat = bpy.data.materials.get('ME_Default')
            if mat is None:
                mat = bpy.data.materials.new(name='ME_Default')
            obj.data.materials.append(mat)
            obj.active_material_index = len(obj.data.materials) - 1 

    # -------------------------------------------------------------------------
    def __swap_names(self, source: bpy.types.Object, target: bpy.types.Object):
            temp = source.name
            source.name = target.name
            target.name = temp

    # -------------------------------------------------------------------------
    def __format_names(self, objects : list[bpy.types.Object]):
        for obj in objects:
            obj.name = obj.name.replace('.', '_')