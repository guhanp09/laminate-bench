# Stiffness and test notes

## Why EI uses the full compliance

A single D11 term constrains the other laminate responses. For a strip with
free transverse and twisting resultants, EI is width divided by the [3,3]
entry of inverse(ABD). This also retains extension–bending coupling in an
unsymmetric layup. The tests include an unsymmetric [0,90] stack and an isotropic
limit, plus a 45-degree stress-rotation check on local ply stresses.

The beam's consistent distributed-load vector reproduces closed-form nodal
displacements to roundoff. Refining that mesh is a useful implementation check,
but it does not validate assumed moduli or a one-dimensional beam approximation.

## Read the layup ranking narrowly

Only longitudinal bending is loaded in this example. All-axial plies are efficient
under that assumption. The mixed-angle alternatives remain in the result because
a real spar would also need transverse, shear, torsional and attachment load cases.
Candidates above 5% tip/span or 0.1 rad rotation are excluded from selection;
their raw linear predictions remain available for diagnosis.

Maximum stress is a ply screening ratio using assumed tension, compression and
shear strengths. It does not model progressive damage, delamination or buckling.

## Match the measurement to the calculation

The synthetic coupon data use the selected laminate at 20 mm width and 120 mm
support span. Every row is labelled SYNTHETIC. A fitted intercept accounts for
seating offset; supplied machine compliance is subtracted before converting
specimen compliance to EI. Statistical fit error excludes calibration and geometry
uncertainty. Support span enters cubically, and thickness would enter cubically
when converting EI to a material modulus.

The CAD and elevation now share the selected thickness and support spacing.
The current model describes the specimen/roller arrangement. A compatible test
frame, crosshead interface, load rating and manufacturing tolerances still need
to be established before making the fixture.
