# trace_windows.cdc -- balanced-ternary trace/window witness declarations.

witness trace-additivity invariant=trace-order-locality claim="trace motion composes across adjacent windows"
witness trace-passive-state invariant=trace-order-locality claim="passive observation leaves field state unchanged"
witness trace-commit-ternary invariant=balanced-ternary-carrier claim="committing measurement returns balanced trits"
witness trace-commit-potential invariant=soundness claim="committing measurement does not increase potential"
witness trace-observer-boundary invariant=trace-order-locality claim="observer effect appears only at commit boundary"
witness trace-multiscale-agency invariant=existence-viability claim="nested child coherence acts as agency signal"
witness trace-overlap-boundaries invariant=trace-order-locality claim="one module can join multiple projected boundaries"
witness trace-causality invariant=trace-order-locality claim="trace windows cannot read future state"
witness trace-role-relative invariant=trace-order-locality claim="observer is role-relative"
witness trace-incidence-boundary invariant=trace-order-locality claim="incidence boundary is a trace target"
witness trace-line-projection invariant=trace-order-locality claim="trace windows expose selected dimensions only"
witness trace-window-relative-time invariant=trace-order-locality claim="trace time is window-relative"
witness trace-local-counter invariant=trace-order-locality claim="each window owns local event order without global tick"
witness trace-smooth-without-tick invariant=trace-order-locality claim="phase flow can accumulate with zero commit events"
witness trace-coupled-observation invariant=trace-order-locality claim="observer and observed are coupled by bounded window relation"
witness trace-recursive-policy invariant=trace-order-locality claim="window policy may adapt projection without new primitive"
witness trace-shared-state-commit invariant=soundness claim="measurement commits a shared ternary boundary state"
witness trace-agency-spectrum invariant=existence-viability claim="the same scope can be passive reactive intentional or self-referential by policy"

expect witness trace-additivity
expect witness trace-passive-state
expect witness trace-commit-ternary
expect witness trace-commit-potential
expect witness trace-observer-boundary
expect witness trace-multiscale-agency
expect witness trace-overlap-boundaries
expect witness trace-causality
expect witness trace-role-relative
expect witness trace-incidence-boundary
expect witness trace-line-projection
expect witness trace-window-relative-time
expect witness trace-local-counter
expect witness trace-smooth-without-tick
expect witness trace-coupled-observation
expect witness trace-recursive-policy
expect witness trace-shared-state-commit
expect witness trace-agency-spectrum
