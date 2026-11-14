# Technical review

Reviewed after the initial study, 15 November 2026.

| Finding | Resolution / retained limit |
| --- | --- |
| width*D11 can overstate free-strip stiffness | EI uses the full ABD compliance, including extension/bending coupling |
| A transform can pass isotropic tests while recovering wrong local stress | Added a 45-degree uniaxial stress-rotation check |
| Very flexible candidates violate small-deflection assumptions | Candidates exceeding 5% tip/span or 0.1 rad slope are flagged and excluded; raw linear values remain traceable |
| A coarse-mesh exact result could be sold as convergence | The beam table is explicitly a consistent-load closed-form verification |
| All-axial layup wins an artificially narrow load case | Report retains that result and its transverse/joint/impact omissions; mixed-angle alternatives remain visible |
| Synthetic data can be mistaken for a physical test | Every generated CSV row carries its source; report and fixture status are explicit |
| Crosshead travel includes frame compliance | Fit a seating intercept and subtract independently supplied machine compliance |
| Fixture envelope did not match the selected laminate | Generated `dimensions.scad` and the SVG share the selected coupon thickness; support spacing and drawing scale corrected |
| Generic material numbers could appear to be allowables | All constants stay in the input file, identified as assumptions with no supplier or batch attribution |

Verification includes isotropic rotation invariance, signed ply strengths,
laminate symmetry/balance, unsymmetric coupling, resultant reconstruction,
beam equilibrium, an off-node point load and synthetic compliance identification.

Unresolved: physical coupon manufacture and testing, fixture load-path detailing,
transverse shear, edge effects, damage, buckling and environmental changes. The
OpenSCAD source is a concept model; local numerical tests do not qualify CAD
manufacturability or a physical test setup.
