# Overnight Data Audit Completion Harness Runbook

Fecha: 2026-06-13
Estado: runbook operativo v0.3
Objetivo: preparar un agente autonomo unico para cerrar una carpeta/dataset por run con calidad comparable a los bloques maduros, preservando auditoria historica.

## 1. Objetivo de la noche

Convertir la auditoria pendiente de data en paquetes institucionales modernos sin destruir ni reescribir la auditoria historica ya hecha.

La prioridad no es escribir "mucho".
La prioridad es que cada carpeta/dataset trabajada quede en uno de estos estados honestos:

- `modern_dossier_complete`;
- `modern_dossier_partial`;
- `modernization_gap_documented`;
- `blocked_needs_human_decision`;
- `not_consumable_no_active_consumer`.

## 2. Datasets target

Foto fisica observada el 2026-06-12:

| Root | Dirs | Files | Parquet | CSV | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `E:/TSIS/data/reference` | 49880 | 52986 | 52983 | 2 | upgrade inspector moderno |
| `E:/TSIS/data/Halts` | 6 | 5702 | 5 | 17 | cerrar despues de reference |
| `E:/TSIS/data/financial` | 49878 | 49882 | 49872 | 8 | cerrar paquete foundation completo |
| `E:/TSIS/data/regime_indicators` | 36 | 69 | 67 | 0 | cerrar como contexto/regime, no alpha |

Correccion 2026-06-13:

Antes de cerrar esos roots fisicos, el agente debe leer y preservar la auditoria historica ya existente para:

- `additional`;
- `halts`;
- `reference`;
- `short`.

Esa auditoria vive bajo:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/
```

Para esos datasets el trabajo no empieza por reauditar. Empieza por reconciliar lo historico contra `01_foundations`.

Fuera de alcance:

- `E:/TSIS/data/images_Flash_Research`

No inventariar, mover, OCRizar, validar ni institucionalizar `images_Flash_Research` en este run.

## 3. Orden recomendado

Orden de carpetas para runs sucesivos:

1. `reference`
2. `halts`
3. `additional`
4. `short`
5. `financial`
6. `regime_indicators`
7. integracion final

Razon:

- `reference` gobierna eventos, ticker changes, splits, dividends e identidad.
- `halts` depende parcialmente de `reference/events` y ya tiene auditoria historica profunda cerrada.
- `additional` y `short` ya tienen auditoria historica cerrada y foundation minima, pero necesitan promocion moderna controlada.
- `financial` requiere una decision estricta de temporal availability y leakage antes de cualquier ML/backtest; antes hay que confirmar que no queda cubierto por `additional/financials_core`.
- `regime_indicators` debe cerrarse como contexto/regimen, no como alpha ni generador de edge.

Regla de ejecucion:

```text
Un run trabaja una sola carpeta/dataset y se detiene.
```

No ejecutar toda la cadena sin revision humana entre carpetas.

## 4. Modelo de ejecucion

El run inmediato es single-agent.

No lanzar varios agentes en paralelo para este cierre.

Motivo:

- aun no hay lock manager runtime;
- no hay integrador automatico validado;
- los indices compartidos y changelogs pueden quedar inconsistentes;
- el primer objetivo es reproducir la calidad humana ya lograda, no maximizar concurrencia.

El agente unico debe:

1. ponerse al dia;
2. leer `historical_audit_preservation_and_promotion_contract.md`;
3. leer benchmarks maduros;
4. seleccionar una sola carpeta/dataset;
5. leer auditoria y certificacion historica si existen;
6. comparar contra `01_foundations`;
7. crear `integration_notes.md` o promotion gap;
8. completar solo esa carpeta/dataset;
9. detenerse para revision humana.

## 5. Rutas prohibidas

Prohibido modificar:

```text
E:/TSIS/data/
C:/TSIS_Data/data/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/run/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/
```

Estas rutas son evidencia/provenance read-only.

Trabajo nuevo permitido:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/<dataset>/
```

## 6. Benchmark obligatorio antes de producir

Antes de crear outputs nuevos, el agente debe entender como estan hechos los bloques maduros.

Lectura minima:

- `inspection_dossiers/README.md`
- `module_contracts/inspection_dossier_model.md`
- `daily/README.md` y sus readouts/casepacks principales
- `quotes/README.md`, subfolder READMEs, readout, open casepacks audit y casepacks
- `trades/README.md`, readouts, notebooks, manifests, global universe, family casepacks y scripts residentes
- `minute/README.md`, notebooks `minute_00` a `minute_05`, dossier visual de `67` imagenes y assets core/vw
- `1m_split_normalized/README.md`, readouts, notebooks, mapa poblacional, casepacks visuales y audit full-universe de eventos

El agente debe dejar en su final report una seccion breve: `Benchmark leido y estandar aplicado`.

## 7. Estandar notebook/visual obligatorio

### Notebooks

Los notebooks son interfaces inspectoras, no almacenes de codigo.

Deben usarse para:

- leer outputs ejecutados;
- navegar casos;
- preservar widgets/selectores cuando hagan falta;
- abrir drilldowns humanos;
- y mostrar evidencia que luego queda encapsulada en markdown/assets.

La logica pesada debe vivir en scripts residentes.

Si el agente crea notebooks nuevos, deben ser ligeros, versionados y explicar su rol.

### Visuales

Los visuales deben seguir orden general-a-particular:

```text
mapa poblacional
-> distribuciones y masas
-> coverage/universo esperado
-> familias de evidencia
-> casos individuales
-> decision de consumo
```

Cada visual o tabla relevante debe contener:

```text
Que muestra
Responde
No responde
Consecuencia
```

Si la imagen no prueba el fenomeno, el agente debe decirlo y crear o pedir evidencia complementaria.

## 8. Output local obligatorio por dataset

Cada agente debe producir:

```text
01_foundations/inspection_dossiers/<dataset>/integration_notes.md
```

Contenido minimo:

- estado inicial;
- root fisico auditado;
- fuentes historicas leidas;
- documentos creados;
- scripts creados;
- assets creados;
- notebooks leidos/creados;
- visuales creados y lectura principal;
- conteos principales;
- consumo permitido/restringido/bloqueado;
- gaps;
- indice/changelog recomendado;
- status final propuesto.

## 9. Criterio de parada

Un agente debe parar y marcar `blocked_needs_human_decision` si:

- no puede leer root fisico;
- no puede determinar consumidor;
- detecta contradiccion entre auditoria y certification;
- no puede parsear datos por ausencia de libreria critica;
- encuentra rutas historicas que no existen y no puede reconciliarlas;
- necesita decidir semantica de mercado no documentada.
- no puede generar visuales necesarios y la evidencia tabular no basta.

No debe fingir cierre.

## 10. Criterios de aceptacion final

El run es exitoso si al terminar la carpeta existe:

- estado del dataset trabajado;
- docs y assets del dataset trabajado;
- integration notes del dataset trabajado;
- notebooks inspectores cuando sean necesarios;
- visuales/casepacks o gap audit visual honesto;
- changelog recomendado o actualizado si procede;
- lista de gaps reales;
- y el dataset no queda sobrepromovido.

Ideal:

- el dataset trabajado queda como `modern_dossier_complete`, `modern_dossier_partial` o `modernization_gap_documented` con evidencia suficiente;

Aceptable:

- el dataset trabajado queda `blocked_needs_human_decision`, pero con razon exacta y evidencia.

Fallo:

- el agente crea outputs fuera del proyecto;
- modifica raw data;
- toca `C:/TSIS_Data/data` o `E:/TSIS/data`;
- actualiza indices de forma conflictiva;
- declara "done" sin evidence assets;
- deja notebooks como unica fuente de verdad;
- genera imagenes sin interpretacion;
- no actualizan changelog;
- no dejan integration notes.

## 11. Comando de lanzamiento recomendado

Abrir una sesion Codex autonoma desde PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File C:\TSIS_Data\START_CODEX_TSIS_AUTONOMOUS.ps1
```

Pegar el prompt:

```text
SINGLE_AGENT_DATA_AUDIT_COMPLETION
```

desde:

```text
10_DATA_QUALITY_HARNESS/runbooks/2026-06-12_data_audit_agent_prompt_pack.md
```

## 12. Primer run recomendado

Primer run recomendado:

1. Trabajar solo `reference`.
2. Leer auditoria historica y certificacion de `reference`.
3. Comparar contra la foundation minima ya promovida.
4. Crear o actualizar `reference/integration_notes.md` con promotion gap.
5. Completar solo los artefactos que faltan para `reference`.
6. Parar para revision humana.

Razon:

- `reference` forma la frontera de identidad, eventos, ticker changes, splits y dividends;
- ya tiene auditoria historica profunda y foundation minima, por lo que permite probar el proceso de promocion sin reauditar desde cero;
- si este run respeta la preservacion historica, despues se puede aplicar a `halts`.

## 13. Cierre

Este runbook no sustituye a los contratos.

El agente debe obedecer:

- contratos raiz TSIS;
- `01_TSIS_backtest_SmallCaps/AGENTS.md`;
- `LOCAL_RULES.md`;
- `inspection_dossier_model.md`;
- `historical_audit_preservation_and_promotion_contract.md`;
- `data_audit_completion_artifact_contract.md`;
- y el prompt unico del run.
