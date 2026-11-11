$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$i.SilentOperation=$true;$g=$i.TransientGeometry
$p=$i.Documents.Open('C:\Users\Legion\Downloads\Inventor\wrench_16mm.ipt',$true);$c=$p.ComponentDefinition
if($c.Features.ChamferFeatures.Count){$c.Features.ChamferFeatures.Item(1).Delete()};if($c.Features.FilletFeatures.Count){$c.Features.FilletFeatures.Item(1).Delete()};if($c.Features.ExtrudeFeatures.Count -gt 2){$c.Features.ExtrudeFeatures.Item(3).Delete()}
function pt([double]$x,[double]$y){$g.CreatePoint2d($x/10,$y/10)}
function jawpt([double]$x,[double]$y){$angle=15*[Math]::PI/180;pt (183+$x*[Math]::Cos($angle)-$y*[Math]::Sin($angle)) ($x*[Math]::Sin($angle)+$y*[Math]::Cos($angle))}
$sk=$c.Sketches.Add($c.WorkPlanes.Item(3));$sk.Name='Open jaw - 16.10 mm at 15 deg'
$l=$sk.SketchLines.AddByTwoPoints((jawpt -3 -8.05),(jawpt 40 -8.05));$l2=$sk.SketchLines.AddByTwoPoints($l.EndSketchPoint,(jawpt 40 8.05));$l3=$sk.SketchLines.AddByTwoPoints($l2.EndSketchPoint,(jawpt -3 8.05))
$null=$sk.SketchArcs.AddByThreePoints($l3.EndSketchPoint,(jawpt -11.05 0),$l.StartSketchPoint)
foreach($ln in $sk.SketchLines){$null=$sk.GeometricConstraints.AddGround($ln)};foreach($a in $sk.SketchArcs){$null=$sk.GeometricConstraints.AddGround($a)}
$cut=$c.Features.ExtrudeFeatures.AddByDistanceExtent($sk.Profiles.AddForSolid(),'Thickness',20993,20482,0);$cut.Name='Milled open jaw - 15 deg'
$edges=$i.TransientObjects.CreateEdgeCollection()
foreach($e in $c.SurfaceBodies.Item(1).Edges){if($e.GeometryType -eq 5123 -and [Math]::Abs($e.StartVertex.Point.Z-$e.StopVertex.Point.Z) -gt .64 -and (([Math]::Abs($e.StartVertex.Point.X-3.7) -lt .001) -or ([Math]::Abs($e.StartVertex.Point.X-16) -lt .001))){$edges.Add($e)}}
$f=$c.Features.FilletFeatures.AddSimple($edges,'3 mm',$false,$false,$false,$false,$true,$false);$f.Name='Shoulder transition R3'
$edges=$i.TransientObjects.CreateEdgeCollection();foreach($e in $c.SurfaceBodies.Item(1).Edges){if([Math]::Abs($e.StartVertex.Point.Z-$e.StopVertex.Point.Z) -lt .00001){$edges.Add($e)}}
$ch=$c.Features.ChamferFeatures.AddUsingDistance($edges,'0.3 mm',$true,$true,$false);$ch.Name='Edge break - 0.3 x 45 deg'
$p.Update2($true)|Out-Null;$p.Save();Write-Output ('Mass kg '+$c.MassProperties.Mass)
foreach($ln in $sk.SketchLines){Write-Output ($ln.StartSketchPoint.Geometry.X.ToString()+','+$ln.StartSketchPoint.Geometry.Y+' -> '+$ln.EndSketchPoint.Geometry.X+','+$ln.EndSketchPoint.Geometry.Y)}

