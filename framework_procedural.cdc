# framework_procedural.cdc -- generalizable procedural-memory framework.
# Binding: a procedure is an ordered reducer job sequence; proceduralization
# is compiling declarative source into reducer IR; skilled execution is the
# IR interpreter path; a held step is native retry semantics; consolidation
# is nest belief integration. The same source is exercised by the C native
# runtime through `run`, `compile`, and `interpret` modes.

capability H2 label="procedural-framework"

field procedural-field dt=0.125 gain=1.0 deadband=0.5

module routine field=procedural-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell routine.a module=routine theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell routine.b module=routine theta=0.0 amplitude=1.0 omega=0.0
cell routine.c module=routine theta=3.141592653589793 amplitude=1.0 omega=0.0

module skill field=procedural-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0 parent=routine
cell skill.a module=skill theta=0.0 amplitude=1.0 omega=0.0
cell skill.b module=skill theta=0.0 amplitude=1.0 omega=0.0
cell skill.c module=skill theta=1.5707963267948966 amplitude=1.0 omega=0.0

module missteps field=procedural-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell missteps.a module=missteps theta=3.141592653589793 amplitude=1.0 omega=0.0
cell missteps.b module=missteps theta=0.0 amplitude=1.0 omega=0.0
cell missteps.c module=missteps theta=1.5707963267948966 amplitude=1.0 omega=0.0

channel routine.a -> routine.b weight=0.25 delay=0.0 angle=0.0 lines=1

# Cue: the routine orients through continuous flow before its first step.
flow procedural-cue field=procedural-field duration=1.0 expect-theta=routine.b:0.25 tolerance=0.000001

# Step: an executed procedure step is an accepted balanced-ternary commit.
commit procedural-execute module=routine expect-trits=0+- expect-balance=admissible expect-status=accepted expect-reason=none

# Retry: a step attempted out of order is held, not corrupted.
commit procedural-retry module=missteps expect-trits=-+0 expect-balance=violated expect-status=held expect-reason=balance-violation

# Consolidate: practiced skill coherence integrates into the parent routine.
nest procedural-consolidate parent=routine child=skill expect-parent-belief=0.666667 expect-child-prior=0.666667 tolerance=0.000001

# Proceduralization: this declarative source compiles to executable reducer IR,
# and the interpreter executes the compiled IR as the skilled path.
compile procedural-ir source=framework_procedural.cdc expect-ops=4 expect-flow=1 expect-commit=2 expect-nest=1
interpret procedural-ir-exec source=framework_procedural.cdc expect-ops=4 expect-flow=1 expect-commit=2 expect-nest=1

witness procedural-cue-native invariant=flow-additivity capability=H2 framework=procedural role=cue reducer=procedural-cue claim="a procedure cue is continuous flow that orients the routine before its first step"
witness procedural-execute-native invariant=preservation capability=H2 framework=procedural role=step reducer=procedural-execute claim="a procedure step is an accepted balanced-ternary commit over the routine module"
witness procedural-retry-native invariant=soundness capability=H2 framework=procedural role=retry reducer=procedural-retry claim="a held commit gives procedures native retry semantics without state corruption"
witness procedural-consolidate-native invariant=existence-viability capability=H2 framework=procedural role=consolidate reducer=procedural-consolidate claim="skill coherence consolidates upward into routine belief"
witness procedural-compile-native capability=H2 framework=procedural role=proceduralize compile=procedural-ir claim="declarative skill source proceduralizes into executable reducer IR"
witness procedural-interpret-native capability=H2 framework=procedural role=skilled-execution interpret=procedural-ir-exec claim="compiled skill IR executes through the native interpreter path"

expect capability H2
expect reducer procedural-cue-native
expect reducer procedural-execute-native
expect reducer procedural-retry-native
expect reducer procedural-consolidate-native
expect compile procedural-compile-native
expect interpret procedural-interpret-native
