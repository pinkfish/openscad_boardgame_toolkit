include <boardgame_toolkit.scad>
CapBoxLidWithLabelAndCustomShape(100, 50, 30, text_width = 70, text_height = 20, text_str = "Frog") {
  ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
     supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
}
