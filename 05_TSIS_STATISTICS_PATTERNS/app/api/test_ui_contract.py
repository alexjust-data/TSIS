from pathlib import Path


APP_ROOT = Path(__file__).parents[1]


def test_cohort_ui_explains_catalog_and_distinguishes_visible_cases() -> None:
    atlas = (APP_ROOT / "app" / "AtlasV2.tsx").read_text(encoding="utf-8")
    css = (APP_ROOT / "app" / "atlas.css").read_text(encoding="utf-8")

    assert "QUÉ SIGNIFICA" in atlas
    assert "Ver las 5 familias" in atlas
    assert "27 etiquetas" not in atlas  # count is reconciled dynamically, not hard-coded in UI
    assert "Mostrando {count(cases.length)} casos más recientes de {count(totalCases)}" in atlas
    assert "Trayectoria mediana" not in atlas
    assert '<div className="path">' not in atlas
    assert ".hero h1{font-size:19px" in css
    assert ".cohort-title h2{display:flex;align-items:baseline" in css


def test_case_ui_links_labels_to_full_lifetime_chart() -> None:
    atlas = (APP_ROOT / "app" / "AtlasV2.tsx").read_text(encoding="utf-8")
    chart = (APP_ROOT / "app" / "TradingChart.tsx").read_text(encoding="utf-8")

    assert "onClick={() => void selectCaseActivation(row.activation_label)}" in atlas
    assert "rows={detail.context}" in atlas
    assert "occurrences={detail.occurrences}" in atlas
    assert "selectedLabel={detail.selected_activation_label}" in atlas
    assert "HistogramSeries" in chart
    assert "chart.timeScale().fitContent()" in chart
    assert "position: 'belowBar'" in chart
    assert "position: 'aboveBar'" in chart
    assert "Vida completa" in chart
    assert "Centrar D0" in chart
