$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application')
$root='C:\Users\Legion\Downloads\Inventor';$g=$i.TransientGeometry
$p=$i.Documents.Add(12290,'C:\Users\Public\Documents\Autodesk\Inventor 2027\Templates\en-US\Metric\Standard (mm).ipt',$true)
$p.UnitsOfMeasure.LengthUnits=11269
$c=$p.ComponentDefinition
function pt($x,$y){$g.CreatePoint2d($x/10,$y/10)}
function line($sk,$x1,$y1,$x2,$y2){$sk.SketchLines.AddByTwoPoints((pt $x1 $y1),(pt $x2 $y2))}
$sk=$c.Sketches.Add($c.WorkPlanes.Item(3));$sk.Name='Forging outline - 200 x 34 mm'
$arc=$sk.SketchArcs.AddByThreePoints((pt 14 14),(pt 0 0),(pt 14 -14))
$l=$sk.SketchLines.AddByTwoPoints($arc.EndSketchPoint,(pt 37 -7))
$l=$sk.SketchLines.AddByTwoPoints($l.EndSketchPoint,(pt 160 -7))
$l=$sk.SketchLines.AddByTwoPoints($l.EndSketchPoint,(pt 175 -15))
$arc2=$sk.SketchArcs.AddByThreePoints($l.EndSketchPoint,(pt 200 0),(pt 175 15))
$l=$sk.SketchLines.AddByTwoPoints($arc2.EndSketchPoint,(pt 160 7))
$l=$sk.SketchLines.AddByTwoPoints($l.EndSketchPoint,(pt 37 7))
$l=$sk.SketchLines.AddByTwoPoints($l.EndSketchPoint,$arc.StartSketchPoint)
foreach($ln in $sk.SketchLines){$null=$sk.GeometricConstraints.AddGround($ln)}
foreach($a in $sk.SketchArcs){$null=$sk.GeometricConstraints.AddGround($a)}
$ex=$c.Features.ExtrudeFeatures.AddByDistanceExtent($sk.Profiles.AddForSolid(),'6.5 mm',20993,20481,0);$ex.Name='Forged blank - thickness'
$ex.Extent.Distance.Name='Thickness'
# Radius the vertical shoulder edges before machining the openings.
$edges=$i.TransientObjects.CreateEdgeCollection()
foreach($e in $c.SurfaceBodies.Item(1).Edges){if($e.GeometryType -eq 5123 -and [Math]::Abs($e.StartVertex.Point.Z-$e.StopVertex.Point.Z) -gt .64){$edges.Add($e)}}
try{$f=$c.Features.FilletFeatures.AddSimple($edges,'3 mm');$f.Name='Forged shoulder blends R3'}catch{Write-Output ('Shoulder fillet omitted: '+$_.Exception.Message)}
$sk=$c.Sketches.Add($c.WorkPlanes.Item(3));$sk.Name='16.10 AF six-point ring'
$r=16.1/[Math]::Sqrt(3);$pts=@()
for($j=0;$j -lt 6;$j++){$a=$j*[Math]::PI/3;$pts+=,(pt (14+$r*[Math]::Cos($a)) ($r*[Math]::Sin($a)))}
$first=$sk.SketchLines.AddByTwoPoints($pts[0],$pts[1]);$prev=$first
for($j=1;$j -lt 6;$j++){if($j -eq 5){$end=$first.StartSketchPoint}else{$end=$pts[$j+1]};$prev=$sk.SketchLines.AddByTwoPoints($prev.EndSketchPoint,$end)}
foreach($ln in $sk.SketchLines){$null=$sk.GeometricConstraints.AddGround($ln)}
$cut=$c.Features.ExtrudeFeatures.AddByDistanceExtent($sk.Profiles.AddForSolid(),'Thickness',20993,20482,0);$cut.Name='Broached ring - 16.10 AF'
$sk=$c.Sketches.Add($c.WorkPlanes.Item(3));$sk.Name='Open jaw - 16.10 mm at 15 deg'
function jawpt([double]$x,[double]$y){$a=15*[Math]::PI/180;pt (183+$x*[Math]::Cos($a)-$y*[Math]::Sin($a)) ($x*[Math]::Sin($a)+$y*[Math]::Cos($a))}
$a=jawpt -3 -8.05;$b=jawpt 40 -8.05;$cc=jawpt 40 8.05;$dd=jawpt -3 8.05
$l=$sk.SketchLines.AddByTwoPoints($a,$b);$l2=$sk.SketchLines.AddByTwoPoints($l.EndSketchPoint,$cc);$l3=$sk.SketchLines.AddByTwoPoints($l2.EndSketchPoint,$dd)
$null=$sk.SketchArcs.AddByThreePoints($l3.EndSketchPoint,(jawpt -11.05 0),$l.StartSketchPoint)
foreach($ln in $sk.SketchLines){$null=$sk.GeometricConstraints.AddGround($ln)}
foreach($a in $sk.SketchArcs){$null=$sk.GeometricConstraints.AddGround($a)}
$cut=$c.Features.ExtrudeFeatures.AddByDistanceExtent($sk.Profiles.AddForSolid(),'Thickness',20993,20482,0);$cut.Name='Milled open jaw - 15 deg'
$edges=$i.TransientObjects.CreateEdgeCollection()
foreach($e in $c.SurfaceBodies.Item(1).Edges){if([Math]::Abs($e.StartVertex.Point.Z-$e.StopVertex.Point.Z) -lt .00001){$edges.Add($e)}}
try{$ch=$c.Features.ChamferFeatures.AddUsingDistance($edges,'0.3 mm',$true,$true,$false);$ch.Name='Edge break - 0.3 x 45 deg'}catch{Write-Output ('Chamfer omitted: '+$_.Exception.Message)}
$mat=$i.AssetLibraries.Item('Autodesk Material Library').MaterialAssets.Item('Steel AISI 6150').CopyTo($p)
$p.ActiveMaterial=$mat
foreach($v in $mat){try{Write-Output ('MAT '+$v.Name+' = '+$v.Value)}catch{}}
$props=$p.PropertySets.Item('Design Tracking Properties');$props.Item('Part Number').Value='WR-016-200';$props.Item('Description').Value='16 mm flat combination wrench - six-point ring / 15 deg open jaw'
$custom=$p.PropertySets.Item('Inventor User Defined Properties')
$meta=@{'Material specification'='AISI 6150 chromium-vanadium steel';'Heat treatment'='Quench and temper; target 44-48 HRC (design requirement)';'Finish'='Satin nickel/chrome plate; openings sized after plating';'Nominal wrench size'='16 mm';'Opening limits'='16.10 +0.05/-0.00 mm, both ends';'Design status'='Nominal flat-pattern design; no standard certification or torque rating';'Process'='Drop forge, heat treat, machine / broach, deburr, plate';'Jaw angle'='15 deg in plane; ring offset 0 deg';'General tolerance'='Linear +/-0.2 mm; angles +/-0.5 deg unless noted';'Density reference'='7850 kg/m^3';'Elastic modulus reference'='210 GPa';'Poisson ratio reference'='0.30'}
foreach($k in $meta.Keys){$null=$custom.Add($meta[$k],$k)}
$p.Update2($true)|Out-Null
if($c.SurfaceBodies.Count -ne 1 -or !$c.SurfaceBodies.Item(1).IsSolid){throw 'Wrench must be one solid'}
$p.SaveAs("$root\wrench_16mm.ipt",$false)
$cam=$i.ActiveView.Camera;$cam.ViewOrientationType=10759;$cam.Apply();$i.ActiveView.Fit();$p.Save()
Write-Output ('WRENCH mass kg '+$c.MassProperties.Mass+' volume cm3 '+$c.MassProperties.Volume)
# Correct the existing bolt's unassigned generic material.
$bolt=$i.Documents.Open("$root\bolt.ipt",$false)
$bm=$i.AssetLibraries.Item('Inventor Material Library').MaterialAssets.Item('Steel, Carbon').CopyTo($bolt)
$bolt.ActiveMaterial=$bm
$bp=$bolt.PropertySets.Item('Inventor User Defined Properties')
foreach($pair in @(@('Strength requirement','ISO 898-1 property class 8.8; design designation, not certified'),@('Material specification','Carbon steel, quenched and tempered to property class 8.8'),@('Compatible wrench','16 mm nominal across flats'),@('Thread specification','M10 x 1.5 - 6g RH; full thread, 30 mm under head'))){try{$bp.Item($pair[0]).Value=$pair[1]}catch{$null=$bp.Add($pair[1],$pair[0])}}
$bolt.Update2($true)|Out-Null;$bolt.Save()
Write-Output ('BOLT material '+$bolt.ActiveMaterial.DisplayName)

