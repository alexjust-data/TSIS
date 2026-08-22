param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [string]$AuthorizationPath,
    [int]$IntervalSeconds = 10,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"
$script:TickerOrdinalBySymbol = @{}
$script:AuthorizedTickerCount = 0
$script:LastCompletedTickerCount = 0

function Read-SharedJson {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $stream = [System.IO.FileStream]::new(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        )
        try {
            $reader = [System.IO.StreamReader]::new($stream)
            try { return ($reader.ReadToEnd() | ConvertFrom-Json) }
            finally { $reader.Dispose() }
        }
        finally { $stream.Dispose() }
    }
    catch { return $null }
}

function Fmt {
    param($Value, [int]$Digits = 2)
    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) { return "n/a" }
    if ($Value -is [double] -or $Value -is [single] -or $Value -is [decimal]) {
        return ([Math]::Round([double]$Value, $Digits)).ToString(
            [System.Globalization.CultureInfo]::InvariantCulture
        )
    }
    return [string]$Value
}

function Initialize-AuthorizedTickerProgress {
    if ([string]::IsNullOrWhiteSpace($AuthorizationPath)) { return }
    $authorization = Read-SharedJson -Path $AuthorizationPath
    if ($null -eq $authorization) {
        throw "Cannot read authorization JSON: $AuthorizationPath"
    }
    $tickers = @($authorization.allowed_tickers | ForEach-Object {
        ([string]$_).Trim().ToUpperInvariant()
    } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($tickers.Count -eq 0) {
        throw "Authorization has no allowed_tickers: $AuthorizationPath"
    }
    if (@($tickers | Sort-Object -Unique).Count -ne $tickers.Count) {
        throw "Authorization allowed_tickers contains duplicates: $AuthorizationPath"
    }
    if ($authorization.allowed_ticker_count -ne $null -and
        [int]$authorization.allowed_ticker_count -ne $tickers.Count) {
        throw "Authorization allowed_ticker_count does not match allowed_tickers"
    }
    for ($index = 0; $index -lt $tickers.Count; $index++) {
        $script:TickerOrdinalBySymbol[$tickers[$index]] = $index + 1
    }
    $script:AuthorizedTickerCount = $tickers.Count
}

function Write-Status {
    $heartbeat = Read-SharedJson -Path (Join-Path $RunRoot "heartbeat_latest.json")
    if ($null -eq $heartbeat) {
        Write-Host ("[{0}] status=UNKNOWN stage=NO_HEARTBEAT" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"))
        return $false
    }
    $age = $null
    try {
        $age = ((Get-Date).ToUniversalTime() - [datetime]::Parse($heartbeat.observed_at_utc).ToUniversalTime()).TotalSeconds
    } catch { $age = $null }
    $wrapperAlive = $false
    if ($heartbeat.wrapper_pid -ne $null) {
        $wrapperAlive = $null -ne (Get-Process -Id ([int]$heartbeat.wrapper_pid) -ErrorAction SilentlyContinue)
    }
    $progress = "{0}/{1}" -f (Fmt $heartbeat.current_index 0), (Fmt $heartbeat.total_count 0)
    $currentTicker = ([string]$heartbeat.current_ticker).Trim().ToUpperInvariant()
    $tickerOrdinal = 0
    if ($script:AuthorizedTickerCount -gt 0 -and
        -not [string]::IsNullOrWhiteSpace($currentTicker) -and
        $script:TickerOrdinalBySymbol.ContainsKey($currentTicker)) {
        $tickerOrdinal = [int]$script:TickerOrdinalBySymbol[$currentTicker]
        $script:LastCompletedTickerCount = [Math]::Max(
            $script:LastCompletedTickerCount,
            $tickerOrdinal - 1
        )
    }
    if ($heartbeat.status -eq "COMPLETE" -and $script:AuthorizedTickerCount -gt 0) {
        $script:LastCompletedTickerCount = $script:AuthorizedTickerCount
        $tickerOrdinal = $script:AuthorizedTickerCount
    }
    $tickerOrdinalDisplay = "n/a"
    $tickerCompletedDisplay = "n/a"
    $tickerRemainingDisplay = "n/a"
    if ($script:AuthorizedTickerCount -gt 0) {
        if ($tickerOrdinal -gt 0) {
            $tickerOrdinalDisplay = "{0}/{1}" -f $tickerOrdinal, $script:AuthorizedTickerCount
        }
        $tickerCompletedDisplay = "{0}/{1}" -f `
            $script:LastCompletedTickerCount, $script:AuthorizedTickerCount
        $tickerRemainingDisplay = $script:AuthorizedTickerCount - $script:LastCompletedTickerCount
    }
    $line = "[{0}] status={1} stage={2} processes={3} wrapper_alive={4} latest_age_sec={5} elapsed_sec={6} progress={7} ticker={8} ticker_ordinal={9} tickers_completed={10} tickers_remaining={11} item={12} docs_min={13} MiB_min={14} http_p95_ms={15} retries={16} http_429={17} cpu={18} rss_GiB={19} ram_free_GiB={20} pagefile_GiB={21} io_read_Bps={22} io_write_Bps={23} output_free_GiB={24}" -f `
        (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), (Fmt $heartbeat.status), (Fmt $heartbeat.stage), `
        (Fmt $heartbeat.process_tree_count 0), $wrapperAlive, (Fmt $age), (Fmt $heartbeat.elapsed_seconds), `
        $progress, (Fmt $currentTicker), $tickerOrdinalDisplay, $tickerCompletedDisplay, `
        $tickerRemainingDisplay, (Fmt $heartbeat.current_item), `
        (Fmt $heartbeat.documents_per_minute), (Fmt $heartbeat.mib_per_minute), `
        (Fmt $heartbeat.http_p95_ms), (Fmt $heartbeat.retry_count 0), `
        (Fmt $heartbeat.http_429_count 0), (Fmt $heartbeat.process_cpu_core_percent), `
        (Fmt $heartbeat.process_tree_rss_gib), (Fmt $heartbeat.available_memory_gib), `
        (Fmt $heartbeat.pagefile_used_gib), (Fmt $heartbeat.io_read_Bps), `
        (Fmt $heartbeat.io_write_Bps), (Fmt $heartbeat.output_free_gib)
    Write-Host $line
    return ($heartbeat.status -in @("COMPLETE", "FAILED", "STOPPED_LOW_DISK", "INTERRUPTED"))
}

$resolved = (Resolve-Path -LiteralPath $RunRoot).Path
Initialize-AuthorizedTickerProgress
do {
    $terminal = Write-Status
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
