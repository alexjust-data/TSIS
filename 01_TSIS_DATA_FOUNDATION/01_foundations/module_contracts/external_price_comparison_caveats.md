# External Price Comparison Caveats - Modulo 01

## 1. Rol del documento

Este documento fija la politica transversal del modulo para comparar precios internos con plataformas externas como:

- TradingView
- Yahoo Finance
- brokers
- vendors publicos
- o cualquier charting front-end equivalente

Su objetivo es evitar falsos diagnosticos cuando dos graficos aparentan mostrar el mismo ticker y la misma fecha, pero no la misma serie economica.

La politica fundacional de semantica de precio y uso en backtest/ML vive en:

- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`

Companion compacto:

- `01_foundations/module_contracts/external_price_comparison_rules_line_by_line.md`

## 2. Principio rector

Una comparacion externa de precio no es valida por defecto.

Antes de interpretar una discrepancia, debe declararse explicitamente:

- si la serie interna es `raw` o `adjusted`
- si la serie externa es `raw`, `adjusted` o desconocida
- y que politica de ajuste o continuidad historica puede estar actuando

## 3. Fuentes tipicas de discrepancia

Las divergencias entre el precio interno y una plataforma externa pueden venir de:

- dividendos acumulados
- splits
- ticker remaps o ticker changes
- continuidad historica del simbolo
- vendor-specific adjustments
- series `raw` frente a series `adjusted`
- diferencias de venue o consolidacion
- diferencias de calendario de sesion o timezone

Estas divergencias no deben interpretarse automaticamente como error del dataset base.

## 4. Regla institucional

Cuando un precio interno no coincida con una plataforma externa, el modulo debe evaluar primero si la discrepancia puede explicarse por:

- ajuste por dividendos
- ajuste por splits
- remap historico del ticker
- o politica externa de continuidad/ajuste del vendor

Solo despues de descartar esas causas puede abrirse una hipotesis de error material del dataset interno.

## 5. Regla de comparacion operativa

Toda comparacion externa relevante debe etiquetarse como una de estas tres:

- `raw_vs_raw`
- `raw_vs_adjusted`
- `adjusted_proxy_vs_adjusted`

Si no puede saberse con suficiente confianza que serie externa se esta viendo, la comparacion debe marcarse como:

- `external_series_not_fully_identified`

## 6. Regla reforzada para tickers con dividendos

Cuando el ticker tenga dividendos relevantes, el modulo debe contemplar dos vistas de contraste:

- vista `raw`
- vista `adjusted_proxy`

La `adjusted_proxy` puede construirse inicialmente como una aproximacion razonable basada en:

- dividendos posteriores al evento
- splits relevantes
- y otros ajustes institucionalmente reconocidos

Su funcion es:

- comprobar si la divergencia visual con la plataforma externa es plausible;
- y distinguir entre `mismatch explicado por ajuste` y `mismatch todavia no explicado`.

La `adjusted_proxy` no sustituye la serie institucional base.

Solo sirve como capa de contraste y explicacion.

## 7. Relacion con los contratos de dataset

Esta politica transversal aplica especialmente a:

- `daily`
- `quotes`

Y debe enlazarse desde sus contratos y, cuando proceda, desde sus dossiers de inspeccion.

## 8. Relacion con los dossiers

Cuando un dossier compare una serie interna con una plataforma externa, debe dejar explicitamente anotado:

- que serie interna se uso
- si era `raw` o `adjusted_proxy`
- que hipotesis explica la discrepancia
- y si la discrepancia queda:
  - `explicada por ajuste`
  - `parcialmente explicada`
  - o `todavia abierta`

## 9. Conclusion operacional

En el modulo 01, una discrepancia visual con una plataforma externa no desacredita por si sola la serie interna.

La lectura correcta es:

- primero identificar el tipo de serie comparada;
- despues evaluar dividendos, splits y remaps;
- y solo al final decidir si existe un problema real del dataset institucional.

Para la arquitectura general de vistas `raw`, `split_normalized`, `adjusted` y `adjusted_proxy`, ver:

- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`

## 10. Respaldo institucional y cientifico

Esta politica se apoya en:

- metodologias institucionales de corporate actions y ajuste de precios;
- literatura de asset pricing que exige retornos comparables;
- y practica cuantitativa que separa senal, ejecucion y benchmarking.

Referencias recomendadas:

- CRSP, *US Stock & Indexes Databases Calculations & Index Methodologies*:
  - https://www.crsp.org/wp-content/uploads/guides/CRSP_Calculations_and_Index_Methodologies.pdf
- Kenneth R. French Data Library:
  - https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- Marcos Lopez de Prado, *Beyond Econometrics: A Roadmap Towards Financial Machine Learning*:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3365282
- Shihao Gu, Bryan Kelly, Dacheng Xiu, *Empirical Asset Pricing via Machine Learning*:
  - https://www.nber.org/papers/w25398
- Andrea Frazzini, Ronen Israel, Tobias Moskowitz, *Trading Costs of Asset Pricing Anomalies*:
  - https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs-of-Asset-Pricing-Anomalies?aqrPDF=1

Lectura institucional derivada:

- una diferencia visual con TradingView, Yahoo u otra plataforma puede ser perfectamente compatible con una serie interna correcta;
- la pregunta correcta no es solo "cuanto difiere el precio", sino "que semantica de precio representa cada lado";
- y el modulo debe dejarlo explicitamente anotado antes de abrir una hipotesis de error del dataset.
