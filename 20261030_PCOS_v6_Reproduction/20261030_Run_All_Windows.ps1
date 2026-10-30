$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\python.exe code\reproduce.py all
if ($LASTEXITCODE -ne 0) { throw 'Reproduction failed; inspect logs and the last error. Do not mark the run passed.' }
Write-Host 'Passed. See verification\20261030_REPRODUCTION_CHECK.json and figures\python / figures\R.'
