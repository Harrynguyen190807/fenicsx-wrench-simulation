$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$p=$i.Documents.Open('C:\Users\Legion\Downloads\Inventor\wrench_16mm.ipt',$true);$c=$p.ComponentDefinition
# Suppress the edge break, round each shoulder, then restore the edge break.
$c.Features.ChamferFeatures.Item(1).Delete()
$edges=$i.TransientObjects.CreateEdgeCollection()
foreach($e in $c.SurfaceBodies.Item(1).Edges){if($e.GeometryType -eq 5123 -and [Math]::Abs($e.StartVertex.Point.Z-$e.StopVertex.Point.Z) -gt .64 -and (([Math]::Abs($e.StartVertex.Point.X-3.7) -lt .001) -or ([Math]::Abs($e.StartVertex.Point.X-16) -lt .001))){$edges.Add($e)}}
Write-Output ('Shoulder edge count '+$edges.Count)
try{$f=$c.Features.FilletFeatures.AddSimple($edges,'3 mm',$false,$false,$false,$false,$true,$false);$f.Name='Shoulder transition R3'}catch{Write-Output $_.Exception.Message}
$edges=$i.TransientObjects.CreateEdgeCollection(); foreach($e in $c.SurfaceBodies.Item(1).Edges){if([Math]::Abs($e.StartVertex.Point.Z-$e.StopVertex.Point.Z) -lt .00001){$edges.Add($e)}}; $ch=$c.Features.ChamferFeatures.AddUsingDistance($edges,'0.3 mm',$true,$true,$false);$ch.Name='Edge break - 0.3 x 45 deg'
$p.Update2($true)|Out-Null;$p.Save();$i.ActiveView.Fit()
foreach($f in $c.Features){Write-Output ($f.Name+' health '+$f.HealthStatus)}

