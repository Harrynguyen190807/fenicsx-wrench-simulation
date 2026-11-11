$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application')
$root='C:\Users\Legion\Downloads\Inventor';$g=$i.TransientGeometry
$p=$i.Documents.Open("$root\bolt.ipt",$true)
$cam=$i.ActiveView.Camera;$cam.ViewOrientationType=10759;$cam.Apply();$i.ActiveView.Fit();$p.Save()
$d=$i.Documents.Add(12292,'C:\Users\Public\Documents\Autodesk\Inventor 2027\Templates\en-US\Metric\ISO.idw',$true)
$s=$d.ActiveSheet;$s.Size=9997;$s.Orientation=10242
if($s.TitleBlock){$s.TitleBlock.Delete()}
if($s.Border){$s.Border.Delete()}
$s.AddDefaultBorder()|Out-Null
$d.UnitsOfMeasure.LengthUnits=11269
$front=$s.DrawingViews.AddBaseView($p,$g.CreatePoint2d(9,10.8),2,10764,32258)
$top=$s.DrawingViews.AddProjectedView($front,$g.CreatePoint2d(9,17),32258,2)
$iso=$s.DrawingViews.AddBaseView($p,$g.CreatePoint2d(21.8,13.4),2,10759,32259)
$d.Update()
function note($x,$y,$t){$s.DrawingNotes.GeneralNotes.AddFitted($g.CreatePoint2d($x,$y),$t)|Out-Null}
note 1.6 19.3 '<StyleOverride FontSize="0.5">HEXAGON HEAD SCREW</StyleOverride>'
note 1.6 18.5 'M10 x 30 | ISO 4017 nominal form'
note 1.6 5.8 "THREAD: M10 x 1.5 - 6g, RIGHT HAND`nFULL THREAD; RUNOUT AT HEAD PER ISO 4017.`nPROPERTY CLASS: 8.8 PER ISO 898-1.`nREMOVE BURRS AND SHARP EDGES."
note 18.3 7.8 'ISOMETRIC | 2:1'
note 7.1 6.6 'FRONT VIEW | 2:1'
note 11.4 17.7 'END VIEW'
$sk=$s.Sketches.Add();$sk.Edit()
foreach($a in @(@(1,1,28.7,1),@(1,3.6,28.7,3.6),@(1,1,1,3.6),@(28.7,1,28.7,3.6),@(17,1,17,3.6),@(23,1,23,2.3),@(17,2.3,28.7,2.3))){$sk.SketchLines.AddByTwoPoints($g.CreatePoint2d($a[0],$a[1]),$g.CreatePoint2d($a[2],$a[3]))|Out-Null};$sk.ExitEdit()
note 1.4 3.25 '<StyleOverride FontSize="0.4">HEX BOLT - M10 x 30</StyleOverride>'
note 1.4 2.5 'DESIGNATION: ISO 4017 - M10 x 30 - 8.8'
note 1.4 1.8 'UNITS: mm | NOMINAL DIMENSIONS | THIRD ANGLE'
note 17.4 3.2 'DRAWING: BOLT-M10-030'
note 17.4 2.7 'DATE: 2026-11-07'
note 17.4 1.9 'SCALE 2:1'
note 23.4 1.9 'A4 | REV A | 1 OF 1'
$d.Update();$d.SaveAs("$root\bolt_drawing.idw",$false)
foreach($v in @($front,$top)){Write-Output ('VIEW '+$v.Name+' '+$v.Position.X+','+$v.Position.Y);$n=0;foreach($cv in $v.DrawingCurves){$n++;try{Write-Output ('C '+$n+' '+$cv.CurveType+' '+$cv.StartPoint.X+','+$cv.StartPoint.Y+' to '+$cv.EndPoint.X+','+$cv.EndPoint.Y)}catch{}}}
$i.ActiveView.Fit()
