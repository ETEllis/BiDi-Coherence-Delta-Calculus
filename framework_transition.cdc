# framework_transition.cdc -- generalizable action/state-change framework.
# Binding: a state machine is a committed module; a transition is a guarded
# balanced-ternary commit; an action is continuous flow; hierarchy is nest.
# Every binding witness below links to a job the C native runtime executes
# through `run` and `surface` modes. No new grammar, no host growth.

capability H1 label="transition-framework"
framework H1 label=transition requires=precondition,action,fire,block,hierarchy,log,observe,policy,state-key,tally permits=guard,flow,commit,nest,trace,measure,policy,bridge,counter

field transition-field dt=0.125 gain=1.0 deadband=0.5
field transition-blocked-field dt=0.125 gain=1.0 deadband=0.5

module fsm field=transition-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell fsm.s1 module=fsm theta=0.0 amplitude=1.0 omega=0.0
cell fsm.s2 module=fsm theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell fsm.s3 module=fsm theta=3.141592653589793 amplitude=1.0 omega=0.0

module fsm-sub field=transition-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0 parent=fsm
cell fsm-sub.a module=fsm-sub theta=0.0 amplitude=1.0 omega=0.0
cell fsm-sub.b module=fsm-sub theta=0.0 amplitude=1.0 omega=0.0
cell fsm-sub.c module=fsm-sub theta=1.5707963267948966 amplitude=1.0 omega=0.0

module blocked field=transition-blocked-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell blocked.a module=blocked theta=3.141592653589793 amplitude=1.0 omega=0.0
cell blocked.b module=blocked theta=0.0 amplitude=1.0 omega=0.0
cell blocked.c module=blocked theta=1.5707963267948966 amplitude=1.0 omega=0.0

channel fsm.s2 -> fsm.s1 weight=0.25 delay=0.0 angle=0.0 lines=1

# Precondition: the machine's crossing cell must be an open equilibrium state.
guard transition-guard cell=fsm.s2 expect-state=open

# Action: continuous phase motion is the act that changes state.
flow transition-action field=transition-field duration=1.0 expect-theta=fsm.s1:0.25 tolerance=0.000001

# Fired transition: the legal state change commits an admissible trit walk.
commit transition-fire module=fsm expect-trits=+0- expect-balance=admissible expect-status=accepted expect-reason=none

# Blocked transition: an illegal state change is held with an explicit reason.
commit transition-blocked module=blocked expect-trits=-+0 expect-balance=violated expect-status=held expect-reason=balance-violation

# Hierarchy: substate coherence lifts upward, superstate context flows down.
nest transition-lift parent=fsm child=fsm-sub expect-parent-belief=0.666667 expect-child-prior=0.666667 tolerance=0.000001

# Transition log, observation, policy, state key, and tally.
trace transition-trace field=transition-field expect-trits=+0-++0 expect-events=4
measure transition-measure observer=fsm target=fsm-sub mode=commit expect-outcome=++0 expect-potential=nonincrease
policy transition-policy window=transition-trace sampling=local commit=guarded adapt=recursive expect-sampling=local expect-commit=guarded expect-adapt=recursive
bridge transition-bridge trace=transition-trace via=bridge64 expect-dyadic=101110 expect-triadic=232
counter transition-counter value=0 increment=2 decrement=1 expect-value=1

witness transition-precondition-native capability=H1 framework=transition role=precondition guard=transition-guard claim="a transition precondition is an open guard state on the crossing cell"
witness transition-action-native invariant=flow-additivity capability=H1 framework=transition role=action reducer=transition-action claim="an action is continuous flow that moves state phase before any commit"
witness transition-fire-native invariant=preservation capability=H1 framework=transition role=fire reducer=transition-fire claim="a fired transition is an accepted balanced-ternary commit over the state module"
witness transition-block-native invariant=soundness capability=H1 framework=transition role=block reducer=transition-blocked claim="an illegal transition is held with balance-violation instead of mutating state"
witness transition-hierarchy-native invariant=existence-viability capability=H1 framework=transition role=hierarchy reducer=transition-lift claim="hierarchical state lifts substate coherence into superstate belief"
witness transition-log-native invariant=trace-order-locality capability=H1 framework=transition role=log trace=transition-trace claim="the transition log is a window-local ternary trace"
witness transition-observe-native invariant=soundness capability=H1 framework=transition role=observe measure=transition-measure claim="observing the active substate commits its ternary outcome without raising potential"
witness transition-policy-native invariant=trace-order-locality capability=H1 framework=transition role=policy policy=transition-policy claim="transition policy samples locally and commits through guards"
witness transition-state-key-native invariant=dyadic-triadic-closure capability=H1 framework=transition role=state-key bridge=transition-bridge claim="a machine configuration projects to one bridge64 coordinate as its state key"
witness transition-tally-native capability=H1 framework=transition role=tally counter=transition-counter claim="net transition count is a local counter"

expect capability H1
expect framework H1 complete
expect guard transition-precondition-native
expect reducer transition-action-native
expect reducer transition-fire-native
expect reducer transition-block-native
expect reducer transition-hierarchy-native
expect trace transition-log-native
expect measure transition-observe-native
expect policy transition-policy-native
expect bridge transition-state-key-native
expect counter transition-tally-native
