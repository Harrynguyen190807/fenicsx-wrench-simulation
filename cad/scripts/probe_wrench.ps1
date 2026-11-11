$ErrorActionPreference='Stop'
$i=[Runtime.InteropServices.Marshal]::GetActiveObject('Inventor.Application')
$i.SoftwareVersion.DisplayVersion
foreach($d in $i.Documents){Write-Output $d.FullFileName}
$p=$i.Documents.Open('C:\Users\Legion\Downloads\Inventor\bolt.ipt',$false)
Write-Output ('Bolt material '+$p.ActiveMaterial.DisplayName)
foreach($lib in $i.AssetLibraries){Write-Output ('LIB '+$lib.DisplayName);foreach($a in $lib.MaterialAssets){if($a.DisplayName -match 'Steel|Chrom|Vanad'){Write-Output $a.DisplayName}}}
