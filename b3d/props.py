import bpy
from bpy.props import *
import math
from typing import Any, Callable
from mathutils import Matrix

from ..t3d.scene import ActorType
from . import utils
from . import medge_tools as medge

# =============================================================================
# RESOURCE BROWSER
# -----------------------------------------------------------------------------
# =============================================================================
class ME_PG_Resource(bpy.types.PropertyGroup):
    def path(self) -> str:
        self.package.name.rstrip('.')
        return self.package.name + '.' + self.name

    name: StringProperty(name='Resource', default='MyResource')
    package_name: StringProperty(name='Package')

# =============================================================================
class ME_PG_Package(bpy.types.PropertyGroup):
    def add_resource(self):
        self.resources.add()
        self.active_idx = len(self.resources) - 1
    
    def remove_active_resource(self):
        self.resources.remove(self.active_idx)
        self.active_idx = min(max(0, self.active_idx - 1), len(self.resources) - 1)

    def empty(self) -> bool:
        if len(self.resources) == 0:
            return True
        return False

    def get_active_resource(self) -> ME_PG_Resource | None:
        if self.resources:
            return self.resources[self.active_idx]
        return None

    def __on_name_update(self, context: bpy.types.Context):
        for r in self.resources:
            r.package_name = self.name

    name: StringProperty(name='Package', default='MyPackage', update=__on_name_update)
    resources: CollectionProperty(type=ME_PG_Resource)
    active_idx: IntProperty(name='Resource Index', default=0)

# =============================================================================
class ME_SCENE_PG_GenericBrowser(bpy.types.PropertyGroup):
    def add_package(self):
        self.packages.add()
        self.active_idx = len(self.packages) - 1
    
    def remove_active_package(self):
        self.packages.remove(self.active_idx)
        self.active_idx = min(max(0, self.active_idx - 1), len(self.packages) - 1)
    
    def empty(self) -> bool:
        if len(self.packages) == 0:
            return True
        return False

    def get_active_package(self) -> ME_PG_Package | None:
        if self.packages:
            return self.packages[self.active_idx]
        return None

    packages: CollectionProperty(type=ME_PG_Package)
    active_idx: IntProperty(name='Package Index', default=0)

# =============================================================================
class ME_UL_GenericList(bpy.types.UIList):
    def draw_item(self, 
                  context: bpy.types.Context | None, 
                  layout: bpy.types.UILayout, 
                  data: Any | None, 
                  item: Any | ME_PG_Package | None, 
                  icon: int | None, active_data: Any, 
                  active_property: str, 
                  index: Any | None = 0, 
                  flt_flag: Any | None = 0):
        layout.label(text=item.name)

# =============================================================================
# ACTORS
# -----------------------------------------------------------------------------
# =============================================================================
def ActorTypeProperty(callback : Callable = None):
    return EnumProperty(
        items=[
            (ActorType.NONE, 'None', 'None'),
            (ActorType.PLAYERSTART, 'PlayerStart', 'PlayerStart'),
            (ActorType.BRUSH, 'Brush', 'Brush'),
            (ActorType.LADDER, 'Ladder', 'TdLadderVolume'),
            (ActorType.PIPE, 'Pipe', 'TdLadderVolume'),
            (ActorType.SWING, 'Swing', 'TdSwingVolume'),
            (ActorType.ZIPLINE, 'Zipline', 'TdZiplineVolume'),
            (ActorType.SPRINGBOARD, 'Springboard', 'P_Gameplay.SpringBoardHigh_layoutMesh'),
            (ActorType.STATICMESH, 'StaticMesh', 'StaticMeshActor')
        ],
        name='ActorType',
        default=ActorType.NONE,
        update=callback
    )
# =============================================================================
ACTOR_DEFAULT_SCALE = {
    ActorType.PLAYERSTART   : (.5, .5, -1),
    ActorType.BRUSH         : (1, 1, 1),
    ActorType.LADDER        : (.5, .5, 2), 
    ActorType.PIPE          : (.5, .5, 2),
    ActorType.SWING         : (1, 1, .5),
    ActorType.ZIPLINE       : (1, 1, 1),
    ActorType.SPRINGBOARD   : (1, 1, 1),
    ActorType.STATICMESH    : (1, 1, 1)
}

# =============================================================================
ACTOR_DEFAULT_STATIC_MESH = {
    ActorType.PLAYERSTART   : ('MyPackage', ''),
    ActorType.BRUSH         : ('MyPackage', ''),
    ActorType.LADDER        : ('P_Generic.Ladders', 'S_LadderSystem_01b'),
    ActorType.PIPE          : ('P_Pipes.PipeSystem_03', 'S_PipeSystem_03h'),
    ActorType.SWING         : ('P_RunnerObjects.SwingPole_01', 'S_SwingPole_01c'),
    ActorType.ZIPLINE       : ('MyPackage', ''),
    ActorType.SPRINGBOARD   : ('P_Gameplay.SpringBoard', 'SpringBoardHigh_layoutMesh'),
    ActorType.STATICMESH    : ('MyPackage', ''),
}

# =============================================================================
class ME_PG_Gizmo(bpy.types.PropertyGroup):
    obj : PointerProperty(type=bpy.types.Object)

# =============================================================================
class ME_ActorBase():
    # -------------------------------------------------------------------------
    def __clear_widgets(self):
        for gm in self.widgets:
            if gm.obj != None:
                bpy.data.objects.remove(gm.obj)
        self.widgets.clear()

    # -------------------------------------------------------------------------
    def reset(self, obj: bpy.types.Object):
        pass
    
    # -------------------------------------------------------------------------
    def set_mesh(self, obj):
        pass

    # -------------------------------------------------------------------------
    def set_display_type(self, obj):
        obj.display_type = 'TEXTURED'

    # -------------------------------------------------------------------------
    def add_widgets(self, obj):
        pass

    # -------------------------------------------------------------------------
    def init(self, obj: bpy.types.Object):
        self.__clear_widgets()
        self.reset(obj)
        self.set_mesh(obj)
        self.set_display_type(obj)
        self.add_widgets(obj)

    # -------------------------------------------------------------------------
    def draw(self, layout: bpy.types.UILayout):
        pass

    # -------------------------------------------------------------------------
    widgets: CollectionProperty(type=ME_PG_Gizmo)
    scale: FloatVectorProperty(default=(1.0, 1.0, 1.0), subtype='TRANSLATION')

# =============================================================================
class ME_ACTOR_PG_PlayerStart(ME_ActorBase, bpy.types.PropertyGroup):
    # -------------------------------------------------------------------------
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.PLAYERSTART]

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):
        utils.set_mesh(obj, utils.create_flag(self.scale))

    # -------------------------------------------------------------------------
    def set_display_type(self, obj):
        obj.display_type = 'WIRE'

# =============================================================================
class ME_ACTOR_PG_Brush(ME_ActorBase, bpy.types.PropertyGroup):
    # -------------------------------------------------------------------------
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.BRUSH]

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):        
        utils.set_mesh(obj, utils.create_cube(self.scale))

    # -------------------------------------------------------------------------
    def draw(self, layout: bpy.types.UILayout):
        col = layout.column(align=True)
        col.prop(self, 'material_package')
        col.prop(self, 'material_name')

    # -------------------------------------------------------------------------
    def material(self) -> str:
        self.material_package.rstrip('.')
        return self.material_package + '.' + self.material_name

    material_package: StringProperty(name='Package')
    material_name: StringProperty(name='Name')

# =============================================================================
class ME_ACTOR_PG_Ladder(ME_ActorBase, bpy.types.PropertyGroup):
    # -------------------------------------------------------------------------
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.LADDER]

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):        
        utils.set_mesh(obj, utils.create_cube(self.scale))

    # -------------------------------------------------------------------------
    def set_display_type(self, obj):
        obj.display_type = 'WIRE'

    # -------------------------------------------------------------------------
    def add_widgets(self, obj):
        arrow = self.widgets.add()
        arrow.obj = utils.new_object('ARROW', utils.create_arrow(self.scale), medge.COLLECTION_WIDGET, obj)
        utils.set_obj_selectable(arrow.obj, False)

# =============================================================================
class ME_ACTOR_PG_Swing(ME_ActorBase, bpy.types.PropertyGroup):
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.SWING]

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):        
        utils.set_mesh(obj, utils.create_cube(self.scale))

    # -------------------------------------------------------------------------
    def set_display_type(self, obj):
        obj.display_type = 'WIRE'

    # -------------------------------------------------------------------------
    def add_widgets(self, obj):
        m_t07_x = Matrix.Translation((.7, 0, 0))
        m_t035_x = Matrix.Translation((.2, 0, 0))
        m_r90_x = Matrix.Rotation(math.radians(90), 3, (1, 0, 0))
        m_r90_y = Matrix.Rotation(math.radians(90), 3, (0, 1, 0))
        m_mir_x = Matrix.Scale(-1, 3, (1, 0, 0))
        arrow0 = self.widgets.add()
        arrow1 = self.widgets.add()
        arrow2 = self.widgets.add()
        for arrow in self.widgets:
            scale = self.scale * .3
            arrow.obj = utils.new_object('ARROW', utils.create_arrow(scale), medge.COLLECTION_WIDGET, obj)
            utils.set_obj_selectable(arrow.obj, False)
        utils.transform(arrow0.obj.data, [m_t07_x , m_r90_x])
        utils.transform(arrow1.obj.data, [m_t035_x, m_r90_x, m_r90_y])
        utils.transform(arrow2.obj.data, [m_t07_x , m_r90_x, m_mir_x])  

# =============================================================================
class ME_ACTOR_PG_Zipline(ME_ActorBase, bpy.types.PropertyGroup):
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.ZIPLINE]

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):  
        utils.set_mesh(obj, utils.create_cube())      
        self.curve = medge.create_zipline()
        self.curve.location = obj.location
        utils.set_parent(self.curve, obj)

    # -------------------------------------------------------------------------
    def set_display_type(self, obj):
        obj.display_type = 'WIRE'

    # -------------------------------------------------------------------------
    def draw(self, layout: bpy.types.UILayout):
        col = layout.column(align=True)
        col.prop(self, 'curve')

    curve: PointerProperty(type=bpy.types.Object, name='Curve')

# =============================================================================
class ME_ACTOR_PG_SpringBoard(ME_ActorBase, bpy.types.PropertyGroup):
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.SPRINGBOARD]

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):  
        utils.set_mesh(obj, medge.create_springboard())

# =============================================================================
class ME_ACTOR_PG_StaticMesh(ME_ActorBase, bpy.types.PropertyGroup):
    # -------------------------------------------------------------------------
    def reset(self, obj: bpy.types.Object):
        self.scale = ACTOR_DEFAULT_SCALE[ActorType.STATICMESH]
        self.parent = obj

    # -------------------------------------------------------------------------
    def set_mesh(self, obj):
        if obj.type == 'MESH':
            utils.set_mesh(obj, utils.create_cube())

    # -------------------------------------------------------------------------
    def draw(self, layout: bpy.types.UILayout):
        col = layout.column(align=True)
        col.prop(self, 'use_material')
        col.prop(self, 'use_prefab')
        if not self.use_prefab:
            col.prop(self, 'ase_export')

        col = layout.column(align=True)
        col.label(text='Static Mesh')
        if self.use_prefab:
            col.prop(self, 'prefab')
        else:
            col.prop(self, 'package')
            col.prop(self, 'name')

            col = layout.column(align=True)
            col.label(text='Material')
            col.prop(self, 'material_package')
            col.prop(self, 'material_name')

    # -------------------------------------------------------------------------
    # obj.name might be changed by Blender; we update self.static_mesh_name in utils.on_depsgraph_update
    def __on_static_mesh_name_update(self, context: bpy.types.Context):
        if self.use_prefab: return
        # Check prevents circular setting of name
        if (obj := context.active_object) != self.parent: return
        if obj.name != self.name:
            obj.name = self.name
            
    # -------------------------------------------------------------------------
    def __on_use_prefab_update(self, context: bpy.types.Context):
        if self.use_prefab:
            self.ase_export = False

    # -------------------------------------------------------------------------
    def __on_prefab_update(self, context: bpy.types.Context):
        obj = context.active_object
        prefab = self.prefab
        if not prefab: 
            self.set_mesh(obj)
            return
        utils.set_mesh(obj, prefab.data)
        me_actor = medge.get_me_actor(prefab)
        self.package = me_actor.static_mesh.package
        self.name = me_actor.static_mesh.name
        if not self.package or not self.name:
            self.report({'WARNING'}, 'Prefab has no package data')

    # -------------------------------------------------------------------------
    def path(self) -> str:
        self.package.rstrip('.')
        return self.package + '.' + self.name

    # -------------------------------------------------------------------------
    def on_depsgraph_update_post_sync_static_mesh_name(scene : bpy.types.Scene, depsgraph : bpy.types.Depsgraph):
        for obj in scene.objects:
            me_actor = medge.get_me_actor(obj)
            if me_actor is None: continue
            if me_actor.static_mesh.name != obj.name:
                me_actor.static_mesh.name = obj.name

    # -------------------------------------------------------------------------
    parent: PointerProperty(type=bpy.types.Object)
    package: StringProperty(name='Package', default='MyPackage')
    name: StringProperty(name='Name', update=__on_static_mesh_name_update)
    use_prefab: BoolProperty(name='Use Prefab', default=False, update=__on_use_prefab_update)
    prefab: PointerProperty(type=bpy.types.Object, name='Prefab', update=__on_prefab_update)
    use_material: BoolProperty(name='Use Material', default=False)
    material_package: StringProperty(name='Package')
    material_name: StringProperty(name='Name')
    ase_export: BoolProperty(name='Export ASE', default=False, description='Object will be export as .ase file.')

# =============================================================================
class ME_OBJECT_PG_Actor(bpy.types.PropertyGroup):
    # -------------------------------------------------------------------------
    def __on_type_update(self, context: bpy.types.Context):
        obj = context.active_object
        obj.name = str(self.type)
        utils.set_active(obj)

        match(self.type):
            case ActorType.PLAYERSTART:
                self.player_start.init(obj)
            case ActorType.BRUSH:
                self.brush.init(obj)
            case ActorType.LADDER:
                self.ladder.init(obj)
            case ActorType.PIPE:
                self.pipe.init(obj)
            case ActorType.SWING:
                self.swing.init(obj)
            case ActorType.ZIPLINE:
                self.zipline.init(obj)
            case ActorType.SPRINGBOARD:
                self.springboard.init(obj)
            case ActorType.STATICMESH:
                self.static_mesh.init(obj)
    
    # -------------------------------------------------------------------------
    type: ActorTypeProperty(__on_type_update)
    t3d_export: BoolProperty(name='Export T3D', default=True, description='Object will be export as part of the .t3d scene')

    player_start: PointerProperty(type=ME_ACTOR_PG_PlayerStart)
    brush: PointerProperty(type=ME_ACTOR_PG_Brush)
    ladder: PointerProperty(type=ME_ACTOR_PG_Ladder)
    pipe: PointerProperty(type=ME_ACTOR_PG_Ladder)
    swing: PointerProperty(type=ME_ACTOR_PG_Swing)
    zipline: PointerProperty(type=ME_ACTOR_PG_Zipline)
    springboard: PointerProperty(type=ME_ACTOR_PG_SpringBoard)
    static_mesh: PointerProperty(type=ME_ACTOR_PG_StaticMesh)



