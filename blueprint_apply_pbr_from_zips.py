# Blueprint PBR ZIP helper for Blender
# Version 0.3.9
#
# Workflow:
# 1) Import blueprint.obj into Blender.
# 2) Save the .blend file in your project folder.
# 3) Put full PBR ZIP files from ambientCG/etc. into a folder named pbr_zips next to the .blend.
# 4) In Blender: Scripting > Open this file > Run Script.
#
# The script extracts the needed maps into textures_pbr_extracted/ and wires
# BaseColor, Roughness, Metallic, Normal, Height/Bump, and optional AO.

import os
import re
import zipfile
from pathlib import Path

import bpy

PBR_ZIP_FOLDER_NAME = "pbr_zips"
EXTRACT_FOLDER_NAME = "textures_pbr_extracted"
TILE_SCALE_METERS = 1.0

# Blueprint material slot -> expected asset id in the downloaded PBR zip filename/path.
# Reused assets are intentional: the same Concrete023 zip can drive several materials.
MATERIAL_ASSETS = {
    "Exterior_Brick": "Bricks038",
    "Exterior_Stylized_Concrete": "Concrete023",
    "Interior_Drywall_Warm": "PaintedPlaster003",
    "Interior_Drywall_White": "PaintedPlaster003",
    "Interior_Drywall_BlueGray": "PaintedPlaster003",
    "Interior_Brick": "Bricks023",
    "Interior_Plain_Concrete": "Concrete023",
    "Interior_Wallpaper_Muted": "Fabric022",
    "Interior_Marble": "Marble012",
    "Ceiling_Tiles": "OfficeCeiling001",
    "Floor_Wood_Dark": "WoodFloor040",
    "Floor_Carpet_Charcoal": "Carpet012",
    "Floor_Carpet_Brown": "Carpet012",
    "Floor_Carpet_BlueGray": "Carpet012",
    "Floor_Tile_Slate": "Tiles027",
    "Floor_Marble_Gray": "Marble001",
    "Floor_Concrete": "Concrete040",
    "Roof_Concrete": "Concrete023",
    "Pillar_Concrete": "Concrete023",
    "Stair_Concrete": "Concrete023",
    "Cut_Edge_Concrete": "Concrete023",
}

# Some simple color tints keep the reused drywall/carpet maps visually distinct.
MATERIAL_TINTS = {
    "Interior_Drywall_Warm": (1.00, 0.96, 0.86, 1.0),
    "Interior_Drywall_White": (1.00, 1.00, 0.96, 1.0),
    "Interior_Drywall_BlueGray": (0.68, 0.76, 0.82, 1.0),
    "Floor_Carpet_Charcoal": (0.45, 0.45, 0.45, 1.0),
    "Floor_Carpet_Brown": (0.55, 0.42, 0.32, 1.0),
    "Floor_Carpet_BlueGray": (0.45, 0.55, 0.62, 1.0),
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".exr"}


def project_dir() -> Path:
    if bpy.data.filepath:
        return Path(bpy.data.filepath).resolve().parent
    return Path.cwd()


def clean_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def find_zip_files(root: Path):
    folders = []
    preferred = root / PBR_ZIP_FOLDER_NAME
    if preferred.exists():
        folders.append(preferred)
    folders.append(root)
    found = []
    seen = set()
    for folder in folders:
        for path in folder.glob("*.zip"):
            if path.resolve() not in seen:
                found.append(path)
                seen.add(path.resolve())
    return found


def classify_map(filename: str):
    lower = filename.lower()
    stem = Path(lower).stem
    if Path(lower).suffix not in IMAGE_EXTS:
        return None
    # Prefer OpenGL normal maps for Blender. DX normal maps need a green-channel flip.
    if "normalgl" in lower or "normal_gl" in lower or "opengl" in lower:
        return "normal_gl"
    if "normaldx" in lower or "normal_dx" in lower or "directx" in lower:
        return "normal_dx"
    if "normal" in lower or stem.endswith("_nor") or stem.endswith("-nor"):
        return "normal"
    if "roughness" in lower or stem.endswith("_rough") or stem.endswith("-rough"):
        return "roughness"
    if "metallic" in lower or "metalness" in lower:
        return "metallic"
    if "ambientocclusion" in lower or "ambient_occlusion" in lower or re.search(r"(^|[_\-])ao($|[_\-])", stem):
        return "ao"
    if "displacement" in lower or "height" in lower or stem.endswith("_disp") or stem.endswith("-disp"):
        return "height"
    if (
        "basecolor" in lower or "base_color" in lower or "albedo" in lower or
        "diffuse" in lower or re.search(r"(^|[_\-])color($|[_\-])", stem) or stem.endswith("_col") or stem.endswith("-col")
    ):
        return "basecolor"
    return None


def choose_asset_zip(asset_id: str, zips):
    target = clean_name(asset_id)
    best = None
    best_score = -1
    for z in zips:
        name_score = 10 if target in clean_name(z.name) else 0
        path_score = 0
        try:
            with zipfile.ZipFile(z) as zf:
                sample = " ".join(zf.namelist()[:80])
                if target in clean_name(sample):
                    path_score = 8
        except Exception:
            continue
        score = name_score + path_score
        if score > best_score:
            best = z
            best_score = score
    return best if best_score > 0 else None


def extract_maps(zip_path: Path, asset_id: str, dest_root: Path, material_name: str):
    dest = dest_root / material_name
    dest.mkdir(parents=True, exist_ok=True)
    maps = {}
    target = clean_name(asset_id)
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename
            if Path(name).suffix.lower() not in IMAGE_EXTS:
                continue
            # Prefer files that include the intended asset id, but allow zips with a single asset folder.
            if target not in clean_name(name) and target not in clean_name(zip_path.name):
                continue
            map_type = classify_map(name)
            if not map_type:
                continue
            # For normal maps, prefer NormalGL over generic over NormalDX.
            if map_type in {"normal_gl", "normal", "normal_dx"}:
                existing = maps.get("normal")
                priority = {"normal_gl": 3, "normal": 2, "normal_dx": 1}[map_type]
                if existing and existing[1] >= priority:
                    continue
                out_path = dest / Path(name).name
                with zf.open(info) as src, open(out_path, "wb") as out:
                    out.write(src.read())
                maps["normal"] = (out_path, priority)
                continue
            if map_type in maps:
                # Keep first useful map of each type.
                continue
            out_path = dest / Path(name).name
            with zf.open(info) as src, open(out_path, "wb") as out:
                out.write(src.read())
            maps[map_type] = out_path
    if isinstance(maps.get("normal"), tuple):
        maps["normal"] = maps["normal"][0]
    return maps


def load_image(path: Path, color_space="sRGB"):
    img = bpy.data.images.load(str(path), check_existing=True)
    # Blender color management values differ by version. Try common ones.
    try:
        img.colorspace_settings.name = color_space
    except Exception:
        if color_space == "Non-Color":
            try:
                img.colorspace_settings.name = "Non-Color Data"
            except Exception:
                pass
    return img


def input_socket(node, *names):
    for name in names:
        sock = node.inputs.get(name)
        if sock:
            return sock
    return None


def output_socket(node, *names):
    for name in names:
        sock = node.outputs.get(name)
        if sock:
            return sock
    return None


def make_tex_node(nodes, path: Path, label: str, color_space="sRGB", x=-700, y=0):
    node = nodes.new(type="ShaderNodeTexImage")
    node.label = label
    node.location = (x, y)
    node.image = load_image(path, color_space)
    return node


def rebuild_material(mat, maps, tint=None):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (350, 0)
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (80, 0)
    links.new(output_socket(bsdf, "BSDF"), input_socket(out, "Surface"))

    base_socket = input_socket(bsdf, "Base Color")
    rough_socket = input_socket(bsdf, "Roughness")
    metal_socket = input_socket(bsdf, "Metallic")
    normal_socket = input_socket(bsdf, "Normal")

    if rough_socket:
        rough_socket.default_value = 0.85
    if metal_socket:
        metal_socket.default_value = 0.0

    base_node = None
    if maps.get("basecolor") and base_socket:
        base_node = make_tex_node(nodes, maps["basecolor"], "BaseColor / Albedo", "sRGB", -760, 180)
        source_color = output_socket(base_node, "Color")
        if tint:
            try:
                tint_node = nodes.new(type="ShaderNodeMixRGB")
                tint_node.location = (-420, 160)
                tint_node.blend_type = "MULTIPLY"
                tint_node.inputs[0].default_value = 0.45
                tint_node.inputs[2].default_value = tint
                links.new(source_color, tint_node.inputs[1])
                links.new(tint_node.outputs[0], base_socket)
            except Exception:
                links.new(source_color, base_socket)
        else:
            links.new(source_color, base_socket)

    if maps.get("ao") and base_node and base_socket:
        try:
            ao_node = make_tex_node(nodes, maps["ao"], "Ambient Occlusion", "Non-Color", -760, 0)
            mix = nodes.new(type="ShaderNodeMixRGB")
            mix.location = (-190, 120)
            mix.blend_type = "MULTIPLY"
            mix.inputs[0].default_value = 0.35
            # Rewire whatever is currently feeding Base Color into the multiply node.
            existing = None
            for link in list(links):
                if link.to_socket == base_socket:
                    existing = link.from_socket
                    links.remove(link)
                    break
            if existing:
                links.new(existing, mix.inputs[1])
            else:
                mix.inputs[1].default_value = (1, 1, 1, 1)
            links.new(output_socket(ao_node, "Color"), mix.inputs[2])
            links.new(mix.outputs[0], base_socket)
        except Exception:
            pass

    if maps.get("roughness") and rough_socket:
        rough_node = make_tex_node(nodes, maps["roughness"], "Roughness", "Non-Color", -760, -160)
        links.new(output_socket(rough_node, "Color"), rough_socket)

    if maps.get("metallic") and metal_socket:
        metal_node = make_tex_node(nodes, maps["metallic"], "Metallic", "Non-Color", -760, -320)
        links.new(output_socket(metal_node, "Color"), metal_socket)

    normal_output = None
    if maps.get("normal"):
        normal_tex = make_tex_node(nodes, maps["normal"], "Normal", "Non-Color", -760, -500)
        normal_map = nodes.new(type="ShaderNodeNormalMap")
        normal_map.location = (-420, -500)
        try:
            normal_map.inputs["Strength"].default_value = 0.85
        except Exception:
            pass
        links.new(output_socket(normal_tex, "Color"), input_socket(normal_map, "Color"))
        normal_output = output_socket(normal_map, "Normal")

    if maps.get("height"):
        try:
            height_tex = make_tex_node(nodes, maps["height"], "Height / Displacement as Bump", "Non-Color", -760, -680)
            bump = nodes.new(type="ShaderNodeBump")
            bump.location = (-180, -560)
            if input_socket(bump, "Strength"):
                input_socket(bump, "Strength").default_value = 0.05
            if input_socket(bump, "Distance"):
                input_socket(bump, "Distance").default_value = 0.06
            links.new(output_socket(height_tex, "Color"), input_socket(bump, "Height"))
            if normal_output and input_socket(bump, "Normal"):
                links.new(normal_output, input_socket(bump, "Normal"))
            normal_output = output_socket(bump, "Normal")
        except Exception:
            pass

    if normal_output and normal_socket:
        links.new(normal_output, normal_socket)


def main():
    root = project_dir()
    zips = find_zip_files(root)
    if not zips:
        raise RuntimeError(f"No ZIP files found. Put full PBR texture ZIPs in {root / PBR_ZIP_FOLDER_NAME} or next to the .blend file.")

    extract_root = root / EXTRACT_FOLDER_NAME
    extract_root.mkdir(parents=True, exist_ok=True)
    applied = []
    missing_materials = []
    missing_zips = []
    missing_maps = []

    for mat_name, asset_id in MATERIAL_ASSETS.items():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            missing_materials.append(mat_name)
            continue
        zip_path = choose_asset_zip(asset_id, zips)
        if not zip_path:
            missing_zips.append(f"{mat_name} -> {asset_id}")
            continue
        maps = extract_maps(zip_path, asset_id, extract_root, mat_name)
        if not maps.get("basecolor"):
            missing_maps.append(f"{mat_name}: no base color found in {zip_path.name}")
            continue
        rebuild_material(mat, maps, MATERIAL_TINTS.get(mat_name))
        applied.append(f"{mat_name} <- {zip_path.name} ({', '.join(sorted(maps.keys()))})")

    print("\n=== Blueprint PBR ZIP Helper ===")
    print(f"Project folder: {root}")
    print(f"ZIP files scanned: {len(zips)}")
    print(f"Materials updated: {len(applied)}")
    for item in applied:
        print("  OK", item)
    if missing_zips:
        print("\nMissing ZIPs:")
        for item in missing_zips:
            print("  ", item)
    if missing_maps:
        print("\nMissing maps:")
        for item in missing_maps:
            print("  ", item)
    if missing_materials:
        print("\nBlueprint materials not present in this Blender file:")
        for item in missing_materials:
            print("  ", item)
    print("\nDone. Switch to Material Preview or Rendered view to inspect the PBR materials.")


if __name__ == "__main__":
    main()
