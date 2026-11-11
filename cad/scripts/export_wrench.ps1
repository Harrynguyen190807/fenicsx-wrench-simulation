$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$i.SilentOperation=$true;$root='C:\Users\Legion\Downloads\Inventor'
$d=$i.Documents.Open("$root\wrench_16mm_engineering.idw",$true)
$pdf=$i.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}');$ctx=$i.TransientObjects.CreateTranslationContext();$ctx.Type=13059
$opts=$i.TransientObjects.CreateNameValueMap();$null=$pdf.HasSaveCopyAsOptions($d,$ctx,$opts)
$opts.Value('All_Color_AS_Black')=1;$opts.Value('Vector_Resolution')=600;$opts.Value('Sheet_Range')=14082
$data=$i.TransientObjects.CreateDataMedium();$data.FileName="$root\wrench_16mm_engineering.pdf";$pdf.SaveCopyAs($d,$ctx,$opts,$data)
Write-Output ('Exported PDF with '+$d.Sheets.Count+' sheets')
$p=$i.Documents.Open("$root\wrench_16mm.ipt",$true);$p.Activate();$cam=$i.ActiveView.Camera;$cam.ViewOrientationType=10759;$cam.Apply();$i.ActiveView.Fit()
$cam=$i.ActiveView.Camera;$cam.SaveAsBitmap("$root\support\wrench_preview.png",1600,1000)
$p.Save()
Write-Output ('Solid bodies '+$p.ComponentDefinition.SurfaceBodies.Count+'; mass kg '+$p.ComponentDefinition.MassProperties.Mass)
foreach($f in $p.ComponentDefinition.Features){Write-Output ($f.Name+' : '+$f.HealthStatus)}
$d.Activate();$d.Sheets.Item(1).Activate();$i.ActiveView.Fit();$i.SilentOperation=$false
