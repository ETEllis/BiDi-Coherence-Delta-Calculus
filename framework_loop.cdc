# framework_loop.cdc -- the generic task loop as one continuous composition.
# One declared organism travels the whole loop: sense -> gate -> act ->
# integrate -> record -> consolidate -> recall -> decide -> enact -> refine,
# and then begins the next cycle. The `run` and `interpret` modes execute two
# full sense/act/integrate cycles over one shared state object -- the second
# cycle's expectations (theta 0.492228, belief 1.333333) are only reachable
# through state carried forward from the first, so the composition is
# executed, not merely described. The `surface`, `council`, and `evolve`
# modes exercise gate, record, recall, refine, key, decide, and enact over
# the same declared source. The decision coordinate equals the recorded
# episode key (110101 -> 311): what the organism records is what it decides.

capability H5 label="task-loop-composition"
framework H5 label=loop requires=sense,act,integrate,recur-sense,recur-act,recur-integrate,gate,record,recall,refine,key,cycle-count,proceduralize,skilled-execution,decide,enact permits=flow,commit,nest,guard,trace,measure,policy,bridge,counter,compile,interpret,council,evolve

field loop-field dt=0.125 gain=1.0 deadband=0.5

module agent field=loop-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell agent.a module=agent theta=0.0 amplitude=1.0 omega=0.0
cell agent.b module=agent theta=0.0 amplitude=1.0 omega=0.0
cell agent.c module=agent theta=1.5707963267948966 amplitude=1.0 omega=0.0

module context field=loop-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell context.a module=context theta=0.0 amplitude=1.0 omega=0.0
cell context.b module=context theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell context.c module=context theta=3.141592653589793 amplitude=1.0 omega=0.0

channel agent.c -> agent.b weight=0.25 delay=0.0 angle=0.0 lines=1

# Cycle 1: sense, act, integrate.
flow loop-sense-1 field=loop-field duration=1.0 expect-theta=agent.b:0.25 tolerance=0.000001
commit loop-act-1 module=agent expect-trits=++0 expect-balance=admissible expect-status=accepted expect-reason=none
nest loop-integrate-1 parent=context child=agent expect-parent-belief=0.666667 expect-child-prior=0.666667 tolerance=0.000001

# Cycle 2: the same organism senses again from its moved phase and its context
# belief accumulates -- carried state is what these expectations check.
flow loop-sense-2 field=loop-field duration=1.0 expect-theta=agent.b:0.492228 tolerance=0.000001
commit loop-act-2 module=agent expect-trits=++0 expect-balance=admissible expect-status=accepted expect-reason=none
nest loop-integrate-2 parent=context child=agent expect-parent-belief=1.333333 expect-child-prior=1.333333 tolerance=0.000001

# Gate, record, recall, refine, key, and cycle count over the same organism.
guard loop-gate cell=agent.c expect-state=open
trace loop-record field=loop-field expect-trits=++0+0- expect-events=4
measure loop-recall observer=context target=agent mode=commit expect-outcome=++0 expect-potential=nonincrease
policy loop-refine window=loop-record sampling=local commit=guarded adapt=recursive expect-sampling=local expect-commit=guarded expect-adapt=recursive
bridge loop-key trace=loop-record via=bridge64 expect-dyadic=110101 expect-triadic=311
counter loop-cycle value=0 increment=2 decrement=0 expect-value=2

# The whole organism proceduralizes: its declarative source compiles to
# reducer IR and the interpreter re-executes both cycles as the skilled path.
compile loop-ir source=framework_loop.cdc expect-ops=6 expect-flow=2 expect-commit=2 expect-nest=2
interpret loop-ir-exec source=framework_loop.cdc expect-ops=6 expect-flow=2 expect-commit=2 expect-nest=2

# Decide and enact: the organism deliberates over its own modules, adopts the
# coordinate its trace records, and writes that decision into source memory.
council loop-council field=loop-field members=agent,context quorum=4 expect-decision=adopt expect-dyadic=110101 expect-triadic=311
deliberate loop-quorum council=loop-council
evolve loop-enact source=framework_loop.cdc output=build/enacted_loop.cdc coordinate=110101 append-witness=loop-decision-memory expect-contains=loop-decision-memory

witness loop-sense-native invariant=flow-additivity capability=H5 framework=loop role=sense reducer=loop-sense-1 claim="the loop senses through continuous flow before any commitment"
witness loop-act-native invariant=preservation capability=H5 framework=loop role=act reducer=loop-act-1 claim="the loop acts through an accepted balanced-ternary commit"
witness loop-integrate-native invariant=existence-viability capability=H5 framework=loop role=integrate reducer=loop-integrate-1 claim="acted coherence integrates into nested context belief"
witness loop-recur-sense-native invariant=flow-additivity capability=H5 framework=loop role=recur-sense reducer=loop-sense-2 claim="the second sense phase starts from the phase the first cycle produced"
witness loop-recur-act-native invariant=preservation capability=H5 framework=loop role=recur-act reducer=loop-act-2 claim="the second act commits from carried continuous state"
witness loop-recur-integrate-native invariant=existence-viability capability=H5 framework=loop role=recur-integrate reducer=loop-integrate-2 claim="context belief accumulates across cycles instead of resetting"
witness loop-gate-native capability=H5 framework=loop role=gate guard=loop-gate claim="the loop gates action on an open crossing state"
witness loop-record-native invariant=trace-order-locality capability=H5 framework=loop role=record trace=loop-record claim="the loop records its configuration as a window-local ternary trace"
witness loop-recall-native invariant=soundness capability=H5 framework=loop role=recall measure=loop-recall claim="the loop recalls its agent state as a committing measurement"
witness loop-refine-native invariant=trace-order-locality capability=H5 framework=loop role=refine policy=loop-refine claim="the loop refines through recursive window policy"
witness loop-key-native invariant=dyadic-triadic-closure capability=H5 framework=loop role=key bridge=loop-key claim="the recorded configuration projects to one bridge64 coordinate"
witness loop-cycle-native capability=H5 framework=loop role=cycle-count counter=loop-cycle claim="cycle count is a local counter across both executed cycles"
witness loop-compile-native capability=H5 framework=loop role=proceduralize compile=loop-ir claim="the whole loop proceduralizes into reducer IR"
witness loop-interpret-native capability=H5 framework=loop role=skilled-execution interpret=loop-ir-exec claim="the compiled loop IR re-executes both cycles through the interpreter"
witness loop-decide-native invariant=dyadic-triadic-closure capability=H5 framework=loop role=decide council=loop-quorum claim="the loop deliberates over its own modules and adopts its recorded coordinate"
witness loop-enact-native capability=H5 framework=loop role=enact evolution=loop-enact claim="the adopted decision is enacted into durable source memory"

expect capability H5
expect framework H5 complete
expect reducer loop-sense-native
expect reducer loop-act-native
expect reducer loop-integrate-native
expect reducer loop-recur-sense-native
expect reducer loop-recur-act-native
expect reducer loop-recur-integrate-native
expect guard loop-gate-native
expect trace loop-record-native
expect measure loop-recall-native
expect policy loop-refine-native
expect bridge loop-key-native
expect counter loop-cycle-native
expect compile loop-compile-native
expect interpret loop-interpret-native
expect council loop-decide-native
expect evolution loop-enact-native
