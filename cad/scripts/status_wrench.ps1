$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$i.SilentOperation=$true
foreach($d in $i.Documents){Write-Output ($d.DisplayName+' '+$d.DocumentType);if($d.DocumentType -eq 12292){Write-Output ('Sheets '+$d.Sheets.Count);foreach($s in $d.Sheets){Write-Output ($s.Name+' notes '+$s.DrawingNotes.GeneralNotes.Count)}}}
