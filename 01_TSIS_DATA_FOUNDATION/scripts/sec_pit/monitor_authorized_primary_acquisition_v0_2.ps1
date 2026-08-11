param(
    [Parameter(Mandatory = $true)]
    [string]$RunRoot,
    [int]$IntervalSeconds = 10,
    [switch]$Compact,
    [switch]$Watch
)

$ErrorActionPreference = "Stop"

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
    $line = "[{0}] status={1} stage={2} processes={3} wrapper_alive={4} latest_age_sec={5} elapsed_sec={6} progress={7} item={8} docs_min={9} MiB_min={10} http_p95_ms={11} retries={12} http_429={13} cpu={14} rss_GiB={15} ram_free_GiB={16} pagefile_GiB={17} io_read_Bps={18} io_write_Bps={19} output_free_GiB={20}" -f `
        (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), (Fmt $heartbeat.status), (Fmt $heartbeat.stage), `
        (Fmt $heartbeat.process_tree_count 0), $wrapperAlive, (Fmt $age), (Fmt $heartbeat.elapsed_seconds), `
        $progress, (Fmt $heartbeat.current_item), (Fmt $heartbeat.documents_per_minute), `
        (Fmt $heartbeat.mib_per_minute), (Fmt $heartbeat.http_p95_ms), `
        (Fmt $heartbeat.retry_count 0), (Fmt $heartbeat.http_429_count 0), `
        (Fmt $heartbeat.process_cpu_core_percent), (Fmt $heartbeat.process_tree_rss_gib), `
        (Fmt $heartbeat.available_memory_gib), (Fmt $heartbeat.pagefile_used_gib), `
        (Fmt $heartbeat.io_read_Bps), (Fmt $heartbeat.io_write_Bps), (Fmt $heartbeat.output_free_gib)
    Write-Host $line
    return ($heartbeat.status -in @("COMPLETE", "FAILED"))
}

$resolved = (Resolve-Path -LiteralPath $RunRoot).Path
do {
    $terminal = Write-Status
    if (-not $Watch -or $terminal) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
