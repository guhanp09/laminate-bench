# Stiffness-test plan

Status: planned physical work; only the synthetic-data reduction has been run.
This is a small-deflection elastic stiffness comparison, not a claimed ASTM test.

## Specimen and fixture

Use at least five coupons per layup made with the same batch, layup schedule and
cure process. Record ply orientation, operator, resin/hardener batch, cure history,
specimen ID, edge preparation, mass and thickness at several locations. Retain
witness coupons. The example coupon is 150 mm long and 20 mm wide, with 120 mm
between support roller centres. The selected example laminate is 5 mm thick;
the CAD uses an illustrative 2 mm coupon envelope and must be adjusted to the
actual specimen before manufacture.

Verify support span and parallel roller axes. Identify a compatible calibrated
test frame and load cell before detailing the crosshead, bearing blocks, load
path, tolerances and fasteners. The current CAD has no load rating. Measure frame
compliance using a sufficiently stiff reference with independently known
deflection, over the same load range and contact arrangement.

## Measurements and reduction

1. Record zero load and displacement; apply a small seating load.
2. Log load, crosshead travel and, preferably, an independent midspan displacement.
   The synthetic example has only tens of micrometres of bending travel; select
   and calibrate instrumentation with adequate resolution before using that range.
3. Use a low elastic load/unload cycle to check seating and hysteresis. Record
   any slip, roller indentation or visible edge damage. Stop and inspect on a
   load drop or changed compliance; do not reinterpret it as elastic stiffness.
4. Select and record the elastic loading window before comparing layups. Pass
   increasing load and paired displacement arrays to `reduce_bend` with the
   independently measured machine compliance. Keep raw data and calibration IDs.
5. Compare EI and residuals by specimen. Investigate between-specimen spread,
   hysteresis and curvature in the load/travel relation. Record fixture contact
   or shear effects before changing material constants to make the model agree.

The synthetic fixture example uses noise seed 817 and marks each CSV row
`SYNTHETIC`. It must never be merged into a directory of measured runs.

## What constitutes useful evidence

Preserve raw CSV, specimen photographs, dimensions, instrument calibration,
fixture revision, setup notes, loading window and the reduction result together.
Report uncertainty from force, displacement, span and frame compliance. For a
failure investigation, document the first visible event and fracture location
before modifying the layup or manufacturing process.
