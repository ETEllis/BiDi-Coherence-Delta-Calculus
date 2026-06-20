# kernel.cdc -- native self-hosting contract for BiDi Coherence-Delta Calculus.
# Python may load and check this file, but the language/kernel contract lives here.

kernel bidi stage=2 target=cdc
  term cell channel module field counter trace window measurement bridge policy

  rule flow commit nest relation trace trace-order window measure adapt synchronize
  rule existence-viability dyadic-triadic-closure invariant-check witness-check

  provides parser-state reducer-state witness-state trace-window-state
  provides balanced-ternary-carrier angular-phase path-relation invariant-gate
  provides dyadic-triadic-bridge closure-64 closure-512 closure-4096
  provides operational-bridge-runtime bridge-coordinate-runtime bridge64-grid interactive-bridge-grid native-reducer-runtime native-compiler-ir finite-proof-checker native-ir-interpreter
  provides trace-order-locality local-time local-counter-synchrony
  provides observer-window-coupling recursive-window-policy shared-state-commit
  provides council-deliberation bridge-coordinate-self-evolution
  provides existence-viability agency-spectrum
  provides native-witness-suite native-capability-suite native-self-hosting-contract

  bootloader read-source parse-lines collect-native-declarations verify-expectations report

  expect native substrate == cdc
  expect host-debt <= 1
  expect python-files == 1
  expect bootloader minimal == true
  expect terms >= 10
  expect rules >= 14
  expect invariants >= 13
  expect witnesses >= 4759
  expect capabilities >= 31
  expect provides parser-state reducer-state witness-state trace-window-state
  expect provides balanced-ternary-carrier angular-phase path-relation invariant-gate
  expect provides dyadic-triadic-bridge closure-64 closure-512 closure-4096
  expect provides operational-bridge-runtime bridge-coordinate-runtime bridge64-grid interactive-bridge-grid native-reducer-runtime native-compiler-ir finite-proof-checker native-ir-interpreter
  expect provides trace-order-locality local-time local-counter-synchrony
  expect provides observer-window-coupling recursive-window-policy shared-state-commit
  expect provides council-deliberation bridge-coordinate-self-evolution
  expect provides existence-viability agency-spectrum
  expect provides native-witness-suite native-capability-suite native-self-hosting-contract
end
