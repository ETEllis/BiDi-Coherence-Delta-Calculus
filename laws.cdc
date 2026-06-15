# laws.cdc — the operator algebra and metatheorems, asserted in native .cdc.
# Each line is a proof obligation the bootstrap discharges against the calculus.
# Run: python3 cdc_boot.py laws.cdc

expect law gate-abelian        # ⊙ gate is an abelian group  ≅ 𝕋ⁿ  (complement = inverse)
expect law interfere-monoid    # ⊞ interfere is a commutative monoid (unit ⊥)
expect law rotation-linear     # ⟳ rotation distributes over ⊞ (time is linear)
expect law corefold-morphism   # ∂ core-fold is a ⊞-linear, ⟳-equivariant morphism (non-idempotent)
expect law preservation        # T1: every commit ⟹ admissible committed state
expect law soundness           # T2: Φ free energy never increases across a commit
expect law normalforms         # T5: ⟶_β-irreducible values = localized closures (Catalan 5 / Motzkin 51)
