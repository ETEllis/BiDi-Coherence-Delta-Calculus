# system.cdc -- native capability witness suite.

capability A1 label="first-principles-primitives"
capability A2 label="host-free-core-spec"
capability A3 label="self-contained-self-interference"
capability A4 label="self-referential-fractalization"
capability B1 label="continuous-time-flow"
capability B2 label="hybrid-flow-and-commit"
capability B3 label="off-grid-event-reactivity"
capability B4 label="multi-scale-temporal-feedback"
capability B5 label="continuous-delay-line"
capability C1 label="first-class-fractal-nesting"
capability C2 label="recursive-self-similar-dynamics"
capability C3 label="scale-relative-socialization"
capability C4 label="multiple-reference-frames"
capability C5 label="bounded-nested-field-tower"
capability D1 label="local-and-global-coherence"
capability D2 label="barrier-and-free-energy-guard"
capability D3 label="active-inference-integration"
capability D4 label="perception-action-free-energy"
capability E1 label="evented-state-and-two-counter"
capability E2 label="neural-dynamics-witnesses"
capability E3 label="same-primitives-multiple-regimes"
capability F1 label="operators-in-flowing-field"
capability F2 label="scale-relative-operator-socialization"
capability F3 label="bidi-maintains-coherent-frames"
capability G1 label="operational-bridge-runtime"
capability G2 label="native-reducer-runtime"
capability G3 label="native-compiler-ir"
capability G4 label="finite-proof-checker"
capability G5 label="council-deliberation"
capability G6 label="bridge-coordinate-self-evolution"
capability G7 label="native-ir-interpreter"

witness A1-native-primitives capability=A1 claim="cell/channel/module/field/commit/bidi-gamma-delta are native terms"
witness A2-host-free-spec capability=A2 claim="formal core names primitives without host-language dependence"
witness A3-self-interference capability=A3 claim="module can interfere with itself through native relation"
witness A4-fractalization capability=A4 claim="module can host child field"
witness B1-continuous-flow capability=B1 claim="phase evolves over duration rather than integer ticks"
witness B2-hybrid-commit capability=B2 claim="flow can interleave with guarded balanced-ternary commit"
witness B3-offgrid-events capability=B3 claim="commit events are located off realization grid"
witness B4-multirate-nesting capability=B4 claim="inner field can run faster than outer field"
witness B5-delay-line capability=B5 claim="channel delay is continuous duration"
witness C1-native-nesting capability=C1 claim="nested field is a first-class term"
witness C2-self-similar capability=C2 claim="bounded recursive scales preserve coherence"
witness C3-socialization capability=C3 claim="receiver boundary state gates influence"
witness C4-reference-frames capability=C4 claim="parent and child frames coexist under bidi-gamma-delta"
witness C5-bounded-tower capability=C5 claim="nested field tower has explicit depth budget"
witness D1-emergent-coherence capability=D1 claim="local relations can raise global coherence"
witness D2-guarded-barrier capability=D2 claim="commit barrier and guard preserve admissibility"
witness D3-active-inference capability=D3 claim="belief tracks evidence across relation"
witness D4-perception-action capability=D4 claim="mismatch can reduce by updating model or acting through output"
witness E1-two-counter capability=E1 claim="evented counter terms express register-machine computation"
witness E2-neural-dynamics capability=E2 claim="same primitives express recurrent predictive and Hebbian regimes"
witness E3-one-program capability=E3 claim="one field source can combine flow and commit"
witness F1-operators capability=F1 claim="gate/interfere/corefold/commit operate inside field"
witness F2-scale-operators capability=F2 claim="operator influence is boundary-gated"
witness F3-bidi-frames capability=F3 claim="bidi-gamma-delta preserves multiple coherent frames"
witness G1-bridge-runtime capability=G1 claim="non-Python runtime consumes bridge64.cdc as lookup table"
witness G2-native-reducer capability=G2 claim="non-Python runtime consumes native_reducer.cdc and executes flow commit nest"

expect capability A1
expect capability A2
expect capability A3
expect capability A4
expect capability B1
expect capability B2
expect capability B3
expect capability B4
expect capability B5
expect capability C1
expect capability C2
expect capability C3
expect capability C4
expect capability C5
expect capability D1
expect capability D2
expect capability D3
expect capability D4
expect capability E1
expect capability E2
expect capability E3
expect capability F1
expect capability F2
expect capability F3
expect capability G1
expect capability G2
expect capability G3
expect capability G4
expect capability G5
expect capability G6
expect capability G7
