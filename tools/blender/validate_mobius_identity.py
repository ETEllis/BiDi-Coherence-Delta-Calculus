"""Validate the Blender master scene and emit a machine-readable report."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path

import bpy


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "assets" / "identity" / "3d"
REPORT = REPO / "build" / "identity-blender" / "validation.json"


def fail(message: str) -> None:
    raise SystemExit(f"identity validation failed: {message}")


def boundary_components(mesh: bpy.types.Mesh) -> tuple[int, int]:
    edge_faces: dict[tuple[int, int], int] = defaultdict(int)
    for polygon in mesh.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            end = vertices[(index + 1) % len(vertices)]
            edge_faces[tuple(sorted((start, end)))] += 1
    boundary = [edge for edge, count in edge_faces.items() if count == 1]
    graph: dict[int, set[int]] = defaultdict(set)
    for start, end in boundary:
        graph[start].add(end)
        graph[end].add(start)
    if any(len(neighbors) != 2 for neighbors in graph.values()):
        fail("boundary is not a cycle")
    remaining = set(graph)
    components = 0
    while remaining:
        components += 1
        queue = deque([remaining.pop()])
        while queue:
            current = queue.popleft()
            for neighbor in graph[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
    return len(boundary), components


def glb_ok(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 20:
        return False
    with path.open("rb") as handle:
        return handle.read(4) == b"glTF"


def main() -> None:
    scene = bpy.context.scene
    body = bpy.data.objects.get("MobiusBody")
    if not body or body.type != "MESH":
        fail("MobiusBody mesh missing")
    if body.get("topology") != "mobius-band" or body.get("half_twists") != 1:
        fail("topology metadata missing or incorrect")

    mesh = body.data
    vertex_count = len(mesh.vertices)
    edge_count = len(mesh.edges)
    face_count = len(mesh.polygons)
    euler = vertex_count - edge_count + face_count
    boundary_edge_count, boundaries = boundary_components(mesh)
    if euler != 0:
        fail(f"Euler characteristic must be 0, got {euler}")
    if boundaries != 1:
        fail(f"Möbius band must have one boundary component, got {boundaries}")
    if set(body.data.shape_keys.key_blocks.keys()) != {"Basis", "UProjection", "DeltaProjection"}:
        fail("projection shape keys incomplete")

    eyes = [obj for obj in bpy.data.objects if obj.get("identity_role") == "literal-animated-eye"]
    if len(eyes) != 2:
        fail(f"expected two literal eyes, got {len(eyes)}")
    if not all(eye.animation_data and eye.animation_data.action for eye in eyes):
        fail("eyes are not animated")

    required_glbs = [
        "mobius-identity-master.glb",
        "mobius-body.glb",
        "mobius-u-operator.glb",
        "mobius-u-code-sigil.glb",
        "mobius-ius-relational.glb",
        "mobius-bidi-delta.glb",
    ]
    bad_glbs = [name for name in required_glbs if not glb_ok(OUTPUT / name)]
    if bad_glbs:
        fail(f"invalid GLB exports: {bad_glbs}")
    oversized = [name for name in required_glbs if (OUTPUT / name).stat().st_size > 5_000_000]
    if oversized:
        fail(f"web GLB exceeds 5 MB target: {oversized}")

    manifest_path = OUTPUT / "identity-manifest.json"
    if not manifest_path.is_file():
        fail("identity manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("formalKernel") != "bidiγΔ":
        fail("formal kernel manifest entry missing")
    if "kernelBiDiDelta" not in manifest.get("components", {}):
        fail("BiDi Delta component missing from manifest")

    report = {
        "status": "PASS",
        "blender": bpy.app.version_string,
        "scene": scene.name,
        "topology": {
            "vertices": vertex_count,
            "edges": edge_count,
            "faces": face_count,
            "eulerCharacteristic": euler,
            "boundaryEdges": boundary_edge_count,
            "boundaryComponents": boundaries,
            "halfTwists": body.get("half_twists"),
        },
        "shapeKeys": list(body.data.shape_keys.key_blocks.keys()),
        "eyes": [eye.name for eye in eyes],
        "glbFiles": {name: (OUTPUT / name).stat().st_size for name in required_glbs},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("MOBIUS_IDENTITY_VALIDATION_PASS", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
