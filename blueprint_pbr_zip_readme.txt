Blueprint full-PBR ZIP workflow
Version 0.3.9

This is for the full ambientCG-style texture ZIPs that contain BaseColor/Color, Roughness, NormalGL/NormalDX, Displacement/Height, AO, etc.

Folder layout:

project-folder/
  your_building.blend
  blueprint.obj
  blueprint.mtl
  pbr_zips/
    Bricks038_1K-JPG.zip
    Concrete023_1K-JPG.zip
    PaintedPlaster003_1K-JPG.zip
    Carpet012_1K-JPG.zip
    ...
  blueprint_apply_pbr_from_zips.py

Steps:
1. Export OBJ from the blueprint tool.
2. Import blueprint.obj into Blender.
3. Save the Blender file in your project folder.
4. Put the full downloaded PBR ZIPs in a folder named pbr_zips next to the .blend file.
5. In Blender, open the Scripting tab.
6. Open blueprint_apply_pbr_from_zips.py and Run Script.
7. Switch to Material Preview or Rendered view.

The script extracts the image maps into textures_pbr_extracted/ and wires Blender materials automatically.
It uses BaseColor, Roughness, Metallic when present, NormalGL/Normal, Height as Bump, and optional Ambient Occlusion.
NormalGL/OpenGL normal maps are preferred for Blender. If only NormalDX is present, the script can still use it, but lighting may look slightly inverted.

Do not drag the ZIPs or JPGs into the Blender collection. The script connects the images to material nodes.
