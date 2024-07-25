# MEdge Editor

With this addon you can export Blender scenes to a T3D file, which can be imported into UnrealEd. See `example_medge_map_editor.blend` in Releases for a complete setup.

## Dependencies

If you want to export StaticMeshes when exporting to T3D, then you need to use [io_scene_ase](https://github.com/medge-tools/io_scene_ase), which is a fork that can export selected objects separately. You can use other addons, but if those operators are called anything other than `io_scene_ase`, then the export option `Export StaticMeshes` will do nothing.

## How It Works

### T3D

Inside UnrealEd a scene or selected objects can be exported to a [T3D](https://wiki.beyondunreal.com/Legacy:T3D_File) file. The T3D file format holds a text list of Unreal objects and their settings. Geometry data of Brushes and Volumes are stored, but meshes and materials are referenced. This addon does the same for Blender objects.

### Inside Blender

Inside UnrealEd meshes and materials are refenced by their package path inside the GenericBrowser. We can replicated this structure inside Blender using Collections. You need a Collection named `GenericBrowser` and add child Collections with the name of the packages as they are in the UnrealEd GenericBrowser. 

The following actors are implemented and are accessible from the addon panel:

| *Actor*        | *Description*
|----------------|----------------
| Brush          | This exports a mesh as a Brush with the CSG_Add option and you can add a material by name
| StaticMesh     | If this is an instance of another StaticMesh, use the option `use_prefab`, e.g. when creating a ladder. If it is not an instance, it will be automatically exported with the export option `Export StaticMeshes`.
| Ladder         | Ladder volume with an `is_pipe` option.
| Swing          | -
| Zipline        | Curve with a bounding box that deforms with the curve. Do remember to put it inside a child Collection of the GenericBrowser.
| Springboard    | Behind the scenes this is a StaticMesh, namely `P_Gameplay.SpringBoard.SpringBoardHigh_ColMesh` and it has an option to hide it in game. However, you don't have to use this mesh to have springboard functionality. You can use this as a reference of where to place two surfaces.
| BlockingVolume | Blocking volume with the option to add a physical material like `TDPhysicalMaterials.Glass.Bulletproof.PM_Glass_BulletproofSlide`. 
| TriggerVolume  | -
| KillVolume     | - 
| PlayerStart    | Player start with the option to make it the time trial start.
| Checkpoint     | Time Trial checkpoint.
|                |
| Lights         | Currently only the Sun light can be exported and rotations are not exported correctly (see [TODO](#todo)).

For some actors, do not apply any transforms, as we want to export those. This is the case for StaticMesh, Ladder, Swing, Springboard and PlayerStart. There are info boxes at those actors to remind you.

### Import Into UnrealEd

1. Before importing your T3D file into UnrealEd, make sure that all referenced meshes and materials are loaded into the GenericBrowser. 

2. Import your T3D file into UnrealEd

3. Build the scene: `Build > Build All`

## How To Extend

### Overview

In this section we go over how to extend the map editor with other Unreal objects that you would like to export from Blender. The relevant source files are:

- `src > t3d > scene.py` This file contains the actor types like Brush, StaticMesh, Volumes in their T3D format.
- `src > t3d > builder.py` For each actor type this file contains the implementation to translate a Blender object to its respective T3D format.
- `src > props.py` For each actor type this file contains its respective PropertyGroup.
- `src > gui.py` For each actor type there is a button to create a instance.

### Step-By-Step

1. Inside UnrealEd export the actors to a T3D file: `File > Export > Selected Only...`

2. UnrealEd exports alot of default data about the actor that you don't need perse to import it back into UnrealEd. Open the T3D file and start removing text that you deem irrelevant, and import the file back to check if it still works. Keep doing this till you are satisfied. As a reference you can export one of the already implemented Unreal objects and compare them to the actor in `scene.py`.

3. Go to `scene.py`, add your actor type to the end of `ActorType` and add your T3D implementation below. If your actor is a volume, you can inherit from `Brush`. Look at the other volumes for reference.

4. Go to `props.py`, create a `PropertyGroup` for your actor, which inherits from `Actor` and override `init()` and `draw()`. Add your actor as a `PointerProperty` to `MET_OBJECT_PG_Actor`, which is at the bottom of the file. In `MET_OBJECT_PG_Actor` you also have to update `draw()` and `__on_type_update()`. While not necessary, we like to write getters as they help with intellisense.

5. Go to `gui.py > MET_PT_actors` and update `draw()` to add a button for your actor.

6. Go to `builder.py`, create a `Builder` for your actor and update `T3DBuilder > build_actor()`, which is at the bottom of the file.

These are all the steps, but you may not need all of them. For example, for the Springboard, which is an instance of a StaticMesh, we skipped step 3. 

## TODO

### Should Have
- Only the sun light can be exported and the conversion method for rotation doesn't work for lights; they probably use quaternions instead of Euler's.
- Player height is 192cm and not 195cm
- To be able to export different level collections to seperate t3d files

### Could Have
- You can add materials to Brushes, but only by name. It would be nice if we could texture Brushes inside Blender and export those materials also.
