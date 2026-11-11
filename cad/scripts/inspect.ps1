$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application')
$i.SoftwareVersion.DisplayVersion
foreach($d in $i.Documents){ Write-Output $d.FullFileName; Write-Output ('Features: '+$d.ComponentDefinition.Features.Count) }
$d=$i.ActiveDocument
foreach($e in $d.ComponentDefinition.SurfaceBodies.Item(1).Edges){Write-Output ('Edge '+$e.GeometryType+' start '+$e.StartVertex.Point.X+','+$e.StartVertex.Point.Y+','+$e.StartVertex.Point.Z+' end '+$e.StopVertex.Point.X+','+$e.StopVertex.Point.Y+','+$e.StopVertex.Point.Z)}
