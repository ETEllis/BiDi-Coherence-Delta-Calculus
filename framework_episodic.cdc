# framework_episodic.cdc -- generalizable episodic-memory framework.
# Binding: an episode is a window-local ternary trace; recording is a
# balanced-ternary commit; consolidation is nest belief integration plus
# bridge projection to a content-addressable coordinate; recall is the
# bidirectional bridge64 codebook lookup; episode order is a local counter,
# not a global clock. Exercised by the C native runtime through `run` and
# `surface` modes, with recall cross-checked by the C bridge runtime.

capability H3 label="episodic-framework"

field episodic-field dt=0.125 gain=1.0 deadband=0.5

module experience field=episodic-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell experience.a module=experience theta=0.0 amplitude=1.0 omega=0.0
cell experience.b module=experience theta=0.0 amplitude=1.0 omega=0.0
cell experience.c module=experience theta=1.5707963267948966 amplitude=1.0 omega=0.0

module archive field=episodic-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell archive.a module=archive theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell archive.b module=archive theta=3.141592653589793 amplitude=1.0 omega=0.0
cell archive.c module=archive theta=0.0 amplitude=1.0 omega=0.0

channel experience.c -> experience.b weight=0.25 delay=0.0 angle=0.0 lines=1

# Live: an episode is first lived as continuous flow, before any record exists.
flow episodic-live field=episodic-field duration=1.0 expect-theta=experience.b:0.25 tolerance=0.000001

# Record: episode content commits as an admissible balanced-ternary word.
commit episodic-record module=experience expect-trits=++0 expect-balance=admissible expect-status=accepted expect-reason=none

# Consolidate: the archive integrates committed episode coherence, and the
# episode's prior now carries the archive context back down.
nest episodic-consolidate parent=archive child=experience expect-parent-belief=0.666667 expect-child-prior=0.666667 tolerance=0.000001

# Aperture, content, recall, policy, key, and ordinal.
guard episodic-guard cell=experience.c expect-state=open
trace episodic-trace field=episodic-field expect-trits=++00-+ expect-events=4
measure episodic-recall observer=archive target=experience mode=commit expect-outcome=++0 expect-potential=nonincrease
policy episodic-policy window=episodic-trace sampling=local commit=guarded adapt=recursive expect-sampling=local expect-commit=guarded expect-adapt=recursive
bridge episodic-key trace=episodic-trace via=bridge64 expect-dyadic=110011 expect-triadic=303
counter episodic-ordinal value=0 increment=1 decrement=0 expect-value=1

witness episodic-live-native invariant=flow-additivity capability=H3 framework=episodic role=live reducer=episodic-live claim="an episode is lived as continuous flow before any record exists"
witness episodic-record-native invariant=preservation capability=H3 framework=episodic role=record reducer=episodic-record claim="episode content commits as an admissible balanced-ternary record"
witness episodic-consolidate-native invariant=existence-viability capability=H3 framework=episodic role=consolidate reducer=episodic-consolidate claim="archive belief integrates committed episode coherence and returns context as prior"
witness episodic-aperture-native capability=H3 framework=episodic role=aperture guard=episodic-guard claim="the recording aperture is an open guard state on the episode's crossing cell"
witness episodic-content-native invariant=trace-order-locality capability=H3 framework=episodic role=content trace=episodic-trace claim="episode content is a window-local ternary trace with no global tick"
witness episodic-recall-native invariant=soundness capability=H3 framework=episodic role=recall measure=episodic-recall claim="recall reads episode content as a committing measurement without raising potential"
witness episodic-key-native invariant=dyadic-triadic-closure capability=H3 framework=episodic role=key bridge=episodic-key claim="an episode consolidates to one bridge64 coordinate as its content-addressable key"
witness episodic-ordinal-native invariant=trace-order-locality capability=H3 framework=episodic role=ordinal counter=episodic-ordinal claim="episode order is a local counter rather than a global clock"
witness episodic-policy-native invariant=trace-order-locality capability=H3 framework=episodic role=policy policy=episodic-policy claim="the recording policy samples locally and adapts recursively within the window"

expect capability H3
expect reducer episodic-live-native
expect reducer episodic-record-native
expect reducer episodic-consolidate-native
expect guard episodic-aperture-native
expect trace episodic-content-native
expect measure episodic-recall-native
expect policy episodic-policy-native
expect bridge episodic-key-native
expect counter episodic-ordinal-native
