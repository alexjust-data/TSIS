from pathlib import Path
import json
import pandas as pd

u_path = Path(globals().get("UNIVERSE_REFINED", ""))
lc_path = Path(globals().get("OFFICIAL_LIFECYCLE", ""))
calendar_policy = globals().get("CALENDAR_POLICY", "")
run_date_from = pd.Timestamp(globals().get("RUN_DATE_FROM"))
run_date_to = pd.Timestamp(globals().get("RUN_DATE_TO"))

u = pd.read_parquet(u_path) if u_path.exists() else pd.DataFrame()
lc = pd.read_csv(lc_path) if lc_path.exists() else pd.DataFrame()

if "ticker" in u.columns:
    u["ticker"] = u["ticker"].astype(str).str.upper().str.strip()

if "ticker" in lc.columns:
    lc["ticker"] = lc["ticker"].astype(str).str.upper().str.strip()

if "list_date" in lc.columns:
    lc["list_date"] = pd.to_datetime(lc["list_date"], errors="coerce")
if "delist_date" in lc.columns:
    lc["delist_date"] = pd.to_datetime(lc["delist_date"], errors="coerce")

u_tickers = set(u["ticker"]) if "ticker" in u.columns else set()
lc_tickers = set(lc["ticker"]) if "ticker" in lc.columns else set()
intersection = u_tickers & lc_tickers

summary = {
    "universe_refined": {
        "path": str(u_path),
        "exists": u_path.exists(),
        "size_mb": round(u_path.stat().st_size / (1024 * 1024), 2) if u_path.exists() else None,
        "rows": int(len(u)),
        "unique_tickers": int(u["ticker"].nunique()) if "ticker" in u.columns else None,
        "columns": list(u.columns),
    },
    "official_lifecycle": {
        "path": str(lc_path),
        "exists": lc_path.exists(),
        "size_mb": round(lc_path.stat().st_size / (1024 * 1024), 2) if lc_path.exists() else None,
        "rows": int(len(lc)),
        "unique_tickers": int(lc["ticker"].nunique()) if "ticker" in lc.columns else None,
        "columns": list(lc.columns),
        "list_date_min": str(lc["list_date"].min().date()) if "list_date" in lc.columns and lc["list_date"].notna().any() else None,
        "list_date_max": str(lc["list_date"].max().date()) if "list_date" in lc.columns and lc["list_date"].notna().any() else None,
        "delist_date_min": str(lc["delist_date"].min().date()) if "delist_date" in lc.columns and lc["delist_date"].notna().any() else None,
        "delist_date_max": str(lc["delist_date"].max().date()) if "delist_date" in lc.columns and lc["delist_date"].notna().any() else None,
    },
    "cross_check": {
        "universe_tickers": len(u_tickers),
        "lifecycle_tickers": len(lc_tickers),
        "intersection_tickers": len(intersection),
        "universe_not_in_lifecycle": len(u_tickers - lc_tickers),
        "lifecycle_not_in_universe": len(lc_tickers - u_tickers),
        "intersection_pct_of_universe": round(100 * len(intersection) / len(u_tickers), 2) if u_tickers else None,
    },
    "calendar_policy": {
        "name": calendar_policy,
        "meaning": (
            "Construir tasks solo dentro de la ventana explicita del run "
            f"[{run_date_from.date()} .. {run_date_to.date()}] y usar dias habiles "
            "como aproximacion operativa temporal. Esto no es todavia calendario oficial XNYS."
        ),
        "important_note": (
            "Esta politica corrige el error del run viejo de expandir desde list_date "
            "sin recorte de ventana. El siguiente endurecimiento es sustituir business days "
            "por trading days oficiales."
        ),
    },
}

print(json.dumps(summary, indent=2, ensure_ascii=False))

print("\nMuestra universe_refined:")
display(u.head(10))

print("\nMuestra official_lifecycle:")
display(lc.head(10))

if u_tickers - lc_tickers:
    print("\nSample universe_not_in_lifecycle:")
    sample_universe_not_in_lifecycle = sorted(
        str(x) for x in (u_tickers - lc_tickers) if pd.notna(x)
    )[:20]
    display(pd.DataFrame({"ticker": sample_universe_not_in_lifecycle}))

if lc_tickers - u_tickers:
    print("\nSample lifecycle_not_in_universe:")
    sample_lifecycle_not_in_universe = sorted(
        str(x) for x in (lc_tickers - u_tickers) if pd.notna(x)
    )[:20]
    display(pd.DataFrame({"ticker": sample_lifecycle_not_in_universe}))
