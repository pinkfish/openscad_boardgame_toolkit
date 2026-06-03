module Layout_container0(height) {
    back(73.5) right(121.0) {
       back(-35.0)
         cuboid([16.5, 32.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(0.0)
         cuboid([16.5, 32.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(35.0)
         cuboid([16.5, 32.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(43.0) right(29.25) {
       cuboid([52.5, 42.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(34.25) right(148.75) {
       cuboid([34.5, 62.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(11.0) right(56.75) {
       right(-40.0)
         cuboid([17.0, 17.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(-20.0)
         cuboid([17.0, 17.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(0.0)
         cuboid([17.0, 17.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(20.0)
         cuboid([17.0, 17.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(40.0)
         cuboid([17.0, 17.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(94.25) right(149.0) {
       cuboid([35.0, 51.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(76.5) right(66.0) {
       back(-17.5)
         cuboid([16.5, 32.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(17.5)
         cuboid([16.5, 32.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(85.75) right(22.25) {
       cuboid([38.5, 37.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(125.25) right(21.75) {
       cuboid([37.5, 35.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(41.75) right(93.25) {
       cuboid([33.5, 39.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(106.25) right(83.75) {
       cuboid([14.5, 83.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(104.5) right(49.75) {
       back(-30.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(-15.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(0.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(15.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(30.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(134.5) right(148.25) {
       cuboid([33.5, 23.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(84.5) right(100.25) {
       cuboid([12.5, 40.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(124.25) right(101.25) {
       cuboid([14.5, 33.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(140.25) right(65.25) {
       cuboid([13.5, 12.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
}
module Layout_Text_container0(height, max_size=15) {
    back(73.5) right(121.0) {
       back(-35.0)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara 2", valign="center", halign="center");
       back(0.0)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara 2", valign="center", halign="center");
       back(35.0)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara 2", valign="center", halign="center");
    }
    back(43.0) right(29.25) {
         linear_extrude(h=height) resize([min(max_size, 52.5), 0], auto=true) text("Elephant", valign="center", halign="center");
    }
    back(34.25) right(148.75) {
         linear_extrude(h=height) resize([0, min(max_size, 62.5)], auto=true) rotate(90) text("Rhino", valign="center", halign="center");
    }
    back(11.0) right(56.75) {
       right(-40.0)
         linear_extrude(h=height) resize([min(max_size, 17.0), 0], auto=true) text("Gopher", valign="center", halign="center");
       right(-20.0)
         linear_extrude(h=height) resize([min(max_size, 17.0), 0], auto=true) text("Gopher", valign="center", halign="center");
       right(0.0)
         linear_extrude(h=height) resize([min(max_size, 17.0), 0], auto=true) text("Gopher", valign="center", halign="center");
       right(20.0)
         linear_extrude(h=height) resize([min(max_size, 17.0), 0], auto=true) text("Gopher", valign="center", halign="center");
       right(40.0)
         linear_extrude(h=height) resize([min(max_size, 17.0), 0], auto=true) text("Gopher", valign="center", halign="center");
    }
    back(94.25) right(149.0) {
         linear_extrude(h=height) resize([0, min(max_size, 51.5)], auto=true) rotate(90) text("Polar Bear", valign="center", halign="center");
    }
    back(76.5) right(66.0) {
       back(-17.5)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara", valign="center", halign="center");
       back(17.5)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara", valign="center", halign="center");
    }
    back(85.75) right(22.25) {
         linear_extrude(h=height) resize([min(max_size, 38.5), 0], auto=true) text("Ornyx", valign="center", halign="center");
    }
    back(125.25) right(21.75) {
         linear_extrude(h=height) resize([min(max_size, 37.5), 0], auto=true) text("Kangaroo", valign="center", halign="center");
    }
    back(41.75) right(93.25) {
         linear_extrude(h=height) resize([0, min(max_size, 39.5)], auto=true) rotate(90) text("Gazelle", valign="center", halign="center");
    }
    back(106.25) right(83.75) {
         linear_extrude(h=height) resize([0, min(max_size, 83.5)], auto=true) rotate(90) text("Crocodile", valign="center", halign="center");
    }
    back(104.5) right(49.75) {
       back(-30.0)
         linear_extrude(h=height) resize([0, min(max_size, 12.0)], auto=true) rotate(90) text("Termite", valign="center", halign="center");
       back(-15.0)
         linear_extrude(h=height) resize([0, min(max_size, 12.0)], auto=true) rotate(90) text("Termite", valign="center", halign="center");
       back(0.0)
         linear_extrude(h=height) resize([0, min(max_size, 12.0)], auto=true) rotate(90) text("Termite", valign="center", halign="center");
       back(15.0)
         linear_extrude(h=height) resize([0, min(max_size, 12.0)], auto=true) rotate(90) text("Termite", valign="center", halign="center");
       back(30.0)
         linear_extrude(h=height) resize([0, min(max_size, 12.0)], auto=true) rotate(90) text("Termite", valign="center", halign="center");
    }
    back(134.5) right(148.25) {
         linear_extrude(h=height) resize([min(max_size, 33.5), 0], auto=true) text("Pig", valign="center", halign="center");
    }
    back(84.5) right(100.25) {
         linear_extrude(h=height) resize([0, min(max_size, 40.0)], auto=true) rotate(90) text("Snake", valign="center", halign="center");
    }
    back(124.25) right(101.25) {
         linear_extrude(h=height) resize([0, min(max_size, 33.5)], auto=true) rotate(90) text("Fox", valign="center", halign="center");
    }
    back(140.25) right(65.25) {
         linear_extrude(h=height) resize([min(max_size, 13.5), 0], auto=true) text("Chipmunk", valign="center", halign="center");
    }
}
module Layout_container1(height) {
    back(69.75) right(82.75) {
       right(-56.0)
         cuboid([25.0, 24.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(-28.0)
         cuboid([25.0, 24.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(0.0)
         cuboid([25.0, 24.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(28.0)
         cuboid([25.0, 24.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(56.0)
         cuboid([25.0, 24.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(10.25) right(69.75) {
       right(-48.0)
         cuboid([21.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(-24.0)
         cuboid([21.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(0.0)
         cuboid([21.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(24.0)
         cuboid([21.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(48.0)
         cuboid([21.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(38.0) right(26.0) {
       cuboid([46.0, 35.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(35.25) right(72.75) {
       cuboid([41.5, 29.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(37.75) right(114.25) {
       cuboid([35.5, 34.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(25.75) right(151.5) {
       cuboid([24.0, 45.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(93.25) right(26.75) {
       cuboid([47.5, 18.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(96.75) right(67.75) {
       cuboid([28.5, 25.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(95.75) right(99.25) {
       cuboid([28.5, 23.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(95.25) right(130.25) {
       cuboid([27.5, 22.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(117.25) right(15.5) {
       cuboid([25.0, 23.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(120.75) right(99.25) {
       cuboid([28.5, 20.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(100.75) right(154.0) {
       cuboid([14.0, 33.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(117.25) right(40.75) {
       cuboid([19.5, 23.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(118.0) right(126.25) {
       cuboid([19.5, 17.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(137.5) right(16.75) {
       cuboid([27.5, 11.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(138.5) right(45.25) {
       cuboid([23.5, 13.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(136.25) right(127.75) {
       cuboid([22.5, 13.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(118.25) right(66.0) {
       cuboid([25.0, 11.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(127.75) right(154.75) {
       cuboid([15.5, 14.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(143.25) right(147.5) {
       cuboid([11.0, 10.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(142.75) right(160.75) {
       cuboid([9.5, 9.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
}
module Layout_Text_container1(height, max_size=15) {
    back(69.75) right(82.75) {
       right(-56.0)
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Turkey", valign="center", halign="center");
       right(-28.0)
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Turkey", valign="center", halign="center");
       right(0.0)
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Turkey", valign="center", halign="center");
       right(28.0)
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Turkey", valign="center", halign="center");
       right(56.0)
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Turkey", valign="center", halign="center");
    }
    back(10.25) right(69.75) {
       right(-48.0)
         linear_extrude(h=height) resize([min(max_size, 21.0), 0], auto=true) text("Pangolin", valign="center", halign="center");
       right(-24.0)
         linear_extrude(h=height) resize([min(max_size, 21.0), 0], auto=true) text("Pangolin", valign="center", halign="center");
       right(0.0)
         linear_extrude(h=height) resize([min(max_size, 21.0), 0], auto=true) text("Pangolin", valign="center", halign="center");
       right(24.0)
         linear_extrude(h=height) resize([min(max_size, 21.0), 0], auto=true) text("Pangolin", valign="center", halign="center");
       right(48.0)
         linear_extrude(h=height) resize([min(max_size, 21.0), 0], auto=true) text("Pangolin", valign="center", halign="center");
    }
    back(38.0) right(26.0) {
         linear_extrude(h=height) resize([min(max_size, 46.0), 0], auto=true) text("Cow", valign="center", halign="center");
    }
    back(35.25) right(72.75) {
         linear_extrude(h=height) resize([min(max_size, 41.5), 0], auto=true) text("Eagle", valign="center", halign="center");
    }
    back(37.75) right(114.25) {
         linear_extrude(h=height) resize([min(max_size, 35.5), 0], auto=true) text("Goat", valign="center", halign="center");
    }
    back(25.75) right(151.5) {
         linear_extrude(h=height) resize([0, min(max_size, 45.5)], auto=true) rotate(90) text("Deer", valign="center", halign="center");
    }
    back(93.25) right(26.75) {
         linear_extrude(h=height) resize([min(max_size, 47.5), 0], auto=true) text("Jaguar", valign="center", halign="center");
    }
    back(96.75) right(67.75) {
         linear_extrude(h=height) resize([min(max_size, 28.5), 0], auto=true) text("Peacock", valign="center", halign="center");
    }
    back(95.75) right(99.25) {
         linear_extrude(h=height) resize([min(max_size, 28.5), 0], auto=true) text("Goanna", valign="center", halign="center");
    }
    back(95.25) right(130.25) {
         linear_extrude(h=height) resize([min(max_size, 27.5), 0], auto=true) text("Monkey", valign="center", halign="center");
    }
    back(117.25) right(15.5) {
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Spider Monkey", valign="center", halign="center");
    }
    back(120.75) right(99.25) {
         linear_extrude(h=height) resize([min(max_size, 28.5), 0], auto=true) text("Lemur", valign="center", halign="center");
    }
    back(100.75) right(154.0) {
         linear_extrude(h=height) resize([0, min(max_size, 33.5)], auto=true) rotate(90) text("Beaver", valign="center", halign="center");
    }
    back(117.25) right(40.75) {
         linear_extrude(h=height) resize([0, min(max_size, 23.5)], auto=true) rotate(90) text("Goose", valign="center", halign="center");
    }
    back(118.0) right(126.25) {
         linear_extrude(h=height) resize([min(max_size, 19.5), 0], auto=true) text("Rabbit", valign="center", halign="center");
    }
    back(137.5) right(16.75) {
         linear_extrude(h=height) resize([min(max_size, 27.5), 0], auto=true) text("Tarsier", valign="center", halign="center");
    }
    back(138.5) right(45.25) {
         linear_extrude(h=height) resize([min(max_size, 23.5), 0], auto=true) text("Platypus", valign="center", halign="center");
    }
    back(136.25) right(127.75) {
         linear_extrude(h=height) resize([min(max_size, 22.5), 0], auto=true) text("Quokka", valign="center", halign="center");
    }
    back(118.25) right(66.0) {
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Loon", valign="center", halign="center");
    }
    back(127.75) right(154.75) {
         linear_extrude(h=height) resize([min(max_size, 15.5), 0], auto=true) text("Hoopoe", valign="center", halign="center");
    }
    back(143.25) right(147.5) {
         linear_extrude(h=height) resize([min(max_size, 11.0), 0], auto=true) text("Jay", valign="center", halign="center");
    }
    back(142.75) right(160.75) {
         linear_extrude(h=height) resize([0, min(max_size, 9.5)], auto=true) rotate(90) text("Fly", valign="center", halign="center");
    }
}
