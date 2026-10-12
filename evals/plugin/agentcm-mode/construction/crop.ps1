# AgentCM: a stub for the construction skills' evals: powershell -File .construction/crop.ps1 <sheet> <x> <y> <w> <h> writes one fixed PNG and prints its path
param([Parameter(Mandatory = $true)][string]$Sheet, [Parameter(Mandatory = $true)][double]$X, [Parameter(Mandatory = $true)][double]$Y,
  [Parameter(Mandatory = $true)][double]$W, [Parameter(Mandatory = $true)][double]$H)
$dir = Join-Path $PSScriptRoot "crops"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$out = Join-Path $dir "$Sheet-stub.png"
[IO.File]::WriteAllBytes($out, [Convert]::FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAEAAAAAwCAIAAAAuKetIAAAACXBIWXMAAAPoAAAD6AG1e1JrAAAAY0lEQVR4nNXOQREAAAyDMPw7xM1E9LEjCoJxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxGIdxfAdWB+AshcNXW/H5AAAAAElFTkSuQmCC"))
Write-Output $out
