# Build Daily Inspection Pack - Modulo 01

## 1. Rol

Este documento describe como debe construirse el dossier de inspeccion de `daily`.

No ejecuta nada.

Fija la intencion operativa para el builder futuro.

## 2. Regla metodologica clave

`daily` no debe presentarse como si toda su decision final viviera en un unico eje.

El builder tiene que respetar dos planos distintos:

- `quality axis`
- `coverage axis`

Eso significa que un pack completo de `daily` no puede limitarse a:

- `good`
- `flagged`
- `bad`

porque esa triparticion visual solo cubre bien la calidad del bar.

El cierre institucional final de `daily` necesita tambien evidenciar:

- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`

a nivel de coverage.

## 3. Fuentes principales

La construccion del pack debe apoyarse en:

- notebooks historicos de auditoria `daily`
- markdowns de auditoria y closeout
- markdowns de certificacion
- imagenes historicas `001.png` a `007.png`
- y artefactos persistidos en runs ya existentes

## 4. Assets que debe producir o clasificar

El builder deberia producir o clasificar:

- tablas resumen por bucket
- ejemplos `good`
- ejemplos `flagged`
- ejemplos `bad`
- ejemplos de coverage
- imagenes reutilizadas y nuevas si hacen falta
- y un indice de casos inspeccionables

Los assets visuales finales no deben quedarse como outputs huerfanos.

Deben terminar:

- incrustados en `daily_inspection_readout_v0_1.md`;
- o incrustados en `good_justification`, `flagged_case_evidence_packs`, `bad_case_evidence_packs` y `coverage_case_evidence_packs`.

## 5. Estructura minima correcta

### A. Calidad del bar

Debe mantenerse la estructura ya existente:

- `good_justification`
- `flagged_case_evidence_packs`
- `bad_case_evidence_packs`

### B. Coverage y recovery

La capa explicita de coverage ya existe en:

- `coverage_case_evidence_packs`
- `coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`

Ahi ya se documentan, con ejemplos visuales historicos promovidos a foundations, las tres familias minimas que hay que distinguir:

- `LIKELY_VALID_GAP_ONLY`
- `AMBIGUOUS_REVIEW`
- `REALLY_PROBLEMATIC_UNEXPECTED`

## 6. Imagenes historicas ya reincorporadas

Las imagenes `001.png` a `007.png` ya fueron reincorporadas en el dossier:

- `coverage_case_evidence_packs/daily_coverage_cases_v0_1.md`

Siguen siendo evidencia historica util y no deben volver a quedar fuera del cierre institucional por haber nacido en notebooks antiguos.

Su funcion no es ornamental.

Sirven para evitar dos errores graves:

- tratar como `bad` huecos que son recuperables sin penalizacion;
- o tratar como `good` huecos que siguen siendo frontera abierta de coverage.

## 7. Objetivo metodologico

El builder no debe inventar una interpretacion nueva.

Debe:

- recuperar la evidencia ya existente;
- organizarla;
- dejarla lista para inspeccion institucional;
- y separar con claridad lo que prueba calidad del bar de lo que prueba coverage.

Eso implica pensar en un lector final:

- no solo generar png;
- sino generar png que luego puedan insertarse directamente en markdown con explicacion fehaciente y con consecuencia operativa explicita.

## 8. Evolucion prevista

Fase actual:

- dossier historico de coverage ya promovido a foundations
- pack visual ya reutilizable para lectura institucional

Fase madura deseable:

- script reproducible equivalente para regenerar tambien la capa de coverage sin depender de rutas historicas
