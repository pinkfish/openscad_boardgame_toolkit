# BoardGame Insert Cheat Sheet

## LibFile: boardgame\_toolkit.scad

### Section: 

Constants: [`m_piece_wiggle_room`](boardgame_toolkit.scad#constant-m_piece_wiggle_room)

### Section: Components

><code>RoundedBoxOnLength(100, 50, 10, 5);</code>  

><code>[RoundedBoxAllSides](boardgame_toolkit.scad#module-roundedboxallsides)(30,20,10,5);</code>  

><code>[RoundedBoxGrid](boardgame_toolkit.scad#module-roundedboxgrid)(20,20,10,5, rows=2, cols=1);</code>  

><code>[RegularPolygon](boardgame_toolkit.scad#module-regularpolygon)(10, 5, 6);</code>  

><code>[RegularPolygonGrid](boardgame_toolkit.scad#module-regularpolygongrid)(10, 2, 1, 2)</code>  

><code>[RegularPolygonGridDense](boardgame_toolkit.scad#module-regularpolygongriddense)(10, 2, 1)</code>  

><code>[HexGridWithCutouts](boardgame_toolkit.scad#module-hexgridwithcutouts)(rows = 4, cols = 3, height = 10, spacing = 0, push\_block\_height = 1, tile\_width = 29);</code>  


### Section: Labels

><code>[MakeStripedGrid](boardgame_toolkit.scad#module-makestripedgrid)(20,50);</code>  

><code>[MakeStripedLidLabel](boardgame_toolkit.scad#module-makestripedlidlabel)(20, 80, 2, label="Australia", border = 2, offset = 4);</code>  


### Section: Lid

><code>[LidMeshHex](boardgame_toolkit.scad#module-lidmeshhex)(width = 70, length = 50, lid\_height = 3, boundary = 10, radius = 5, shape\_thickness = 2);</code>  

><code>[LidMeshRepeating](boardgame_toolkit.scad#module-lidmeshrepeating)(50, 20, 3, 5, 10);</code>  

><code>[SlidingLidFingernail](boardgame_toolkit.scad#module-slidinglidfingernail)(radius = 10, lid\_height = 3);</code>  

><code>[MakeLidTab](boardgame_toolkit.scad#module-makelidtab)(5, 10, 2);</code>  

><code>[MakeTabs](boardgame_toolkit.scad#module-maketabs)(50, 100, wall\_thickness = 2, lid\_height = 2);</code>  


### Section: SlidingBox

><code>[SlidingLid](boardgame_toolkit.scad#module-slidinglid)(width=10, length=30, lid\_height=3, wall\_thickness = 2, lid\_size\_spacing = 0.2);</code>  

><code>[SlidingBoxLidWithLabel](boardgame_toolkit.scad#module-slidingboxlidwithlabel)(</code>  
><code>    width = 100, length = 100, lid\_height = 3, text\_width = 60,</code>  
><code>    text\_length = 30, text\_str = "Trains", label\_rotated = false);</code>  

><code>[MakeHexBoxWithSlidingLid](boardgame_toolkit.scad#module-makehexboxwithslidinglid)(5, 7, 19, 1, 29);</code>  

><code>[MakeBoxWithSlidingLid](boardgame_toolkit.scad#module-makeboxwithslidinglid)(50,100,20);</code>  


### Section: TabbedBox

><code>[MakeInsetLid](boardgame_toolkit.scad#module-makeinsetlid)(50, 100);</code>  

><code>[MakeBoxWithTabsInsetLid](boardgame_toolkit.scad#module-makeboxwithtabsinsetlid)(width = 30, length = 100, height = 20);</code>  

><code>[MakeHexBoxWithTabsInsetLid](boardgame_toolkit.scad#module-makehexboxwithtabsinsetlid)(rows = 4, cols = 3, height = 15, push\_block\_height = 1, tile\_width = 29);</code>  


