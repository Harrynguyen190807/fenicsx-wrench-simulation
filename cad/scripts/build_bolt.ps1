$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application')
$root='C:\Users\Legion\Downloads\Inventor'
$p=$i.Documents.Open("$root\bolt.ipt",$true)
if($p.ComponentDefinition.Features.Count -ne 0){$p.Close($true);$p=$i.Documents.Open("$root\bolt.ipt",$true)}
Copy-Item -LiteralPath "$root\bolt.ipt" -Destination "$root\bolt_original.ipt" -Force
$c=$p.ComponentDefinition; $g=$i.TransientGeometry
while($c.Sketches.Count -gt 0){$c.Sketches.Item(1).Delete()}
$p.UnitsOfMeasure.LengthUnits=11269
$sk=$c.Sketches.Add($c.WorkPlanes.Item(3)); $sk.Name='Hexagon - 16 mm across flats'
$pts=@(); $r=1.6/[Math]::Sqrt(3)
for($j=0;$j -lt 6;$j++){ $a=$j*[Math]::PI/3; $pts+=,$g.CreatePoint2d($r*[Math]::Cos($a),$r*[Math]::Sin($a)) }
$first=$sk.SketchLines.AddByTwoPoints($pts[0],$pts[1]);$prev=$first
for($j=1;$j -lt 5;$j++){ $prev=$sk.SketchLines.AddByTwoPoints($prev.EndSketchPoint,$pts[$j+1]) }
$null=$sk.SketchLines.AddByTwoPoints($prev.EndSketchPoint,$first.StartSketchPoint)
foreach($ln in $sk.SketchLines){$null=$sk.GeometricConstraints.AddGround($ln)}
$hd=$c.Features.ExtrudeFeatures.AddByDistanceExtent($sk.Profiles.AddForSolid(), '6.4 mm',20993,20481,0); $hd.Name='Hex head - 6.4 mm'
$ss=$c.Sketches.Add($c.WorkPlanes.Item(3)); $ss.Name='M10 blank'
$ci=$ss.SketchCircles.AddByCenterRadius($g.CreatePoint2d(0,0),0.5)
$null=$ss.GeometricConstraints.AddGround($ci)
$sh=$c.Features.ExtrudeFeatures.AddByDistanceExtent($ss.Profiles.AddForSolid(),'30 mm',20994,20481,0); $sh.Name='Bolt length - 30 mm under head'
$edges=$i.TransientObjects.CreateEdgeCollection()
foreach($e in $c.SurfaceBodies.Item(1).Edges){ if([Math]::Abs($e.StartVertex.Point.Z-0.64) -lt 0.00001 -and [Math]::Abs($e.StopVertex.Point.Z-0.64) -lt 0.00001){$edges.Add($e)} }
$ch=$c.Features.ChamferFeatures.AddUsingDistance($edges,'0.8 mm',$true,$true,$false);$ch.Name='Head edge chamfer'
$tip=$i.TransientObjects.CreateEdgeCollection()
foreach($e in $c.SurfaceBodies.Item(1).Edges){if($e.GeometryType -eq 5124 -and [Math]::Abs($e.Geometry.Center.Z+3) -lt .00001){$tip.Add($e)}}
if($tip.Count -eq 0){throw 'Tip edge not found'}
$ch2=$c.Features.ChamferFeatures.AddUsingDistance($tip,'1 mm',$true,$true,$false);$ch2.Name='Thread lead-in - 1 x 45 deg'
$cyl=$null
foreach($f in $c.SurfaceBodies.Item(1).Faces){if($f.SurfaceType -eq 5891){$cyl=$f;break}}
if(!$cyl){throw 'Cylinder not found'}
$ti=$c.Features.ThreadFeatures.CreateStandardThreadInfo($false,$true,'ISO Metric profile','M10x1.5','6g')
$th=$c.Features.ThreadFeatures.Add($cyl,$cyl.Edges.Item(1),$ti,$false,$true);$th.Name='M10 x 1.5 - 6g RH full thread'
$p.PropertySets.Item('Design Tracking Properties').Item('Part Number').Value='ISO 4017 - M10 x 30'
$p.PropertySets.Item('Design Tracking Properties').Item('Description').Value='Hexagon head screw M10 x 30 - 1.5 pitch - class 8.8'
try{$p.ActiveMaterial=$p.MaterialAssets.Item('Steel')}catch{}
$p.Update2($true)|Out-Null
$i.ActiveView.GoHome();$i.ActiveView.Fit()
$p.Save()
Write-Output ('Saved bolt, volume cm3: '+$c.MassProperties.Volume)
