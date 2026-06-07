from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"


SETUP = r"""
from pathlib import Path
import subprocess
import sys

import ipywidgets as widgets
import pandas as pd
from IPython.display import Image, Markdown, display, clear_output

PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"
CORE_ROOT = DOSSIER_DIR / "evidence_assets" / "core_quality"
CASEPACK_ROOT = DOSSIER_DIR / "core_quality_case_evidence_packs"
MANIFEST_PATH = CORE_ROOT / "minute_core_quality_manifest_v0_1.parquet"
VISUAL_MANIFEST_PATH = CASEPACK_ROOT / "minute_core_quality_visual_case_manifest_v0_1.csv"
VISUAL_READOUT_PATH = CASEPACK_ROOT / "minute_core_quality_visual_cases_v0_1.md"
"""


def nb(cells):
    notebook = nbf.v4.new_notebook()
    notebook["cells"] = cells
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "pygments_lexer": "ipython3"}
    return notebook


def write(name: str, cells) -> None:
    path = DOSSIER_DIR / name
    nbf.write(nb(cells), path)
    print(path)


def main() -> None:
    write(
        "minute_00_universe_quality_overview_v0_1.ipynb",
        [
            nbf.v4.new_markdown_cell("# Minute 00 | Universe Quality Overview\n\nLauncher notebook. Heavy logic lives in scripts and persisted assets."),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(
                "df = pd.read_parquet(MANIFEST_PATH)\n"
                "display(Markdown(f'Rows: `{len(df):,}` | tickers: `{df.ticker.nunique():,}` | years: `{int(df.year.min())}-{int(df.year.max())}`'))\n"
                "display(df[['core_quality_state','vw_quality_state','combined_quality_state','allowed_consumption']].describe(include='all'))"
            ),
            nbf.v4.new_code_cell(
                "for col in ['core_quality_state','vw_quality_state','combined_quality_state','allowed_consumption','core_issue_family','vw_issue_family']:\n"
                "    display(Markdown(f'## {col}'))\n"
                "    display(df[col].astype(str).value_counts().to_frame('count'))"
            ),
        ],
    )

    write(
        "minute_01_core_quality_model_v0_1.ipynb",
        [
            nbf.v4.new_markdown_cell(
                "# Minute 01 | Core Quality Model\n\nLauncher notebook. It does not keep materialization logic in cells. Use the script layer for reproducible exports."
            ),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(
                "display(Markdown('Existing core manifest:'))\n"
                "display(Markdown(f'`{MANIFEST_PATH}` exists = `{MANIFEST_PATH.exists()}`'))\n"
                "display(pd.read_csv(CORE_ROOT / 'minute_core_quality_summary_v0_1.csv'))"
            ),
            nbf.v4.new_code_cell(
                "display(Markdown('To regenerate visual casepacks from persisted manifest:'))\n"
                "display(Markdown('`python scripts/inspection/minute/export_minute_core_quality_casepacks.py`'))"
            ),
        ],
    )

    write(
        "minute_02_core_quality_population_readout_v0_1.ipynb",
        [
            nbf.v4.new_markdown_cell("# Minute 02 | Core Quality Population Readout\n\nLight readout over persisted manifests."),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(
                "df = pd.read_parquet(MANIFEST_PATH)\n"
                "matrix = pd.crosstab(df['core_quality_state'], df['vw_quality_state'])\n"
                "display(matrix)\n"
                "display(pd.read_csv(CORE_ROOT / 'minute_core_quality_family_counts_v0_1.csv'))"
            ),
        ],
    )

    write(
        "minute_03_casepack_builder_v0_1.ipynb",
        [
            nbf.v4.new_markdown_cell(
                "# Minute 03 | Casepack Builder Launcher\n\nRuns the script that exports fixed visual casepacks. Heavy plotting lives outside the notebook."
            ),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(
                "cmd = [sys.executable, str(PROJECT_ROOT / 'scripts' / 'inspection' / 'minute' / 'export_minute_core_quality_casepacks.py')]\n"
                "display(Markdown('Command: `' + ' '.join(cmd) + '`'))\n"
                "# Uncomment to regenerate:\n"
                "# subprocess.run(cmd, check=True)"
            ),
            nbf.v4.new_code_cell(
                "visual = pd.read_csv(VISUAL_MANIFEST_PATH)\n"
                "display(visual.groupby('visual_section').size().to_frame('cases'))\n"
                "display(visual[['visual_section','visual_rank','ticker','year','month','image']])"
            ),
        ],
    )

    write(
        "minute_04_ticker_month_inspector_v0_1.ipynb",
        [
            nbf.v4.new_markdown_cell("# Minute 04 | Ticker-Month Inspector\n\nWidget viewer over exported PNGs. No heavy plotting in cells."),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(
                "visual = pd.read_csv(VISUAL_MANIFEST_PATH)\n"
                "options = [(f\"{r.visual_section} | {int(r.visual_rank):02d} | {r.ticker} {int(r.year)}-{int(r.month):02d}\", i) for i, r in visual.iterrows()]\n"
                "dropdown = widgets.Dropdown(options=options, description='case', layout=widgets.Layout(width='900px'))\n"
                "out = widgets.Output()\n"
                "def show(change=None):\n"
                "    with out:\n"
                "        clear_output(wait=True)\n"
                "        r = visual.iloc[dropdown.value]\n"
                "        display(Markdown(f\"## {r.ticker} {int(r.year)}-{int(r.month):02d}\"))\n"
                "        display(Image(filename=str(CASEPACK_ROOT / r.image)))\n"
                "        display(r.to_frame('value'))\n"
                "dropdown.observe(show, names='value')\n"
                "display(dropdown, out)\n"
                "show()"
            ),
        ],
    )

    write(
        "minute_05_final_readout_v0_1.ipynb",
        [
            nbf.v4.new_markdown_cell("# Minute 05 | Final Readout\n\nLight entrypoint linking the fixed visual dossier and manifests."),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(
                "display(Markdown(f'Visual readout: `{VISUAL_READOUT_PATH}`'))\n"
                "display(Markdown(f'Visual manifest: `{VISUAL_MANIFEST_PATH}`'))\n"
                "visual = pd.read_csv(VISUAL_MANIFEST_PATH)\n"
                "display(visual.groupby(['visual_section']).size().to_frame('cases'))"
            ),
        ],
    )


if __name__ == "__main__":
    main()
