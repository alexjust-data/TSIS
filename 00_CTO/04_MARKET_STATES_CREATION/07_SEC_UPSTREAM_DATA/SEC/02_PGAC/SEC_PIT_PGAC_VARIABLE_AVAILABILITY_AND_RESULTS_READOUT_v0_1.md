# SEC PIT PGAC Variable Availability and Results Readout `v0_1`

No. La descarga de PGAC terminó correctamente, pero todavía no se han extraído ni materializado todas las variables del proyecto.

PGAC tiene ahora 68 documentos SEC primarios verificados. Eso certifica la adquisición, no los valores fundamentales. El siguiente paso debe ser ejecutar el pipeline de extracción, reconciliación PIT y auditoría variable por variable.

## Las 10 variables PIT objetivo

Estas son las salidas institucionales definidas por el [contrato de outputs diarios PIT](DAILY_PIT_FUNDAMENTAL_CONTEXT_OUTPUTS_REFERENCE_v0_1.md):

| Variable objetivo | Resultado actual para PGAC | Evidencia disponible |
|---|---|---|
| `SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN` | **No extraída** | 14 documentos candidatos para O/S; una búsqueda textual preliminar detecta marcadores en 7 documentos. |
| `FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN` | **No calculada** | 47 documentos candidatos de ownership y 34 de beneficial owners, pero faltan extracción, deduplicación y resolución temporal. |
| `FLOAT_TRADABILITY_ELIGIBILITY_ESTIMATE_AS_KNOWN` | **No calculada** | 10 documentos candidatos de restricciones; 9 contienen marcadores de lockup/restricción. Esto no demuestra libre negociabilidad. |
| `FLOAT_PERCENT_ESTIMATE_AS_KNOWN` | **No calculada** | Depende de O/S y float owner-exclusion. Además, hay que corregir una discrepancia entre el contrato `%` y el código, que actualmente parece producir una fracción 0–1. |
| `INSIDER_AFFILIATE_OWNERSHIP_PERCENT_AS_KNOWN` | **No implementada como salida separada** | Hay documentos de ownership, pero no una serie diaria específica y gobernada de insiders/afiliados. |
| `LARGE_BENEFICIAL_OWNER_PERCENT_AS_KNOWN` | **No implementada como salida separada** | Los Schedule 13D/13G proporcionan candidatos, pero aún no se han reconciliado titulares, amendments, fechas y duplicados. |
| `INSTITUTIONAL_OWNERSHIP_PERCENT_AS_KNOWN` | **No disponible** | Requiere la adquisición global independiente de information tables 13F. Los filings del issuer PGAC no sustituyen esa fuente. |
| `PRESESSION_REFERENCE_MARKET_CAP` | **No calculada** | Requiere O/S PIT reconciliado y precio de cierre previo ajustado a la base corporativa correcta. |
| `ENTERPRISE_VALUE_ESTIMATE_AS_KNOWN` | **No calculada** | Existen filings periódicos candidatos, pero todavía no se han extraído y reconciliado cash, debt, preferred equity y otros componentes. |
| `NET_CASH_PER_SHARE_ESTIMATE_AS_KNOWN` | **No calculada** | Depende de cash, debt y O/S PIT; ninguno ha sido materializado todavía para PGAC desde esta descarga. |

Por tanto, el resultado actual para estas diez variables es:

- **0/10 materializadas para PGAC desde la nueva descarga SEC.**
- **8/10 tienen alguna evidencia documental candidata.**
- **1/10 —institutional ownership— necesita una fuente global 13F todavía no adquirida.**
- **1/10 —float tradability— puede seguir siendo `UNAVAILABLE` incluso después de extraer los documentos si no existe prueba positiva de libre negociabilidad.**

## Qué contienen los 68 documentos PGAC

La adquisición sí produjo una buena base documental:

- 47 documentos candidatos de ownership.
- 34 candidatos de beneficial-owner events.
- 14 candidatos para shares outstanding.
- 10 candidatos de restricciones y tradabilidad.
- 10 candidatos de eventos 8-K.
- 7 periodic anchors.
- 6 candidatos de registration chain.
- 6 eventos Forms 3/4/5.
- 4 proxy ownership anchors.
- 1 documento de lifecycle.

Sin embargo, el enlace documento–instrumento todavía no está demostrado de forma definitiva:

- 45 documentos son candidatos de prehistoria y necesitan revisión entre posibles instrumentos.
- 13 pertenecen al intervalo objetivo, pero solo están clasificados como candidato único, no como vínculo probado.
- 10 son posteriores al intervalo y no tienen candidato instrumental.

El run está identificado por `run_id=sec_pit_pgac_primary_v0_2_20260811T1035Z`; su `final_manifest.json` se incluye en el paquete externo de auditoría.

## Comparación con lo ya obtenido para BNAI

BNAI sí pasó por una primera ejecución experimental de extracción:

| Variable | Resultado BNAI |
|---|---:|
| Shares outstanding | 485/496 sesiones; entre 33,296,995 y 42,274,461 acciones |
| Float owner-exclusion | 82/496 sesiones; entre 32,301,749 y 32,317,476 |
| Float percent | 82/496, pero **no certificable todavía por la discrepancia de unidad** |
| Tradability eligibility | 0/496; bloqueada por falta de evidencia positiva |
| Insider/affiliate ownership % | No materializada separadamente |
| Large beneficial owner % | No materializada separadamente |
| Institutional ownership % | No disponible; falta adquisición global 13F |
| Presession market cap | 485/496; entre $5.07M y $266.33M |
| Core enterprise value | 391/496; entre $8.72M y $269.97M |
| Core net cash/share | 391/496; entre -$0.8620 y -$0.0409 |

La matriz metodológica BNAI completa está en [SEC_PIT_IMPLEMENTATION_READOUT_v0_1.md](SEC_PIT_IMPLEMENTATION_READOUT_v0_1.md).

## Las 63 métricas contables existentes para PGAC

Existe además otro dataset, `fundamentals_asof_table_v0_1`, que contiene cuatro filas de PGAC:

- 2 income statements.
- 1 balance sheet.
- 1 cash-flow statement.
- Las 4 filas pasan su control temporal.
- Periodo terminado el `2025-09-30`.
- Filing disponible el `2025-11-10`.
- 43 de las 63 métricas tienen algún valor.
- 20 de las 63 están ausentes.

Importante: estos valores proceden del dataset financiero vendor ya gobernado; **no son resultados extraídos de los 68 documentos SEC recién descargados**.

### Income statement: 19 métricas

Con valor:

- `cost_of_revenue`: 0 / 0
- `other_operating_expenses`: 225,283 / 747,972
- `total_operating_expenses`: 225,283 / 747,972
- `operating_income`: -225,283 / -747,972
- `other_income_expense`: 0 / 0
- `total_other_income_expense`: 911,969 / 2,709,511
- `income_before_income_taxes`: 686,686 / 1,961,539
- `consolidated_net_income_loss`: 686,686 / 1,961,539
- `net_income_loss_attributable_common_shareholders`: 149,507 / 858,607
- `basic_earnings_per_share`: 0.06 / 0.12
- `diluted_earnings_per_share`: 0.06 / 0.12
- `basic_shares_outstanding`: 2,400,500 / 4,425,375
- `diluted_shares_outstanding`: 2,400,500 / 4,425,375
- `ebitda`: -225,283 / -747,972

Ausentes:

- `revenue`
- `gross_profit`
- `selling_general_administrative`
- `interest_expense`
- `income_taxes`

### Balance sheet: 26 métricas

Con valor:

- `cash_and_equivalents`: 349,018
- `receivables`: 0
- `other_current_assets`: 107,869
- `total_current_assets`: 456,887
- `other_assets`: 89,228,389
- `total_assets`: 89,685,276
- `accounts_payable`: 117,265
- `accrued_and_other_current_liabilities`: 457,500
- `total_current_liabilities`: 574,765
- `other_noncurrent_liabilities`: 862,500
- `total_liabilities`: 1,437,265
- `common_stock`: 240
- `retained_earnings_deficit`: -980,618
- `other_equity`: 0
- `total_equity_parent`: -980,378
- `total_equity`: -980,378
- `total_liabilities_and_equity`: 89,685,276

Ausentes:

- `inventories`
- `property_plant_equipment_net`
- `intangible_assets`
- `additional_paid_in_capital`
- `accumulated_other_comprehensive_income`
- `long_term_debt_and_capital_lease`
- `goodwill`
- `debt_current`
- `preferred_stock`

### Cash flow: 18 métricas

Con valor:

- `other_operating_activities`: -911,969
- `change_other_operating_assets_liabilities`: -2,843
- `other_investing_activities`: 0
- `long_term_debt_issuances_repayments`: 282,500
- `dividends`: 0
- `other_financing_activities`: 0
- `net_income`: 686,686
- `cash_from_operations_continuing`: -228,126
- `net_cash_from_operations`: -228,126
- `cash_from_financing_continuing`: 282,500
- `net_cash_from_financing`: 282,500
- `change_in_cash`: 54,374

Ausentes:

- `depreciation_and_amortization`
- `capital_expenditure_purchase`
- `property_plant_equipment_sale`
- `cash_from_investing_continuing`
- `net_cash_from_investing`
- `foreign_exchange_effect`

El schema de estas métricas se incluye en el paquete externo como `fundamentals_asof_table_schema_contract.md`.

Conclusión: **la descarga PGAC es válida, pero aún no podemos afirmar que las variables fundamentales estén extraídas**. Antes de descargar otro ticker debemos ejecutar sobre PGAC el probe completo: enlace inequívoco documento–instrumento, extracción, reconciliación, resolución diaria PIT y auditoría de las diez salidas. Así evitamos multiplicar una descarga cuyo pipeline de variables todavía no ha sido certificado.
