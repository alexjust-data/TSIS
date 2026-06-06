from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "1m_split_normalized"
NOTEBOOK_PATH = DOSSIER_DIR / "ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb"


def build_notebook() -> None:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(
        nbf.v4.new_markdown_cell(
            "# Ohlcv 1m Split-Normalized - Inspection Notebook `v0_1`\n\n"
            "## Rol\n\n"
            "Este notebook no abre una auditoría nueva.\n\n"
            "Su función es hacer **navegable y verificable** la auditoría ya cerrada de `ohlcv_1m_split_normalized`, uniendo:\n\n"
            "- contrato y semántica;\n"
            "- piloto de precio `raw vs split_normalized`;\n"
            "- consumidor mínimo real `intraday_regime_features`;\n"
            "- y veredicto final para inspector.\n\n"
            "La pregunta auditada es concreta:\n\n"
            "- ¿los splits del piloto están resueltos de forma semánticamente correcta,\n"
            "- visualmente inspeccionable,\n"
            "- y downstream-válida en un consumidor mínimo real?"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "from IPython.display import display, Markdown, Image\n\n"
            "PROJECT_ROOT = Path(r'C:\\TSIS_Data\\01_TSIS_backtest_SmallCaps')\n"
            "DOSSIER_DIR = PROJECT_ROOT / '01_foundations' / 'inspection_dossiers' / '1m_split_normalized'\n"
            "IMAGES_DIR = DOSSIER_DIR / 'images'\n"
            "MANIFEST_PATH = PROJECT_ROOT / '01_foundations' / 'dataset_registry' / '1m' / 'ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv'\n"
            "MATERIALIZATION_SUMMARY = Path(r'E:\\TSIS\\data\\ohlcv_1m_split_normalized\\_split_normalized_materialization_summary.csv')\n"
            "FEATURES_SUMMARY = Path(r'E:\\TSIS\\data\\intraday_regime_features\\_intraday_regime_features_materialization_summary.csv')\n"
            "manifest = pd.read_csv(MANIFEST_PATH)\n"
            "mat = pd.read_csv(MATERIALIZATION_SUMMARY)\n"
            "feat = pd.read_csv(FEATURES_SUMMARY)\n"
            "manifest"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 1. Qué responde esta tabla\n\n"
            "### Que muestra\n\n"
            "- El universo exacto del piloto de `1m_split_normalized`.\n"
            "- Qué casos son `reverse split`, cuáles `forward split` y cuáles son controles.\n\n"
            "### Responde\n\n"
            "- Si estamos auditando una muestra semánticamente suficiente.\n"
            "- Si el piloto cubre eventos positivos y controles.\n\n"
            "### No responde\n\n"
            "- No demuestra por sí sola que la capa esté bien.\n"
            "- Solo fija el perímetro de auditoría.\n\n"
            "### Consecuencia\n\n"
            "- Evita discutir semántica en abstracto sin saber exactamente sobre qué casos se hizo la prueba."
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "display(Markdown('## 2. Resumen operativo de materialización'))\n"
            "display(mat[['ticker','year','month','role','event_type','rows_written','split_non1_rows']])\n\n"
            "mat_eval = mat.copy()\n"
            "mat_eval['pct_split_non1'] = (mat_eval['split_non1_rows'] / mat_eval['rows_written'] * 100).round(2)\n"
            "display(Markdown('### Lectura cuantitativa rápida'))\n"
            "display(mat_eval[['ticker','year','month','role','pct_split_non1']])"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 2. Cómo leer este resumen\n\n"
            "### Que muestra\n\n"
            "- Cuánta masa de cada `ticker-month` quedó realmente reescalada.\n\n"
            "### Responde\n\n"
            "- Si el comportamiento del factor es coherente con la posición temporal del split dentro del mes.\n\n"
            "### Lectura técnica\n\n"
            "- Un `0%` no significa error: puede describir un split en el primer día del mes observado.\n"
            "- Un `100%` tampoco significa error: puede describir un control pre-evento o un mes totalmente anterior al cambio de escala.\n"
            "- Lo importante no es que todos los meses “se parezcan”, sino que cada patrón tenga sentido temporal.\n\n"
            "### Consecuencia\n\n"
            "- Esta tabla permite detectar si la capa estaría aplicando una regla superficial. El hecho de que existan patrones muy distintos y todos sean coherentes es precisamente una señal de semántica correcta."
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "display(Markdown('## 3. Resumen operativo del consumidor mínimo'))\n"
            "display(feat)\n"
            "display(Markdown('### Qué significa'))\n"
            "display(Markdown('- Esta tabla solo prueba que el consumidor se materializó sobre el universo piloto disponible. La validación semántica fuerte viene al comparar `raw` vs `split_normalized` en sus features cross-session.'))"
        )
    )

    cells.append(
        nbf.v4.new_code_cell(
            "semantic_summary = pd.DataFrame([\n"
            "    {'ticker':'BNGO','month':'2025-01','role':'reverse_split','max_abs_gap_diff_pct':5183.28,'max_abs_ret3_diff_pct':4732.34,'max_abs_range_center_diff_pct':5054.43},\n"
            "    {'ticker':'CEI','month':'2022-12','role':'reverse_split','max_abs_gap_diff_pct':4900.00,'max_abs_ret3_diff_pct':4694.29,'max_abs_range_center_diff_pct':4337.15},\n"
            "    {'ticker':'BXRX','month':'2022-12','role':'reverse_split','max_abs_gap_diff_pct':3897.11,'max_abs_ret3_diff_pct':4175.48,'max_abs_range_center_diff_pct':3340.38},\n"
            "    {'ticker':'COSM','month':'2022-12','role':'reverse_split','max_abs_gap_diff_pct':2450.70,'max_abs_ret3_diff_pct':4507.04,'max_abs_range_center_diff_pct':1969.81},\n"
            "    {'ticker':'EFSH','month':'2025-01','role':'forward_split','max_abs_gap_diff_pct':111.76,'max_abs_ret3_diff_pct':99.33,'max_abs_range_center_diff_pct':110.25},\n"
            "    {'ticker':'LIVE','month':'2014-02','role':'forward_split','max_abs_gap_diff_pct':66.67,'max_abs_ret3_diff_pct':119.08,'max_abs_range_center_diff_pct':66.47},\n"
            "    {'ticker':'PD','month':'2006-03','role':'forward_split','max_abs_gap_diff_pct':49.81,'max_abs_ret3_diff_pct':52.38,'max_abs_range_center_diff_pct':51.01},\n"
            "    {'ticker':'SAVA','month':'2023-12','role':'forward_split','max_abs_gap_diff_pct':28.49,'max_abs_ret3_diff_pct':35.45,'max_abs_range_center_diff_pct':28.21},\n"
            "    {'ticker':'BXRX','month':'2022-11','role':'control','max_abs_gap_diff_pct':0.0,'max_abs_ret3_diff_pct':0.0,'max_abs_range_center_diff_pct':0.0},\n"
            "    {'ticker':'BNGO','month':'2025-02','role':'control','max_abs_gap_diff_pct':0.0,'max_abs_ret3_diff_pct':0.0,'max_abs_range_center_diff_pct':0.0},\n"
            "])\n"
            "display(Markdown('## 4. Resumen semántico del consumidor'))\n"
            "display(semantic_summary.sort_values(['max_abs_gap_diff_pct'], ascending=False).reset_index(drop=True))"
        )
    )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 4. Cómo leer esta tabla del consumidor\n\n"
            "### Que muestra\n\n"
            "- La divergencia real entre calcular las mismas features cross-session con `raw` y con `split_normalized`.\n\n"
            "### Responde\n\n"
            "- Si `1m_split_normalized` cambia de verdad un uso downstream sensible a splits.\n\n"
            "### Lectura técnica\n\n"
            "- Los reverse splits fuertes enseñan contaminaciones monstruosas bajo `raw`, de miles por ciento.\n"
            "- Los forward splits también pueden deformar materialmente el gap y la memoria multi-sesión.\n"
            "- Los controles a `0.00%` son tan importantes como los positivos fuertes: prueban que la corrección no se inventa donde no toca.\n\n"
            "### Consecuencia\n\n"
            "- Aquí es donde la auditoría deja de ser solo visual sobre precios y se convierte en validación de un uso real."
        )
    )

    for title, img in [
        ("Caso positivo fuerte | BNGO 2025-01", "BNGO_2025_01.png"),
        ("Caso positivo fuerte | CEI 2022-12", "CEI_2022_12.png"),
        ("Control pre-evento | BXRX 2022-11", "BXRX_2022_11.png"),
        ("Control post-evento | BNGO 2025-02", "BNGO_2025_02.png"),
    ]:
        cells.append(
            nbf.v4.new_markdown_cell(
                f"## {title}\n\n"
                "### Que muestra\n\n"
                "- Comparación visual `raw` vs `split_normalized` en el caso elegido.\n\n"
                "### Responde\n\n"
                "- Si el comportamiento del factor y de la serie es coherente con el tipo de caso.\n"
            )
        )
        cells.append(
            nbf.v4.new_code_cell(
                f"display(Image(filename=str(IMAGES_DIR / '{img}')))"
            )
        )

    cells.append(
        nbf.v4.new_markdown_cell(
            "## 5. Veredicto final para inspector\n\n"
            "### Que ya puede afirmarse\n\n"
            "- La semántica de `ohlcv_1m_split_normalized` está bien definida.\n"
            "- El piloto de precio la respeta en patrones positivos y controles.\n"
            "- Un consumidor mínimo real deja de producir falsos shocks cross-session cuando usa la vista correcta.\n\n"
            "### Que no debe afirmarse todavía\n\n"
            "- No es una promoción full-universe cerrada.\n"
            "- No es el final de toda la auditoría de `1m` para cualquier consumidor futuro.\n\n"
            "### Conclusión prudente\n\n"
            "- En el perímetro inspeccionado, los casos de split del piloto quedan semánticamente bien resueltos, visualmente auditados y downstream-válidos en un consumidor mínimo real."
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
