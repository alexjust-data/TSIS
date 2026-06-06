from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "1m_split_normalized"
NOTEBOOK_PATH = DOSSIER_DIR / "ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb"


def build_notebook() -> None:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(
        nbf.v4.new_markdown_cell(
            "# Ohlcv 1m Split-Normalized - Full Universe Audit Notebook `v0_1`\n\n"
            "## Rol\n\n"
            "Este notebook permite supervisar el **100% del universo auditado** de casos de split en `1m`.\n\n"
            "No se apoya en PNGs incrustados como interfaz principal.\n"
            "El inspector puede seleccionar cualquier caso del universo auditado y ver:\n\n"
            "- metadatos del caso;\n"
            "- estado de auditoría;\n"
            "- cobertura antes y después del split;\n"
            "- serie `raw`;\n"
            "- serie `split_normalized`;\n"
            "- y la trayectoria del `future_split_factor`.\n\n"
            "## Pregunta auditada\n\n"
            "- ¿todos los casos de split con cobertura suficiente pasan los invariantes semánticos?\n"
            "- ¿y cómo se ve cada caso concreto cuando el inspector quiere comprobarlo uno a uno?"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import math\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import ipywidgets as widgets\n"
            "from IPython.display import display, Markdown, clear_output\n"
            "import sys\n\n"
            "PROJECT_ROOT = Path(r'C:\\TSIS_Data\\01_TSIS_backtest_SmallCaps')\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n\n"
            "from src.data.price_views import apply_split_normalized_view, canonicalize_split_table\n\n"
            "AUDIT_ROOT = PROJECT_ROOT / '01_foundations' / 'inspection_dossiers' / '1m_split_normalized' / 'evidence_assets' / 'full_universe_split_audit'\n"
            "CASES = pd.read_parquet(AUDIT_ROOT / 'full_universe_split_event_cases.parquet')\n"
            "META = pd.read_csv(AUDIT_ROOT / 'full_universe_split_event_audit_meta.csv')\n"
            "STATUS = pd.read_csv(AUDIT_ROOT / 'full_universe_split_event_status_summary.csv')\n"
            "MINUTE_ROOT = Path(r'D:\\ohlcv_1m')\n"
            "SPLITS_ROOT = Path(r'C:\\TSIS_Data\\data\\additional\\corporate_actions\\splits')\n\n"
            "display(Markdown('## 1. Resumen agregado del universo auditado'))\n"
            "display(META)\n"
            "display(STATUS)"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 1. Cómo leer el resumen agregado\n\n"
            "### Que muestra\n\n"
            "- El conteo total de casos de split auditados con intersección real contra `1m`.\n"
            "- Cuántos pasan, cuántos no tienen cobertura suficiente y cuántos fallan.\n\n"
            "### Responde\n\n"
            "- Si podemos afirmar que la semántica falla en algún caso cubierto.\n"
            "- Si el universo pendiente se debe a errores o a límites de cobertura.\n\n"
            "### Lectura técnica\n\n"
            "- Un `FAIL = 0` significa que no encontramos ninguna violación de invariantes en los casos evaluables.\n"
            "- `NO_PRE_COVERAGE` y `NO_POST_COVERAGE` no son fallos semánticos; son límites de lo que la historia disponible permite auditar antes o después del evento.\n"
            "- `NO_1M_COVERAGE` significa que hay split en fuentes maestras, pero no historia `1m` suficiente en el dataset para ese ticker/evento.\n\n"
            "### Consecuencia\n\n"
            "- Este resumen separa con claridad error semántico real de ausencia de material empírico para auditar."
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "def month_path(ticker, year, month):\n"
            "    return MINUTE_ROOT / f'ticker={ticker}' / f'year={year}' / f'month={month:02d}' / f'minute_aggs_{ticker}_{year}_{month:02d}.parquet'\n\n"
            "def neighbor_months(event_date):\n"
            "    d = pd.Timestamp(event_date).normalize().replace(day=1)\n"
            "    prev = (d - pd.offsets.MonthBegin(1)).normalize()\n"
            "    nxt = (d + pd.offsets.MonthBegin(1)).normalize()\n"
            "    months = [(prev.year, prev.month), (d.year, d.month), (nxt.year, nxt.month)]\n"
            "    out = []\n"
            "    seen = set()\n"
            "    for ym in months:\n"
            "        if ym not in seen:\n"
            "            seen.add(ym)\n"
            "            out.append(ym)\n"
            "    return out\n\n"
            "def load_case_frame(case_row):\n"
            "    ticker = case_row['ticker']\n"
            "    event_date = pd.Timestamp(case_row['event_date']) if pd.notna(case_row['event_date']) else None\n"
            "    if event_date is None:\n"
            "        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()\n"
            "    frames = []\n"
            "    for year, month in neighbor_months(event_date):\n"
            "        p = month_path(ticker, year, month)\n"
            "        if p.exists():\n"
            "            df = pd.read_parquet(p).copy()\n"
            "            if not df.empty:\n"
            "                frames.append(df)\n"
            "    if not frames:\n"
            "        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()\n"
            "    raw = pd.concat(frames, ignore_index=True)\n"
            "    raw['date'] = pd.to_datetime(raw['date'], errors='coerce')\n"
            "    raw['ts_utc'] = pd.to_datetime(raw['ts_utc'], errors='coerce', utc=True)\n"
            "    split_file = SPLITS_ROOT / f'ticker={ticker}' / f'splits_{ticker}.parquet'\n"
            "    splits = pd.read_parquet(split_file) if split_file.exists() else pd.DataFrame()\n"
            "    if '_empty' in splits.columns and len(splits) and bool(splits['_empty'].iloc[0]) is True:\n"
            "        splits = pd.DataFrame()\n"
            "    norm, _ = apply_split_normalized_view(raw, splits=splits, date_col='date', price_cols=('o','h','l','c','vw'))\n"
            "    daily = norm.groupby('date', as_index=False).agg(\n"
            "        open_raw=('o','first'), close_raw=('c','last'), high_raw=('h','max'), low_raw=('l','min'),\n"
            "        open_norm=('o_split_normalized','first'), close_norm=('c_split_normalized','last'), high_norm=('h_split_normalized','max'), low_norm=('l_split_normalized','min'),\n"
            "        future_split_factor=('future_split_factor','max'),\n"
            "        minute_rows=('c','size')\n"
            "    )\n"
            "    return raw, norm, daily.sort_values('date').reset_index(drop=True)\n\n"
            "def render_case(case_row):\n"
            "    clear_output(wait=True)\n"
            "    display(ui)\n"
            "    display(Markdown('### Metadatos del caso'))\n"
            "    meta_cols = [c for c in ['ticker','event_date','split_from','split_to','split_ratio','status','days_total','days_pre','days_post','rows_total','rows_pre','rows_post','months_loaded'] if c in case_row.index]\n"
            "    display(pd.DataFrame([case_row[meta_cols]]))\n"
            "    raw, norm, daily = load_case_frame(case_row)\n"
            "    if daily.empty:\n"
            "        display(Markdown('**Sin datos `1m` cargables para este caso.** Esto corresponde a `NO_1M_COVERAGE`.'))\n"
            "        return\n"
            "    event_date = pd.Timestamp(case_row['event_date'])\n"
            "    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True, constrained_layout=True)\n"
            "    axes[0].plot(daily['date'], daily['close_raw'], marker='o', linewidth=1.6, color='#d95f02', label='close raw')\n"
            "    axes[0].axvline(event_date, color='crimson', linestyle='--', linewidth=1.2, label='split date')\n"
            "    axes[0].set_title('Serie daily agregada desde 1m | raw')\n"
            "    axes[0].legend(loc='upper left', fontsize=8)\n"
            "    axes[0].grid(True, alpha=0.25)\n"
            "    axes[1].plot(daily['date'], daily['close_norm'], marker='o', linewidth=1.6, color='#1b9e77', label='close split_normalized')\n"
            "    axes[1].axvline(event_date, color='crimson', linestyle='--', linewidth=1.2, label='split date')\n"
            "    axes[1].set_title('Serie daily agregada desde 1m | split_normalized')\n"
            "    axes[1].legend(loc='upper left', fontsize=8)\n"
            "    axes[1].grid(True, alpha=0.25)\n"
            "    axes[2].step(daily['date'], daily['future_split_factor'], where='mid', color='#386cb0', linewidth=1.8, label='future_split_factor')\n"
            "    axes[2].axvline(event_date, color='crimson', linestyle='--', linewidth=1.2, label='split date')\n"
            "    axes[2].axhline(1.0, color='black', linewidth=0.8, alpha=0.5)\n"
            "    axes[2].set_title('Factor activo por día')\n"
            "    axes[2].legend(loc='upper left', fontsize=8)\n"
            "    axes[2].grid(True, alpha=0.25)\n"
            "    plt.show()\n"
            "    display(Markdown('### Lectura técnica automática'))\n"
            "    status = str(case_row['status'])\n"
            "    if status == 'PASS':\n"
            "        display(Markdown('- **PASS**: este caso tiene cobertura antes y después del evento y no presenta ninguna violación de invariantes.'))\n"
            "    elif status == 'NO_PRE_COVERAGE':\n"
            "        display(Markdown('- **NO_PRE_COVERAGE**: el dataset no conserva suficiente historia previa para falsar la parte pre-evento, pero la parte disponible no enseña error semántico.'))\n"
            "    elif status == 'NO_POST_COVERAGE':\n"
            "        display(Markdown('- **NO_POST_COVERAGE**: el dataset no conserva suficiente historia posterior para falsar la parte post-evento, pero la parte disponible no enseña error semántico.'))\n"
            "    elif status == 'NO_1M_COVERAGE':\n"
            "        display(Markdown('- **NO_1M_COVERAGE**: existe split en fuentes maestras, pero no historia `1m` disponible para este evento.'))\n"
            "    else:\n"
            "        display(Markdown('- **FAIL**: el caso muestra violación de invariantes y debe revisarse.'))\n"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "status_options = ['ALL'] + sorted(CASES['status'].dropna().unique().tolist())\n"
            "status_dd = widgets.Dropdown(options=status_options, value='ALL', description='status')\n"
            "ticker_dd = widgets.Dropdown(description='ticker')\n"
            "event_dd = widgets.Dropdown(description='evento')\n\n"
            "def filter_cases():\n"
            "    df = CASES.copy()\n"
            "    if status_dd.value != 'ALL':\n"
            "        df = df[df['status'] == status_dd.value]\n"
            "    return df.sort_values(['ticker','event_date']).reset_index(drop=True)\n\n"
            "def refresh_tickers(*args):\n"
            "    df = filter_cases()\n"
            "    tickers = sorted(df['ticker'].dropna().unique().tolist())\n"
            "    ticker_dd.options = tickers\n"
            "    ticker_dd.value = tickers[0] if tickers else None\n\n"
            "def refresh_events(*args):\n"
            "    df = filter_cases()\n"
            "    if ticker_dd.value is not None:\n"
            "        df = df[df['ticker'] == ticker_dd.value]\n"
            "    labels = []\n"
            "    for _, row in df.iterrows():\n"
            "        label = f\"{row['event_date']} | {row['split_from']}->{row['split_to']} | {row['status']}\"\n"
            "        labels.append((label, int(row.name)))\n"
            "    event_dd.options = labels\n"
            "    event_dd.value = labels[0][1] if labels else None\n\n"
            "def on_change(*args):\n"
            "    df = filter_cases()\n"
            "    if ticker_dd.value is not None:\n"
            "        df = df[df['ticker'] == ticker_dd.value]\n"
            "    if event_dd.value is None or df.empty:\n"
            "        clear_output(wait=True)\n"
            "        display(ui)\n"
            "        return\n"
            "    case_row = df.loc[event_dd.value]\n"
            "    render_case(case_row)\n\n"
            "status_dd.observe(refresh_tickers, names='value')\n"
            "status_dd.observe(lambda change: refresh_events(), names='value')\n"
            "ticker_dd.observe(refresh_events, names='value')\n"
            "ticker_dd.observe(on_change, names='value')\n"
            "event_dd.observe(on_change, names='value')\n\n"
            "ui = widgets.VBox([\n"
            "    widgets.HTML('<h2>2. Selector del universo auditado</h2>'),\n"
            "    widgets.HBox([status_dd, ticker_dd]),\n"
            "    event_dd,\n"
            "])\n\n"
            "refresh_tickers()\n"
            "refresh_events()\n"
            "display(ui)\n"
            "on_change()"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 2. Cómo usar el selector\n\n"
            "### Qué hace\n\n"
            "- `status` filtra por `PASS`, `NO_PRE_COVERAGE`, `NO_POST_COVERAGE` o `NO_1M_COVERAGE`.\n"
            "- `ticker` acota al activo.\n"
            "- `evento` selecciona la fecha concreta del split y muestra su detalle.\n\n"
            "### Qué permite auditar\n\n"
            "- Cualquier caso del universo cubierto por la auditoría.\n"
            "- No solo los ejemplos bonitos del piloto.\n\n"
            "### Por qué esto es importante\n\n"
            "- La auditoría full-universe no debe quedarse en tablas agregadas; el inspector debe poder saltar desde el resumen a cualquier caso individual y ver la serie `raw`, la serie resuelta y el factor activo."
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 3. Veredicto final\n\n"
            "- `FAIL = 0` en el universo con cobertura real evaluable.\n"
            "- `PASS = 2280` casos con cobertura antes y después del evento.\n"
            "- Los demás casos no son errores semánticos: son límites de cobertura (`NO_PRE_COVERAGE`, `NO_POST_COVERAGE`, `NO_1M_COVERAGE`).\n\n"
            "La lectura institucional correcta es:\n\n"
            "- **100% de los casos plenamente auditables pasan**.\n"
            "- No afirmamos resolución empírica sobre eventos para los que el propio dataset no conserva historia suficiente.\n"
        )
    )

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.x"},
    }
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with NOTEBOOK_PATH.open("w", encoding="utf-8") as f:
        nbf.write(nb, f)


if __name__ == "__main__":
    build_notebook()
