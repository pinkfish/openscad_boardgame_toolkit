#/usr/bin/awk -f
BEGIN {ORS=" "}

/^module [a-zA-Z_-]*(.*).*`make`.me.*/ {
  gsub(/module /, "");
  gsub(/\(.*\).*$/, "");
  printf "output/%s__%s.stl ", BASEFILE, $0;
}
