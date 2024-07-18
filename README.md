# MEdge Editor

## How It Works
A Blender scene is exported to a [.t3d](https://wiki.beyondunreal.com/Legacy:T3D_File) file. The T3D file format holds a text list of Unreal objects and their settings. Geometry data of brushes and volumes are stored, but meshes are referenced.

## How To Extend
### Overview
In this section we go over how to extend the map editor with other Unreal objects that you would like to export. The relevant source files are:

- ` src > t3d > scene.py `: This file contains the actor types like Brush, StaticMesh, Volumes and their respective .t3d format.
- ` src > t3d > builder.py `: For each actor type this file contains the implementation to translate a Blender object to its respective .t3d format.
- ` src > props.py `: For each actor type this file contains its respective PropertyGroup.

### Step-By-Step
1. Inside UnrealEd export the object to a .t3d file: ` File > Export > Selected Only... `
2. Unreal exports alot of default data about the object that you don't care about. Open the .t3d file and start removing text that you deem irrelevant, and import the file back to check if it still works. Keep doing this till you are satisfied. As a reference you can export one of the already implemented Unreal objects and compare them to the text in `scene.py`.
3. Go to `scene.py`, add your object type to `ActorType` and add your .t3d implementation below. If your object is a volume, you can inherit from `Brush`. Look at the other objects for reference.
4. Go to `props.py`, create a `PropertyGroup` for your object: inherit from `Actor` and implement `init()` and `draw()`. Add your object as a `PointerProperty` to `MET_OBJECT_PG_Actor`, which is at the bottom of the file. In `MET_OBJECT_PG_Actor` you also have to update `draw()` and `__on_type_update()`. While not necessary I like to write getters as they provide intellisense.
5. Go to `builder.py`, create a `Builder` for your object and update `T3DBuilder.build_actor()`, which is at the bottom of the file.

## TODO
Currently, only the sun light can be exported and the conversion method for rotation doesn't work for lights; probably because they use quaternions instead of Euler's
