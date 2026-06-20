# council_bridge.cdc -- source-level council deliberation and bridge-coordinate evolution scenario.

field council-field dt=0.125 gain=1.0 deadband=0.5

module alpha field=council-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell alpha.a module=alpha theta=0.0 amplitude=1.0 omega=0.0
cell alpha.b module=alpha theta=1.5707963267948966 amplitude=1.0 omega=0.0

module beta field=council-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell beta.a module=beta theta=3.141592653589793 amplitude=1.0 omega=0.0
cell beta.b module=beta theta=0.0 amplitude=1.0 omega=0.0

module gamma field=council-field belief=0.0 prior=0.0 precision=1.0 action-gain=1.0
cell gamma.a module=gamma theta=1.5707963267948966 amplitude=1.0 omega=0.0
cell gamma.b module=gamma theta=3.141592653589793 amplitude=1.0 omega=0.0

council bridge-council field=council-field members=alpha,beta,gamma quorum=4 expect-decision=adopt expect-dyadic=101101 expect-triadic=231
deliberate bridge-deliberation council=bridge-council

evolve bridge-coordinate-evolution source=native_reducer.cdc output=build/evolved_native_reducer.cdc coordinate=101101 append-witness=self-evolution-bridge expect-contains=self-evolution-bridge

witness council-deliberation-native capability=G5 council=bridge-deliberation claim="native runtime deliberates across council members into a bridge coordinate decision"
witness self-evolution-native capability=G6 evolution=bridge-coordinate-evolution claim="native runtime edits a .cdc source copy through a bridge coordinate"

expect council council-deliberation-native
expect evolution self-evolution-native
