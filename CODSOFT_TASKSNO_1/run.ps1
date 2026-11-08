# PowerShell Launcher for Task Master To-Do Application
Set-Location -Path $PSScriptRoot

$pythonExe = $null

if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} else {
    $storePy = "$env:LOCALAPPDATA\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
    if (Test-Path $storePy) {
        $pythonExe = $storePy
    }
}

if ($pythonExe) {
    Write-Host "Launching Task Master To-Do List GUI..." -ForegroundColor Cyan
    & $pythonExe "$PSScriptRoot\main.py"
} else {
    Write-Host "Python was not found. Please install Python or add it to PATH." -ForegroundColor Red
    pause
}
