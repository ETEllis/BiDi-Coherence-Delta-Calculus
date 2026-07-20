# Möbi𝒰s Motion Specification

The animation is a product-state transition, not a logo reveal pasted onto the
product. It must keep the body continuous and the eyes present.

## Seven states

1. **Presence** — the closed `ö` rests on the surface; eyes blink and track.
2. **Attention** — gaze converges, the body biases by `φ`, and the seam becomes
   legible.
3. **Opening** — the closure releases and the same curve opens toward `𝒰`.
4. **One-turn lock** — the static `Möbi𝒰s` wordmark holds on the inverted sheet;
   `i𝒰` and the Korean components remain reflected by design.
5. **Frame flip** — the ground stroke becomes a crease and the interaction
   changes from inside the interface to on the device surface.
6. **Second-turn restoration** — `UI` restores, then the components pass through
   a brief correctly ordered `의` state.
7. **Return** — the ribbon re-closes into `ö`; the seam retains one breath of
   phase residue before rest.

## Timing

- Full loop: `10–12 s` for a brand/system study; product-triggered transitions
  may be `900–1400 ms` without the long hold states.
- `의` recognition tests: `200 ms`, `320 ms`, and `450 ms` with eased arrival.
- The one-turn lock should hold long enough to be the canonical static frame.
- Eyes move continuously across the morph; they never fade out or merge.

## Motion tiers

### Static

- one-turn wordmark;
- Level-2 reflected `의` components;
- phase ground;
- endpoint color polarity.

### Kinetic

- continuous `ö ↔ 𝒰` deformation;
- UI restoration;
- `의` flash-frame;
- reference-frame flip;
- full dark → indigo → white → cyan temperature progression;
- blink/wink behavior and return residue.

## Accessibility

`prefers-reduced-motion: reduce` freezes the system at the one-turn wordmark.
The frame meanings remain available as text and the code sigil remains static.
No information depends on a blink, a color transition, or a sub-second frame.

## Prototype contract

`demo/mobius-identity.html` provides a local scrubber, auto-play, explicit
stage names, persistent eyes, a path interpolation from closed body to open
operator, and reduced-motion behavior. It is the reference motion lab for the
identity branch, not a claim that the production Swift mesh already performs
the exact morph.
