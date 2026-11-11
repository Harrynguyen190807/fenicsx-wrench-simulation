$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$p=$i.Documents.Open('C:\Users\Legion\Downloads\Inventor\wrench_16mm.ipt',$false)
$sk=$p.ComponentDefinition.Sketches.Item(3)
foreach($l in $sk.SketchLines){Write-Output ($l.StartSketchPoint.Geometry.X.ToString()+','+$l.StartSketchPoint.Geometry.Y+' -> '+$l.EndSketchPoint.Geometry.X+','+$l.EndSketchPoint.Geometry.Y)}
foreach($c in $sk.GeometricConstraints){Write-Output ('constraint '+$c.Type)}
$g=$i.TransientGeometry
function pt($x,$y){$g.CreatePoint2d($x/10,$y/10)}
function jawpt($x,$y){$a=15*[Math]::PI/180;pt (183+$x*[Math]::Cos($a)-$y*[Math]::Sin($a)) ($x*[Math]::Sin($a)+$y*[Math]::Cos($a))}
$a=jawpt -3 -8.05;Write-Output ('expected '+$a.X+','+$a.Y)
