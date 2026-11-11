$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$g=$i.TransientGeometry;$root='C:\Users\Legion\Downloads\Inventor'
$i.SilentOperation=$true; try{$old=$i.Documents.Item("wrench_16mm_engineering.idw");$old.Close($true)}catch{}; $p=$i.Documents.Open("$root\wrench_16mm.ipt",$true)
$d=$i.Documents.Add(12292,'C:\Users\Public\Documents\Autodesk\Inventor 2027\Templates\en-US\Metric\ISO.idw',$true)
$s=$d.ActiveSheet;$s.Size=9996;$s.Orientation=10242
if($s.TitleBlock){$s.TitleBlock.Delete()};if($s.Border){$s.Border.Delete()};$null=$s.AddDefaultBorder()
$d.UnitsOfMeasure.LengthUnits=11269
$v=$s.DrawingViews.AddBaseView($p,$g.CreatePoint2d(15,19),1,10764,32258)
$side=$s.DrawingViews.AddProjectedView($v,$g.CreatePoint2d(15,13.6),32258,1)
$iso=$s.DrawingViews.AddBaseView($p,$g.CreatePoint2d(31.9,12.5),.75,10759,32259)
$d.Update()
function note($x,$y,$t,$size=.32){$s.DrawingNotes.GeneralNotes.AddFitted($g.CreatePoint2d($x,$y),('<StyleOverride FontSize="'+$size+'">'+$t+'</StyleOverride>'))|Out-Null}
note 1.6 27.9 '16 mm COMBINATION WRENCH' .65
note 1.6 26.65 'SIX-POINT RING / 15 deg OPEN JAW / FLAT PATTERN' .36
note 29 27.8 'PART: WR-016-200 | REV A' .4
note 29 26.9 'MATERIAL: AISI 6150 Cr-V STEEL'
note 29 26.3 ('CALCULATED MASS: '+[Math]::Round($p.ComponentDefinition.MassProperties.Mass*1000,1)+' g')
note 29 25.7 'DENSITY: 7850 kg/m^3 (library)'
note 29 25.1 'E: 210 GPa; POISSON RATIO: 0.30*'
note 29 24.5 '*REFERENCE VALUES; NO FEA RATING' .27
note 11.8 16.1 'FRONT / WORKING FACE | 1:1'
note 11.8 12.45 'TOP / EDGE VIEW | 1:1'
note 28.2 5.8 'ISOMETRIC | 3:4'
note 1.6 10.8 'MANUFACTURING / DESIGN REQUIREMENTS' .4
note 1.6 9.9 "1. FORGE AISI 6150; QUENCH AND TEMPER TO 44-48 HRC.`n2. SATIN NICKEL/CHROME PLATE; FINISH OPENINGS AFTER PLATING.`n3. BOTH OPENINGS: 16.10 +0.05/-0.00 A/F, THROUGH.`n4. EDGE BREAK: 0.3 x 45 deg BOTH FACES; REMOVE ALL BURRS.`n5. UNLESS NOTED: LINEAR +/-0.2; ANGLES +/-0.5 deg.`n6. RING OFFSET: 0 deg. OPEN JAW: 15 deg IN PLANE.`n7. NOMINAL CAD DESIGN; STRENGTH / TORQUE NOT VALIDATED." .3
$sk=$s.Sketches.Add();$sk.Edit()
foreach($a in @(@(1,1,41,1),@(1,4,41,4),@(1,1,1,4),@(41,1,41,4),@(24,1,24,4),@(33,1,33,4),@(24,2.5,41,2.5))){$null=$sk.SketchLines.AddByTwoPoints($g.CreatePoint2d($a[0],$a[1]),$g.CreatePoint2d($a[2],$a[3]))};$sk.ExitEdit()
note 1.4 3.65 '16 mm COMBINATION WRENCH' .45
note 1.4 2.75 'WR-016-200 | AISI 6150 | SATIN CHROME'
note 1.4 1.95 'UNITS: mm | THIRD ANGLE | DO NOT SCALE' .3
note 24.4 3.6 '2026-11-07 | REV A'
note 24.4 2.1 'SCALE: AS SHOWN'
note 33.4 3.6 'A3 | SHEET 1 OF 2'
note 33.4 2.1 'DESIGN MODEL' .3
$d.Update();$d.SaveAs("$root\wrench_16mm_engineering.idw",$false)
foreach($view in @($v,$side)){Write-Output ('VIEW '+$view.Name+' width '+$view.Width+' height '+$view.Height);$j=0;foreach($cv in $view.DrawingCurves([Type]::Missing)){$j++;try{Write-Output ('C '+$j+' type '+$cv.CurveType+' '+[Math]::Round($cv.StartPoint.X,4)+','+[Math]::Round($cv.StartPoint.Y,4)+' to '+[Math]::Round($cv.EndPoint.X,4)+','+[Math]::Round($cv.EndPoint.Y,4))}catch{}}}
$i.ActiveView.Fit()


