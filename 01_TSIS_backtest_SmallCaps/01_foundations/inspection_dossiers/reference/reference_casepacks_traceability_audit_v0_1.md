# Reference Casepacks Traceability Audit v0.1

Fecha: 2026-06-13
Estado: pass

## Rol

Este documento valida que los casepacks modernos de `reference` no son muestras sueltas sin provenance.

Cada casepack procede de indices historicos en:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/cache_v2
```

Los parquets pesados quedan read-only en la auditoria historica.

## Manifiesto activo

Manifest:

- `evidence_assets/case_manifest/reference_case_manifest_v0_1.csv`
- `evidence_assets/case_manifest/reference_case_manifest_v0_1.md`

Casepacks:

| Casepack | Estado | Rol |
| --- | --- | --- |
| `good_justification/reference_good_identity_and_payload_cases_v0_1.md` | good | identidad buena, split event y dividend event |
| `flagged_case_evidence_packs/reference_review_identity_and_quotes_cases_v0_1.md` | review | simbolos/transient y ticker_change cerca de quotes anomalies |
| `bad_case_evidence_packs/reference_bad_unresolved_identity_cases_v0_1.md` | bad | identidad no resuelta y overview 404 |
| `causal_case_evidence_packs/reference_causal_overlay_cases_v0_1.md` | causal | splits->trades, events->halts, events->quotes |
| `coverage_case_evidence_packs/reference_presence_coverage_cases_v0_1.md` | coverage | overview 404 y gaps de presencia |

## Que muestra

El paquete cubre las familias necesarias para leer `reference` desde masa poblacional hasta casos:

- good identity;
- good corporate action payload;
- review identity;
- review ticker_change/quotes detector;
- bad unresolved identity;
- coverage/presence limits;
- causal overlays.

## Responde

Responde si el dossier moderno tiene casos concretos trazables para cada estado operativo principal.

## No responde

No reemplaza una auditoria visual manual exhaustiva de todos los casos.

Tampoco prueba:

- continuidad economica completa;
- uso de ticker changes como alpha;
- universe membership final;
- ni limpieza total de `quotes`, `trades`, `daily` o `1m`.

## Consecuencia

Los casepacks son suficientes para cerrar la promocion moderna de `reference` como dossier inspector de foundation layer.

No habilitan consumidores sensibles nuevos.

## Veredicto

Pass.

No hay casepacks huerfanos: todos aparecen en el manifest y estan consumidos por el readout v0.2.

