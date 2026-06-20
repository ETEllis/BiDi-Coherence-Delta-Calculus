# native_surface.cdc -- full checked native surface scenario for the C runtime.

field surface-field dt=0.125 gain=1.0 deadband=0.5

module surface-alpha field=surface-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell surface-alpha.a module=surface-alpha theta=0.0 amplitude=1.0 omega=0.0
cell surface-alpha.b module=surface-alpha theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell surface-alpha.c module=surface-alpha theta=3.141592653589793 amplitude=1.0 omega=0.0

module surface-beta field=surface-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell surface-beta.a module=surface-beta theta=0.0 amplitude=1.0 omega=0.0
cell surface-beta.b module=surface-beta theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell surface-beta.c module=surface-beta theta=3.141592653589793 amplitude=1.0 omega=0.0

guard surface-guard cell=surface-alpha.b expect-state=open
trace surface-trace field=surface-field expect-trits=+0-+0- expect-events=4
measure surface-measure observer=surface-alpha target=surface-beta mode=commit expect-outcome=+0- expect-potential=nonincrease
policy surface-policy window=surface-trace sampling=local commit=guarded adapt=recursive expect-sampling=local expect-commit=guarded expect-adapt=recursive
bridge surface-bridge trace=surface-trace via=bridge64 expect-dyadic=101101 expect-triadic=231
counter surface-counter value=2 increment=3 decrement=1 expect-value=4

witness surface-guard-native capability=G8 guard=surface-guard claim="native runtime evaluates source-declared guard state"
witness surface-trace-native invariant=trace-order-locality capability=G8 trace=surface-trace claim="native runtime samples field trits through a source-declared trace"
witness surface-measure-native invariant=soundness capability=G8 measure=surface-measure claim="native runtime evaluates source-declared committing measurement"
witness surface-policy-native invariant=trace-order-locality capability=G8 policy=surface-policy claim="native runtime validates source-declared trace policy"
witness surface-bridge-native invariant=dyadic-triadic-closure capability=G8 bridge=surface-bridge claim="native runtime projects source-declared trace through bridge64"
witness surface-counter-native capability=G8 counter=surface-counter claim="native runtime executes source-declared counter arithmetic"

expect guard surface-guard-native
expect trace surface-trace-native
expect measure surface-measure-native
expect policy surface-policy-native
expect bridge surface-bridge-native
expect counter surface-counter-native
