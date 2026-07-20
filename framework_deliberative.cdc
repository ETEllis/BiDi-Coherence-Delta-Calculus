# framework_deliberative.cdc -- generalizable decision/agency framework.
# Binding: options are modules; deliberation is a council quorum over member
# trits; a decision is one bridge coordinate; enactment is a bridge-coordinate
# source evolution that writes the decision into durable source memory.
# Exercised by the C native runtime through `council` and `evolve` modes.

capability H4 label="deliberative-framework"

field deliberative-field dt=0.125 gain=1.0 deadband=0.5

module option-a field=deliberative-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell option-a.1 module=option-a theta=0.0 amplitude=1.0 omega=0.0
cell option-a.2 module=option-a theta=0.0 amplitude=1.0 omega=0.0

module option-b field=deliberative-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell option-b.1 module=option-b theta=3.141592653589793 amplitude=1.0 omega=0.0
cell option-b.2 module=option-b theta=0.0 amplitude=1.0 omega=0.0

module option-c field=deliberative-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell option-c.1 module=option-c theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell option-c.2 module=option-c theta=3.141592653589793 amplitude=1.0 omega=0.0

# Deliberation: option trits project into one occupancy word; the decision is
# adopted only when committed occupancy reaches quorum.
council deliberative-council field=deliberative-field members=option-a,option-b,option-c quorum=4 expect-decision=adopt expect-dyadic=111101 expect-triadic=331
deliberate deliberative-quorum council=deliberative-council

# Enactment: the adopted coordinate is written back into a source copy, so the
# decision becomes durable memory instead of a transient outcome.
evolve deliberative-enactment source=framework_deliberative.cdc output=build/enacted_decision.cdc coordinate=111101 append-witness=deliberative-decision-memory expect-contains=deliberative-decision-memory

witness deliberative-quorum-native invariant=dyadic-triadic-closure capability=H4 framework=deliberative role=deliberate council=deliberative-quorum claim="options deliberate to quorum and project into one bridge coordinate decision"
witness deliberative-enactment-native capability=H4 framework=deliberative role=enact evolution=deliberative-enactment claim="an adopted decision is enacted as a bridge-coordinate source evolution and remembered in source"

expect capability H4
expect council deliberative-quorum-native
expect evolution deliberative-enactment-native
