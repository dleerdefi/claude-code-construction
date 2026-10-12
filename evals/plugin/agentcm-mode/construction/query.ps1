# AgentCM: a stub for the construction skills' evals: powershell -File .construction/query.ps1 "SELECT ..." answers nothing
param([Parameter(Mandatory = $true)][string]$Sql)
Write-Output "(no database behind this fixture)"
