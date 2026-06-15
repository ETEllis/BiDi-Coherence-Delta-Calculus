# system.cdc — the Coherence-Delta Calculus, exercised in its own native source.
# No host language appears here. Each `field` / `counter` is a calculus term;
# `flow` is continuous reduction ⟶_d, `commit` is guarded reduction ⟶_β,
# `expect` asserts a measured property. Run: python3 cdc_boot.py system.cdc

deadband 0.5

# — continuous-time coupled dynamics: two oscillators phase-lock (CTRNN regime) —
field sync open=yes gain=2.5 dt=0.02
  module x theta 0    omega 1.0
  module y theta 2.6  omega 1.25
  channel x -> y weight 1.6
  channel y -> x weight 1.6
  flow 30
  expect coherence-global >= 0.85
end

# — variable continuous delay line: destination lags source by ω·τ —
field delayline open=yes gain=0.0 dt=0.01
  module W theta 0 omega 1.0
  module D theta 0 omega 0.0
  channel W -> D weight 1.0 delay 0.7
  flow 5
  expect delay W D 0.7
end

# — hybrid continuous/discrete: an event-driven commit fires off the grid —
field hybrid open=no gain=1.0 dt=0.02
  module A theta 0 omega 1.0
  guard A crossing 0
  flow 15
  expect events-offgrid
end

# — fast inner field nested inside a slow outer breath (multirate, native) —
field outer open=yes gain=1.2 dt=0.04
  module P theta pi/2 omega 0.5
  nest P dt=0.005 open=yes
    module c theta 0 omega 5.0
    module d theta 1 omega 5.0
    channel c -> d
    channel d -> c
  end
  flow 0.2
  expect multirate >= 4
end

# — predictive-coding: belief descends prediction error toward evidence —
field perceive open=yes gain=1.0 dt=0.02
  module W theta 0 omega 0.0
  module G theta pi/2 precision 40
  channel W -> G weight 1.0
  flow 6
  expect belief G near 1.0 0.1
end

# — local plasticity: a correlated channel strengthens itself —
field learn open=no gain=0.0 dt=0.02
  module a theta 0 omega 0.0
  module b theta 0 omega 0.0
  channel a -> b weight 0.5 plastic
  flow 6
  expect weight a b > 0.6
end

# — a guarded commit lands an admissible, localized normal-form value —
field close open=no gain=0.0 dt=0.02
  module M trits + + - - + -
  commit M
  expect admissible M
  expect localized M
end

# — computational universality: a two-counter program adds, by generic commits —
counter add
  reg c1 3
  reg c2 4
  instr L0 jzdec c2 -> L1 | H
  instr L1 inc c1 -> L0
  instr H halt
  run from L0
  expect reg c1 == 7
end

counter mul-by-doubling
  reg c1 5
  reg t  0
  instr D0 jzdec c1 -> D1 | H
  instr D1 inc t -> D2
  instr D2 inc t -> D0
  instr H halt
  run from D0
  expect reg t == 10
end
