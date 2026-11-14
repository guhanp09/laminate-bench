// Concept fixture, dimensions in mm. Not a load-rated machine component.
// The dimensioned drawing is generated independently by examples/study.py.
$fn = 64;
span = 120;
roller_d = 10;
coupon_width = 20;
base_l = 180;
base_w = 60;
base_t = 8;
support_h = 22;

module roller(x, z) {
    translate([x, 0, z]) rotate([90, 0, 0])
        cylinder(h=coupon_width+20, d=roller_d, center=true);
}

// Base and four mounting holes. Hole placement is a concept, not a fit spec.
color("silver") difference() {
    translate([0, 0, -base_t/2]) cube([base_l, base_w, base_t], center=true);
    for (x=[-75,75], y=[-20,20])
        translate([x,y,-base_t]) cylinder(h=base_t+1,d=6.5);
}
for (x=[-span/2,span/2]) {
    for(y=[-18,18]) color("gray")
        translate([x,y,support_h/2]) cube([18,10,support_h],center=true);
    color("steelblue") roller(x, support_h);
}
color([0.15,0.15,0.15,0.8])
    translate([0,0,support_h+roller_d/2+1]) cube([150,coupon_width,2],center=true);
color("darkorange") roller(0,support_h+roller_d+2);
// Upper roller is shown without a crosshead or load cell; those are interfaces
// to a calibrated test frame and must be designed for the actual equipment.
