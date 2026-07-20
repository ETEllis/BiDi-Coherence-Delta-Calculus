#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

REBUILD=0
REQUIRE_MOTION=0
while (($#)); do
  case "$1" in
    --rebuild) REBUILD=1 ;;
    --require-motion) REQUIRE_MOTION=1 ;;
    *) echo "usage: $0 [--rebuild] [--require-motion]" >&2; exit 2 ;;
  esac
  shift
done

if ((REBUILD)); then
  ./scripts/build_identity_3d.sh
fi

MOBIUS_BLENDER_BIN="${MOBIUS_BLENDER_BIN:-$(command -v blender || true)}"
MASTER="assets/identity/3d/mobius-identity-master.blend"
VALIDATION_LOG="build/identity-blender/validation.log"

test -s "$MASTER" || {
  echo "missing Blender master: $MASTER" >&2
  exit 1
}

if [[ -n "$MOBIUS_BLENDER_BIN" ]]; then
  echo "+ $MOBIUS_BLENDER_BIN --background $MASTER --python tools/blender/validate_mobius_identity.py"
  "$MOBIUS_BLENDER_BIN" --background "$MASTER" \
    --python tools/blender/validate_mobius_identity.py 2>&1 | tee "$VALIDATION_LOG"
  grep -q 'MOBIUS_IDENTITY_VALIDATION_PASS' "$VALIDATION_LOG" || {
    echo "Blender topology validation did not emit its pass witness" >&2
    exit 1
  }
else
  echo "Blender unavailable; validating committed interchange artifacts only"
fi

MOBIUS_REQUIRE_MOTION="$REQUIRE_MOTION" python3 - <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(".")
identity = root / "assets" / "identity"
output = identity / "3d"
renders = identity / "renders"

svgs = [
    identity / "mobius-embodied-mark.svg",
    identity / "mobius-u-operator.svg",
    identity / "mobius-u-code-sigil.svg",
    identity / "mobius-u-code-sigil-dark.svg",
    identity / "mobius-ius-relational.svg",
    identity / "mobius-bi-seed.svg",
    identity / "mobius-bidi-kernel.svg",
    identity / "mobius-bidi-delta.svg",
    identity / "mobius-u-wordmark-dark.svg",
    identity / "mobius-u-wordmark-light.svg",
]
for path in svgs:
    if not path.is_file():
        raise SystemExit(f"missing SVG component: {path}")
    node = ET.parse(path).getroot()
    if "viewBox" not in node.attrib:
        raise SystemExit(f"SVG lacks viewBox: {path}")
    if not any(child.tag.endswith("title") for child in node):
        raise SystemExit(f"SVG lacks accessible title: {path}")

manifest_path = output / "identity-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest["identity"] != "Möbi𝒰s" or manifest["formalKernel"] != "bidiγΔ":
    raise SystemExit("manifest identity hierarchy is incorrect")
topology = manifest["topology"]
expected_topology = {
    "surface": "mobius-band",
    "halfTwists": 1,
    "connectedComponents": 1,
    "eulerCharacteristic": 0,
    "boundaryComponents": 1,
}
if topology != expected_topology:
    raise SystemExit(f"manifest topology mismatch: {topology}")

required_components = {
    "embodiedBody",
    "operatorU",
    "relationalIUs",
    "codeSigil",
    "kernelBiDiDelta",
    "animatedMaster",
}
if not required_components.issubset(manifest["components"]):
    raise SystemExit("manifest 3D component family is incomplete")
for group in ("components", "components2d", "renderWitnesses"):
    for value in manifest[group].values():
        path = (manifest_path.parent / value).resolve()
        if not path.is_file():
            raise SystemExit(f"manifest projection missing: {group}.{value}")

expected_ranges = {
    "PRESENCE": [1, 23],
    "ATTENTION": [24, 47],
    "U_OPERATIVE": [48, 119],
    "ONE_TURN": [120, 149],
    "FRAME_FLIP": [150, 167],
    "EUI_RESTORATION": [168, 191],
    "RETURN": [192, 227],
    "BIDI_DELTA_EXTRACTION": [228, 300],
}
if manifest["stateRanges"] != expected_ranges:
    raise SystemExit("manifest state ranges do not match the Blender master")

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

for record in manifest["files"]:
    path = root / record["path"]
    if not path.is_file():
        raise SystemExit(f"manifest file missing: {path}")
    if path.stat().st_size != record["bytes"]:
        raise SystemExit(f"manifest byte count mismatch: {path}")
    # The blend file is saved again after manifest generation so that it embeds
    # the final scene state; validate its presence/size here and hash all stable
    # interchange and render artifacts.
    if path.suffix != ".blend" and sha256(path) != record["sha256"]:
        raise SystemExit(f"manifest checksum mismatch: {path}")

for path in output.glob("*.glb"):
    with path.open("rb") as handle:
        magic, version, length = struct.unpack("<4sII", handle.read(12))
        json_length, json_kind = struct.unpack("<I4s", handle.read(8))
        gltf = json.loads(handle.read(json_length).decode("utf-8").rstrip(" \x00"))
    if magic != b"glTF" or version != 2 or length != path.stat().st_size:
        raise SystemExit(f"invalid GLB header: {path}")
    if json_kind != b"JSON" or not gltf.get("meshes"):
        raise SystemExit(f"GLB lacks a valid scene payload: {path}")
    if path.stat().st_size > 5_000_000:
        raise SystemExit(f"GLB exceeds five-megabyte web target: {path}")

master_gltf = output / "mobius-identity-master.glb"
with master_gltf.open("rb") as handle:
    handle.read(12)
    json_length, _ = struct.unpack("<I4s", handle.read(8))
    master_json = json.loads(handle.read(json_length).decode("utf-8").rstrip(" \x00"))
animation_names = {animation.get("name") for animation in master_json.get("animations", [])}
required_animation_names = {"MobiusBodyMeshAction", "Eye_LeftAction", "Eye_RightAction", "Kernel_BiDiAction"}
if not required_animation_names.issubset(animation_names):
    raise SystemExit(f"animated master is missing required tracks: {required_animation_names - animation_names}")

required_renders = {
    "mobius-presence.png",
    "mobius-u-operative.png",
    "mobius-one-turn.png",
    "mobius-restoration.png",
    "mobius-bidi-delta.png",
}
for name in required_renders:
    path = renders / name
    with path.open("rb") as handle:
        signature = handle.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"invalid PNG signature: {path}")
    width, height = struct.unpack(">II", signature[16:24])
    if (width, height) != (960, 960):
        raise SystemExit(f"unexpected render dimensions {width}x{height}: {path}")

required_states = {
    "PRESENCE",
    "U_OPERATIVE",
    "EUI_RESTORATION",
    "BIDI_DELTA_EXTRACTION",
}
if not required_states.issubset(manifest["semanticStates"]):
    raise SystemExit("semantic state surface is incomplete")

if os.environ.get("MOBIUS_REQUIRE_MOTION") == "1":
    motion = root / "assets" / "identity" / "motion" / "mobius-identity-master.mp4"
    if not motion.is_file() or motion.stat().st_size < 50_000:
        raise SystemExit("motion master is missing or too small")
    with motion.open("rb") as handle:
        header = handle.read(12)
    if b"ftyp" not in header:
        raise SystemExit("motion master lacks an MP4 ftyp header")
    records = {record["path"]: record for record in manifest["files"]}
    key = str(motion.relative_to(root))
    if key not in records or records[key]["sha256"] != sha256(motion):
        raise SystemExit("motion master is absent or stale in the identity manifest")
    if manifest["components"].get("motionMaster") != "../motion/mobius-identity-master.mp4":
        raise SystemExit("motion master is not exposed as a consumable component")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise SystemExit("ffprobe is required for the full motion release gate")
    probe = json.loads(
        subprocess.check_output(
            [
                ffprobe,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,width,height,r_frame_rate,pix_fmt:format=duration",
                "-of", "json",
                str(motion),
            ],
            text=True,
        )
    )
    stream = probe["streams"][0]
    if (stream["codec_name"], stream["width"], stream["height"], stream["r_frame_rate"], stream["pix_fmt"]) != ("h264", 720, 720, "24/1", "yuv420p"):
        raise SystemExit(f"motion encoding contract mismatch: {stream}")
    if abs(float(probe["format"]["duration"]) - 12.5) > 0.01:
        raise SystemExit("motion duration is not the expected 12.5 seconds")

print(
    "MOBIUS_IDENTITY_ARTIFACT_PASS",
    f"svg={len(svgs)}",
    f"glb={len(list(output.glob('*.glb')))}",
    f"renders={len(required_renders)}",
)
PY

echo "MOBIUS_IDENTITY_RELEASE_GATE_PASS"
