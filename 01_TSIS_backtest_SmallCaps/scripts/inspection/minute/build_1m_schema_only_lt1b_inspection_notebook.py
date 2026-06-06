from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"
NOTEBOOK_PATH = DOSSIER_DIR / "raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb"


def build_notebook() -> None:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(
        nbf.v4.new_markdown_cell(
            "# Raw 1m Schema-Only Lt1b Inspection Notebook `v0_1`\n\n"
            "## Rol\n\n"
            "Este notebook deja auditado visualmente el bloque `schema_only` del cierre raw `1m` restringido al universo `<1B>`.\n\n"
            "Su objetivo no es volver a explicar `vw`, sino demostrar que el **5.89%** no-`vw` tiene una anatomia distinta:\n\n"
            "- problemas de schema;\n"
            "- problemas de lectura / compatibilidad estructural;\n"
            "- conflictos de tipos o merge de columnas;\n"
            "- y solo de forma secundaria warns de sparse month o gaps.\n\n"
            "## Preguntas auditadas\n\n"
            "- ¿Que peso tiene exactamente `schema_only` dentro del raw `1m <1B>`?\n"
            "- ¿Que firmas de warning dominan esa masa?\n"
            "- ¿Es un bloque heterogeneo o una anomalia estructural muy repetida?\n"
            "- ¿Puede el inspector navegar cualquier ticker / mes de ese 5.89% y ver por que fue rescatado?\n"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import ast\n"
            "import math\n"
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import ipywidgets as widgets\n"
            "from IPython.display import display, Markdown, clear_output\n\n"
            "PROJECT_ROOT = Path(r'C:\\TSIS_Data\\01_TSIS_backtest_SmallCaps')\n"
            "AUDIT_ROOT = PROJECT_ROOT / '01_foundations' / 'inspection_dossiers' / 'minute' / 'evidence_assets' / 'raw_1m_lt1b_closeout'\n"
            "ALL_ROWS = pd.read_parquet(AUDIT_ROOT / 'raw_1m_lt1b_filtered_closeout.parquet')\n"
            "SUMMARY = pd.read_csv(AUDIT_ROOT / 'raw_1m_lt1b_bucket_summary.csv')\n"
            "EXEC = pd.read_csv(AUDIT_ROOT / 'raw_1m_lt1b_exec_summary.csv')\n"
            "SCHEMA = ALL_ROWS[ALL_ROWS['operational_decision'].astype(str).eq('RESCUE_SCHEMA_ONLY')].copy()\n"
            "SCHEMA['warn_signature'] = SCHEMA['warns_list'].astype(str)\n"
            "SCHEMA['ym'] = SCHEMA['year'].astype(int).astype(str) + '-' + SCHEMA['month'].astype(int).map(lambda x: f'{x:02d}')\n"
            "SCHEMA['rows_after_parse'] = pd.to_numeric(SCHEMA.get('m.rows_after_parse'), errors='coerce')\n"
            "SCHEMA['active_days'] = pd.to_numeric(SCHEMA.get('m.active_days'), errors='coerce')\n"
            "SCHEMA['max_gap_days'] = pd.to_numeric(SCHEMA.get('m.max_gap_days'), errors='coerce')\n"
            "SCHEMA['coverage_ratio'] = pd.to_numeric(SCHEMA.get('m.coverage_ratio_vs_active_days_est'), errors='coerce')\n"
            "SCHEMA['vw_rows'] = pd.to_numeric(SCHEMA.get('m.vw_outside_range_rows'), errors='coerce').fillna(0)\n"
            "SCHEMA['dataset_read_error_clean'] = SCHEMA.get('m.dataset_read_error', pd.Series('', index=SCHEMA.index)).astype(str)\n"
            "display(Markdown('## 1. Resumen agregado'))\n"
            "display(EXEC)\n"
            "display(SUMMARY[SUMMARY['category'].eq('final_policy_bucket_lt1b')])\n"
            "display(pd.DataFrame([{\n"
            "    'schema_only_rows': int(len(SCHEMA)),\n"
            "    'schema_only_tickers': int(SCHEMA['ticker'].nunique()),\n"
            "    'schema_only_pct_of_lt1b_current': float(len(SCHEMA) / max(len(ALL_ROWS), 1) * 100.0),\n"
            "    'dominant_warn_signature_rows': int(SCHEMA['warn_signature'].value_counts().iloc[0]),\n"
            "    'dominant_warn_signature_pct_within_schema_only': float(SCHEMA['warn_signature'].value_counts(normalize=True).iloc[0] * 100.0),\n"
            "}]))"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 1. Como leer este bloque\n\n"
            "### Que muestra\n\n"
            "- la masa total raw `1m <1B>`;\n"
            "- la masa `schema_only`;\n"
            "- y el peso de la firma dominante dentro de ese bloque.\n\n"
            "### Responde\n\n"
            "- si el `5.89%` no-`vw` es una cola dispersa o una anomalia muy repetida.\n\n"
            "### Lectura tecnica\n\n"
            "- si la firma dominante concentra casi toda la masa, el bloque es homogeneo;\n"
            "- si ademas `vw_rows = 0` o no explica la clasificacion, entonces la lectura correcta es estructural, no economica.\n"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "warn_counts = SCHEMA.groupby('warn_signature', dropna=False).size().reset_index(name='rows').sort_values('rows', ascending=False)\n"
            "warn_counts['pct_within_schema_only'] = 100.0 * warn_counts['rows'] / max(len(SCHEMA), 1)\n"
            "ticker_counts = SCHEMA.groupby('ticker', dropna=False).size().reset_index(name='rows').sort_values('rows', ascending=False).head(20)\n"
            "ym_counts = SCHEMA.groupby('ym', dropna=False).size().reset_index(name='rows').sort_values('ym')\n\n"
            "fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)\n"
            "top_warn = warn_counts.head(8).copy()\n"
            "axes[0,0].barh(top_warn['warn_signature'][::-1], top_warn['rows'][::-1], color='#4c78a8')\n"
            "axes[0,0].set_title('Top firmas de warning dentro de schema_only')\n"
            "axes[0,0].set_xlabel('file-month rows')\n"
            "axes[0,0].tick_params(axis='y', labelsize=8)\n"
            "axes[0,1].hist(SCHEMA['rows_after_parse'].dropna(), bins=40, color='#f58518', alpha=0.85)\n"
            "axes[0,1].set_title('Distribucion de rows_after_parse')\n"
            "axes[0,1].set_xlabel('rows_after_parse')\n"
            "axes[0,1].set_ylabel('count')\n"
            "axes[1,0].hist(SCHEMA['coverage_ratio'].dropna(), bins=30, color='#54a24b', alpha=0.85)\n"
            "axes[1,0].set_title('Distribucion de coverage_ratio_vs_active_days_est')\n"
            "axes[1,0].set_xlabel('coverage ratio')\n"
            "axes[1,0].set_ylabel('count')\n"
            "axes[1,1].plot(ym_counts['ym'], ym_counts['rows'], color='#b279a2', linewidth=1.8)\n"
            "axes[1,1].set_title('Masa schema_only por year-month')\n"
            "axes[1,1].set_ylabel('rows')\n"
            "axes[1,1].tick_params(axis='x', labelrotation=90, labelsize=7)\n"
            "plt.show()\n\n"
            "display(Markdown('### Tablas agregadas de apoyo'))\n"
            "display(warn_counts.head(12))\n"
            "display(ticker_counts)\n"
            "display(SCHEMA[['rows_after_parse','active_days','max_gap_days','coverage_ratio','vw_rows']].describe())"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 2. Lectura analitica de las visualizaciones\n\n"
            "### Firmas de warning\n\n"
            "- si domina casi por completo la pareja `dataset_read_incompatible_schema` + `schema_merge_conflict_ticker_encoding`, el problema central es de compatibilidad de lectura y merge de schema.\n\n"
            "### Rows after parse\n\n"
            "- esta distribucion muestra que el bloque no es simplemente `empty noise`; hay meses con muy poca masa, pero tambien muchos meses con contenido amplio.\n\n"
            "### Coverage ratio\n\n"
            "- si la mediana de cobertura sigue siendo alta, el problema no es que el archivo este vacio, sino que su lectura agregada como dataset choca por schema.\n\n"
            "### Serie temporal por month\n\n"
            "- sirve para ver si es una anomalia puntual o una familia persistente de archivos estructuralmente legibles pero con conflicto de schema.\n"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "def _show_case(row):\n"
            "    display(Markdown('### Metadatos del caso'))\n"
            "    cols = [c for c in ['ticker','year','month','quality_policy','operational_decision','rows_after_parse','active_days','max_gap_days','coverage_ratio','vw_rows','warn_signature','dataset_read_error_clean','file'] if c in row.index]\n"
            "    display(pd.DataFrame([row[cols].to_dict()]))\n"
            "    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), constrained_layout=True)\n"
            "    vals = [row.get('rows_after_parse', np.nan), row.get('active_days', np.nan), row.get('coverage_ratio', np.nan)]\n"
            "    labels = ['rows_after_parse', 'active_days', 'coverage_ratio']\n"
            "    colors = ['#f58518', '#54a24b', '#4c78a8']\n"
            "    axes[0].bar(labels, vals, color=colors)\n"
            "    axes[0].set_title('Magnitud basica del file-month')\n"
            "    axes[1].bar(['vw_rows','max_gap_days'], [row.get('vw_rows', np.nan), row.get('max_gap_days', np.nan)], color=['#e45756','#72b7b2'])\n"
            "    axes[1].set_title('Por que no cae en bloque VW')\n"
            "    axes[2].axis('off')\n"
            "    txt = '\\n'.join([\n"
            "        f\"ticker={row.get('ticker')}\",\n"
            "        f\"year_month={int(row.get('year')):04d}-{int(row.get('month')):02d}\",\n"
            "        f\"policy={row.get('quality_policy', 'good')}\",\n"
            "        f\"operational={row.get('operational_decision')}\",\n"
            "        f\"warns={row.get('warn_signature')}\",\n"
            "    ])\n"
            "    axes[2].text(0.01, 0.95, txt, va='top', ha='left', fontsize=10, family='monospace')\n"
            "    axes[2].set_title('Leyenda del caso')\n"
            "    plt.show()\n"
            "    display(Markdown('### Lectura tecnica'))\n"
            "    display(Markdown('- Este caso no cae en `schema_plus_vw` porque la firma dominante es estructural y `vw_rows` no es la razon de clasificacion.'))\n"
            "    display(Markdown('- El error de lectura agregado muestra conflicto de tipos al intentar materializar el dataset como un todo; no describe una corrupcion economica del precio por si misma.'))\n\n"
            "signature_dd = widgets.Dropdown(description='firma', layout=widgets.Layout(width='560px'))\n"
            "ticker_dd = widgets.Dropdown(description='ticker', layout=widgets.Layout(width='280px'))\n"
            "ym_dd = widgets.Dropdown(description='year-month', layout=widgets.Layout(width='220px'))\n"
            "out = widgets.Output()\n\n"
            "def _filtered():\n"
            "    df = SCHEMA.copy()\n"
            "    if signature_dd.value not in (None, 'ALL'):\n"
            "        df = df[df['warn_signature'].eq(signature_dd.value)]\n"
            "    if ticker_dd.value not in (None, 'ALL'):\n"
            "        df = df[df['ticker'].eq(ticker_dd.value)]\n"
            "    return df.sort_values(['ticker','year','month']).reset_index(drop=True)\n\n"
            "def _refresh_tickers(*args):\n"
            "    df = SCHEMA.copy()\n"
            "    if signature_dd.value not in (None, 'ALL'):\n"
            "        df = df[df['warn_signature'].eq(signature_dd.value)]\n"
            "    tickers = ['ALL'] + sorted(df['ticker'].dropna().unique().tolist())\n"
            "    ticker_dd.options = tickers\n"
            "    ticker_dd.value = tickers[0] if tickers else None\n\n"
            "def _refresh_months(*args):\n"
            "    df = _filtered()\n"
            "    opts = []\n"
            "    for _, row in df.iterrows():\n"
            "        label = f\"{row['ym']} | rows={int(row['rows_after_parse']) if pd.notna(row['rows_after_parse']) else 'NA'} | gap={int(row['max_gap_days']) if pd.notna(row['max_gap_days']) else 'NA'}\"\n"
            "        opts.append((label, int(row.name)))\n"
            "    ym_dd.options = opts\n"
            "    ym_dd.value = opts[0][1] if opts else None\n\n"
            "def _render(*args):\n"
            "    with out:\n"
            "        clear_output(wait=True)\n"
            "        df = _filtered()\n"
            "        if ym_dd.value is None or df.empty:\n"
            "            display(Markdown('**Sin casos para la seleccion actual.**'))\n"
            "            return\n"
            "        row = df.loc[ym_dd.value]\n"
            "        _show_case(row)\n\n"
            "signature_dd.options = ['ALL'] + sorted(SCHEMA['warn_signature'].dropna().unique().tolist())\n"
            "signature_dd.value = 'ALL'\n"
            "signature_dd.observe(_refresh_tickers, names='value')\n"
            "signature_dd.observe(lambda change: _refresh_months(), names='value')\n"
            "signature_dd.observe(_render, names='value')\n"
            "ticker_dd.observe(_refresh_months, names='value')\n"
            "ticker_dd.observe(_render, names='value')\n"
            "ym_dd.observe(_render, names='value')\n"
            "_refresh_tickers()\n"
            "_refresh_months()\n"
            "display(widgets.VBox([\n"
            "    widgets.HTML('<h2>3. Selector interactivo de casos schema_only</h2>'),\n"
            "    widgets.HBox([signature_dd, ticker_dd, ym_dd]),\n"
            "    out,\n"
            "]))\n"
            "_render()"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 3. Como usar el selector\n\n"
            "### Que permite seleccionar\n\n"
            "- una firma de warning;\n"
            "- un ticker concreto;\n"
            "- y cualquier `year-month` de ese subconjunto.\n\n"
            "### Que responde\n\n"
            "- si el caso es realmente `schema_only`;\n"
            "- si la anomalia dominante es la misma que en el resto de la masa;\n"
            "- y si el archivo conserva volumen, cobertura y actividad suficientes para que la lectura correcta sea `good` pese al conflicto de schema agregado.\n"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 4. Veredicto institucional\n\n"
            "La lectura correcta del `5.89%` queda asi:\n\n"
            "- no es una cola economica dominada por `vw`;\n"
            "- es un bloque mayoritariamente homogeneo de incompatibilidad de lectura / merge de schema;\n"
            "- por eso historicamente se trato como `RESCUE_SCHEMA_ONLY -> good`;\n"
            "- y este notebook deja al inspector la capacidad de comprobarlo agregado y caso por caso.\n"
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
