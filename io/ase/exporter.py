import bpy
from bpy.props           import StringProperty, BoolProperty, EnumProperty
from bpy.types           import Operator, Context, Object, TOPBAR_MT_file_export
from bpy_extras.io_utils import ExportHelper
from mathutils           import Matrix

from ...                 import b3d_utils
from ...map_editor.props import get_actor_prop
from ..t3d.scene         import ActorType


# -----------------------------------------------------------------------------
class ASEExportError(Exception):
    pass


# -----------------------------------------------------------------------------
class MET_OT_ASE_Export(Operator, ExportHelper):
    '''Process selection before exporting to a .ase files'''
    bl_idname = 'medge_map_editor.ase_export'
    bl_label = 'Export ASE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    filename_ext = '.ase'


    filter_glob: StringProperty(
        default='*.ase',
        options={'HIDDEN'},
        maxlen=255) # Max internal buffer length, longer would be highlighted.


    combine_meshes: BoolProperty(
        default=False,
        name='Combine Meshes')


    units: EnumProperty(
        default='M',
        items=(('M', 'Meters', ''),
               ('U', 'Unreal', '')),
        name='Units')
    
    
    selected_objects: BoolProperty(
        name='Selected Objects',
        default=False)


    def draw(self, _context:Context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(self, 'units')
        layout.prop(self, 'selected_objects')
        layout.prop(self, 'combine_meshes')


    def execute(self, _context:Context):
        # Apply transform to temporary copies and mirror x-axis
        temp_objs_to_export = []

        # To convert curves to mesh we create a new mesh to keep the curve intact.
        # But the new mesh needs the name of the original mesh, because the original name is what is written to .t3d.
        # Therefore, swap the names before export and swap back after.
        orig_obj_names = []

        objects = _context.scene.objects

        if self.selected_objects:
            objects = _context.selected_objects

        for obj in objects:

            me_actor = get_actor_prop(obj)

            if me_actor.type != ActorType.STATIC_MESH.name: continue
            if me_actor.static_mesh.use_prefab: continue

            # Convert to mesh
            if obj.type == 'CURVE':
                new_obj = b3d_utils.duplicate_object(obj, False)
                b3d_utils.convert_to_mesh_in_place(new_obj)

            else:
                new_obj = b3d_utils.duplicate_object(obj, False)
            
            # This will translate the object origin to the world origin
            new_obj.parent = None

            # Mirror x, y because the ASE exporter rotates the models 180 degrees around z-axis, around the origin
            b3d_utils.transform(new_obj.data, [Matrix.Scale(-1, 3, (1, 0, 0)), Matrix.Scale(-1, 3, (0, 1, 0))])

            temp_objs_to_export.append(new_obj)
            orig_obj_names.append((obj, obj.name))
            
            self.__swap_names(obj, new_obj)

        self.__check_material(temp_objs_to_export)
        self.__format_names(temp_objs_to_export)

        # Select objects to export
        b3d_utils.deselect_all_objects()

        for obj in temp_objs_to_export:
            b3d_utils.select_object(obj)

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
            b3d_utils.remove_object(obj)
            
        return {'FINISHED'}
    

    # Add default material if missing; required for ASE Export
    def __check_material(self, _objects:list[Object]):
        for obj in _objects:
            if len(obj.data.materials) > 0: continue
            
            mat = bpy.data.materials.get('ME_Default')
            if mat is None:
                mat = bpy.data.materials.new(name='ME_Default')
            obj.data.materials.append(mat)
            obj.active_material_index = len(obj.data.materials) - 1 


    def __swap_names(self, _source:Object, _target:Object):
            temp = _source.name
            _source.name = _target.name
            _target.name = temp


    def __format_names(self, _objects:list[Object]):
        for obj in _objects:
            obj.name = obj.name.replace('.', '_')


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def menu_func_export(self, _context:Context):
    self.layout.operator(MET_OT_ASE_Export.bl_idname, text='MEdge ASE (.ase)')


# -----------------------------------------------------------------------------
def register():
    TOPBAR_MT_file_export.append(menu_func_export)


# -----------------------------------------------------------------------------
def unregister():
    TOPBAR_MT_file_export.remove(menu_func_export)