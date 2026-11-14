# Mechanics and assumptions

Angles are degrees from x towards y, listed bottom to top. The geometric
midplane is z=0. Engineering shear strain gamma_xy is used throughout.
Lengths are metres, stresses pascals, forces newtons and moments N·m.

For an orthotropic ply under plane stress,

```text
nu21 = nu12 E2/E1
Q11 = E1/(1-nu12 nu21)
Q22 = E2/(1-nu12 nu21)
Q12 = nu12 E2/(1-nu12 nu21)
Q66 = G12
```

The transformed Qbar is integrated through thickness to produce A [N/m],
B [N] and D [N·m]. The six-component relation is

```text
[N; M] = [A B; B D] [epsilon_mid; kappa]
```

N is force per width [N/m], M is moment per width [N], epsilon is dimensionless
and curvature is 1/m. Global ply-face stresses follow from Qbar times local
through-thickness strain; stress rotation gives fibre, transverse and ply shear
components. The largest absolute stress/appropriate strength ratio is reported.

For a strip free of Nx, Ny, Nxy, My and Mxy, let S = inverse(ABD).
EI = width/S[3,3]. This includes extension–bending coupling and free transverse
and twist curvatures. Simply using width*D11 constrains degrees of freedom that
may actually be free. A narrow-beam equivalent does not resolve edge effects or
anisotropic warping; the mixed-angle cases need a higher-fidelity comparison.

The finite-element model uses the cubic Hermite two-node bending element, with
displacement and slope at each node. Distributed loads use their consistent
force and moment vector. Point loads within an element are distributed with
the same interpolation. Reactions come from K u - f after solving free DOFs.

For the cantilever UDL verification, delta_tip=q L⁴/(8EI). The consistent
load vector reproduces nodal deflections to roundoff even on a coarse mesh;
the element-count table is a verification study, not evidence of physical
accuracy. The simply supported centre-load relation is delta=P L³/(48EI).

## Bend reduction

Fit displacement = C_measured P + intercept over a user-selected elastic window.
Then C_specimen = C_measured - C_machine and EI = support_span³/(48 C_specimen).
Nonpositive corrected compliance and invalid load windows are rejected. Linear
fit uncertainty alone omits calibration and geometry uncertainty. In particular,
a relative span error is amplified threefold in EI. Thickness uncertainty is
even more consequential when converting EI into a material modulus.

## Reference and material provenance

[A. T. Nettles, NASA RP-1351](https://ntrs.nasa.gov/citations/19950009349)
is the constitutive-mechanics reference. Its scope does not supply strength
allowables or validate the illustrative constants in this repository. E1=130 GPa,
E2=9 GPa, G12=5 GPa, nu12=0.3, density=1580 kg/m³ and all strength inputs are
explicit assumptions in `examples/design.json`; there is no represented material
batch, resin cure cycle or supplier test certificate.
