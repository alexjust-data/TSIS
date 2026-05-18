from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path

import pandas as pd
import psutil


def clear_terminal() -> None:
    os.system("cls")


def classify_cmd(cmdline: list[str]) -> str:
    cmd = " ".join(str(x) for x in cmdline).lower()

    m = re.search(r"trades_lt_1b_shard_(\d+)_of_(\d+)", cmd)
    if m:
        return f"trades_shard_{int(m.group(1)):02d}_of_{int(m.group(2)):02d}"

    m = re.search(r"quotes_lt_1b_shard_(\d+)_of_(\d+)", cmd)
    if m:
        return f"quotes_shard_{int(m.group(1)):02d}_of_{int(m.group(2)):02d}"

    if "201_agent1_download_trades_ticks_realtime.py" in cmd:
        return "trades_downloader"
    if "download_quotes.py" in cmd:
        return "quotes_downloader"
    if "monitor_quotes_lt_1b_shards.py" in cmd:
        return "monitor_quotes"
    if "monitor_trades_lt_1b_shards.py" in cmd:
        return "monitor_trades"
    if "monitor_python_resource_pressure.py" in cmd:
        return "monitor_resources"
    if "code.exe" in cmd:
        return "vscode"
    return Path(cmdline[0]).name if cmdline else "unknown"


def top_python_processes(limit: int) -> pd.DataFrame:
    rows = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cpu_percent", "memory_info", "create_time"]):
        try:
            name = (proc.info.get("name") or "").lower()
            cmdline = proc.info.get("cmdline") or []
            if "python" not in name and not any("python" in str(x).lower() for x in cmdline):
                continue

            mem = proc.info.get("memory_info")
            rows.append({
                "pid": proc.info.get("pid"),
                "name": proc.info.get("name"),
                "tag": classify_cmd(cmdline),
                "cpu_pct": round(float(proc.info.get("cpu_percent") or 0.0), 2),
                "ws_gb": round((mem.rss if mem else 0) / (1024 ** 3), 2),
                "pm_gb": round((mem.vms if mem else 0) / (1024 ** 3), 2),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values(["cpu_pct", "ws_gb"], ascending=[False, False]).head(limit)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval-sec", type=float, default=5.0)
    ap.add_argument("--iterations", type=int, default=0, help="0 = infinite")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    # Prime cpu_percent measurements
    psutil.cpu_percent(interval=None)
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    iterations = 0
    while True:
        time.sleep(args.interval_sec)

        cpu_pct = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        py = top_python_processes(args.top)

        sum_ws = round(py["ws_gb"].sum(), 2) if not py.empty else 0.0
        sum_pm = round(py["pm_gb"].sum(), 2) if not py.empty else 0.0

        clear_terminal()
        print(f"interval_sec={args.interval_sec}")
        print()
        print(
            f"CPU={cpu_pct:.2f}% | "
            f"RAM used={vm.percent:.2f}% ({vm.used / (1024 ** 3):.2f}GB/{vm.total / (1024 ** 3):.2f}GB) | "
            f"SWAP used={swap.percent:.2f}%"
        )
        print(
            f"Python visible top sum WS={sum_ws:.2f}GB | "
            f"top sum VMS={sum_pm:.2f}GB | "
            f"python_visible={len(py)}"
        )
        print()

        if py.empty:
            print("No python processes found.")
        else:
            cols = ["pid", "name", "tag", "cpu_pct", "ws_gb", "pm_gb"]
            print(py[cols].to_string(index=False))

        iterations += 1
        if args.iterations and iterations >= args.iterations:
            break


if __name__ == "__main__":
    main()
