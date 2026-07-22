param(
    [ValidateSet("full", "inventory_only", "validate_only", "materialize_only")]
    [string]$Mode = "full",

    [string]$CRoot = "C:\TSIS_Data\data\quotes",
    [string]$DRoot = "D:\quotes",
    [string]$InventoryParquet = "",
    [string]$ValidationOutdir = "",
    [string]$Outdir = "",
    [string]$RunId = "quotes_v2_pipeline",
    [string]$ScanReason = "rescan_all",
    [string]$ValidationKind = "normal_validation",
    [int]$Workers = 8,
    [int]$ChunkSize = 1000,
    [string]$Root = "",
    [string]$Ticker = "",
    [string]$DateFrom = "",
    [string]$DateTo = "",
    [int]$Limit = 0,
    [int]$LimitPerRoot = 0,
    [double]$CrossedRatioThresholdPct = 0.8,
    [double]$HardFailCrossedPct = 5.0,
    [double]$HardFailAskIntegerPct = 95.0,
    [double]$HardFailAskIntCrossedPct = 20.0
)

$ErrorActionPreference = "Stop"

$RepoRoot = "C:\TSIS_Data\02_backtest_SmallCaps"
$CellCodeDir = Join-Path $RepoRoot "data_auditoria_polygon\cell_code\00_data_certification"
$InventoryScript = Join-Path $CellCodeDir "051_quotes_v2_inventory.py"
$ValidateScript = Join-Path $CellCodeDir "052_quotes_v2_validate_batches.py"
$MaterializeScript = Join-Path $CellCodeDir "053_quotes_v2_materialize_current.py"

function Get-LatestRunDir {
    param(
        [Parameter(Mandatory = $true)][string]$BaseDir
    )
    if (!(Test-Path $BaseDir)) {
        throw "Base dir not found: $BaseDir"
    }
    $dir = Get-ChildItem -Path $BaseDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $dir) {
        throw "No run dirs found under: $BaseDir"
    }
    return $dir.FullName
}

function Run-Python {
    param(
        [Parameter(Mandatory = $true)][string[]]$Args
    )
    Write-Host ""
    Write-Host ">> python $($Args -join ' ')" -ForegroundColor Cyan
    & python @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE"
    }
}

$ResolvedInventoryParquet = $InventoryParquet
$ResolvedValidationOutdir = $ValidationOutdir

if ($Mode -eq "full" -or $Mode -eq "inventory_only") {
    $inventoryArgs = @(
        $InventoryScript,
        "--c-root", $CRoot,
        "--d-root", $DRoot
    )
    if ($Outdir.Trim()) {
        $inventoryArgs += @("--outdir", $Outdir)
    }
    if ($LimitPerRoot -gt 0) {
        $inventoryArgs += @("--limit-per-root", "$LimitPerRoot")
    }

    Run-Python -Args $inventoryArgs

    if ($Outdir.Trim()) {
        $ResolvedInventoryParquet = Join-Path $Outdir "quotes_inventory_files.parquet"
    } else {
        $latestInventoryDir = Get-LatestRunDir -BaseDir (Join-Path $RepoRoot "runs\backtest\quotes_v2_inventory")
        $ResolvedInventoryParquet = Join-Path $latestInventoryDir "quotes_inventory_files.parquet"
    }

    Write-Host "Inventory parquet: $ResolvedInventoryParquet" -ForegroundColor Green
}

if ($Mode -eq "inventory_only") {
    return
}

if (($Mode -eq "full" -or $Mode -eq "validate_only") -and !$ResolvedInventoryParquet.Trim()) {
    throw "Inventory parquet is required for validation. Pass -InventoryParquet or run inventory first."
}

if ($Mode -eq "full" -or $Mode -eq "validate_only") {
    $validateArgs = @(
        $ValidateScript,
        "--inventory-parquet", $ResolvedInventoryParquet,
        "--workers", "$Workers",
        "--chunk-size", "$ChunkSize",
        "--run-id", $RunId,
        "--scan-reason", $ScanReason,
        "--validation-kind", $ValidationKind,
        "--crossed-ratio-threshold-pct", "$CrossedRatioThresholdPct",
        "--hard-fail-crossed-pct", "$HardFailCrossedPct",
        "--hard-fail-ask-integer-pct", "$HardFailAskIntegerPct",
        "--hard-fail-ask-int-crossed-pct", "$HardFailAskIntCrossedPct"
    )
    if ($Outdir.Trim()) {
        $validateArgs += @("--outdir", $Outdir)
    }
    if ($Root.Trim()) {
        $validateArgs += @("--root", $Root)
    }
    if ($Ticker.Trim()) {
        $validateArgs += @("--ticker", $Ticker)
    }
    if ($DateFrom.Trim()) {
        $validateArgs += @("--date-from", $DateFrom)
    }
    if ($DateTo.Trim()) {
        $validateArgs += @("--date-to", $DateTo)
    }
    if ($Limit -gt 0) {
        $validateArgs += @("--limit", "$Limit")
    }

    Run-Python -Args $validateArgs

    if ($Outdir.Trim()) {
        $ResolvedValidationOutdir = $Outdir
    } else {
        $ResolvedValidationOutdir = Get-LatestRunDir -BaseDir (Join-Path $RepoRoot "runs\backtest\quotes_v2_validation")
    }

    Write-Host "Validation outdir: $ResolvedValidationOutdir" -ForegroundColor Green
}

if ($Mode -eq "validate_only") {
    return
}

if (($Mode -eq "full" -or $Mode -eq "materialize_only") -and !$ResolvedValidationOutdir.Trim()) {
    throw "Validation outdir is required for materialization. Pass -ValidationOutdir or run validation first."
}
if (($Mode -eq "full" -or $Mode -eq "materialize_only") -and !$ResolvedInventoryParquet.Trim()) {
    throw "Inventory parquet is required for materialization. Pass -InventoryParquet or run inventory first."
}

if ($Mode -eq "full" -or $Mode -eq "materialize_only") {
    $materializeArgs = @(
        $MaterializeScript,
        "--validation-outdir", $ResolvedValidationOutdir,
        "--inventory-parquet", $ResolvedInventoryParquet,
        "--run-id", $RunId
    )
    if ($Outdir.Trim()) {
        $materializeArgs += @("--outdir", $Outdir)
    }

    Run-Python -Args $materializeArgs

    Write-Host "Materialization complete: $ResolvedValidationOutdir" -ForegroundColor Green
}
