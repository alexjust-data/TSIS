from __future__ import annotations

import pandas as pd


def build_taxonomy_side_view(taxonomy_side: pd.DataFrame) -> pd.DataFrame:
    taxonomy_side_view = taxonomy_side[
        [
            "taxonomy",
            "break_side",
            "files",
            "pct_in_taxonomy",
            "median_abs_break",
            "p95_abs_break",
            "median_pct_break",
            "p95_pct_break",
        ]
    ].sort_values(["taxonomy", "files"], ascending=[True, False]).copy()

    for col in [
        "pct_in_taxonomy",
        "median_abs_break",
        "p95_abs_break",
        "median_pct_break",
        "p95_pct_break",
    ]:
        taxonomy_side_view[col] = pd.to_numeric(taxonomy_side_view[col], errors="coerce").round(3)

    return taxonomy_side_view
