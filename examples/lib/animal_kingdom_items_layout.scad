module Layout_container0(height) {
    back(73.5) right(49.0) {
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
    back(24.0) right(85.75) {
       cuboid([54.0, 43.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(34.25) right(132.25) {
       cuboid([36.0, 64.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(69.75) right(159.75) {
       back(-48.0)
         cuboid([16.0, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(-24.0)
         cuboid([16.0, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(0.0)
         cuboid([16.0, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(24.0)
         cuboid([16.0, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(48.0)
         cuboid([16.0, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(94.25) right(11.0) {
       back(-40.0)
         cuboid([17.5, 17.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(-20.0)
         cuboid([17.5, 17.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(0.0)
         cuboid([17.5, 17.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(20.0)
         cuboid([17.5, 17.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       back(40.0)
         cuboid([17.5, 17.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(65.5) right(85.25) {
       cuboid([53.0, 36.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(103.5) right(82.5) {
       cuboid([47.5, 36.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(104.75) right(127.75) {
       cuboid([40.0, 39.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(82.25) right(29.25) {
       cuboid([16.0, 85.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(20.25) right(20.75) {
       cuboid([37.0, 36.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(136.0) right(82.25) {
       cuboid([47.0, 25.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(137.75) right(122.25) {
       cuboid([29.0, 24.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(75.75) right(131.75) {
       cuboid([35.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(134.25) right(29.75) {
       cuboid([17.0, 16.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(132.0) right(144.25) {
       cuboid([12.0, 12.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(144.25) right(157.25) {
       cuboid([11.0, 11.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
}
module Layout_Text_container0(height, max_size=15) {
    back(73.5) right(49.0) {
       back(-35.0)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara 2", valign="center", halign="center");
       back(0.0)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara 2", valign="center", halign="center");
       back(35.0)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara 2", valign="center", halign="center");
    }
    back(24.0) right(85.75) {
         linear_extrude(h=height) resize([min(max_size, 52.5), 0], auto=true) text("Elephant", valign="center", halign="center");
    }
    back(34.25) right(132.25) {
         linear_extrude(h=height) resize([0, min(max_size, 62.5)], auto=true) rotate(90) text("Rhino", valign="center", halign="center");
    }
    back(69.75) right(159.75) {
       back(-48.0)
         linear_extrude(h=height) resize([0, min(max_size, 21.0)], auto=true) rotate(90) text("Pangolin", valign="center", halign="center");
       back(-24.0)
         linear_extrude(h=height) resize([0, min(max_size, 21.0)], auto=true) rotate(90) text("Pangolin", valign="center", halign="center");
       back(0.0)
         linear_extrude(h=height) resize([0, min(max_size, 21.0)], auto=true) rotate(90) text("Pangolin", valign="center", halign="center");
       back(24.0)
         linear_extrude(h=height) resize([0, min(max_size, 21.0)], auto=true) rotate(90) text("Pangolin", valign="center", halign="center");
       back(48.0)
         linear_extrude(h=height) resize([0, min(max_size, 21.0)], auto=true) rotate(90) text("Pangolin", valign="center", halign="center");
    }
    back(94.25) right(11.0) {
       back(-40.0)
         linear_extrude(h=height) resize([0, min(max_size, 17.0)], auto=true) rotate(90) text("Gopher", valign="center", halign="center");
       back(-20.0)
         linear_extrude(h=height) resize([0, min(max_size, 17.0)], auto=true) rotate(90) text("Gopher", valign="center", halign="center");
       back(0.0)
         linear_extrude(h=height) resize([0, min(max_size, 17.0)], auto=true) rotate(90) text("Gopher", valign="center", halign="center");
       back(20.0)
         linear_extrude(h=height) resize([0, min(max_size, 17.0)], auto=true) rotate(90) text("Gopher", valign="center", halign="center");
       back(40.0)
         linear_extrude(h=height) resize([0, min(max_size, 17.0)], auto=true) rotate(90) text("Gopher", valign="center", halign="center");
    }
    back(65.5) right(85.25) {
         linear_extrude(h=height) resize([min(max_size, 51.5), 0], auto=true) text("Polar Bear", valign="center", halign="center");
    }
    back(103.5) right(82.5) {
         linear_extrude(h=height) resize([min(max_size, 46.0), 0], auto=true) text("Cow", valign="center", halign="center");
    }
    back(104.75) right(127.75) {
         linear_extrude(h=height) resize([min(max_size, 38.5), 0], auto=true) text("Ornyx", valign="center", halign="center");
    }
    back(82.25) right(29.25) {
         linear_extrude(h=height) resize([0, min(max_size, 83.5)], auto=true) rotate(90) text("Crocodile", valign="center", halign="center");
    }
    back(20.25) right(20.75) {
         linear_extrude(h=height) resize([min(max_size, 35.5), 0], auto=true) text("Goat", valign="center", halign="center");
    }
    back(136.0) right(82.25) {
         linear_extrude(h=height) resize([min(max_size, 45.5), 0], auto=true) text("Deer", valign="center", halign="center");
    }
    back(137.75) right(122.25) {
         linear_extrude(h=height) resize([min(max_size, 27.5), 0], auto=true) text("Monkey", valign="center", halign="center");
    }
    back(75.75) right(131.75) {
         linear_extrude(h=height) resize([min(max_size, 33.5), 0], auto=true) text("Fox", valign="center", halign="center");
    }
    back(134.25) right(29.75) {
         linear_extrude(h=height) resize([min(max_size, 15.5), 0], auto=true) text("Hoopoe", valign="center", halign="center");
    }
    back(132.0) right(144.25) {
         linear_extrude(h=height) resize([0, min(max_size, 11.0)], auto=true) rotate(90) text("Jay", valign="center", halign="center");
    }
    back(144.25) right(157.25) {
         linear_extrude(h=height) resize([0, min(max_size, 9.5)], auto=true) rotate(90) text("Fly", valign="center", halign="center");
    }
}
module Layout_container1(height) {
    back(14.25) right(82.75) {
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
    back(83.0) right(138.0) {
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
    back(46.25) right(21.75) {
       cuboid([39.0, 37.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(45.25) right(63.25) {
       cuboid([41.0, 35.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(43.25) right(106.75) {
       cuboid([43.0, 31.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(52.25) right(157.75) {
       cuboid([20.0, 49.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(72.25) right(40.5) {
       right(-30.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(-15.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(0.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(15.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
       right(30.0)
         cuboid([12.0, 12.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(76.5) right(97.75) {
       cuboid([35.0, 24.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(93.25) right(17.25) {
       cuboid([30.0, 27.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(92.25) right(48.75) {
       cuboid([30.0, 25.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(120.75) right(15.5) {
       cuboid([26.5, 25.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(119.25) right(45.25) {
       cuboid([30.0, 22.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(99.0) right(154.75) {
       cuboid([14.0, 41.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(139.5) right(71.75) {
       cuboid([35.0, 15.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(100.75) right(92.75) {
       cuboid([25.0, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(131.75) right(157.0) {
       cuboid([18.5, 21.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(94.25) right(71.5) {
       cuboid([12.5, 29.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(142.0) right(14.75) {
       cuboid([25.0, 14.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(142.25) right(40.75) {
       cuboid([24.0, 15.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(103.5) right(113.25) {
       cuboid([13.0, 26.5, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
    back(119.75) right(69.25) {
       cuboid([15.0, 14.0, height],
        rounding=1,
        edges=[FRONT+LEFT, FRONT+RIGHT, BACK+LEFT, BACK+RIGHT],
        anchor=BOTTOM);
    }
}
module Layout_Text_container1(height, max_size=15) {
    back(14.25) right(82.75) {
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
    back(83.0) right(138.0) {
       back(-17.5)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara", valign="center", halign="center");
       back(17.5)
         linear_extrude(h=height) resize([0, min(max_size, 32.0)], auto=true) rotate(90) text("Capybara", valign="center", halign="center");
    }
    back(46.25) right(21.75) {
         linear_extrude(h=height) resize([min(max_size, 37.5), 0], auto=true) text("Kangaroo", valign="center", halign="center");
    }
    back(45.25) right(63.25) {
         linear_extrude(h=height) resize([min(max_size, 39.5), 0], auto=true) text("Gazelle", valign="center", halign="center");
    }
    back(43.25) right(106.75) {
         linear_extrude(h=height) resize([min(max_size, 41.5), 0], auto=true) text("Eagle", valign="center", halign="center");
    }
    back(52.25) right(157.75) {
         linear_extrude(h=height) resize([0, min(max_size, 47.5)], auto=true) rotate(90) text("Jaguar", valign="center", halign="center");
    }
    back(72.25) right(40.5) {
       right(-30.0)
         linear_extrude(h=height) resize([min(max_size, 12.0), 0], auto=true) text("Termite", valign="center", halign="center");
       right(-15.0)
         linear_extrude(h=height) resize([min(max_size, 12.0), 0], auto=true) text("Termite", valign="center", halign="center");
       right(0.0)
         linear_extrude(h=height) resize([min(max_size, 12.0), 0], auto=true) text("Termite", valign="center", halign="center");
       right(15.0)
         linear_extrude(h=height) resize([min(max_size, 12.0), 0], auto=true) text("Termite", valign="center", halign="center");
       right(30.0)
         linear_extrude(h=height) resize([min(max_size, 12.0), 0], auto=true) text("Termite", valign="center", halign="center");
    }
    back(76.5) right(97.75) {
         linear_extrude(h=height) resize([min(max_size, 33.5), 0], auto=true) text("Pig", valign="center", halign="center");
    }
    back(93.25) right(17.25) {
         linear_extrude(h=height) resize([min(max_size, 28.5), 0], auto=true) text("Peacock", valign="center", halign="center");
    }
    back(92.25) right(48.75) {
         linear_extrude(h=height) resize([min(max_size, 28.5), 0], auto=true) text("Goanna", valign="center", halign="center");
    }
    back(120.75) right(15.5) {
         linear_extrude(h=height) resize([min(max_size, 25.0), 0], auto=true) text("Spider Monkey", valign="center", halign="center");
    }
    back(119.25) right(45.25) {
         linear_extrude(h=height) resize([min(max_size, 28.5), 0], auto=true) text("Lemur", valign="center", halign="center");
    }
    back(99.0) right(154.75) {
         linear_extrude(h=height) resize([0, min(max_size, 40.0)], auto=true) rotate(90) text("Snake", valign="center", halign="center");
    }
    back(139.5) right(71.75) {
         linear_extrude(h=height) resize([min(max_size, 33.5), 0], auto=true) text("Beaver", valign="center", halign="center");
    }
    back(100.75) right(92.75) {
         linear_extrude(h=height) resize([min(max_size, 23.5), 0], auto=true) text("Goose", valign="center", halign="center");
    }
    back(131.75) right(157.0) {
         linear_extrude(h=height) resize([0, min(max_size, 19.5)], auto=true) rotate(90) text("Rabbit", valign="center", halign="center");
    }
    back(94.25) right(71.5) {
         linear_extrude(h=height) resize([0, min(max_size, 27.5)], auto=true) rotate(90) text("Tarsier", valign="center", halign="center");
    }
    back(142.0) right(14.75) {
         linear_extrude(h=height) resize([min(max_size, 23.5), 0], auto=true) text("Platypus", valign="center", halign="center");
    }
    back(142.25) right(40.75) {
         linear_extrude(h=height) resize([min(max_size, 22.5), 0], auto=true) text("Quokka", valign="center", halign="center");
    }
    back(103.5) right(113.25) {
         linear_extrude(h=height) resize([0, min(max_size, 25.0)], auto=true) rotate(90) text("Loon", valign="center", halign="center");
    }
    back(119.75) right(69.25) {
         linear_extrude(h=height) resize([min(max_size, 13.5), 0], auto=true) text("Chipmunk", valign="center", halign="center");
    }
}
