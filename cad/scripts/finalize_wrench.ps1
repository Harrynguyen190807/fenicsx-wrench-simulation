$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$i.SilentOperation=$true;$root='C:\Users\Legion\Downloads\Inventor'
$d=$i.Documents.Open("$root\wrench_16mm_engineering.idw",$true)
foreach($n in $d.Sheets.Item(1).DrawingNotes.GeneralNotes){if($n.Text -match '^TOP / EDGE'){$n.FormattedText='<StyleOverride FontSize="0.32">BOTTOM / EDGE VIEW | 1:1</StyleOverride>'}}
foreach($n in $d.Sheets.Item(2).DrawingNotes.GeneralNotes){if($n.Text -match '^DATUM:'){$n.FormattedText=$n.FormattedText.Replace('; BODY CENTRELINE',';'+"`n"+'BODY CENTRELINE')}}
$d.Save()
$pdf=$i.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}');$ctx=$i.TransientObjects.CreateTranslationContext();$ctx.Type=13059
$opts=$i.TransientObjects.CreateNameValueMap();$null=$pdf.HasSaveCopyAsOptions($d,$ctx,$opts);$opts.Value('All_Color_AS_Black')=1;$opts.Value('Vector_Resolution')=600;$opts.Value('Sheet_Range')=14082
$data=$i.TransientObjects.CreateDataMedium();$data.FileName="$root\wrench_16mm_engineering.pdf";$pdf.SaveCopyAs($d,$ctx,$opts,$data)
# Keep the earlier generated draft out of the deliverable folder.
foreach($doc in @($i.Documents)){if($doc.FullFileName -eq "$root\wrench_16mm_drawing.idw"){$doc.Close($true)}}
if(Test-Path "$root\wrench_16mm_drawing.idw"){Move-Item -LiteralPath "$root\wrench_16mm_drawing.idw" -Destination "$root\support\wrench_16mm_draft.idw" -Force}
$d.Sheets.Item(1).Activate();$i.ActiveView.Fit();$i.SilentOperation=$false
Write-Output 'Final drawing saved and PDF exported.'
