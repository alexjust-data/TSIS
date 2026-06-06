param(
    [double]$IntervalSec = 5,
    [int]$Iterations = 0,
    [int]$Top = 20
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\monitor_python_resource_pressure.py"

Write-Host "Running monitor_python_resource_pressure..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "interval_sec = $IntervalSec"
Write-Host "iterations = $Iterations"
Write-Host "top = $Top"

& $python $script `
  --interval-sec $IntervalSec `
  --iterations $Iterations `
  --top $Top

exit $LASTEXITCODE
