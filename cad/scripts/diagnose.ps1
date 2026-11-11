$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$p=$i.ActiveDocument;$sk=$p.ComponentDefinition.Sketches.Item(1)
foreach($e in $sk.SketchEntities){try{Write-Output ($e.Type.ToString()+' '+$e.StartSketchPoint.Geometry.X+','+$e.StartSketchPoint.Geometry.Y+' to '+$e.EndSketchPoint.Geometry.X+','+$e.EndSketchPoint.Geometry.Y)}catch{}}
$pr=$sk.Profiles.AddForSolid();Write-Output ('paths '+$pr.Count);foreach($path in $pr){Write-Output ('closed '+$path.Closed+' adds '+$path.AddsMaterial+' count '+$path.Count)}
Add-Type -Path 'D:\Inventor\Inventor 2027\Bin\Autodesk.Inventor.Interop.dll'
[Enum]::GetValues([Inventor.PartFeatureOperationEnum]) | ForEach-Object {Write-Output ($_.ToString()+[int]$_)}

