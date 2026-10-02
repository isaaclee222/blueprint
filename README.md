<h1 align="center">Blueprint — Smart Building Sketch</h1>

<p align="center">
  <strong>Sketch a multi-story building in 2D. Get a textured, room-by-room 3D model in Blender.</strong>
</p>

<p align="center">
  JavaScript · HTML · CSS · Geometry · JSON · Wavefront OBJ · Blender (Python)
</p>

<p align="center">
  <a href="https://isaaclee222.github.io/blueprint-smart-building-sketch/"><strong>Live demo</strong></a> ·
  <a href="#demo-videos">Demo videos</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#what-i-contributed">What I contributed</a>
</p>

<img width="1403" height="918" alt="blueprintscreenshot" src="https://github.com/user-attachments/assets/4de397f9-5c17-4c71-b9f6-daa0a10d633e" />

---

## Overview

**Blueprint** is a browser-based 2D building-layout editor built for rapid 3D prototyping. You draw walls on a snapping grid, pull them out into rooms, add doors, windows, stairs and pillars, stack as many floors as you need, and export. A companion Blender script then builds the full 3D structure with PBR materials already applied to the correct surfaces.

It exists to remove the slowest part of level and building blockouts: modeling walls, floors and openings by hand in a 3D package. With Blueprint, a layout that would take a long session of manual modeling becomes a short sketch, and the result is a clean, organized starting point for Blender, Unity or Unreal.

<img width="1569" height="918" alt="blenderexample" src="https://github.com/user-attachments/assets/94d95b6b-251a-42cc-a5f6-bdaf2b0f1420" />


## Features

**Layout editing**
- Grid-snapped wall drawing with endpoint lengthening and wall pushing
- **Shift + drag** the red reticles at a wall's midpoint to extrude it into a complete room: four walls, a floor and a ceiling
- Selection, erase, delete, and full **undo / redo**
- No fixed cap on building footprint or number of floors

**Building elements**
- Full walls and half walls
- Doors, stairs, pillars
- **Floor cutouts** for stairwells and open-to-below spaces
- Windows on selected walls in four sizes: **standard, wide, huge, and tall huge**
- Exterior wall and exterior brick material presets, plus a paint tool

**Multi-floor workflow**
- Floor switcher (F1, F2, F3 and more) with the floor below shown as a reference outline
- Rooms are tracked per floor with their own names and areas

**Export pipeline**
- **JSON**: structured plan data for the building
- **OBJ**: generated 3D geometry for Blender and other 3D tools
- **PBR texture packs**: material setup that the Blender script applies automatically
- **PNG**: image export of the plan

## Demo videos

**1. Drawing a building in the editor**


https://github.com/user-attachments/assets/1fd395c9-4236-46b6-94c7-9697d86f21b3

**2. Importing into Blender**


https://github.com/user-attachments/assets/1e76746a-ece9-4dbc-8f84-7fd73b4395d2

## How it works

1. **Draw walls.** Click and drag on the grid. Endpoints snap into place so layouts stay clean.
2. **Make rooms.** Hold **Shift** and drag the red reticle near a wall's midpoint to pull it out into an enclosed room with a floor and ceiling.
3. **Add detail.** Place doors, half walls, pillars and stairs. Cut openings in the floor for stairwells. Select a wall and use **Windows** to choose a window size.
4. **Build upward.** Add floors and switch between them. The outline of the floor below stays visible so everything stacks correctly.
5. **Export.** Export the plan as JSON and OBJ, along with the PBR texture packs.
6. **Open in Blender.** Run the included Python script. Every surface receives the right PBR material, and each room arrives as its own object.

### Rooms stay separate in Blender

Every room is exported as an individual object, organized under one parent collection. That means you can delete a room, hide floors, or preview a single room in isolation without touching the rest of the building, which makes iterating on a layout much faster than working with one merged mesh.

### Shortcuts

| Tool | Key | | Tool | Key |
|---|---|---|---|---|
| Select | `V` | | Pillar | `P` |
| Wall | `W` | | Erase | `E` |
| Half wall | `I` | | Windows | `N` |
| Door | `D` | | Snap | `G` |
| Stairs | `S` | | Delete selection | `Del` |
| Cutout | `C` | | | |

## What I contributed

Blueprint was built with an LLM as a coding partner. My role was closer to **product owner, systems designer and QA lead**. The model produced code; I decided what to build, how it should behave, and whether it needed further refinements and polish. The parts of the project that make it useful are the parts I drove:

- **Defined the product and the workflow.** I specified the core idea (sketch in 2D, get a usable 3D prototype) and designed the interactions, including snapped wall drawing, the Shift-drag room extrusion, floor cutouts for stairs, and per-wall window sizing.
- **Made the geometry line up.** A building generator is only useful if its output is clean. I made sure walls, floors, ceilings and openings meet at shared edges, across rooms and across floors, so the exported model needs no manual repair.
- **Designed the Blender handoff.** I specified that rooms export as separate, named objects and that PBR materials land on the correct surfaces automatically, because the real goal was a model people can pick up and keep working with.
- **Tested the whole pipeline end to end.** Every change was verified by exporting a real building and opening it in Blender, not only by checking that the editor looked right.
- **Directed the revision cycle.** I wrote specific bug reports from what I saw in Blender, had fixes made, then re-tested previous behavior to catch regressions. The current build is prototype **0.3.10**, the result of many revision passes.
- **Kept the project maintainable.** I kept state, geometry and export concerns separated so features could be added without destabilizing existing ones, and kept the tool dependency-free so it runs from a single file.

I am particularly proud of the simplicity I was able to maintain in in the editor. It should look familiar with other similar programs, but also be easy enough to a person unfamiliar with editors (a child learning to build a video game) to intuitively grasp how to use it. For this reason I kept the features as simple and intuitive as possible, with click-to-drag, undo and redo buttons, and automatic snapping.
One of the biggest problems I originally faced was how to have all of the walls, floors, and ceilings align together without overlapping. This was a major problem that required many iterations to get perfect, as it was important not to have odd shapes such as triangular ends, and to make sure the textures perfectly align without noticeable seams between walls.
Another major hurdle to overcome was the difficulty of doors and windows, because it requires splitting an existing wall that is one rectangular prism into the parts above and below the window, and around it. This required putting in constraints about where they could be placed in the editor, to prevent an unrealistic building look.
Another hurdle was keeping the rooms segmented so that they could be easily modified, worked on, or "repaired" if the editor in Blender made an accidental modification to the structure; you can simply put the object in again, grab the part that was messed up, and reconnect it to the original.

## Technical highlights

- **State and geometry model** for editable architectural layouts: walls, partitions, openings, stairs, pillars and floor cutouts
- **Snapping, selection and wall manipulation** logic, including room ownership tracking
- **Multi-floor navigation** with reference outlines from the floor below
- **Undo / redo** across edits
- **Structured JSON serialization** of building plans
- **Wavefront OBJ generation** with procedural UV mapping for texturing
- **Automated Blender material setup** in Python for PBR textures

## Getting started

**Run the editor.** No install or build step required.
Just download blueprint_v10.html and open it
Alternatively, download the setup_pbr_materials.py and the accompanying readme if you want to load the material textures in Blender.

**Bring a plan into Blender.**

1. In the editor, click **Export OBJ** and **PBR ZIPs**.
2. Open Blender and import the OBJ.
3. Run `blender/setup_pbr_materials.py` from Blender's **Scripting** tab.
4. Your building appears with materials applied and each room as a separate object.

## Project structure

```
blueprint-smart-building-sketch/
├── blueprint_v10.html            # The editor (HTML, CSS and JavaScript)
├── blender/              # Python script for automatic PBR material setup
├── examples/             # Sample exported plan (.json) and model (.obj)
├── docs/                 # Screenshots and demo media
└── README.md
```

## About the author

**Isaac Erwin** — building toward a career in AI and software development, with hands-on experience in LLM evaluation and feedback and a strong interest in tooling that turns simple inputs into useful output.

[GitHub](https://github.com/isaaclee222) · [dgreat.guide](https://dgreat.guide)

