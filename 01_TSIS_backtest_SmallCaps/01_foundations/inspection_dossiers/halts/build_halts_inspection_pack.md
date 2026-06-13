# Build Halts Inspection Pack v0.1

## Objetivo

Construir el pack moderno de inspeccion de `halts_v0_1` sin mover ni modificar datos raw/historicos.

El builder convierte la auditoria historica preservada en artefactos ligeros de foundation:

- inventories;
- root audit;
- population summary;
- population visuals;
- casepack manifest;
- casepacks interpretados;
- run manifest.

## Script residente

- `scripts/inspection/halts/build_halts_inspection_pack.py`

## Comando

Desde `C:\TSIS_Data`:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\inspection\halts\build_halts_inspection_pack.py" --json
```

## Inputs read-only

Raices fisicas:

- `E:\TSIS\data\Halts`
- `D:\Halts`

Auditoria historica:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/cache_v2/`

Certification historica:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/`

## Outputs

Todos los outputs viven bajo:

- `01_foundations/inspection_dossiers/halts/`

Outputs del run `2026-06-13`:

| Output | Rows / count |
| --- | ---: |
| historical cache inventory | 19 rows |
| certification inventory | 10 rows |
| physical root audit | 6 rows |
| population summary | 16 rows |
| population visuals | 5 PNG |
| casepacks | 5 markdown packs |

## Garantias

El `run_manifest.json` declara:

- `status: pass`;
- no raw data was modified;
- historical parquets were not copied to foundations;
- outputs are lightweight manifests, summaries, visuals and casepacks.

## Rol de notebooks

No se crea notebook nuevo para `halts` en esta version porque:

- la auditoria historica ya cerro la lectura profunda;
- el dataset es event/reference, no un tape continuo que requiera navegacion ticker-month como `minute`;
- el builder residente produce outputs estables y markdowns promovidos;
- y las conclusiones no quedan encerradas en un notebook.

Si en el futuro se necesita un inspector interactivo, debe ser launcher/drilldown humano. La logica pesada debe permanecer en scripts residentes y cualquier conclusion estable debe promoverse a readout/manifest/casepack.

## Regla final

El builder puede regenerar artefactos de foundation, pero no debe escribir en:

- `E:\TSIS\data`;
- `C:\TSIS_Data\data`;
- `01_research`;
- `run`;
- `runs`.
