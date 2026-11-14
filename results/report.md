# Composite strip screening

Inputs: `examples/design.json` (SHA-256 `22488c83ad7191c4c61554518b5482af2fc38e9a1e11f87c0b2694b5f91b160f`).
All material values are illustrative assumptions, not measured allowables.

For a 350 × 40 mm cantilever strip under 120 N/m,
the lightest passing candidate in the enumerated set is **axial-40**:
5.00 mm thick, 110.6 g,
EI = 54.167 N·m², tip deflection = 4.156 mm.
Its largest ply maximum-stress index is 0.049, against a
declared screen of 0.50. This is not a certified safety factor.

The axial stack wins this one-dimensional load case. It has no demonstrated
transverse, attachment or impact capability. Choosing it for a real wing spar
would require shear webs, joints, torsional loads, buckling and damage assessment.
The study therefore keeps the mixed-angle alternatives rather than declaring
one layup universally optimal. Full stacks appear in `selected_layup.json`.

Candidates with predicted tip travel above 5% of span or rotation above 0.1 rad
are flagged outside the declared small-deflection screen. Their linear-model
numbers are retained for traceability but cannot be taken as valid deformations.

The Euler–Bernoulli FE nodes match the consistent-load closed form to roundoff.
`beam_verification.csv` shows element count and equilibrium residuals. That
agreement verifies the implementation, not the material inputs or beam assumptions.

The 120 mm support-span, 20 mm wide synthetic coupon has true EI = 27.0833
N·m²; the reduction recovers 27.1494 N·m² after subtracting machine
compliance. A fitted intercept handles seating offset. The reported statistical
standard error excludes force calibration, support span, displacement calibration,
machine compliance and laminate thickness uncertainty.

The fixture source and schematic are concept CAD. Neither fixture manufacture nor
coupon testing has occurred. Next: fabricate witness coupons, measure thickness
at several points, verify support alignment, calibrate frame compliance and compare
measured stiffness and failure mode against these predictions.
