# Möbi𝒰s Identity Assets

These are non-destructive identity-system candidates derived from the executed
Universal Operator and the existing embodied Möbius product mark. They do not
rename the package, the `.cdc` source format, or the formal paper.

- `mobius-embodied-mark.svg` — closed, present, eye-bearing product body.
- `mobius-u-wordmark-dark.svg` — dark-surface wordmark and phase ground.
- `mobius-u-wordmark-light.svg` — light-surface wordmark.
- `mobius-u-code-sigil.svg` — monochrome `𝒰_` for small technical surfaces.
- `mobius-u-code-sigil-dark.svg` — two-ink dark-surface `𝒰_`.
- `mobius-u-operator.svg` — standalone operator without the code cursor.
- `mobius-ius-relational.svg` — independent `i𝒰s` relational lockup.
- `mobius-bi-seed.svg` — the `bi` source extracted from the name.
- `mobius-bidi-kernel.svg` — the mirrored/duplicated `bidi` kernel word.
- `mobius-bidi-delta.svg` — portable BiDi-Delta sub-brand lockup.

The word skeleton begins from the original Möbius landing-page family, Syne,
then converts the visible characters to portable outlines. The `𝒰`, eyes,
phase trajectory, spacing, and return line are engineered identity geometry.
The operator skeleton begins from the STIX Two Math script `𝒰` so it remains
mathematically recognizable, then receives the identity keyline, scale, and
optical placement. No live font is loaded by the assets.

The implementation contract lives in `docs/identity/` and the interactive
motion study lives at `demo/mobius-identity.html`.

## Spatial production master

`3d/mobius-identity-master.blend` is generated from the versioned Blender
scripts in `tools/blender/`. It owns one continuous Möbius topology and the
`ö`, `𝒰`, and `Δ` projection states. `3d/identity-manifest.json` maps the master
and the independently consumable GLBs for product, web, code, and kernel use.
The selected transparent key-state renders are in `renders/`; the encoded
12.5-second reference sequence is in `motion/`.

Build and verify the full package with:

```bash
./scripts/release_identity_3d.sh
```
