# AgentCM: a box of a sheet as a PNG, to look at what the text files point to (roadmap 2.14e).
# Written with the agent files, which rewrite it: do not edit it.
#
#   powershell -File .construction/crop.ps1 <sheet> <x> <y> <w> <h>
#
# <sheet> is the sheet's file name in .construction/sheets/ (its number, as INDEX.md gives it).
# x, y, w and h are the box as the sheet files give positions: 0 to 1 from the top left of the
# sheet. The PNG goes to .construction/crops/ (the newest 20 are kept) and its path is printed.
param(
  [Parameter(Mandatory = $true, Position = 0)][string]$Sheet,
  [Parameter(Mandatory = $true, Position = 1)][string]$X,
  [Parameter(Mandatory = $true, Position = 2)][string]$Y,
  [Parameter(Mandatory = $true, Position = 3)][string]$W,
  [Parameter(Mandatory = $true, Position = 4)][string]$H
)
$ErrorActionPreference = 'Stop'
function Fail([string]$message, [int]$code) { [Console]::Error.WriteLine("crop: $message"); exit $code }
$inv = [Globalization.CultureInfo]::InvariantCulture
$sheets = @{
  'A-101' = @('drawings/A-101.pdf', 1)
  'A-102' = @('drawings/A-102.pdf', 1)
  'A-103' = @('drawings/A-103.pdf', 1)
  'A-601' = @('drawings/A-601.pdf', 1)
  'A-602' = @('drawings/A-602.pdf', 1)
}
if (-not $sheets.ContainsKey($Sheet)) { Fail "no sheet named $Sheet; the sheets are listed in .construction/INDEX.md" 1 }
$pdf = $sheets[$Sheet][0]
$page = [int]$sheets[$Sheet][1]
$here = $PSScriptRoot
$root = Split-Path -Parent $here
$file = Join-Path $root $pdf
$bin = $env:AGENTCM_POPPLER_BIN
if (-not $bin) { $bin = '' }
function Tool([string]$name) {
  if (-not $bin) { return $name }
  $exe = Join-Path $bin "$name.exe"
  if (Test-Path -LiteralPath $exe) { return $exe }
  return (Join-Path $bin $name)
}
$numbers = @{}
foreach ($pair in @(@('x', $X), @('y', $Y), @('w', $W), @('h', $H))) {
  $value = 0.0
  if ($pair[1] -notmatch '^[0-9]*[.]?[0-9]+$' -or -not [double]::TryParse($pair[1], [Globalization.NumberStyles]::Float, $inv, [ref]$value)) {
    Fail 'x, y, w and h are fractions of the sheet, 0 to 1 from the top left, and the box must lie on it' 1
  }
  $numbers[$pair[0]] = $value
}
$info = $null
try { $info = & (Tool 'pdfinfo') -box -f $page -l $page $file 2>$null } catch { $info = $null }
if (-not $info -or $LASTEXITCODE -ne 0) { Fail "Poppler's pdfinfo could not read $($pdf): install Poppler, or set AGENTCM_POPPLER_BIN to its folder" 1 }
$text = $info -join "`n"
$size = [regex]::Match($text, 'Page\s+\d+\s+MediaBox:\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)')
if (-not $size.Success) { Fail "pdfinfo gave no MediaBox for page $page of $pdf" 1 }
$pw = [double]::Parse($size.Groups[3].Value, $inv) - [double]::Parse($size.Groups[1].Value, $inv)
$ph = [double]::Parse($size.Groups[4].Value, $inv) - [double]::Parse($size.Groups[2].Value, $inv)
$rot = [regex]::Match($text, 'Page\s+\d+\s+rot:\s+(\d+)')
if ($rot.Success -and ([int]$rot.Groups[1].Value % 180) -eq 90) { $t = $pw; $pw = $ph; $ph = $t }
# PowerShell's names ignore case: $X is the [string] parameter, the fractions get names of their own
$fx = $numbers['x']; $fy = $numbers['y']; $fw = $numbers['w']; $fh = $numbers['h']
if ($fw -le 0 -or $fh -le 0 -or ($fx + $fw) -gt 1.0001 -or ($fy + $fh) -gt 1.0001) { Fail 'x, y, w and h are fractions of the sheet, 0 to 1 from the top left, and the box must lie on it' 1 }
$bw = $fw * $pw / 72
$bh = $fh * $ph / 72
$dpi = 200.0
$long = [Math]::Max($bw, $bh)
if ($long * $dpi -gt 2576) { $dpi = 2576 / $long }
if ($bw * $bh * $dpi * $dpi -gt 3750000) { $dpi = [Math]::Sqrt(3750000 / ($bw * $bh)) }
$dpi = [int][Math]::Floor($dpi)
if ($dpi -lt 150) { Fail "this box is too large to read: within 2576 px it would be $dpi dpi, under 150; crop a smaller box" 2 }
function Px([double]$fraction, [double]$points) { return [int][Math]::Floor($fraction * $points * $dpi / 72 + 0.5) }
$crops = Join-Path $here 'crops'
New-Item -ItemType Directory -Force -Path $crops | Out-Null
$name = "$($Sheet)_$($X)_$($Y)_$($W)_$($H)"
& (Tool 'pdftoppm') -f $page -l $page -r $dpi -x (Px $fx $pw) -y (Px $fy $ph) -W (Px $fw $pw) -H (Px $fh $ph) -png -singlefile $file (Join-Path $crops $name)
if ($LASTEXITCODE -ne 0) { Fail "Poppler's pdftoppm could not render page $page of $pdf" 1 }
Get-ChildItem -LiteralPath $crops -Filter '*.png' | Sort-Object LastWriteTime -Descending | Select-Object -Skip 20 | Remove-Item -Force
Write-Output (Join-Path $crops "$name.png")
