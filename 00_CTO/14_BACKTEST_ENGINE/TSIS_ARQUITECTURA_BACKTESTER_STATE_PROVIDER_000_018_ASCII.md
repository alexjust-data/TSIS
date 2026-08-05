Exit code: 0
Wall time: 0.2 seconds
Output:
# TSIS - Arquitectura backtester, State Provider y tablas 000-018

```text
╔ TSIS · BACKTESTER → STATE PROVIDER → TABLAS 000-018 → ESTRATEGIA ═════════════════════════════════════════════════════════╗
║ CASO OBJETIVO: long activado por WAKE-UP y cerrado mediante deteccion causal de FRONTSIDE TERMINATION.                   ║
║ REGLA: el backtester solicita representaciones semanticas gobernadas; nunca solicita tablas o paths libremente.          ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                                              │
                                                              ▼
┌ 0 · CORRECCION DEL MODELO MENTAL ─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                            │
│ INCORRECTO                                                    CORRECTO                                                     │
│ Backtester → «dame market_state_table»                        BacktestRunSpec → «resuelve estos perfiles,                 │
│ Backtester → «abre este Parquet»                              objetos, eventos, instrumentos, fechas y politicas PIT»     │
│ Backtester → «dame todas las columnas»                                                                                     │
│                                                                                                                            │
│ 016_market_state_table y 017_event_state_table son superficies materializadas; no son APIs de libre consulta.             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 1 · MODELO CIENTIFICO DE LA ESTRATEGIA ───────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                            │
│ Trades + Quotes + barras + contexto                                                                                        │
│                    │                                                                                                       │
│                    ▼                                                                                                       │
│ Market State observable y legal en t                                                                                       │
│                    │                                                                                                       │
│                    ▼                                                                                                       │
│ Wake-up Detector causal → Event State wake-up → Tradable In-Play / Entry Policy → BUY                                     │
│                    │                                                                                                       │
│                    ▼                                                                                                       │
│ Frontside State Tracker                                                                                                    │
│ HEALTHY → STRESSED → WARNING → RISK_HIGH → TERMINATION_DETECTED → Exit Policy → SELL                                      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ DECISION · ¿WAKE-UP Y FRONTSIDE TERMINATION SON EVENT TYPES ADMITIDOS Y CAUSALES? ────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│ NO · ESTADO ACTUAL                                          │ SI · ARQUITECTURA OBJETIVO                                  │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Event Type admitido:                                        │ Event Type Registry contiene versiones aceptadas de:        │
│ event_type:market_data:session_opened                      │ wake_up_event                                                 │
│                                                             │ frontside_termination_detected                               │
│ wake_up y termination son candidatos cientificos.           │                                                              │
│ La estrategia completa no esta autorizada.                  │ Cada detector congela inputs, ventanas, reglas, version,     │
│                                                             │ occurred_at, detected_at, available_at y fingerprint.       │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                         RUTA OBJETIVO
                                                              │
                                                              ▼
┌ 2 · BACKTEST RUN SPEC ─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ backtest_id · strategy_id/version · universe_id · date_range · exchange_scope                                              │
│ market_data_profile_id · market_state_profile_id(s) · event_state_profile_id(s) · event_type_ids                          │
│ required_information_objects · required_fields · decision_resolution · consumption_purpose = backtest                    │
│ calendar_authority_id · point_in_time_policy_id · temporal/coverage/source-version/reuse policies                         │
│ execution/cost/risk policies · seeds · entorno                                                                             │
│                                                                                                                            │
│ PROHIBIDO: paths fisicos libres · tablas completas sin perfil · versiones ambiguas · columnas no contratadas.             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 3 · RUN PREFLIGHT · REQUESTS NORMALIZADAS ────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                            │
│ ┌ MARKET STATE REQUEST ──────────────────────────────┐       ┌ EVENT STATE REQUEST ──────────────────────────────────────┐ │
│ │ profile_id/version exactos                        │       │ Event State profile/version                             │ │
│ │ exchange + explicit_instrument_ids                │       │ Event Type IDs + registry snapshot                      │ │
│ │ session_dates + resolution                        │       │ Event Instance policy                                   │ │
│ │ calendar + PIT + source-version policies          │       │ Event Window policy/definition                          │ │
│ │ output_mode + reuse_policy                        │       │ Instrument Projection policy                            │ │
│ └────────────────────────────────────────────────────┘       │ Market State dependency profile/reuse policy             │ │
│                                                             │ exchange + instruments + sessions + calendar + PIT       │ │
│                                                             └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 4 · STATE RESOLUTION REQUEST · ENVELOPE COMUN ────────────────────────────────────────────────────────────────────────────┐
│ request_id · request_ref · request_type · state_kind · request_fingerprint · request_contract_version                     │
│ consumer_id · consumption_purpose · operation · resolution_policy · specialized payload                                   │
│                                                                                                                            │
│ payload = market_state_request o event_state_request                                                                       │
│ Event State puede emitir o resolver una subrequest gobernada de Market State.                                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 5 · PROVIDER CONTROL-PLANE · TODAVIA NO LEE FILAS FISICAS ────────────────────────────────────────────────────────────────┐
│ Runtime User Invocation Interface                                                                                          │
│              │                                                                                                             │
│              ▼                                                                                                             │
│ JSON Schema exacto + additionalProperties=false → validacion semantica fail-closed                                         │
│              │                                                                                                             │
│              ▼                                                                                                             │
│ Fingerprint canonico de request + autoridades                                                                              │
│              │                                                                                                             │
│              ▼                                                                                                             │
│ Capability Registry + Effective View → Profile Resolver → Source Resolver                                                  │
│              │                                                                                                             │
│              ▼                                                                                                             │
│ Universe Resolver → Calendar Resolver → Partition/Coverage Resolver → Reuse Resolver                                      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
Exit code: 0
Wall time: 0.2 seconds
Output:
                                                              ▼
┌ DECISION DEL RUNTIME ──────────────────────────────────────────────────────────────────────────────────────────────────────┐
├──────────────────────────────────────┬───────────────────────────────────────┬─────────────────────────────────────────────┤
│ REUSE HIT                            │ BUILD AUTHORIZATION REQUIRED          │ BLOCKED                                     │
├──────────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────────────────┤
│ Dataset exacto y validado.           │ No existe representacion exacta.     │ Request, profile o Event Type invalido.     │
│ Request/schema/lineage/PIT coinciden.│ Se congela un execution plan.        │ Scope, path o consumo no autorizado.        │
│ Coverage y restricciones sirven.     │ Debe aprobarse antes de leer.        │ Contrato provider/consumer incompatible.    │
└──────────────────────────────────────┴───────────────────────────────────────┴─────────────────────────────────────────────┘
                   │                                      │
                   │                                      ▼
                   │  ┌ EXECUTION PLAN CONGELADO ─────────────────────────────────────────────────────────────────────────┐
                   │  │ request/profile/source/universe/calendar fingerprints                                           │
                   │  │ logical partitions + coverage + builders + schemas                                              │
                   │  │ input aliases + output fields + validators + autorizacion exacta + hashes ejecutables           │
                   │  └───────────────────────────────────────────────────────────────────────────────────────────────────┘
                   └──────────────────────────────────────────┐
                                                              ▼
┌ 6 · RESOLUCION SEMANTICA DEL PERFIL ─────────────────────────────────────────────────────────────────────────────────────┐
│ Profile Manifest                                                                                                           │
│       │                                                                                                                    │
│       ▼                                                                                                                    │
│ required_information_objects                                                                                               │
│       │                                                                                                                    │
│       ▼                                                                                                                    │
│ 03_INFORMATION_OBJECTS: Domain Definition → Candidate → Formal Admission / Admission With Restrictions                    │
│       │                                                                                                                    │
│       ▼                                                                                                                    │
│ Modelos de representacion / capacidades cientificas                                                                        │
│       │                                                                                                                    │
│       ▼                                                                                                                    │
│ 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING                                                                                  │
│ capability → variable fisica → formula/version → tabla fuente → regla temporal → perfil                                   │
│       │                                                                                                                    │
│       ▼                                                                                                                    │
│ 05_STATE_BUILDER_VALIDATION: schema · formula · calidad · coverage · lineage · temporalidad · no leakage                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 7 · PERFILES NECESARIOS PARA WAKE-UP / FRONTSIDE ─────────────────────────────────────────────────────────────────────────┐
│                                                                                                                            │
│ MARKET STATE CORE-FOUR ACTUAL                               EXTENSIONES NECESARIAS                                         │
│ Price Location / Structure = 5                              Liquidity                                                      │
│ Price Movement = 5                                         Market Microstructure State                                   │
│ Trading Activity = 4                                       Order Flow Pressure                                            │
│ Volatility / Range State = 3                               News / Fundamental / Short / Halt Context                     │
│ Total = 17 valores cientificos                             Broad Market Context                                           │
│                                                                                                                            │
│ El core-four no demuestra por si solo la deteccion microestructural de wake-up o frontside termination.                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 8 · 02_TABLE_REPRESENTATION_REVIEW · CONTROL DE CADA TABLA ───────────────────────────────────────────────────────────────┐
│  1. Table identity                         10. Que produce                                                                 │
│  2. Entidad/representacion/funcion         11. Informacion prohibida                                                       │
│  3. Fenomenos representados               12. Clasificacion/taxonomia de columnas                                        │
│  4. Preguntas cientificas                  13. Information Objects implementados                                         │
│  5. Consumidores                           14. Elegibilidad para State Profiles                                           │
│  6. Informacion minima/atributos           15. Variables injustificadas o ausentes                                       │
│  7. Grain                                  16. Solapamientos                                                              │
│  8. Primary key                            17. Legalidad temporal y Event-State legality                                  │
│  9. Que consume                            18. Estado fisico/contractual/validacion/promocion + evidence + decision        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
╔ 9 · TABLAS 000-018 REVISADAS Y GOBERNADAS ═════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                            ║
║ CONTROL / IDENTIDAD / CALENDARIO                         CONTEXTO Y HECHOS                                                 ║
║ 000 instrument_master                                  004 master_daily_table                                             ║
║ 001 market_calendar                                    005 corporate_actions_table                                       ║
║ 002 expected_data_calendar                             006 halts_table                                                   ║
║ 003 dataset_certification_matrix                       007 event_windows_table                                           ║
║                                                          009 fundamentals_asof_table                                       ║
║ OUTCOMES · Y / FUTURO AISLADO                          010 news_context_table                                             ║
║ 008 outcomes_table                                     011 short_context_table                                            ║
║ MFE/MAE/future returns/frontside_peak                  012 regime_context_table                                          ║
║ nunca input del estado o estrategia                    018 intraday_scanner_candidates_table                             ║
║                                                                                                                            ║
║ MARKET DATA / VARIABLES FISICAS                        REPRESENTACIONES MATERIALIZADAS                                    ║
║ 013 ohlcv_1m_quote_guarded                             016 market_state_table                                             ║
║ 014 master_intraday_bar_table                          017 event_state_table                                              ║
║ 015 microstructure_features_table                                                                                         ║
║                                                                                                                            ║
║ 016 y 017 son outputs de representacion; no son fuentes primarias de si mismas.                                            ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                                              │
                                                              ▼
┌ 10 · SOURCE BINDING FISICO ───────────────────────────────────────────────────────────────────────────────────────────────┐
│ Information Object                                                                                                        │
│       ↓ capability/model                                                                                                   │
│       ↓ variable + formula/version                                                                                         │
│       ↓ table_id + field_id                                                                                                │
│       ↓ dataset/version + relative path + schema fingerprint                                                               │
│       ↓ file size + SHA-256 + hash-before/hash-after                                                                       │
│       ↓ physical row locator + lineage + repair/quality/restriction flags                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 11 · JOINS POINT-IN-TIME LEGALES ─────────────────────────────────────────────────────────────────────────────────────────┐
│ instrument_id · session_date · decision_timestamp                                                                          │
Exit code: 0
Wall time: 0.2 seconds
Output:
│ source_timestamp/bar_end <= decision_timestamp                                                                             │
│ valid_from <= decision_timestamp < valid_to                                                                                │
│ as_of_utc <= decision_timestamp · input_available_at <= decision_timestamp                                                │
│                                                                                                                            │
│ 004 daily          → prior session as-of; datos finales actuales solo tras cierre.                                        │
│ 009 fundamentals   → ultima version conocida antes de t.                                                                  │
│ 010 news           → publicacion disponible antes o en t.                                                                 │
│ 013/014 intraday   → solo barras cerradas y disponibles.                                                                  │
│ 015 microstructure → ventana cerrada; window_end/available_at <= t.                                                       │
│ 008 outcomes       → ninguna ruta hacia el builder.                                                                       │
│                                                                                                                            │
│ Ambiguedad · autoridad ausente · duplicado · early delivery · futuro → FAIL CLOSED.                                      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 12 · FEATURE BUILDERS ─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Inputs admitidos + ventanas cerradas + cutoffs + min_rows + formulas versionadas                                          │
│       ├── Price Location / Structure                                                                                       │
│       ├── Price Movement                                                                                                   │
│       ├── Trading Activity                                                                                                 │
│       ├── Volatility / Range State                                                                                         │
│       ├── Liquidity / Microstructure / Order Flow extensions                                                               │
│       └── Context features admitidas                                                                                       │
│                                                                                                                            │
│ Cada output conserva builder_id · inputs · lookback · window · cutoff · available_at_rule · hashes.                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 13 · MARKET STATE BUILDER ────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Variables validas y legalmente disponibles → profile exacto → 016 market_state_table/candidate dataset                   │
│                                                                                                                            │
│ instrument + decision_timestamp + payload tipado                                                                           │
│ state_as_of_utc + state_available_at_utc                                                                                   │
│ object completeness + quality + policies + formulas                                                                        │
│ source lineage + restriction domains + input/output fingerprints                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 14 · EVENT DETECTION · CAPACIDAD SEPARADA ────────────────────────────────────────────────────────────────────────────────┐
│ Market State/observaciones disponibles → detector causal versionado → Event Instance                                      │
│                                                                                                                            │
│ event_type_id · event_instance_id · occurred_at_utc · detected_at_utc · available_at_utc                                  │
│ detector_version · evidence · fingerprint · restrictions                                                                   │
│                                                                                                                            │
│ Wake-up no puede emitirse antes de que existan sus inputs.                                                                │
│ El maximo retrospectivo del frontside no puede convertirse en detected_at.                                                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 15 · EVENT STATE BUILDER ──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Event Type Registry + Event Instance + Event Window Binding + Instrument Projection                                       │
│        + Market State dependency exacta por ID/fingerprint                                                                 │
│        │                                                                                                                   │
│        ▼                                                                                                                   │
│ exactly-one binding → 017 event_state_table/candidate dataset                                                             │
│                                                                                                                            │
│ event_state_available_at_utc >= maximo available_at de todas las dependencias                                             │
│ payload tipado + contexto relativo + lineage + restriction domains + fingerprint                                          │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 16 · VALIDACION Y PROMOCION DEL CANDIDATO ────────────────────────────────────────────────────────────────────────────────┐
│ Schema · cardinalidad · coverage · identities · fingerprints · formulas · lineage                                         │
│ temporalidad · disponibilidad · restricciones · componentes · determinismo · hashes                                       │
│                                                                                                                            │
│ Materializer no se autocertifica. Validator independiente produce PASS / PASS_WITH_RESTRICTIONS / FAIL.                   │
│ Candidate Dataset Registry registra status y elegibilidad de reutilizacion.                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 17 · RUNTIME RESPONSE + STATE BUNDLE MANIFEST ─────────────────────────────────────────────────────────────────────────────┐
│ RuntimeInvocationResponse: request fingerprint · decision · capability/profile · dataset/status · coverage/restrictions   │
│                                                                                                                            │
│ StateBundleManifest: request/response bindings · dataset refs · profile/schema versions                                   │
│ source dataset IDs/hashes · artifact refs/hashes · field lineage · temporal policy                                        │
│ coverage · validation · restrictions · reuse · materialization · consumption authorization                                │
│ official/production/downstream flags                                                                                       │
│                                                                                                                            │
│ El bundle referencia artefactos gobernados; no entrega una ruta elegida libremente por el backtester.                     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ DECISION · RUN PREFLIGHT DEL BACKTESTER ───────────────────────────────────────────────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│ BACKTEST_INPUTS_FAIL                                        │ BACKTEST_INPUTS_PASS                                         │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Hash/schema/coverage/lineage no coincide.                   │ Bundle exacto y autorizado.                                 │
│ Restricciones incompatibles.                                │ Coverage compatible con RunSpec.                            │
│ Estado disponible demasiado tarde.                          │ Temporalidad y restricciones propagables.                   │
│ Profile/Event Type/capability no autorizado.                │ Consumo fisico autorizado para ese scope.                   │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                         RUTA DE PASS
                                                              │
                                                              ▼
┌ 18 · BACKTEST INPUT MANIFEST ──────────────────────────────────────────────────────────────────────────────────────────────┐
│ MarketData bundle + Market State bundle + Event State bundle                                                              │
│ versiones · fingerprints · hashes · coverage · restrictions · temporal policies · codigo · entorno                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
Exit code: 0
Wall time: 0.2 seconds
Output:
┌ 19 · REPLAY CAUSAL EN EL EVENT LOOP ──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                            │
│ HistoricalReplayFeed                       State Consumer/Feed autorizado                                                  │
│          │                                            │                                                                    │
│          ▼                                            ▼                                                                    │
│ ReplayBarEvent                 BoundedMarketStateAvailable / BoundedEventStateAvailable                                   │
│          └──────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┐   │
│                                         ▼                                                                              │   │
│ available_at → event_type_priority → session → ticker → identity                                                       │   │
│                                         │                                                                              │   │
│                                         ▼                                                                              │   │
│ BAR → MARKET_STATE → EVENT_STATE · early delivery = FAIL CLOSED                                                        │   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 20 · CONSUMO POR LA ESTRATEGIA ────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                            │
│ MarketStateStore                         EventStateStore                                                                   │
│        └───────────────────┬──────────────────┘                                                                            │
│                            ▼                                                                                               │
│                    Strategy Decision Clock                                                                                 │
│       ┌────────────────────┴────────────────────┐                                                                          │
│       ▼                                         ▼                                                                          │
│ Wake-up Event State                     Frontside State Tracker                                                            │
│ WATCH / ENTRY_ELIGIBLE                  WARNING / RISK_HIGH / TERMINATION_DETECTED                                         │
│       │                                         │                                                                          │
│       ▼                                         ▼                                                                          │
│ Entry Policy + riesgo/tradability              Exit Policy                                                                 │
│       │                                         │                                                                          │
│       ▼                                         ▼                                                                          │
│ BUY Order                                    SELL Order                                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 21 · EJECUCION Y ACCOUNTING · SEPARADOS DE STATE ─────────────────────────────────────────────────────────────────────────┐
│ Order → Execution Simulator ← precio ejecutable unicamente desde MarketData                                               │
│                         │                                                                                                  │
│                         ▼                                                                                                  │
│ Fill → Position → Cash Ledger → Costs → Equity → Trade                                                                    │
│                                                                                                                            │
│ Market State y Event State nunca suministran el precio de fill.                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
┌ 22 · FRONTERA X / Y ───────────────────────────────────────────────────────────────────────────────────────────────────────┐
├─────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│ X · INPUT LEGAL EN DECISION TIME                            │ Y · FUTURO / OUTCOMES                                       │
├─────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ MarketData, Market State y Event State disponibles.         │ frontside_peak retrospectivo.                               │
│ Event Instances causales.                                   │ MFE / MAE / future return.                                   │
│ Restricciones y contexto PIT.                               │ wake-up exitoso/fallido y backside ex post.                  │
│ Unica informacion accesible por la estrategia.              │ No existe ruta Y → detector → decision.                      │
└─────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
╔ ESTADO INSTITUCIONAL DE ESTA ESTRATEGIA ═══════════════════════════════════════════════════════════════════════════════════╗
║ DEMOSTRADO: replay fisico + consumo bounded PIT de Market State core-four + Event State session_opened.                   ║
║ NO DEMOSTRADO: Market State microestructural suficiente para wake-up/frontside termination.                               ║
║ NO ADMITIDO: Event Types wake_up_event y frontside_termination_detected.                                                   ║
║ NO AUTORIZADO: ejecutar la estrategia completa long wake-up → frontside termination.                                      ║
║ SIGUIENTE: admitir objetos/perfiles/detectores/Event Types y demostrarlos causalmente antes del strategy run.             ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```
