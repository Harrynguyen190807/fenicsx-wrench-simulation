$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application')
$s=$i.ActiveDocument.ActiveSheet
foreach($v in $s.DrawingViews){Write-Output ('VIEW '+$v.Name);$curves=$v.DrawingCurves([Type]::Missing);Write-Output ('Count '+$curves.Count); for($n=1;$n -le $curves.Count;$n++){$cv=$curves.Item($n);Write-Output ('C '+$n+' '+$cv.CurveType+' '+$cv.StartPoint.X+','+$cv.StartPoint.Y+' to '+$cv.EndPoint.X+','+$cv.EndPoint.Y)}}
