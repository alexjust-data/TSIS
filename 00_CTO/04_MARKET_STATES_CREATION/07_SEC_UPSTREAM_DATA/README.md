El proceso SEC PIT no está en una única carpeta. En `C:\TSIS_Data` está dividido por función; los documentos pesados descargados están en `D:`.

## Preparación vigente Massive SEC v0.1

La descarga Massive todavía no está autorizada. La autoridad de alcance es
01_MASSIVE_SEC_OBJETIVO_01.md; el plan ejecutable/recovery y el registro vivo
son 04_MASSIVE_SEC_ACQUISITION_EXECUTION_AND_RECOVERY_PLAN_v0_1.md y
05_MASSIVE_SEC_ACQUISITION_MILESTONE_REGISTER_v0_1.md. El output pesado
reservado es D:/sec_float_pit_MASSIVE. El plan-only pasó sin red ni escritura
en D; licencia/retención, probe live y full run siguen pendientes.

Para entregar a otro agente la preparación específica de Massive SEC, usar:

- [Handoff Massive SEC vigente](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/02_MASSIVE_SEC_AGENT_HANDOFF_v0_2.md)

Los artefactos v0.1 se conservan como handoff histórico previo a la
implementación y no describen el estado ejecutable vigente.

El ZIP v0.1 original es contexto histórico portable y no constituye
autorización para lanzar una descarga larga.

La antigua carpeta:

```text
C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\_DESCAGRA_DATOS_NECESARIA_
```

ya no existe. Fue reorganizada en la estructura siguiente.

## 1. Arquitectura y documentación principal

La raíz conceptual actual es:

[SEC upstream](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/SEC)

Contiene:

```text
SEC/
├── 00_CONTRACTS
├── 01_SCALE_CONTROL
├── 02_PGAC
├── 03_SEVEN_TICKER_PROBES
├── 04_COHORT_01
├── 05_FORM_13F
├── 06_OUTPUT_REFERENCES
└── 07_AUDITS
```

Para entender la ejecución de los 4.824, el documento principal es:

[Plan de adquisición descendente 4.824](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/SEC/04_COHORT_01/SEC_PIT_4824_DESCENDING_ACQUISITION_EXECUTION_PLAN_v0_1.md)

Los contratos fundamentales están en:

[Contratos SEC PIT](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/SEC/00_CONTRACTS)

Especialmente:

- [Contrato de adquisición y resolución](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/SEC/00_CONTRACTS/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md)
- [Metodología owner-exclusion](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/SEC/00_CONTRACTS/SEC_PIT_OWNER_EXCLUSION_METHODOLOGY_CONTRACT_v0_1.md)
- [Selección lifecycle](C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/SEC/00_CONTRACTS/SEC_PIT_LIFECYCLE_SOURCE_SELECTION_POLICY_v0_2.md)

## 2. Código ejecutable

Todo el código de adquisición, parsing, O/S, ownership y float está aquí:

[Código SEC PIT](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit)

Entradas importantes:

```text
run_submissions_metadata_profile.py
build_4824_cohort_metadata_gate.py
run_authorized_primary_acquisition_v0_2.py
run_owner_exclusion_resolution_batch.py
ownership_v2.py
float_estimate.py
class_os_extract_v3.py
monitor_authorized_primary_acquisition_v0_2.ps1
```

Su orientación técnica está en:

[README del código SEC PIT](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/README.md)

## 3. Configuraciones y autorizaciones

Están en:

[Configs de Data Foundation](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs)

Los archivos SEC empiezan por:

```text
sec_pit_*.json
```

La autorización concreta de los primeros 250 tickers es:

[Autorización C01 tranche 01](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/sec_pit_primary_download_authorization_c01_t01_0250_v0_1_20260814.json)

## 4. Contratos operativos, schemas y policies

- [Contrato del almacenamiento SEC](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/sec_pit/sec_pit_storage_root_and_legacy_pilot_decision_v0_1.md)
- [Schemas SEC PIT](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas)
- [Policies de consumo](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies)
- [Validadores SEC](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/validators/sec_pit)

## 5. Resultados de pruebas y auditorías científicas

Los readouts de PGAC, siete tickers, 100 casos, shards y versiones v0.13–v0.21 están aquí:

[Dossiers SEC PIT](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit)

El punto de entrada es:

[Handoff SEC PIT](C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/README.md)

Este README está algo desactualizado respecto a la descarga posterior de los primeros 250.

## 6. Runtime de la ejecución 4.824

Los manifests, metadata, gates, logs y auditoría posdescarga están aquí:

[Runtime 4.824](C:/TSIS_Data/runtime/sec_pit_4824_descending_acquisition_v0_1)

Estructura:

```text
sec_pit_4824_descending_acquisition_v0_1/
├── preflight_20260813T215254Z
├── metadata/cohort_01
├── metadata_gate/cohort_01_v0_2
├── launch_logs
└── postdownload_audit
```

Este es el lugar que refleja mejor el estado actual del proceso.

## 7. Documentos SEC pesados

No están en `C:`. La raíz activa gobernada es:

```text
D:\TSIS\fundamental_context\sec_pit_v0_1
```

Con:

```text
objects\
    CAS comprimido por SHA-256

runs\
    ejecuciones, manifests, heartbeats y logs
```

La descarga de los primeros 250 está en:

[Run C01 T01](D:/TSIS/fundamental_context/sec_pit_v0_1/runs/sec_pit_c01_primary_t01_0250_v0_1_20260814)

El piloto antiguo está congelado en:

```text
D:\sec_float_pit_v0_1
```

y no admite nuevas escrituras.

En resumen:

```text
DISEÑO Y DECISIONES
C:\TSIS_Data\00_CTO\...\07_SEC_UPSTREAM_DATA\SEC

CÓDIGO Y CONTRATOS OPERATIVOS
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\...

RUNTIME Y AUDITORÍAS DE EJECUCIÓN
C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1

DOCUMENTOS SEC PESADOS
D:\TSIS\fundamental_context\sec_pit_v0_1
```
