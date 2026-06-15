# BiDi Coherence-Delta Calculus

Date: 2026-06-15

Status: public engineering specification, v1.

BiDi Coherence-Delta Calculus is a universal substrate for hybrid systems that need continuous dynamics, discrete commitments, delayed coupling, local invariants, nested reference frames, and coherence-preserving operators.

## One-Line Definition

BiDi Coherence-Delta Calculus is a host-independent calculus for coupled bounded processes: phase-state cells are grouped into boundary modules, connected by delayed weighted channels, evolved continuously, and periodically committed through event-triggered invariant gates that preserve coherence and reduce variational prediction error.

## What It Gives An Engineer

The calculus gives one compact substrate for:

- continuous-time dynamics;
- event-driven state transitions;
- delayed signal propagation;
- local learning and weight adaptation;
- predictive-coding style belief updates;
- active-inference style action updates;
- nested multi-scale systems;
- reference-frame coupling across scales;
- gated policy/invariant enforcement;
- symbolic/discrete computation through configured instruction modules;
- a small native surface notation for declaring fields, modules, channels, flow, and commits.

The key value is not that it replaces every existing runtime. The value is that it gives a unified language for systems that are usually split across state machines, reactive runtimes, neural dynamics, simulations, control loops, and policy gates.

## Core Implementation Contract

The canonical calculus primitives are:

- cell
- channel
- module
- field
- commit
- `bidi-gamma-delta` / `bidiγΔ`

The current reference reducer, `bidi_calculus.py`, exposes implementation names
retained for API stability: `Thread` = cell, `Strand` = channel, `Knot` = module,
`Breathfield` = field, and `breath` = commit.

A conforming implementation must preserve these behaviors:

- `Thread.trit`
- `Thread.kappa`
- `Knot.coherence`
- `Knot.free_energy`
- `Knot.gate`
- `Knot.interfere`
- `Knot.corefold`
- `Knot.breath`
- `Breathfield.afferent`
- `Breathfield.step`
- `Breathfield.advance`
- `Breathfield.global_coherence`
- `CounterField`
- `minsky_add`
- `parse_legacy_program`
- acceptance witnesses for each major capability claim

These implementation names are callable anchors. The canonical calculus vocabulary
is the smaller cell/channel/module/field/commit set above.

## Implementation Alias Map

| Reference API | Calculus term | Meaning |
| --- | --- | --- |
| Thread | phase cell | A continuous state carrier with phase, amplitude, plasticity, latched pole, and memory. |
| Strand | delayed channel | A directed weighted edge with continuous delay. |
| Knot | boundary module | A unit of phase cells with input/output cones, belief state, priors, precision, and optional child field. |
| Breathfield | coupled field | A graph of boundary modules evolving under continuous dynamics and evented commits. |
| breath | commit | A guarded discrete state update that quantizes, enforces invariants, updates belief, and latches output. |
| read cone | input cone | The receiving half of a boundary module. |
| write cone | output cone | The projecting half of a boundary module. |
| permeability | boundary openness | How strongly a phase cell is allowed to exchange influence. |
| coherence | phase-order magnitude | Magnitude of mean orientation, in `[0, 1]`. |
| coherence barrier | nonnegative balance invariant | A prefix-walk constraint that prevents negative coherence debt. |
| surprise | prediction error | Difference between received evidence and current belief/prior. |
| Core-fold | latent projection | A reduced internal representation distilled from middle state channels. |
| bidiγΔ | bidirectional coherence-delta coupling | Up/down coupling of coherence and error across nested scales. |

Formal phrasing:

> The formal cross-scale operator is `bidi-gamma-delta`: bidirectional coherence-delta coupling. It carries context downward, evidence upward, and coherence/error differences across nested reference frames.

## Formal Object Model

### Phase Cell (`Thread`)

A phase cell holds:

```text
theta: phase angle
a: amplitude
p: plasticity
sigma: latched binary pole
mu: memory
omega: intrinsic angular velocity
```

Its runtime value is ternary:

```text
+  if cos(theta) > deadband
-  if cos(theta) < -deadband
0  otherwise
```

Its boundary openness is:

```text
kappa(theta) = max(0, 1 - abs(cos(theta)) / deadband)
```

Interpretation:

- phase gives continuous state;
- ternary value gives runtime symbolic state;
- latched pole gives persistent discrete state;
- openness controls how much influence passes through the boundary;
- plasticity controls coupling adaptation.

### Delayed Coupling Channel (`Strand`)

A channel connects source boundary module to destination boundary module:

```text
source -> destination
weight
delay tau
optional line index
optional Hebbian adaptation
```

Interpretation:

- this is signal propagation with delay;
- delay is continuous, not tick-indexed;
- influence can be all-channel or line-specific;
- optional plasticity changes channel strength from correlation.

### Boundary Module (`Knot`)

A boundary module is a self-contained process:

```text
phase cells
input cone
output cone
belief vector
prior vector
precision
action gain
optional child field
history for delayed reads
optional instruction fields
```

Interpretation:

- input cone receives evidence;
- output cone projects state;
- belief and prior implement predictive-coding style inference;
- precision weights prediction error;
- action gain lets the module change projection to make sensed input match priors;
- child field enables nested multi-scale computation.

### Coupled Process Field (`Breathfield`)

A field contains modules and coupling channels:

```text
modules: name -> boundary module
channels: delayed weighted couplings
dt: integration step for realization
gain: coupling gain
deadband: ternary quantization threshold
guards: event predicates
events: off-grid commit log
```

Interpretation:

- the mathematical model is continuous-time;
- a realization approximates it numerically;
- event guards fire commits by threshold crossing, not by global clock;
- nesting gives multirate dynamics.

## Dynamics

### 1. Afferent Signal

For each destination module, incoming influence is the delayed weighted sum of source outputs, modulated by source and destination boundary openness.

Operational meaning:

> Every boundary module reads a delayed complex-valued superposition from its neighbors. Closed boundaries reduce coupling. Open boundaries admit more exchange.

This is a useful bridge to:

- signal processing;
- coupled oscillators;
- graph neural dynamics;
- recurrent control systems;
- electromagnetic/wave interference analogies.

### 2. Continuous Flow

Between commits:

- phase turns toward incoming signal;
- amplitude relaxes;
- belief descends prediction error toward evidence and prior;
- plastic channels adapt by correlation;
- optional action dynamics alter output to reduce mismatch.

Operational meaning:

> The field behaves like a continuous recurrent dynamical system with delayed coupling, local predictive state, and optional adaptive weights.

### 3. Evented Commit (`breath`)

A commit fires when a guard crosses its threshold upward. The event time is interpolated off the numerical integration grid.

The commit performs:

1. move phases partly toward nearest pole;
2. enforce the nonnegative balance invariant;
3. rotate invalid negative-debt cells to the open crossing state;
4. update belief toward evidence;
5. reject the commit if free energy increases;
6. latch committed runtime poles into persistent `sigma`.

Operational meaning:

> A breath is an atomic guarded commit with invariant enforcement and free-energy rejection. It is the bridge between continuous dynamics and discrete state.

### 4. Free Energy

Each boundary module tracks a local objective:

```text
prediction error
+ complexity / prior deviation
- orientation alignment with incoming signal
```

It is reduced by two mechanisms:

- perception: update belief toward evidence;
- action: alter projected phase so incoming evidence shifts toward prior.

Operational meaning:

> The module can reduce mismatch by changing its internal model or by changing its output into the coupled field.

### 5. Bidi-Gamma-Delta Coupling

Preserved formal concept: `bidiγΔ`, written in engineering prose as **bidirectional coherence-delta coupling**.

Definition:

- gamma (`gamma`) is coherence, the phase-order magnitude;
- delta (`delta`) is the difference between predicted/actual, parent/child, or local/global coherence;
- down-coupling sends parent context into child priors;
- up-coupling sends child coherence into parent evidence;
- the two directions together define reference-frame coupling.

Operational meaning:

> `bidi-gamma-delta` couples nested systems by sending context downward and evidence upward, while exposing the coherence/error delta between scales.

This maps cleanly to:

- hierarchical predictive processing;
- multiscale control;
- message passing on nested graphs;
- coarse-graining and renormalization-style summaries;
- distributed systems with local/global state reconciliation;
- reference-frame consistency in simulation and mixed-reality systems.

## Operators

### Gate

Function:

```python
Knot.gate(other)
```

Engineering meaning:

> Compose two boundary states by multiplying corresponding complex phase values. A module can act as an operator on another module.

Use cases:

- context-dependent transformation;
- policy gate;
- phase-conditioned routing;
- operator-as-data.

### Interfere

Function:

```python
Knot.interfere(other, gain=1.0)
```

Engineering meaning:

> Superpose two boundary states. Reinforcement or cancellation depends on phase relation.

Use cases:

- correlation;
- binding;
- conflict detection;
- coherence scoring;
- consensus formation.

### Core-Fold

Function:

```python
Knot.corefold()
```

Engineering meaning:

> Project a larger boundary state into a compact latent representation using internal channels.

Use cases:

- abstraction;
- summary state;
- portable hidden state;
- lower-dimensional control surface.

## Native Surface Notation

The `.cdc` notation has a compact engineering reading:

```text
deadband <real>
field <name> dt=<real> gain=<real>
module <name> theta <theta1..theta6>
module <name> trits <s1..s6>
channel <a> -> <b> delay=<real> weight=<real> [plastic]
guard <name> crossing <i>
flow <real>
commit <name>
end
```

Interpretation:

- declare a field;
- declare boundary modules;
- declare delayed channels;
- declare event triggers;
- advance continuous flow;
- perform guarded commits.

This is enough to express a small reactive dynamical program without appealing to Python syntax as the language definition.

## Acceptance Witnesses In Engineering Terms

The `acceptance.py` witnesses cover:

| Group | Engineering claim |
| --- | --- |
| A | primitives instantiate, host-free spec exists, self-interference and nesting work |
| B | continuous flow, hybrid evented commits, off-grid events, multirate nesting, continuous delays |
| C | nested fields, scale-relative coupling, multiple reference frames, bounded recursion |
| D | emergent coherence, free-energy guarded commits, predictive belief tracking, action/perception split |
| E | evented state machines, Minsky-counter computation, neural-style dynamics, native syntax |
| F | Gate/interfere/Core-fold, scale-gated operators, multiscale coherence under load |

Local run result on 2026-06-15:

```text
24/24 boxes green
```

The witnesses are capability witnesses. They prove expressive coverage of the listed behaviors in small configurations. They do not prove industrial performance, scaling limits, or optimality.

## Strong Claims, Clean Version

### Computational Universality

> The substrate can express universal computation by configuring instruction modules and counters whose guarded commits implement increment and conditional decrement. The reference witness demonstrates this with a two-counter construction.

Boundary: this establishes expressivity, not automatic superiority over every existing computational runtime.

### Neural Substrate

> The substrate can express continuous recurrent dynamics, predictive belief updates, active correction, local Hebbian plasticity, and nested multiscale feedback. These are core ingredients of neural computation.

Boundary: this establishes native support for core neural-computation motifs, not state-of-the-art training efficiency or a full biological brain model.

### Backend Runtime

> The substrate can express state machines, reactive guards, dataflow, delayed signals, adaptive weights, nested processes, and discrete commits in one model.

Boundary: this establishes a unified backend logic model, not an assertion that every production workload should use this runtime.

### Free-Energy Monotonicity

> The belief flow descends local prediction error, and guarded commits reject transitions that increase the local free-energy objective. Global monotonic descent requires additional assumptions about coupling symmetry, delay, and gain.

## Why This Is A Universal Tool

The calculus is useful wherever a system needs the following simultaneously:

- a continuous state;
- a discrete committed state;
- delayed influence;
- local boundaries;
- gated exchange;
- belief/prior mismatch;
- evented commits;
- nested scale;
- multi-agent or multi-module coherence.

Typical software splits these across multiple systems:

- physics/simulation engine;
- event bus;
- state machine;
- reactive UI runtime;
- neural model;
- workflow orchestrator;
- policy engine;
- database state;
- distributed consensus layer.

The calculus provides a common substrate vocabulary for all of them.

## Likely Application Areas

### Agent Orchestration

Use boundary modules as agents or agent states. Use channels for dependency, communication, and delayed evidence. Use commits for guarded handoffs or irreversible state changes.

### Mixed-Reality / Impressions-Style World Models

Use nested fields for reference frames. Use `bidi-gamma-delta` for map/traversal/embodied coherence. Use gates for visibility, consent, maturity, confidence, and privacy.

### Social Field Simulation

Use phase coherence and interference to model group convergence, conflict, resonance, cancellation, and place solidity without exposing raw individuals.

### Policy And Consent Systems

Use the nonnegative balance invariant and free-energy rejection as patterns for "no unsafe commit" behavior.

### Adaptive UI State

Use the continuous/discrete split for interfaces that need fluid state while preserving auditable commits.

### Research / Modeling

Use the system as a small formal lab for active inference, multiscale dynamical systems, and discrete-continuous hybrid computation.

## Interoperation With Adjacent Substrates

The calculus can interoperate with adjacent substrate layers:

- WEFT: boundary / state / transition calculus.
- GIST: evidence / reasoning / proof lattice.
- BiDi Coherence-Delta Calculus: continuous-time boundary dynamics, evented commit, nested coherence, and bidirectional coherence-delta coupling.

Possible future integration:

```text
BiDi Coherence-Delta Calculus generates and evolves candidate states.
WEFT constrains admissible boundary transitions.
GIST records evidence, counterfactuals, contradiction clusters, and proof packets.
```

That is an integration hypothesis, not a merge instruction.

## Abstract

BiDi Coherence-Delta Calculus is a formal substrate for hybrid systems that must behave continuously and commit discretely. It models computation as nested boundary modules made of phase-state cells, connected by delayed weighted channels. The field evolves through continuous dynamics, while event-triggered commits quantize state, enforce invariants, update belief, and reject incoherent transitions. Its cross-scale operator, `bidi-gamma-delta`, sends context downward and evidence upward so nested reference frames can stay compatible. The result is a compact language for simulations, agents, adaptive UI, policy gates, predictive control, social fields, and mixed-reality world models.

## Minimal Engineer Handoff

If you are implementing or reviewing BiDi Coherence-Delta Calculus, preserve these invariants:

1. A phase cell has continuous phase plus latched committed pole.
2. Runtime ternary value is derived from phase by deadband quantization.
3. Boundary openness gates influence.
4. Channels are directed, weighted, and continuously delayed.
5. A boundary module owns input/output cones, belief, prior, precision, and optional child field.
6. Continuous flow updates phase, amplitude, belief, and plastic weights.
7. Guards fire evented commits off-grid.
8. A commit enforces the nonnegative balance invariant.
9. A commit is rejected if it increases local free energy.
10. Nested fields exchange context downward and coherence/evidence upward through `bidi-gamma-delta`.
11. Operators `gate`, `interfere`, and `corefold` remain primitive operations over boundary state.
12. The native notation must be able to declare modules, channels, guards, flow, and commits.
13. Capability claims should be backed by small witness programs.
14. Performance and scaling claims require separate benchmarks.

## Canonical Naming

Use:

- BiDi Coherence-Delta Calculus as the system/calculus name.
- `bidi-gamma-delta` / `bidiγΔ` as the preserved formal concept.
- cell, channel, module, field, and commit as the canonical formal vocabulary.
- `Thread`, `Strand`, `Knot`, `Breathfield`, and `breath` only as reference-reducer API names.

Use in engineering docs:

- phase cell;
- delayed coupling channel;
- boundary module;
- coupled process field;
- evented commit;
- bidirectional coherence-delta coupling.

This keeps the long-lived coherence-delta concept intact while giving the system a clean technical surface for engineers, researchers, and product builders.
