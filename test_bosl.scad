include <BOSL2/std.scad>
r1 = [square(10)];
r2 = [translate([5,5], p=square(10))];
r_u = union(r1, r2);
echo(r_u);
