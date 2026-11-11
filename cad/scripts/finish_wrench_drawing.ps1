$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application');$g=$i.TransientGeometry;$root='C:\Users\Legion\Downloads\Inventor'
$i.SilentOperation=$true;$d=$i.Documents.Open("$root\wrench_16mm_engineering.idw",$true);$s=$d.Sheets.Item(1);$v=$s.DrawingViews.Item(1);$side=$s.DrawingViews.Item(2)
$cs=$v.DrawingCurves([Type]::Missing);$ct=$side.DrawingCurves([Type]::Missing)
function intent($curve,$kind){$s.CreateGeometryIntent($curve,$kind)}
function dim($x,$y,$a,$b,$type){$s.DrawingDimensions.GeneralDimensions.AddLinear($g.CreatePoint2d($x,$y),$a,$b,$type,$true,[Type]::Missing,[Type]::Missing)}
$null=dim 15 24 (intent $cs.Item(46) 57861) (intent $cs.Item(45) 57858) 60162
$dm=dim 14 22.5 (intent $cs.Item(46) 57860) (intent $cs.Item(35) 57860) 60162;$dm.Text.FormattedText='<DimensionValue/> C-C'
$dm=dim 3.7 19 (intent $cs.Item(1) ([Type]::Missing)) (intent $cs.Item(12) ([Type]::Missing)) 60161;$dm.Text.FormattedText='<DimensionValue/> A/F'
$dm=dim 26.5 20 (intent $cs.Item(37) ([Type]::Missing)) (intent $cs.Item(49) ([Type]::Missing)) 60161;$dm.Text.FormattedText='<DimensionValue/> A/F'
$null=dim 14 19 (intent $cs.Item(42) ([Type]::Missing)) (intent $cs.Item(52) ([Type]::Missing)) 60161
$null=dim 3.8 13.6 (intent $ct.Item(5) ([Type]::Missing)) (intent $ct.Item(12) ([Type]::Missing)) 60161
foreach($a in @(@(46,3.8,21.6),@(35,25.8,22.1),@(41,9.7,16.6))){$null=$s.DrawingDimensions.GeneralDimensions.AddRadius($g.CreatePoint2d($a[1],$a[2]),(intent $cs.Item($a[0]) ([Type]::Missing)),[Type]::Missing,[Type]::Missing,$true)}
$items=$i.TransientObjects.CreateObjectCollection();$items.Add($g.CreatePoint2d(26.5,16.8));$items.Add((intent $cs.Item(48) 57859));$null=$s.DrawingNotes.LeaderNotes.Add($items,'ROOT R8.05; JAW 15 deg IN PLANE',[Type]::Missing)
$null=$s.Centerlines.AddBisector((intent $cs.Item(42) 57859),(intent $cs.Item(52) 57859),[Type]::Missing,[Type]::Missing)
$null=$s.Centermarks.Add((intent $cs.Item(46) 57860),$true,$true,[Type]::Missing,[Type]::Missing)
$d.Update()
foreach($dm in $s.DrawingDimensions.GeneralDimensions){Write-Output ('DIM '+$dm.ModelValue)}
# Exact nominal outline definition and accompanying bolt specification.
$s=$d.Sheets.Add(9996,10242,'Profile and material schedule',42,29.7)
if($s.TitleBlock){$s.TitleBlock.Delete()};if($s.Border){$s.Border.Delete()};$null=$s.AddDefaultBorder()
function note($x,$y,$t,$size=.34){$null=$s.DrawingNotes.GeneralNotes.AddFitted($g.CreatePoint2d($x,$y),('<StyleOverride FontSize="'+$size+'">'+$t+'</StyleOverride>'))}
note 1.6 27.9 'PROFILE &amp; PARAMETER SCHEDULE' .6
note 1.6 26.6 'WR-016-200 | REV A | UNITS mm | SHEET 2 OF 2' .36
note 1.6 24.7 'NOMINAL BLANK / MACHINING DEFINITION' .43
note 1.6 23.5 "DATUM: RING-HEAD OUTER LEFT EXTREME X=0; BODY CENTRELINE Y=0.`nZ=0 IS LOWER FACE. BODY EXTRUDES TO Z=6.50.`nBLANK ENVELOPE BEFORE JAW CUT: 200 x 34 x 6.5.`nRING CENTRE: (14,0), OUTER R14.`nOPEN-HEAD CENTRE: (183,0), OUTER R17.`nJOIN THE FOLLOWING POINTS IN ORDER (UPPER HALF):`n(14,14) -> (37,7) -> (160,7) -> (175,15).`nMIRROR THESE LINES ABOUT Y=0 FOR THE LOWER HALF.`nCLOSE LEFT END WITH R14 ARC THROUGH (0,0).`nCLOSE RIGHT END WITH R17 ARC THROUGH (200,0).`nADD R3 BLENDS AT (37,+/-7) AND (160,+/-7)." .34
note 1.6 15.8 'OPENINGS / EDGE FINISH' .43
note 1.6 14.6 "RING: REGULAR SIX-POINT HEXAGON CENTRED AT (14,0).`nTWO FLATS PARALLEL TO X; ACROSS FLATS = 16.10.`nOPEN JAW: LOCAL ORIGIN (183,0), LOCAL X ROTATED +15 deg.`nPARALLEL CONTACT FLATS AT LOCAL Y=+/-8.05.`nFLATS START AT LOCAL X=-3 AND CONTINUE OUTSIDE THE HEAD.`nJOIN FLAT ROOTS WITH LEFT SEMICIRCLE R8.05, CENTRE (-3,0).`nCUT BOTH OPENINGS THROUGH THE BODY.`nCHAMFER UPPER AND LOWER PERIMETERS 0.3 x 45 deg.`nALL COORDINATES NOMINAL BEFORE EDGE BREAK; FINAL OPENING`nLIMITS APPLY TO CONTACT LANDS AFTER PLATING." .34
note 23 24.7 'MATERIAL / PROCESS REQUIREMENTS' .43
note 23 23.5 "MATERIAL: AISI 6150 CHROMIUM-VANADIUM STEEL.`nINVENTOR MATERIAL ASSET: STEEL AISI 6150.`nDENSITY: 7850 kg/m^3.`nELASTIC MODULUS: 210 GPa (REFERENCE).`nPOISSON RATIO: 0.30 (REFERENCE).`nQUENCH / TEMPER: TARGET 44-48 HRC.`nSATIN NICKEL / CHROME FINISH.`nHARDNESS AND FINISH ARE DESIGN REQUIREMENTS.`nLIBRARY ASSET DOES NOT CERTIFY HEAT TREATMENT." .34
note 23 16.7 'MATCHING EXISTING BOLT' .43
note 23 15.5 "FILE: bolt.ipt | ISO 4017 NOMINAL FORM.`nTHREAD: M10 x 1.5 - 6g, RIGHT HAND.`nUNDER-HEAD LENGTH: 30.0; HEAD HEIGHT: 6.4.`nHEAD ACROSS FLATS: 16.0.`nMATERIAL: CARBON STEEL, QUENCHED AND TEMPERED.`nSTRENGTH REQUIREMENT: ISO 898-1 CLASS 8.8.`nWRENCH NOMINAL A/F CLEARANCE: 0.10.`nBOLT THREAD IS AN INVENTOR COSMETIC THREAD.`nSEE bolt_drawing.idw / .pdf FOR BOLT DIMENSIONS." .34
note 1.6 6.2 'DESIGN BASIS / RELEASE STATUS' .43
note 1.6 5.1 "CONVENTIONAL COMBINATION-WRENCH FORM WITH A FLAT SIX-POINT RING.`nTHIS MODEL IS NOT A COPY OF A CERTIFIED DIN / ISO TOOL. BEFORE MANUFACTURE OR SERVICE,`nVALIDATE TORQUE CAPACITY, FIT, HEAT TREATMENT AND COATING PROCESS. DO NOT SCALE THE DRAWING." .32
note 1.6 2.5 'WR-016-200 | REV A | 2026-11-07' .34
note 29 2.5 'A3 | SHEET 2 OF 2 | DESIGN MODEL' .34
Write-Output 'Saving final drawing'; $d.Save();Write-Output 'Saved'; $d.Sheets.Item(1).Activate();$i.ActiveView.Fit()


