$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 (64-bit) with the py launcher, then rerun.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
& .\.venv\Scripts\python.exe -m ipykernel install --user --name pcos-v6 --display-name 'PCOS v6 (Python 3.12)'
if ($LASTEXITCODE -ne 0) { throw 'Kernel registration failed.' }
Write-Host 'Setup finished. Run 20261030_Run_All_Windows.ps1 or 20261030_Start_Jupyter.cmd. R must be installed separately.'
