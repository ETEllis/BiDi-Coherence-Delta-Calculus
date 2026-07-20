# Möbi𝒰s Integration Contract

## One identity package, bounded projections

`assets/identity/3d/identity-manifest.json` is the machine-readable entry point.
All paths inside it are relative to the manifest. Consumers select the smallest
projection that carries the required behavior; they do not reconstruct or
redraw the mark.

| Surface | Primary asset | Fallback | Contract |
|---|---|---|---|
| Favicon, 16–23 px | `mobius-u-code-sigil.svg` | solid monochrome `𝒰` | no keyline or motion |
| Terminal, package, file identity | `mobius-u-code-sigil-dark.svg` | monochrome code sigil | underscore is the only horizontal invariant |
| Product/app icon | `mobius-embodied-mark.svg` | `mobius-presence.png` | both literal eyes remain visible |
| Wordmark | dark or light wordmark SVG | none | first read remains Möbi𝒰s |
| Website hero | `mobius-identity-master.mp4` | live SVG study, then presence PNG | honor reduced motion |
| Interactive web 3D | `mobius-identity-master.glb` | MP4 | use manifest frame ranges |
| Native spatial product | `mobius-body.glb` or animated master GLB | embodied SVG | eyes and body share a scene root |
| Universal Operator | `mobius-u-operator.glb` | operator SVG | same closed band, U-shaped projection |
| Relational composition | `mobius-ius-relational.glb` | `mobius-ius-relational.svg` | preserve asymmetric i–𝒰–s spacing |
| Formal kernel / sub-brand | `mobius-bidi-delta.glb` | `mobius-bidi-delta.svg` | `bi → bidi → Δ` is a decomposition state |

## State and motion

The 300-frame master runs at 24 fps. The manifest owns the authoritative state
ranges. Product code may jump to a state, scrub continuously, or use the two
published sequences:

- frames 1–216: embodied identity cycle;
- frames 228–300: `bi → bidi → Δ` kernel extraction.

Frames 217–227 are intentional visual breathing room between those sequences.
The bundled MP4 plays the complete 12.5-second composition. The GLB retains the
editable animation data for real-time engines.

## Web

The demo uses the MP4 as its primary visual runtime and automatically retains
the live SVG construction if video loading fails. It pauses at the restoration
state for `prefers-reduced-motion` users and exposes a frame-accurate scrubber.

Production websites should preload only metadata, provide the presence PNG as
a poster, and defer the animated GLB until interaction requires spatial control.
Do not make a multi-megabyte 3D file the favicon or first-contentful-paint path.

## Native products

Bundle the manifest and resolve its assets through the application resource
system. RealityKit, SceneKit, game engines, and WebGL runtimes should load the
published GLB rather than the `.blend`; Blender is a production dependency, not
a customer runtime dependency. Preserve the root transform and named objects so
eye attention, body projection, and kernel extraction remain independently
addressable.

## Code and repository identity

`𝒰_` is the code-language sigil. It does not silently rename `.cdc`, packages,
formal theorem namespaces, or compatibility surfaces. Those remain governed by
the migration audit. The sigil can ship immediately while any language-name or
extension migration remains an explicit versioned decision.

## Invariants across every consumer

1. The phase angle is `0.125 rad` (`7.161972°`).
2. The master body remains a single one-sided band with one boundary loop.
3. Eyes are literal product anatomy, never ornamental dots.
4. `ö`, `𝒰`, and `Δ` are projections of one conserved topology.
5. A surface gets at most one horizontal invariant: ground, cursor, fold, or blink.
6. Reduced-size assets simplify appearance without changing semantic ownership.
7. Korean/Chinese resonances emerge in motion and composition; they are not
   substituted for language or presented as etymological claims.

## Release authority

Run `scripts/release_identity_3d.sh`. A consumer-facing artifact is releasable
only after topology validation, GLB/PNG/MP4 checks, manifest hashes, the complete
calculus suite, and whitespace validation all pass. MCP manipulation is useful
for live design work but never replaces the deterministic generator or gate.
