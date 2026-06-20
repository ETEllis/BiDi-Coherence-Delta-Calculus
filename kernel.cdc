# kernel.cdc -- native self-hosting contract for BiDi Coherence-Delta Calculus.
# This file is intentionally .cdc, not Python. It pins the language's own
# semantic kernel as native source that the temporary host bridge must obey.

kernel bidi stage=1 target=cdc
  term cell
  term channel
  term module
  term field
  term counter
  term trace
  term window
  term measurement
  term bridge

  rule flow
  rule commit
  rule nest
  rule relation
  rule trace
  rule trace-order
  rule window
  rule measure
  rule existence-viability
  rule dyadic-triadic-closure

  provides parser-state reducer-state witness-state trace-window-state
  provides balanced-ternary-carrier angular-phase path-relation invariant-gate
  provides dyadic-triadic-bridge closure-64
  provides trace-order-locality local-time
  provides existence-viability agency-spectrum
  bootloader read-source parse-blocks dispatch-kernel

  expect native substrate == cdc
  expect host-debt <= 1
  expect terms >= 9
  expect rules >= 9
  expect provides parser-state reducer-state witness-state trace-window-state
  expect provides balanced-ternary-carrier angular-phase path-relation invariant-gate
  expect provides dyadic-triadic-bridge closure-64
  expect provides trace-order-locality local-time
  expect provides existence-viability agency-spectrum
end
