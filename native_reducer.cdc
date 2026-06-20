# native_reducer.cdc -- executable reducer clauses for the non-Python native runtime.
# The Python bootloader only records these declarations. The C native runtime
# consumes them and executes flow, commit, and nest transitions.

field reducer-field dt=0.125 gain=1.0 deadband=0.5

module council field=reducer-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell council.a module=council theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell council.b module=council theta=0.0 amplitude=1.0 omega=0.0
cell council.c module=council theta=3.141592653589793 amplitude=1.0 omega=0.0

module child field=reducer-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0 parent=council
cell child.a module=child theta=0.0 amplitude=1.0 omega=0.0
cell child.b module=child theta=0.0 amplitude=1.0 omega=0.0
cell child.c module=child theta=1.5707963267948966 amplitude=1.0 omega=0.0

channel council.a -> council.b weight=0.25 delay=0.0 angle=0.0 lines=1

flow reducer-flow field=reducer-field duration=1.0 expect-theta=council.b:0.25 tolerance=0.000001
commit reducer-commit module=council expect-trits=0+- expect-balance=admissible
nest reducer-nest parent=council child=child expect-parent-belief=0.666667 expect-child-prior=0.666667 tolerance=0.000001
compile reducer-ir source=native_reducer.cdc expect-ops=3 expect-flow=1 expect-commit=1 expect-nest=1
interpret reducer-ir-exec source=native_reducer.cdc expect-ops=3 expect-flow=1 expect-commit=1 expect-nest=1
proof trit-walk-n6 carrier=balanced-ternary arity=6 expect-total=729 expect-admissible=267 expect-localized=51 expect-saturated=20 expect-catalan=5

witness reducer-flow-native invariant=flow-additivity reducer=reducer-flow claim="C native runtime executes source-declared flow"
witness reducer-commit-native invariant=preservation reducer=reducer-commit claim="C native runtime executes source-declared balanced-ternary commit"
witness reducer-nest-native invariant=existence-viability reducer=reducer-nest claim="C native runtime executes source-declared parent-child nest exchange"
witness compiler-reducer-ir capability=G3 compile=reducer-ir claim="C native runtime compiles source-declared reducer jobs into reducer IR"
witness interpreter-reducer-ir capability=G7 interpret=reducer-ir-exec claim="C native runtime interprets compiled reducer IR"
witness proof-trit-walk-n6 invariant=normalforms capability=G4 proof=trit-walk-n6 claim="C native runtime exhaustively checks the finite balanced-ternary n=6 walk spectrum"

expect reducer reducer-flow-native
expect reducer reducer-commit-native
expect reducer reducer-nest-native
expect compile compiler-reducer-ir
expect interpret interpreter-reducer-ir
expect proof proof-trit-walk-n6
