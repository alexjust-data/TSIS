# Data Quality Harness

Estado: design-to-runtime bridge v0.3
Fecha: 2026-06-13
Ambito: auditoria historica de data y futura vigilancia live de TSIS.

## Rol

Este Harness convierte la auditoria historica de `01_TSIS_backtest_SmallCaps/01_foundations` en un sistema operativo agentico.

No existe para inventar una auditoria paralela.
Existe para que un agente pueda:

- leer contratos;
- verificar roots fisicos;
- producir evidence assets;
- generar readouts;
- construir notebooks inspectores cuando sean necesarios;
- generar visuales estables y casepacks;
- interpretar visuales uno a uno;
- validar manifests;
- actualizar registries/policies/validators;
- y dejar una decision de consumo defendible.

## Correccion operativa v0.2

Para el siguiente run se usara un solo agente, estilo SersanSistemas.

El modelo multi-agente queda como arquitectura futura, no como ejecucion nocturna inmediata.

La razon es practica: aun no existe un orquestador runtime que coordine locks, integracion, revision cruzada y promocion de estado. Hasta que exista, un solo agente autonomo debe ejecutar el ciclo completo de forma secuencial y dejar trazabilidad.

## Correccion operativa v0.3

Antes de completar datasets pendientes, el Harness debe preservar y promocionar la auditoria historica ya hecha.

La auditoria historica bajo:

```text
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/
```

contiene trabajo profundo para `additional`, `halts`, `reference` y `short`: contratos, notebooks, builders, caches, closeouts, causal overlays y certificaciones.

Por tanto, un agente no debe reauditar esas carpetas desde cero. Primero debe leer la auditoria historica, compararla contra `01_foundations`, declarar que esta ya promovido, que falta, y trabajar una sola carpeta/dataset antes de parar para revision humana.

## Documentos activos

Leer en este orden:

1. `data_audit_harness_agentic_operating_map.md`
   - Snapshot auditor de `01_foundations` y mapa general para convertir la auditoria historica en Harness.
2. `historical_audit_preservation_and_promotion_contract.md`
   - Contrato de preservacion: obliga a leer y reconciliar la auditoria historica de `additional`, `halts`, `reference` y `short` antes de crear artefactos modernos.
3. `data_audit_completion_artifact_contract.md`
   - Contrato comun de outputs para cerrar datasets pendientes con calidad comparable a `daily`, `quotes`, `trades` y `1m`.
4. `runbooks/2026-06-12_overnight_data_audit_completion_harness_runbook.md`
   - Runbook single-agent para cerrar datasets pendientes.
5. `runbooks/2026-06-12_data_audit_agent_prompt_pack.md`
   - Prompt unico recomendado para el agente Codex autonomo.
6. `future_live_data_quality_contract.md`
   - Seed futuro para live data quality. No es todavia runtime operativo.

## Datasets maduros usados como benchmark

El estandar de excelencia actual no es solo documental. Es un sistema inspector completo.

Un dataset pendiente no esta a la altura si solo tiene README, contrato, registry y policy. Debe aproximarse, cuando aplique, al patron real de los bloques maduros:

- `daily`
  - separa calidad del bar y coverage;
  - tiene readout principal, build guide, casepacks de good/flagged/bad/coverage, imagenes y assets;
  - no colapsa gaps de coverage en `good/bad`.
- `quotes`
  - separa calidad local del libro, severidad economica, crossed/locked behavior, contexto externo y consumo;
  - usa imagenes globales, casepacks por estado, manifests y auditoria de casepacks abiertos;
  - no trata contexto externo como rehabilitacion automatica.
- `trades`
  - combina readouts, notebooks inspectores, universo global `57f`, visuales poblacionales, manifests estratificados, family casepacks y scripts residentes;
  - distingue snapshot poblacional, muestra metodologica, full closeout, familias semanticas y estado final;
  - no usa `good` como proxy de utilidad total.
- `minute / ohlcv_1m_raw`
  - tiene notebooks modernos `minute_00` a `minute_05`, incluyendo notebooks con widgets;
  - separa core OHLCV y `vw`;
  - tiene un dossier visual fijo de `67` imagenes: `7` mapas poblacionales y `60` casos;
  - cada imagen se lee individualmente con `Que muestra / Responde / No responde / Consecuencia`.
- `1m_split_normalized`
  - trata una capa derivada, no raw 1m;
  - tiene readout final, notebooks, mapa visual poblacional, casepacks de eventos split y auditoria full-universe de eventos auditables;
  - distingue auditoria full-universe de eventos de materializacion fisica full-universe.

Un dataset pendiente no debe considerarse cerrado al mismo nivel si solo tiene contrato narrativo.
Debe tener, cuando aplique:

- README local;
- dataset contract;
- canonical schemas;
- dataset registry;
- consumption policy;
- validators;
- inspection readout;
- evidence assets;
- manifests;
- casepacks;
- builder/toolchain residente;
- changelog;
- y estado de madurez honesto.

## Regla sobre notebooks

Los notebooks no son almacenes de codigo.

En este proyecto cumplen roles inspectores:

- exploracion;
- lectura de outputs ejecutados;
- widgets y selectores para navegar casos;
- drilldown por ticker, fecha, mes, familia o estado;
- generacion inicial de evidencia;
- y validacion humana de hipotesis.

La logica pesada y estable debe vivir, cuando el formato este claro, en scripts o builders residentes bajo:

```text
01_TSIS_backtest_SmallCaps/scripts/inspection/<dataset>/
```

Si un notebook demuestra una conclusion estable, esa conclusion debe quedar encapsulada en markdown institucional, manifest, visual pack o asset persistido. No debe quedar solo dentro del notebook.

## Regla visual

Las imagenes no son decoracion.

Todo visual, tabla o panel relevante debe declarar:

```text
Que muestra
Responde
No responde
Consecuencia
```

Ademas, la explicacion debe salir de la lectura real del visual.

Reglas:

- si el fenomeno se ve, hay que decir donde se ve;
- si no se ve bien, hay que decirlo;
- si el panel no prueba la causa, debe pedirse panel o tabla complementaria;
- no se puede justificar un caso solo por el nombre del bucket;
- no se puede sustituir mapa poblacional por dos ejemplos bonitos;
- no se puede sustituir caso forense por solo estadistica agregada.

## Datasets pendientes de cierre moderno

Foto operacional a 2026-06-13:

| Dataset/root | Estado actual | Decision Harness |
| --- | --- | --- |
| `reference` | auditoria historica profunda cerrada; foundation minima promovida; gap inspector documentado | no reauditar; completar promocion moderna desde la auditoria historica y parar |
| `halts` / `E:/TSIS/data/Halts` | auditoria historica profunda cerrada y certificada; promocion foundation incompleta | no re-descargar ni reconstruir; promover contract/registry/policy/validators/dossier desde evidencia historica |
| `additional` | auditoria historica profunda cerrada; foundation minima existe | no tratar como dataset plano; promocionar subbloques y gaps modernos solo donde aporten decision |
| `short` | auditoria historica profunda cerrada; foundation minima existe; FINRA baseline preservado | no tratar Polygon short como baseline; promocionar policy/evidence moderna condicionada |
| `E:/TSIS/data/financial` | schemas existen, sin paquete foundation completo | cerrar contrato, registry, policy, validator y dossier |
| `E:/TSIS/data/regime_indicators` | schemas existen, sin paquete foundation completo | cerrar como capa de contexto/indicadores, no como alpha |

Fuera de alcance para este Harness:

- `E:/TSIS/data/images_Flash_Research`

`images_Flash_Research` no forma parte del cierre de auditoria Polygon de este Harness. No debe inventariarse, moverse, validar, OCRizar ni institucionalizarse en este run.

## Rutas de no tocar

Prohibido modificar, mover, limpiar, normalizar o reorganizar:

```text
E:/TSIS/data/
C:/TSIS_Data/data/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/run/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/
```

Esas rutas solo se leen como evidencia y provenance.

El trabajo nuevo vive en:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/<dataset>/
```

## Regla de ejecucion recomendada

El siguiente run debe ejecutarse con un unico agente autonomo.

Orden:

1. Leer contratos raiz, locales y CTO/Harness.
2. Leer `historical_audit_preservation_and_promotion_contract.md`.
3. Leer el contrato de dossier inspector.
4. Leer los benchmarks maduros, incluyendo notebooks y visual packs declarados.
5. Seleccionar una sola carpeta/dataset.
6. Leer auditoria historica y certificacion si existen.
7. Comparar contra `01_foundations`.
8. Crear `integration_notes.md` o promotion gap antes de tocar indices globales.
9. Completar solo esa carpeta/dataset.
10. Validar.
11. Parar para revision humana.

Si el tiempo no alcanza, el agente debe preservar trazabilidad y no sobrepromover estado.

No se debe ejecutar una cadena completa `reference -> Halts -> financial -> regime_indicators` sin revision humana entre carpetas mientras el Harness este en esta fase.

## Regla final

El objetivo del Harness no es que "termine el agente".
El objetivo es que cada dataset quede con evidencia suficiente para que otro humano o agente pueda inspeccionar la decision sin depender del chat.
