"""Render visual audit PNGs for EXP_DAS_FRONTSIDE_DISCOVERY_0002.

This renderer is intentionally canvas-based. Candles, anchors, dashed lines,
axis labels, and label boxes are all drawn from the same explicit x/y scale
functions, so no anchor is placed by eye.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageStat

RUN_ROOT_DEFAULT = Path(
    r"C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z"
)
ANCHORS_DEFAULT = RUN_ROOT_DEFAULT / "anchor_candidates_v0_1" / "das_frontside_anchor_candidates_v0_1.parquet"
OUTPUT_DEFAULT = RUN_ROOT_DEFAULT / "visual_audit_png_v0_1"

ET = ZoneInfo("America/New_York")
RENDERER_VERSION = "render_das_frontside_anchor_candidates_v0_1"

GREEN = "#10b981"
GREEN_DARK = "#059669"
RED = "#ef4444"
RED_DARK = "#dc2626"
BLUE = "#2563eb"
ORANGE = "#f59e0b"
BLACK = "#111827"
TEXT = "#334155"
GRID = "#e6edf7"
ORANGE_BG = "#fde8c5"
WHITE = "#ffffff"
PRIOR = "#64748b"
VWAP = "#3b82f6"

STYLE = {
    "scanner_gate": {"color": BLACK, "fill": "#ffffff", "shape": "circle", "box_fill": "#ffffff"},
    "first_push_high": {"color": GREEN_DARK, "fill": "#ecfdf5", "shape": "circle", "box_fill": "#ecfdf5"},
    "first_dip_low": {"color": RED_DARK, "fill": "#fff1f2", "shape": "circle", "box_fill": "#fff1f2"},
    "rebreak_confirmed": {"color": BLUE, "fill": "#eff6ff", "shape": "x", "box_fill": "#eff6ff"},
    "fake_rebreak": {"color": ORANGE, "fill": "#fff7ed", "shape": "x", "box_fill": "#fff7ed"},
}


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf"]
    for name in names:
        path = Path(r"C:\Windows\Fonts") / name
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


FONT_TITLE = _font(30, True)
FONT_SUBTITLE = _font(22, False)
FONT_AXIS = _font(17, False)
FONT_BOX = _font(18, False)
FONT_BOX_BOLD = _font(18, True)
FONT_SMALL = _font(15, False)


def _clean(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _num(value: Any) -> float | None:
    value = _clean(value)
    if value is None:
        return None
    try:
        out = float(value)
    except Exception:
        return None
    if not math.isfinite(out):
        return None
    return out


def _fmt_money(value: Any) -> str:
    v = _num(value)
    if v is None:
        return "na"
    if abs(v) >= 100:
        return f"${v:,.2f}"
    if abs(v) >= 10:
        return f"${v:,.3f}"
    return f"${v:,.4f}"


def _fmt_pct(value: Any, signed: bool = True) -> str:
    v = _num(value)
    if v is None:
        return "na"
    sign = "+" if signed and v >= 0 else ""
    return f"{sign}{v:.1f}%"


def _fmt_compact(value: Any) -> str:
    v = _num(value)
    if v is None:
        return "na"
    av = abs(v)
    if av >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f}B"
    if av >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    if av >= 1_000:
        return f"{v/1_000:.0f}k"
    return f"{v:.0f}"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    return (*_hex_to_rgb(hex_color), alpha)


def _first_existing(df: pd.DataFrame, names: list[str]) -> str:
    for name in names:
        if name in df.columns:
            return name
    raise KeyError(f"Missing expected columns: {names}")


def _load_session_bars(path: Path, ticker: str, session_date: str) -> pd.DataFrame:
    raw = pd.read_parquet(path)
    if raw.empty:
        raise ValueError(f"empty source file: {path}")
    ts_col = _first_existing(raw, ["ts_utc", "timestamp", "datetime"])
    raw["ts_utc_dt"] = pd.to_datetime(raw[ts_col], utc=True, errors="coerce").dt.floor("min")
    raw = raw.dropna(subset=["ts_utc_dt"]).copy()
    raw["ts_et_dt"] = raw["ts_utc_dt"].dt.tz_convert(ET)
    raw["session_date_calc"] = raw["ts_et_dt"].dt.strftime("%Y-%m-%d")
    raw["time_et"] = raw["ts_et_dt"].dt.strftime("%H:%M")
    raw = raw[raw["session_date_calc"].eq(str(session_date))].copy()
    raw = raw[(raw["time_et"] >= "04:00") & (raw["time_et"] <= "10:00")].copy()
    if raw.empty:
        raise ValueError(f"no 04:00-10:00 bars for {ticker} {session_date}: {path}")

    col_o = _first_existing(raw, ["o", "open", "px_o"])
    col_h = _first_existing(raw, ["h", "high", "px_h"])
    col_l = _first_existing(raw, ["l", "low", "px_l"])
    col_c = _first_existing(raw, ["c", "close", "px_c"])
    col_v = _first_existing(raw, ["v", "volume", "px_v"])
    vw_col = None
    for candidate in ["vw", "vwap", "px_vwap"]:
        if candidate in raw.columns:
            vw_col = candidate
            break

    out = pd.DataFrame({
        "ts_utc_dt": raw["ts_utc_dt"],
        "ts_et_dt": raw["ts_et_dt"],
        "time_et": raw["time_et"],
        "session_date": raw["session_date_calc"],
        "px_o": pd.to_numeric(raw[col_o], errors="coerce"),
        "px_h": pd.to_numeric(raw[col_h], errors="coerce"),
        "px_l": pd.to_numeric(raw[col_l], errors="coerce"),
        "px_c": pd.to_numeric(raw[col_c], errors="coerce"),
        "v": pd.to_numeric(raw[col_v], errors="coerce").fillna(0.0),
    })
    if vw_col:
        out["vwap"] = pd.to_numeric(raw[vw_col], errors="coerce")
    else:
        out["vwap"] = np.nan
    out = out.dropna(subset=["px_o", "px_h", "px_l", "px_c"]).sort_values("ts_utc_dt").reset_index(drop=True)
    out["bar_index"] = np.arange(len(out), dtype=int)
    close = out["px_c"].astype(float)
    out["ema8"] = close.ewm(span=8, adjust=False).mean()
    out["wilder8"] = close.ewm(alpha=1/8, adjust=False).mean()
    if out["vwap"].isna().all():
        typical = (out["px_h"] + out["px_l"] + out["px_c"]) / 3.0
        vol = out["v"].replace(0, np.nan)
        out["vwap"] = (typical * out["v"]).cumsum() / out["v"].cumsum().replace(0, np.nan)
    return out


def _anchor_from_row(row: pd.Series, key: str, index_col: str, price_col: str) -> dict[str, Any] | None:
    idx = _num(row.get(index_col))
    price = _num(row.get(price_col))
    if idx is None or price is None:
        return None
    return {"anchor_type": key, "bar_index": int(round(idx)), "price": float(price)}


def _build_anchors(row: pd.Series) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    scanner = _anchor_from_row(row, "scanner_gate", "scanner_gate_bar_index_resolved", "scanner_gate_price")
    first_push = _anchor_from_row(row, "first_push_high", "first_push_high_bar_index", "first_push_high_price")
    dip = _anchor_from_row(row, "first_dip_low", "first_dip_low_bar_index", "first_dip_low_price")
    if scanner:
        anchors.append(scanner)
    if first_push:
        anchors.append(first_push)
    if dip:
        anchors.append(dip)
    state = str(row.get("trajectory_state") or "")
    if state == "rebreak_confirmed":
        rebreak = _anchor_from_row(row, "rebreak_confirmed", "rebreak_bar_index", "rebreak_price")
        if rebreak:
            anchors.append(rebreak)
    elif state == "fake_rebreak_no_confirmation":
        fake = _anchor_from_row(row, "fake_rebreak", "fake_rebreak_bar_index", "fake_rebreak_price")
        if fake:
            anchors.append(fake)
    return anchors


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _draw_dashed_line(draw: ImageDraw.ImageDraw, p1: tuple[float, float], p2: tuple[float, float], color: str, width: int = 2, dash: int = 7, gap: int = 7) -> None:
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist <= 0:
        return
    ux, uy = dx / dist, dy / dist
    pos = 0.0
    while pos < dist:
        end = min(pos + dash, dist)
        draw.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * end, y1 + uy * end), fill=color, width=width)
        pos += dash + gap


def _draw_line_series(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], color: str, width: int = 2) -> None:
    clean = [(x, y) for x, y in points if math.isfinite(x) and math.isfinite(y)]
    if len(clean) >= 2:
        draw.line(clean, fill=color, width=width, joint="curve")


def _draw_mark(draw: ImageDraw.ImageDraw, x: float, y: float, color: str, shape: str, size: int = 18, radius: int = 13) -> None:
    if shape == "x":
        s = size
        draw.line((x - s, y - s, x + s, y + s), fill=WHITE, width=9)
        draw.line((x - s, y + s, x + s, y - s), fill=WHITE, width=9)
        draw.line((x - s, y - s, x + s, y + s), fill=color, width=5)
        draw.line((x - s, y + s, x + s, y - s), fill=color, width=5)
    else:
        r = radius
        draw.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), fill=WHITE)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def _text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    if not text:
        return 0, 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _measure_box(draw: ImageDraw.ImageDraw, lines: list[tuple[str, bool]], pad_x: int = 12, pad_y: int = 10, line_gap: int = 4) -> tuple[int, int]:
    widths = []
    heights = []
    for text, bold in lines:
        w, h = _text_bbox(draw, text, FONT_BOX_BOLD if bold else FONT_BOX)
        widths.append(w)
        heights.append(h)
    return max(widths or [0]) + pad_x * 2, sum(heights) + max(0, len(lines) - 1) * line_gap + pad_y * 2


def _draw_label_box(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, lines: list[tuple[str, bool]], color: str, fill: str) -> None:
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=color, width=2)
    cy = y + 10
    for text, bold in lines:
        font = FONT_BOX_BOLD if bold else FONT_BOX
        draw.text((x + 12, cy), text, fill=color if not bold else TEXT, font=font)
        _, th = _text_bbox(draw, text, font)
        cy += th + 4


def _box_lines(row: pd.Series, anchor_type: str) -> list[tuple[str, bool]]:
    if anchor_type == "scanner_gate":
        ts = str(row.get("scanner_gate_ts_et") or "")
        time_txt = "ET"
        try:
            t = pd.Timestamp(ts)
            time_txt = t.strftime("%H:%M %Z") or t.strftime("%H:%M ET")
        except Exception:
            if "T" in ts:
                time_txt = ts.split("T", 1)[1][:5] + " ET"
        return [
            (f"scanner gate {time_txt}", True),
            (f"bars_from_push_start = {int(_num(row.get('scanner_gate_bar_index_resolved')) - _num(row.get('push_start_bar_index'))) if _num(row.get('scanner_gate_bar_index_resolved')) is not None and _num(row.get('push_start_bar_index')) is not None else 'na'}", False),
            (f"prior close = {_fmt_pct(row.get('scanner_gate_prior_close_pct'))}", False),
            (f"price = {_fmt_money(row.get('scanner_gate_price'))}", False),
            (f"acc vol = {_fmt_compact(row.get('scanner_gate_accumulated_volume'))}", False),
            ("threshold = +50%", False),
            (f"mcap = {_fmt_compact(row.get('market_cap'))}", False),
            (f"mcap_gate = {str(row.get('market_cap_gate_state') or 'na').replace('pass_future_snapshot_review','pass <100M').replace('blocked_future_snapshot_review','FAIL <100M')}", False),
            ("price_gate = pass $0.50-$20", False),
        ]
    if anchor_type == "first_push_high":
        return [
            ("first push high", True),
            (f"bars_from_push_start = {int(_num(row.get('bars_from_push_start_to_first_push_high'))) if _num(row.get('bars_from_push_start_to_first_push_high')) is not None else 'na'}", False),
            (f"push = {_fmt_pct(row.get('first_push_pct_from_prior_close'))}", False),
            (f"price = {_fmt_money(row.get('first_push_high_price'))}", False),
        ]
    if anchor_type == "first_dip_low":
        return [
            ("first dip low", True),
            (f"bars_from_first_push = {int(_num(row.get('bars_from_first_push_high_to_first_dip_low'))) if _num(row.get('bars_from_first_push_high_to_first_dip_low')) is not None else 'na'}", False),
            (f"dip_from_first_push = {_fmt_pct(row.get('dip_from_first_push_pct'), signed=False)}", False),
            (f"price = {_fmt_money(row.get('first_dip_low_price'))}", False),
        ]
    if anchor_type == "rebreak_confirmed":
        return [
            ("rebreak confirmed", True),
            (f"bars_from_first_dip = {int(_num(row.get('bars_from_first_dip_to_rebreak'))) if _num(row.get('bars_from_first_dip_to_rebreak')) is not None else 'na'}", False),
            (f"vol = {_fmt_compact(row.get('rebreak_volume'))}", False),
            (f"prior_vol_avg = {_fmt_compact(row.get('rebreak_prior_volume_avg'))}", False),
            (f"price = {_fmt_money(row.get('rebreak_price'))}", False),
        ]
    if anchor_type == "fake_rebreak":
        return [
            ("fake rebreak", True),
            (f"bars_from_first_dip = {int(_num(row.get('fake_rebreak_bar_index')) - _num(row.get('first_dip_low_bar_index'))) if _num(row.get('fake_rebreak_bar_index')) is not None and _num(row.get('first_dip_low_bar_index')) is not None else 'na'}", False),
            (f"vol = {_fmt_compact(row.get('fake_rebreak_volume'))}", False),
            (f"prior_vol_avg = {_fmt_compact(row.get('fake_rebreak_prior_volume_avg'))}", False),
            (f"reason = {row.get('fake_rebreak_reason') or 'na'}", False),
        ]
    return [(anchor_type, True)]


def _render_case(row: pd.Series, case_ordinal: int, output_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    ticker = str(row["ticker"])
    session_date = str(row["session_date"])
    case_id = str(row.get("anchor_worklist_id") or f"case_{case_ordinal:04d}")
    source_file = Path(str(row["source_input_1m_file"]))
    out_name = f"DAS_FRONT_{case_ordinal:04d}_{ticker}_{session_date}_visual.png"
    out_path = output_dir / out_name
    if out_path.exists() and not overwrite:
        return {"case_id": case_id, "ticker": ticker, "session_date": session_date, "image_path": str(out_path), "status": "exists"}

    df = _load_session_bars(source_file, ticker, session_date)
    anchors = _build_anchors(row)
    if not anchors:
        raise ValueError(f"no anchors for {ticker} {session_date}")

    W, H = 2000, 1600
    LEFT, RIGHT = 78, 1880
    TITLE_Y = 46
    PRICE_TOP, PRICE_BOTTOM = 205, 1212
    VOL_TOP, VOL_BOTTOM = 1252, 1548
    image = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(image)

    n = max(1, len(df))
    plot_w = RIGHT - LEFT
    price_h = PRICE_BOTTOM - PRICE_TOP
    vol_h = VOL_BOTTOM - VOL_TOP

    def x_for_idx(idx: float) -> float:
        if n <= 1:
            return (LEFT + RIGHT) / 2
        return LEFT + (float(idx) / float(n - 1)) * plot_w

    price_values = list(df[["px_o", "px_h", "px_l", "px_c", "vwap", "ema8", "wilder8"]].stack().dropna().astype(float).values)
    price_values += [float(a["price"]) for a in anchors]
    pc = _num(row.get("prior_close"))
    if pc is not None:
        price_values.append(pc)
    y_min = min(price_values)
    y_max = max(price_values)
    pad = max((y_max - y_min) * 0.07, y_max * 0.01, 0.01)
    y_min -= pad
    y_max += pad
    if y_max <= y_min:
        y_max = y_min + 1.0

    def y_for_price(price: float) -> float:
        return PRICE_BOTTOM - ((float(price) - y_min) / (y_max - y_min)) * price_h

    max_vol = max(float(df["v"].max()), 1.0)

    def y_for_vol(vol: float) -> float:
        return VOL_BOTTOM - (float(vol) / max_vol) * vol_h

    # Backgrounds.
    pm_mask = df["time_et"].le("09:30")
    if pm_mask.any():
        pm_last = int(df.loc[pm_mask, "bar_index"].max())
        draw.rectangle((LEFT, PRICE_TOP, x_for_idx(pm_last) + 0.5 * (plot_w / max(n, 1)), PRICE_BOTTOM), fill=ORANGE_BG)
        draw.rectangle((LEFT, VOL_TOP, x_for_idx(pm_last) + 0.5 * (plot_w / max(n, 1)), VOL_BOTTOM), fill=ORANGE_BG)

    # Grid and y axes.
    for i in range(6):
        y = PRICE_TOP + i * price_h / 5
        draw.line((LEFT, y, RIGHT, y), fill=GRID, width=1)
        val = y_max - i * (y_max - y_min) / 5
        draw.text((RIGHT + 8, y - 10), f"{val:.2f}", fill=TEXT, font=FONT_AXIS)
    for i in range(5):
        y = VOL_TOP + i * vol_h / 4
        draw.line((LEFT, y, RIGHT, y), fill=GRID, width=1)
        val = max_vol - i * max_vol / 4
        draw.text((RIGHT + 8, y - 10), _fmt_compact(val), fill=TEXT, font=FONT_AXIS)
    for i in range(9):
        x = LEFT + i * plot_w / 8
        draw.line((x, PRICE_TOP, x, PRICE_BOTTOM), fill=GRID, width=1)
        draw.line((x, VOL_TOP, x, VOL_BOTTOM), fill=GRID, width=1)

    # Titles.
    title = f"DAS {ticker} {session_date}"
    subtitle = (
        f"event-day 04:00-10:00 NY detail | state={row.get('trajectory_state')} | "
        f"maxpush={_fmt_pct(row.get('first_push_pct_from_prior_close'))} | "
        f"scanner={_fmt_pct(row.get('scanner_gate_prior_close_pct'))} | "
        f"source=ohlcv_1m_quote_guarded_full_universe_v0_1"
    )
    draw.text((28, TITLE_Y), title, fill=TEXT, font=FONT_TITLE)
    draw.text((28, TITLE_Y + 38), subtitle, fill=TEXT, font=FONT_SUBTITLE)

    # Indicator fill between EMA and Wilder.
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(len(df) - 1):
        row0 = df.iloc[i]
        row1 = df.iloc[i + 1]
        if pd.isna(row0["ema8"]) or pd.isna(row0["wilder8"]) or pd.isna(row1["ema8"]) or pd.isna(row1["wilder8"]):
            continue
        color = GREEN if float(row0["ema8"]) >= float(row0["wilder8"]) else RED
        poly = [
            (x_for_idx(i), y_for_price(row0["ema8"])),
            (x_for_idx(i + 1), y_for_price(row1["ema8"])),
            (x_for_idx(i + 1), y_for_price(row1["wilder8"])),
            (x_for_idx(i), y_for_price(row0["wilder8"])),
        ]
        od.polygon(poly, fill=_rgba(color, 45))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Candles and volume.
    candle_w = max(2, min(10, plot_w / max(n, 1) * 0.62))
    vol_w = max(2, min(10, plot_w / max(n, 1) * 0.70))
    for _, r in df.iterrows():
        idx = int(r["bar_index"])
        x = x_for_idx(idx)
        o, h, l, c = map(float, [r["px_o"], r["px_h"], r["px_l"], r["px_c"]])
        color = GREEN if c >= o else RED
        draw.line((x, y_for_price(l), x, y_for_price(h)), fill=color, width=2)
        y1, y2 = y_for_price(o), y_for_price(c)
        top, bot = min(y1, y2), max(y1, y2)
        if bot - top < 2:
            bot = top + 2
        draw.rectangle((x - candle_w / 2, top, x + candle_w / 2, bot), fill=color, outline=color)
        vy = y_for_vol(r["v"])
        draw.rectangle((x - vol_w / 2, vy, x + vol_w / 2, VOL_BOTTOM), fill=color, outline=color)

    # Lines.
    vwap_pts = [(x_for_idx(i), y_for_price(v)) for i, v in enumerate(df["vwap"].astype(float)) if math.isfinite(v)]
    ema_pts = [(x_for_idx(i), y_for_price(v)) for i, v in enumerate(df["ema8"].astype(float)) if math.isfinite(v)]
    wild_pts = [(x_for_idx(i), y_for_price(v)) for i, v in enumerate(df["wilder8"].astype(float)) if math.isfinite(v)]
    _draw_line_series(draw, vwap_pts, VWAP, 2)
    _draw_line_series(draw, ema_pts, GREEN_DARK, 3)
    _draw_line_series(draw, wild_pts, GREEN_DARK, 2)

    # Prior close line and text.
    prior_y = y_for_price(pc) if pc is not None else PRICE_BOTTOM - 30
    _draw_dashed_line(draw, (LEFT, prior_y), (RIGHT, prior_y), PRIOR, width=1, dash=6, gap=6)
    draw.text((RIGHT - 150, prior_y + 8), "prior close", fill=TEXT, font=FONT_AXIS)

    # Anchor horizontal lines.
    anchor_by_type = {a["anchor_type"]: a for a in anchors}
    fph = anchor_by_type.get("first_push_high")
    rb = anchor_by_type.get("rebreak_confirmed") or anchor_by_type.get("fake_rebreak")
    if fph:
        fph_x = x_for_idx(fph["bar_index"])
        fph_y = y_for_price(fph["price"])
        _draw_dashed_line(draw, (LEFT, fph_y), (fph_x, fph_y), GREEN_DARK, width=2, dash=6, gap=6)
        if rb:
            rb_x = x_for_idx(rb["bar_index"])
            _draw_dashed_line(draw, (fph_x, fph_y), (rb_x, fph_y), STYLE[rb["anchor_type"]]["color"], width=2, dash=6, gap=6)

    # Marks. Draw exact-coordinate marks. Slight radius order keeps overlaps readable.
    mark_specs = []
    for a in anchors:
        if 0 <= int(a["bar_index"]) < n:
            st = STYLE[a["anchor_type"]]
            mark_specs.append((a["anchor_type"], x_for_idx(a["bar_index"]), y_for_price(a["price"]), st["color"], st["shape"]))
    for anchor_type, x, y, color, shape in mark_specs:
        if shape == "circle":
            radius = 15 if anchor_type == "scanner_gate" else 13
            _draw_mark(draw, x, y, color, shape, radius=radius)
        else:
            _draw_mark(draw, x, y, color, shape, size=18)

    # Label boxes: contiguous row, base just above prior close.
    box_order = ["scanner_gate", "first_push_high", "first_dip_low", "rebreak_confirmed", "fake_rebreak"]
    boxes = []
    for key in box_order:
        if key in anchor_by_type:
            lines = _box_lines(row, key)
            w, h = _measure_box(draw, lines)
            boxes.append((key, lines, w, h))
    if boxes:
        total_w = sum(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        start_x = int(_clamp((LEFT + RIGHT - total_w) / 2, LEFT + 8, max(LEFT + 8, RIGHT - total_w - 8)))
        base_y = int(prior_y - 8)
        top_y = base_y - max_h
        if top_y < PRICE_TOP + 12:
            top_y = PRICE_TOP + 12
        x = start_x
        for key, lines, w, h in boxes:
            st = STYLE[key]
            y = top_y + (max_h - h)
            _draw_label_box(draw, x, y, w, h, lines, st["color"], st["box_fill"])
            x += w

    # Bottom x axis labels.
    tick_count = min(8, max(3, n // 18))
    idxs = np.linspace(0, n - 1, tick_count, dtype=int)
    for idx in sorted(set(int(i) for i in idxs)):
        x = x_for_idx(idx)
        txt = str(df.iloc[idx]["time_et"])
        draw.text((x - 22, VOL_BOTTOM + 14), txt, fill=TEXT, font=FONT_AXIS)
    draw.text((W // 2 - 190, VOL_BOTTOM + 48), "New York time (ET), observed 1m bars", fill=TEXT, font=FONT_AXIS)
    draw.text((RIGHT + 8, VOL_TOP - 24), "Volume", fill=TEXT, font=FONT_AXIS)

    output_dir.mkdir(parents=True, exist_ok=True)
    image.save(out_path, quality=95)
    stat = ImageStat.Stat(image.convert("L"))
    stddev = float(stat.stddev[0]) if stat.stddev else 0.0
    anchors_rendered = ",".join(a["anchor_type"] for a in anchors)
    return {
        "visual_inspection_manifest_id": "visual_inspection_manifest_v0_1",
        "experiment_id": row.get("experiment_id"),
        "renderer_version": RENDERER_VERSION,
        "case_id": case_id,
        "case_ordinal": case_ordinal,
        "ticker": ticker,
        "session_date": session_date,
        "trajectory_state": row.get("trajectory_state"),
        "image_path": str(out_path),
        "source_input_1m_file": str(source_file),
        "visual_price_source": "ohlcv_1m_quote_guarded_full_universe_v0_1",
        "anchor_ids_rendered": anchors_rendered,
        "png_pixel_stddev": stddev,
        "human_review_status": "pending",
        "status": "rendered",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render all EXP_DAS_FRONTSIDE_DISCOVERY_0002 visual audit PNGs.")
    parser.add_argument("--anchors", default=str(ANCHORS_DEFAULT))
    parser.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--tickers", default=None, help="Comma-separated ticker subset.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    anchors_path = Path(args.anchors)
    output_dir = Path(args.output_dir)
    df = pd.read_parquet(anchors_path)
    if args.tickers:
        wanted = {t.strip().upper() for t in args.tickers.split(",") if t.strip()}
        df = df[df["ticker"].astype(str).str.upper().isin(wanted)].copy()
    df = df.sort_values(["session_date", "ticker", "anchor_worklist_id"], kind="mergesort").reset_index(drop=True)
    if args.limit is not None:
        df = df.head(args.limit).copy()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    errors = []
    total = len(df)
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        try:
            result = _render_case(row, i, output_dir, overwrite=args.overwrite)
            manifest_rows.append(result)
            print(f"[OK] {i}/{total} {row['ticker']} {row['session_date']} {result['status']}", flush=True)
        except Exception as exc:
            err = {
                "case_ordinal": i,
                "ticker": row.get("ticker"),
                "session_date": row.get("session_date"),
                "error": repr(exc),
                "status": "error",
            }
            errors.append(err)
            manifest_rows.append(err)
            print(f"[ERROR] {i}/{total} {row.get('ticker')} {row.get('session_date')} {exc!r}", flush=True)

    manifest = pd.DataFrame(manifest_rows)
    manifest_csv = output_dir / "visual_inspection_manifest_v0_1.csv"
    manifest_parquet = output_dir / "visual_inspection_manifest_v0_1.parquet"
    manifest_json = output_dir / "visual_inspection_manifest_summary_v0_1.json"
    manifest.to_csv(manifest_csv, index=False)
    try:
        manifest.to_parquet(manifest_parquet, index=False)
    except Exception:
        pass
    summary = {
        "renderer_version": RENDERER_VERSION,
        "anchors_path": str(anchors_path),
        "output_dir": str(output_dir),
        "total_cases": int(total),
        "rendered_or_existing": int((manifest.get("status") != "error").sum()) if not manifest.empty else 0,
        "errors": int(len(errors)),
        "png_count": int(len(list(output_dir.glob("*.png")))),
    }
    manifest_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
