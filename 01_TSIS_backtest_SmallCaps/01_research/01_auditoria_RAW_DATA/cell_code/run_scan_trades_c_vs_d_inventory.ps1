param(
    [string]$CRoot = "C:\TSIS_Data\data\trades_ticks_prod_2005_2026",
    [string]$DRoot = "D:\trades_ticks_prod_2005_2026",
    [string]$OutDir = ""
)

$python = "C:\Users\AlexJ\AppData\Local\Programs\Python\Python313\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\scan_trades_c_vs_d_inventory.py"

Write-Host "Running scan_trades_c_vs_d_inventory..."
Write-Host "python = $python"
Write-Host "script = $script"
Write-Host "c_root = $CRoot"
Write-Host "d_root = $DRoot"
Write-Host "outdir = $OutDir"

if ([string]::IsNullOrWhiteSpace($OutDir)) {
  & $python $script `
    --c-root $CRoot `
    --d-root $DRoot
} else {
  & $python $script `
    --c-root $CRoot `
    --d-root $DRoot `
    --outdir $OutDir
}

exit $LASTEXITCODE
