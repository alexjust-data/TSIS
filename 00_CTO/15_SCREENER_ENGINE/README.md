# Screener Engine: autoridad general y frontera con consumidores

## 0. Estado de este documento

| Campo | Valor |
|---|---|
| `document_role` | `ARCHITECTURAL_ORIENTATION_AND_BOUNDARY` |
| `document_status` | `CURRENT_CONCEPTUAL_ORIENTATION` |
| `created_at` | `2026-08-15` |
| `conceptual_home` | `C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE` |
| `runtime_status` | `NOT_CREATED_NOT_AUTHORIZED` |
| `canonical_screener_status` | `NOT_PROMOTED` |

Este documento explica qué representa esta carpeta, dónde debe vivir el futuro
Screener Engine ejecutable y cómo deben consumirlo Trading Activity, Wake-up,
Backtest, research, live y Offline RL. No es un README de navegación genérico.

## 1. Veredicto arquitectónico

`C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE` es el lugar correcto para la autoridad
conceptual general del Screener Engine de TSIS.

No es una carpeta exclusiva de Trading Activity Binding A o Binding B. Tampoco
debe convertirse en la ubicación del código productivo ni en una segunda Data
Foundation.

```text
00_CTO/15_SCREENER_ENGINE
= arquitectura, contratos, taxonomía, gates y decisiones

futuro runtime independiente
= código ejecutable del Screener Engine

01_TSIS_DATA_FOUNDATION
= inputs PIT gobernados, datasets fuente, lineage y calidad

Backtest / Trading Activity / Wake-up / Research / Live / Offline RL
= consumidores autorizados de artefactos sellados
```

La propuesta de nombre `C:/TSIS_Data/07_TSIS_SCREENER_ENGINE` para el runtime
independiente sigue pendiente de decisión humana y de un gate de creación. La
existencia de esta carpeta CTO no autoriza a crear ese runtime.

## 2. Qué debe ser el Daily Eligible Universe Selector

El primer componente general del Screener Engine debe resolver una sola vez por
sesión qué instrumentos pertenecen al universo observable bajo una política PIT
versionada.

```text
Master Instrument/Session Frame
        ↓
Daily Eligible Universe Selector
        ↓
daily_eligible_universe.parquet
+ manifest
+ hashes
+ estados y razones de exclusión
        ├── Trading Activity A/B
        ├── Wake-up
        ├── Backtest
        ├── Research
        ├── Live
        └── Offline RL
```

El selector general debe preservar el denominador completo. No puede devolver
únicamente los elegibles ni borrar los casos desconocidos. Debe distinguir al
menos:

```text
ELIGIBLE
INELIGIBLE_PRICE
INELIGIBLE_MARKET_CAP
PRICE_UNAVAILABLE
SHARES_UNAVAILABLE
STALE_SHARES_PROXY
IDENTITY_REVIEW
CORPORATE_ACTION_REVIEW
OUTSIDE_PARENT_FRAME
```

## 3. Una autoridad; múltiples consumidores

El proyecto no debe tener una copia del filtro en cada módulo. La autoridad de
membresía es única y sus consumidores reciben identidades, states, policy IDs,
manifests y hashes.

```text
selector owns membership
consumers replay membership
consumers never redefine membership
```

Esto significa que un consumidor autorizado no puede:

- recalcular `price` o `market-cap proxy`;
- cambiar las fronteras `[0.50, 20.00]` o `<100M` conservando el mismo ID;
- elegir otra fuente de precio;
- reinterpretar el TTL de shares;
- rellenar sesiones ausentes;
- arrastrar el último universo conocido;
- modificar la membresía durante replay;
- tratar elegibilidad como Wake-up, In-Play o decisión de entrada.

## 4. Relación con Backtest Engine

Backtest debe consumir exactamente el snapshot diario sellado mediante un
adapter y un preflight propios:

```text
sealed Screener artifact
-> Backtest ScreenerArtifactAdapter
-> RunPreflight validation
-> frozen universe_manifest
-> session-by-session membership replay
```

El Backtest no debe implementar localmente:

```text
if price between 0.50 and 20.00
and market_cap_proxy < 100M
```

El gate de consumo propuesto sigue siendo `BT-GATE-016`, que permanece
`NOT_OPEN` y cuya implementación no está autorizada. La futura apertura de ese
gate autorizaría únicamente el consumo, no la redefinición del selector.

## 5. Relación con Trading Activity A/B y Wake-up

Binding A y Binding B representan `Trading Activity`. No son screeners y no
son propietarios del universo diario.

Ambos deben consumir exactamente la misma membresía para que la comparación
A/B sea válida. Wake-up debe observar todos los symbol-seconds elegibles,
incluidos los instrumentos que nunca despiertan, porque esos casos constituyen
el denominador necesario para medir falsas activaciones.

La secuencia correcta es:

```text
Daily Eligible Universe
-> Wake-up observation population
-> Binding A / Binding B sobre identidades idénticas
-> Wake-up Detector
-> Active Symbol Set
-> observación pesada / In-Play / estrategia
```

## 6. El gate actual de A/B es un puente, no el screener general

El gate
`daily_eligible_universe_restricted_consumption_gate_v0_1_20260815` no es el
Screener Engine general y no promueve un universo canónico.

Es un puente controlado que permite continuar el experimento Trading Activity
A/B utilizando el candidato presesión existente, de forma hash-bound y sin
duplicar los filtros dentro de los bindings.

```text
gate restringido A/B
= consumo experimental del candidato existente

NO equivale a
= Screener Engine general
= runtime canónico
= autorización live
= integración Backtest
= market cap histórica exacta
```

Cuando exista un artefacto canónico del Screener Engine, A/B y los demás
consumidores deberán adoptar ese artefacto mediante contratos y gates propios.
El puente restringido no puede transformarse silenciosamente en la autoridad
general ni cambiar de semántica conservando su versión.

## 7. Estado real

```text
arquitectura conceptual                    = BIEN UBICADA
propuesta                                  = DRAFT_FOR_HUMAN_REVIEW
candidato presesión                        = VALIDATED_EXPERIMENTAL
gate restringido para experimento A/B      = PASS
screener general canónico                  = NO CREADO
runtime independiente                      = NO CREADO
adapter Backtest                           = NO IMPLEMENTADO
BT-GATE-016                                = NOT_OPEN
consumo indiscriminado                     = NO AUTORIZADO
```

No cualquiera puede utilizar todavía el candidato como autoridad
institucional. Cada consumidor necesita un contrato explícito que valide
schema, grain, policy, fechas, manifests, hashes, states y restricciones.

## 8. Qué falta antes de construir el runtime

```text
1. Promover esta carpeta como owner conceptual mediante decisión humana.
2. Congelar el contrato exacto del Daily Eligible Universe.
3. Congelar schema, grain, states, reason codes y accounting.
4. Congelar la adopción o sustitución del candidato presesión actual.
5. Decidir el nombre y ubicación del runtime independiente.
6. Crear sus contratos, reglas locales, roadmap y gate inicial.
7. Implementar con tests y probes por shard equivalentes a producción.
8. Certificar artefactos, determinismo, PIT, lineage y fail-closed behavior.
9. Abrir gates separados para cada consumidor, incluido Backtest.
```

## 9. Regla operativa corta

```text
El parent universe define el marco.
El Daily Eligible Universe define a quién podemos observar hoy.
Trading Activity representa actividad negociada en los elegibles.
Wake-up detecta quién deja de estar dormido.
In-Play clasifica relevancia operativa o estratégica.
La estrategia decide qué hacer.
El Backtest reproduce artefactos; no reescribe autoridades upstream.
```

## 10. Documentos relacionados

- `SCREENER_ENGINE_ARCHITECTURE_PROPOSAL_v0_1.md`: propuesta completa, todavía
  `draft_for_human_review`.
- `00_STRUCTURE_SYSTEM.md`: desarrollo de la arquitectura por capas y relojes.
- `EVIDENCE_INDEX.md`: fuentes y evidencia utilizadas por la propuesta.
- `01_LAYER_1/initial_idea.MD`: idea inicial del universo diario basado en
  market-cap proxy.
- `../04_MARKET_STATES_CREATION/DAILY_ELIGIBLE_UNIVERSE_SELECTOR_AND_BINDING_CONSUMPTION_CONTRACT_v0_1.md`:
  frontera entre el selector y Trading Activity A/B.

