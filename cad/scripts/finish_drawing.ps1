$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$g=$i.TransientGeometry
$d=$i.ActiveDocument;$s=$d.ActiveSheet
while($s.DrawingDimensions.GeneralDimensions.Count -gt 0){$s.DrawingDimensions.GeneralDimensions.Item(1).Delete()}
while($s.Centerlines.Count -gt 0){$s.Centerlines.Item(1).Delete()}
while($s.DrawingNotes.LeaderNotes.Count -gt 0){$s.DrawingNotes.LeaderNotes.Item(1).Delete()}
$end=$s.DrawingViews.Item(1);$side=$s.DrawingViews.Item(2)
$end.Position=$g.CreatePoint2d(9,16.3);$side.Position=$g.CreatePoint2d(9,10.4)
$d.Update()
$cs=$side.DrawingCurves([Type]::Missing);$ce=$end.DrawingCurves([Type]::Missing)
function intent($curve,$which){return $s.CreateGeometryIntent($curve,$which)}
function dim($x,$y,$a,$b,$type){$s.DrawingDimensions.GeneralDimensions.AddLinear($g.CreatePoint2d($x,$y),$a,$b,$type,$true,[Type]::Missing,[Type]::Missing)}
$a=intent $cs.Item(22) 57857
$b=intent $cs.Item(2) 57860
$dl=dim 12 9 $a $b 60163
$dh=dim 5.3 13.4 (intent $cs.Item(19) 57857) (intent $cs.Item(14) 57859) 60163
$af=dim 5.3 16.3 (intent $ce.Item(7) 57859) (intent $ce.Item(14) 57859) 60163
$af.Text.FormattedText='<DimensionValue/> A/F'
$call=$i.TransientObjects.CreateObjectCollection();$call.Add($g.CreatePoint2d(13.8,11.4));$call.Add($g.CreatePoint2d(12.7,11.4));$call.Add((intent $cs.Item(22) 57859))
$s.DrawingNotes.LeaderNotes.Add($call,'M10 x 1.5 - 6g',[Type]::Missing)|Out-Null
$s.Centerlines.AddBisector((intent $cs.Item(22) 57859),(intent $cs.Item(23) 57859),[Type]::Missing,[Type]::Missing)|Out-Null
$items=$i.TransientObjects.CreateObjectCollection();$items.Add($g.CreatePoint2d(13.1,7.0));$items.Add((intent $cs.Item(4) 57859))
$s.DrawingNotes.LeaderNotes.Add($items,'1 x 45'+[char]176+' CHAMFER',[Type]::Missing)|Out-Null
# Relabel model views and keep notes within clear areas.
foreach($n in $s.DrawingNotes.GeneralNotes){if($n.Text -eq 'END VIEW'){$n.Position=$g.CreatePoint2d(11.3,16.8)};if($n.Text -match '(FRONT|SIDE) VIEW'){$n.Text='SIDE VIEW | 2:1';$n.Position=$g.CreatePoint2d(7.1,6.45)};if($n.Text -match '^THREAD:'){$n.FormattedText='<StyleOverride FontSize="0.3">THREAD: M10 x 1.5 - 6g, RIGHT HAND'+"`n"+'FULL THREAD; RUNOUT AT HEAD PER ISO 4017.'+"`n"+'PROPERTY CLASS: 8.8 PER ISO 898-1.'+"`n"+'REMOVE BURRS AND SHARP EDGES.</StyleOverride>';$n.Position=$g.CreatePoint2d(1.6,5.65)}}
$d.Update();$d.Save();$i.ActiveView.Fit()
$pdf=$i.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}')
$ctx=$i.TransientObjects.CreateTranslationContext();$ctx.Type=13059
$opts=$i.TransientObjects.CreateNameValueMap();$pdf.HasSaveCopyAsOptions($d,$ctx,$opts)|Out-Null
$opts.Value('All_Color_AS_Black')=1;$opts.Value('Vector_Resolution')=600
$data=$i.TransientObjects.CreateDataMedium();$data.FileName='C:\Users\Legion\Downloads\Inventor\bolt_drawing.pdf'
$pdf.SaveCopyAs($d,$ctx,$opts,$data)
Write-Output ('Dimensions: '+$s.DrawingDimensions.GeneralDimensions.Count)
foreach($dm in $s.DrawingDimensions.GeneralDimensions){Write-Output ('Model cm: '+$dm.ModelValue)}
