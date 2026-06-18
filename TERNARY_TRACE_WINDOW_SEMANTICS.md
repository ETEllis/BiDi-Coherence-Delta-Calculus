# Ternary Trace/Window Semantics

This document defines the first derived observer layer for BiDi Coherence-Delta
Calculus. It does not add a new foundation, a Boolean observer, or a new
collapse operator. It gives names to what the existing calculus already makes
possible: phase-time, event counters, observer-relative windows, measurement
records, and higher-order boundaries projected from subordinate dynamics.

The foundational spine remains:

```text
flow     continuous phase-time reduction
commit   guarded balanced-ternary event reduction
nest     scale-relative bidi-gamma-delta coupling
```

Everything below is a projection over that spine.

## Balanced-Ternary Constraint

The discrete layer is always balanced ternary:

```text
+1   expansion / outward commitment / asserted pole
 0   resting equilibrium / crossing / aperture / unresolved pivot
-1   contraction / return commitment / opposed pole
```

The middle value is not false, null, or absence. It is the live crossing where a
boundary is most open to relation. This is why measurement records in BIDI
produce balanced trits, not Boolean outcomes.

## Time

BIDI has three compatible notions of time:

```text
phase-time      smooth flow and rotation through continuous duration
event-time      count/order of guarded commits
trace-time      event/phase history observed through a window
```

`dt` is a realization step, not fundamental time. A trace window has its own
event counter because different windows can observe different commit densities
over the same underlying field. Relative time is therefore the mismatch between
phase flow, delay, and commit density across windows.

## Window

A window is a bounded projection over a field:

```text
WindowSpec =
  name
  scope_path
  horizon_time or horizon_events
  lines
  angle_frame
  projection
  sampling_policy
  commit_policy
```

The window reuses path, angle, and line projection from relation channels. It is
not a second relation system.

## Trace

A trace is the history observed through a window:

```text
TraceSpan =
  scope_path
  t0, t1
  event0, event1
  samples
  commit_count
  mean_cos_delta
  mean_sin_delta
  mean_gamma
  mean_energy
  total_phase_motion
```

Passive trace extraction must not change field state. It may create a record,
but it does not alter phase, belief, events, commits, or free energy.

Trace windows are causal. They may read current and past field state, including
delayed history. They may not read future state.

## Observer

An observer is not a substance or privileged entity. It is a role:

```text
ObserverSpec =
  holder_path
  window
  mode
```

Any module, relation, or projected boundary can hold a window. That means every
operator can function relationally as observer, participant, or measurement
interface depending on the window it holds and the relation in which it appears.

## Measurement

Measurement is a precision-amplified windowed relation whose committing form
uses the existing guarded commit:

```text
MeasurementRecord =
  observer_path
  target_path
  window
  pre_trace
  post_trace
  outcome_trit
  phi_delta
  relation_energy
  committed
  barrier_applied
```

There is no new collapse primitive. A committing measurement is a trace
contraction through `commit`; it must preserve admissibility and must not
increase local free energy. Its outcome is a vector of trits.

Passive observation and committing measurement differ only at the commit
boundary. Before that boundary, they can share the same target trace; after it,
the committing path may diverge because it has changed the target state.

## Multiscale Agency

Scale-relative agency is a windowed performance summary:

```text
AgencySummary =
  scope_path
  window
  free_energy_drop
  prediction_error_drop
  action_effect
  cross_scale_gain
  stability
```

This lets the same substrate describe cells, tissues, brains, organisms,
interfaces, and social fields without importing biology-specific primitives.
Local modules can act as competent sub-agents inside higher-order boundaries
while still reading their own local environment honestly.

## Incidence And Emergent Boundary

A higher-order boundary can be projected from subordinate paths:

```text
IncidenceSpec =
  name
  source_paths
  window
  aggregate_rule
  corefold_rule
```

The same subordinate module may participate in multiple projected boundaries.
This models overlapping objecthood without exclusive ownership: a local component
can be part of several coherent higher-order structures, depending on window,
phase alignment, relation energy, and scale.

## Acceptance Witnesses

`trace_window_witness.py` checks:

- trace motion composes across adjacent windows;
- passive observation leaves field state unchanged;
- committing measurement yields only balanced-ternary outcomes;
- committing measurement does not increase `Phi`;
- observer effect appears only after the commit boundary;
- nested child coherence can act as a multiscale agency signal;
- one subordinate module can participate in multiple projected boundaries;
- trace windows cannot read future state.
- observer mode is role-relative rather than substance-relative;
- projected incidence boundaries are first-class trace targets.

These witnesses make the layer executable without changing the calculus's
foundation.
