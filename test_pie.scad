include <BOSL2/std.scad>

divisions = 3;
w_div = 2;
width = 100;
ang = 360 / divisions;
hex_path = offset(regular_ngon(n=6, d=width), r=-4);

for (i=[0:divisions-1]) {
  wedge = concat([[0, 0]], arc(r=width*2, start=i*ang, angle=ang));
  thinned = offset(wedge, r=-w_div/2, closed=true);
  sub_region = intersection([hex_path], [thinned]);
  echo("SUB REGION:", len(sub_region[0]));
}
