# relations.cdc -- angular, dimension-projected, and cross-scale bidi-gamma-delta.
# The relation is the channel; angle is rotation; nesting is the alpha=0 case.

deadband 0.5

# An anti-phase angular bias makes a relation's interference destructive.
field angled open=yes gain=0.0 dt=0.02
  module A theta pi/2
  module B theta pi/2
  channel A -> B angle=pi weight=1.0
  expect interference A B cos <= -0.9
  expect interference A B energy >= 1.5
end

# A dimension projection: couple only chosen cells.
field projected open=yes gain=0.0 dt=0.02
  module S theta 0 0 0 0 0 0
  module T theta pi/2 pi/2 pi/2 pi/2 pi/2 pi/2
  channel S -> T angle=0 lines=0,2 weight=1.0
  expect interference S T cos <= 0.1
end

# A cross-scale path relation at alpha=0 transports child coherence up to parent.
field tower open=yes gain=1.5 dt=0.02
  module P theta 1.0 omega 0.0
  nest P dt=0.005 open=yes
    module c theta 0.0 omega 0.0
  end
  channel P/c -> P weight=2.0 angle=0
  flow 5.0
  expect interference P/c P cos >= 0.9
end
