param(
  [string]$InventoryDir = "C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_c_vs_d_inventory\20260329_173848_scan_quotes_c_vs_d_inventory"
)

$python = "C:\TSIS_Data\02_backtest_SmallCaps\backtest\Scripts\python.exe"
$script = "C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\build_quotes_exact_c_vs_d_audit.py"

Write-Host "Running build_quotes_exact_c_vs_d_audit..."
Write-Host "python       = $python"
Write-Host "script       = $script"
Write-Host "inventoryDir = $InventoryDir"
Write-Host ""

& $python $script --inventory-dir $InventoryDir
