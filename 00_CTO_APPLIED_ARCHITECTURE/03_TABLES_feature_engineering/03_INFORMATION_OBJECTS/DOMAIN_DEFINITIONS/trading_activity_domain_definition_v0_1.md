# Trading Activity - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_1_pre_landscape_pre_admission`

Este documento define el dominio semantico `Trading Activity`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Trading Activity
```

## Que Informacion Intenta Preservar

```text
La intensidad con la que el mercado participa en la negociacion de un instrumento en una escala temporal declarada.
```

`Participation` no queda como Objeto separado por defecto. En este dominio, participation es la propiedad semantica que `Trading Activity` intenta preservar.  El dominio intenta preservar informacion sobre:

```text
cuanto se negocia, con que frecuencia se negocia, a que ritmo aparece la actividad, si la actividad es normal o anomala, si la actividad se concentra en una ventana, y si el estado observado tiene participacion suficiente para ser interpretable.
```

La informacion central no es el precio. La informacion central es la participacion negociada.

## Por Que Este Dominio Merece Existir

```text
Porque dos estados con el mismo precio, la misma direccion o el mismo patron tecnico no tienen el mismo significado si la participacion del mercado es distinta.
```

En small caps y microcaps, la participacion no es un detalle secundario.  Es una propiedad estructural del mercado:

```text
un movimiento con poca actividad puede ser ruido, un movimiento con actividad anomala puede ser atencion, un evento sin participacion puede ser irrelevante, un scanner sin actividad suficiente puede producir falsos candidatos, y una decision sin contexto de participacion puede ser inoperable.
```

Este dominio merece existir porque conserva una incertidumbre que otros dominios no conservan de forma suficiente:

```text
esta el mercado participando realmente, o solo estamos observando precio con poca negociacion?
```

## Que Perderia TSIS Si Este Dominio Desapareciera  TSIS perderia capacidad para distinguir:

```text
movimiento de precio con participacion real vs movimiento de precio con prints escasos;  sesion activa vs sesion dormida;  actividad normal vs actividad anomala;  evento con atencion negociada vs evento sin respuesta del mercado;  liquidez aparente por precio vs actividad negociada observada;  estado seleccionado con participacion observable vs superficie de seleccion sin evidencia suficiente de actividad negociada.
```

Tambien perderia una dimension critica para:

```text
Market State, Event State, intraday scanners, backtests, ML, RL, execution-aware research, and AlphaEvolve candidate evaluation.
```

## Que No Representa  Este dominio no representa:

```text
direccion del precio, retorno, pendiente, aceleracion de precio, localizacion contra VWAP/HOD/LOD, spread, profundidad visible, coste de negociacion, order-flow direction, agresion compradora o vendedora, sentimiento de noticias, fundamentales, short crowding, outcomes futuros, ni calidad tecnica del dataset.
```

Puede usar algunas variables que tambien sirven como proxies en otros dominios.  Ejemplo:

```text
dollar_volume
```

En este dominio significa:

```text
cantidad economica negociada.
```

En `Liquidity` podria significar:

```text
proxy de tradability o capacidad de absorcion.
```

El significado no lo decide la variable aislada. Lo decide el dominio, el modelo y el uso.

## Principio Semantico Aplicado

```text
El significado no pertenece a una variable aislada.  Pertenece a:  Dominio  -> Objeto de Informacion  -> Modelo de Representacion  -> Uso temporalmente legal
```

Este principio aplica a todo TSIS, aunque aqui se use para resolver el caso de `dollar_volume`.

## Preguntas Cientificas Que Permite Formular

```text
El movimiento observado esta soportado por participacion real?  La actividad actual es anomala respecto a su baseline historico?  La actividad se esta acelerando dentro de la sesion?  Los eventos relevantes generan participacion negociada o solo aparecen como contexto externo?  La probabilidad de continuacion, fallo o expansion cambia cuando la actividad es alta vs baja?  Los scanners intradia seleccionan estados con actividad real o solo condiciones de precio?  Que perfiles de Market State son operables dada la intensidad de participacion?
```

## Candidatos Incluidos  Detectados en la primera pasada:

```text
Trading Activity Daily Trading Activity Intraday Trading Activity Attention Activity Candidate
```

Lectura actual:

```text
Trading Activity = candidato principal a Objeto de Informacion.  Daily Trading Activity = especializacion temporal / modelo diario.  Intraday Trading Activity = especializacion temporal / modelo intradia.  Attention Activity Candidate = posible superficie de seleccion o proxy de atencion; no debe admitirse como Objeto sin revisar scanner bias.
```

## Posibles Objetos Dentro Del Dominio

```text
Trading Activity
```

Candidato principal.

```text
Relative Trading Activity
```

Probablemente modelo o submodelo de `Trading Activity`, no Objeto separado por defecto.

```text
Participation Intensity
```

Probablemente modelo de representacion, no Objeto separado por defecto.  Regla anti-duplicacion:

```text
Un cambio de baseline, normalizacion, ventana, parametrizacion o resolucion temporal no crea automaticamente un nuevo Objeto de Informacion.
```

Primero debe probarse que preserva una informacion semanticamente distinta.

```text
Attention Activity
```

No esta listo para admission. Puede ser contexto, superficie de seleccion o sesgo de scanner.

## Posibles Modelos De Representacion  Estos modelos no quedan seleccionados todavia. Solo quedan identificados para el `Representation Landscape`.

```text
daily participation model intraday accumulation model intraday pace model relative activity model trade intensity window model trade size distribution model dollar turnover model scanner activity threshold model
```

## Capacidades Derivables Relacionadas

### Capacidades Imprescindibles  Estas capacidades son el nucleo minimo del dominio:

```text
daily__volume daily__transaction_count daily__dollar_volume intraday__bar_volume intraday__bar_transaction_count trades__trade_count_WINDOW trades__total_volume_WINDOW trades__dollar_volume_WINDOW
```

### Capacidades Complementarias  Estas capacidades refinan el dominio, pero no lo definen por si solas:

```text
daily__volume_20d_avg daily__rvol_20d daily__volume_Nd_avg daily__rvol_Nd daily__dollar_volume_Nd_avg intraday__session_volume_to_time intraday__session_dollar_volume_to_time intraday__volume_pace_W intraday__dollar_volume_pace_W trades__trade_rate_WINDOW trades__size_median_WINDOW trades__size_p90_WINDOW
```

### Capacidades Fronterizas  Estas capacidades probablemente pertenecen a otro dominio salvo que un modelo explicito demuestre lo contrario:

```text
trades__signed_flow_WINDOW trades__aggressor_imbalance_WINDOW
```

### Registro Operativo  Capacidades existentes o definidas:

```text
daily__volume daily__transaction_count daily__dollar_volume daily__volume_20d_avg daily__rvol_20d intraday__bar_volume intraday__bar_transaction_count intraday__session_volume_to_time intraday__session_dollar_volume_to_time trades__total_volume_WINDOW trades__dollar_volume_WINDOW trades__size_median_WINDOW trades__size_p90_WINDOW
```

Capacidades que requieren variantes:

```text
daily__volume_Nd_avg daily__rvol_Nd daily__dollar_volume_Nd_avg intraday__volume_pace_W intraday__dollar_volume_pace_W trades__trade_count_WINDOW trades__trade_rate_WINDOW
```

Capacidades candidatas o fronterizas:

```text
trades__signed_flow_WINDOW trades__aggressor_imbalance_WINDOW
```

Lectura:

```text
signed_flow y aggressor_imbalance probablemente pertenecen mejor a Order Flow Pressure.  Solo deberian entrar en Trading Activity si el modelo define actividad direccional como submodelo explicito.
```

## Tablas Que Aportan Evidencia

```text
004_master_daily_table = actividad diaria: volume, transaction_count, dollar_volume, relative volume.  014_master_intraday_bar_table = actividad intradia por barras cerradas: bar volume, transaction_count, session volume to time, volume pace.  015_microstructure_features_table = actividad de trades por ventana: trade count, trade rate, total volume, dollar volume, size distribution.  018_intraday_scanner_candidates_table = superficie de seleccion: motion/tradability thresholds and scanner lineage.
```

`018` no prueba por si solo el Objeto. Solo prueba que existen reglas de seleccion que pueden usar actividad como criterio.

## Fronteras Con Otros Dominios 

| Dominio vecino | Frontera |
| --- | --- |
| `Liquidity` | `Trading Activity` mide participacion negociada. `Liquidity` mide facilidad/coste/disponibilidad de negociar. `dollar_volume` puede aparecer en ambos con significado distinto. |
| `Price Movement` | `Trading Activity` no mide direccion, retorno, slope o aceleracion de precio. Solo contextualiza si esos movimientos ocurren con participacion suficiente. |
| `Price Location / Structure` | `Trading Activity` no mide donde esta el precio respecto a VWAP, HOD, LOD, open o prior close. |
| `Volatility / Range State` | `Trading Activity` no mide amplitud o dispersion del precio. Puede explicar si una expansion ocurre con participacion. |
| `Market Microstructure State` | `Trading Activity` no mide spread, depth, locked/crossed state ni quote condition. |
| `Order Flow Pressure` | `Trading Activity` es intensidad principalmente no direccional. `Order Flow Pressure` mide signo, agresion e imbalance. |
| `Short-Side Context` | `Short Activity` usa fuentes short con lag y semantica de crowding. No debe fusionarse automaticamente con trading activity observada intradia. |
| `Selection Surfaces` | Scanner/in-play candidates pueden usar actividad, pero no son actividad en si. Deben controlar sesgo de seleccion. |
| `Representation Quality State` | Missingness, coverage, repair lineage y gates de calidad no son participacion; solo condicionan si la actividad es interpretable. |

## Riesgos De Fusion O Division  Riesgo de fusion incorrecta:

```text
Fusionar Trading Activity con Liquidity porque ambas pueden usar dollar_volume o trade_count.
```

Riesgo de division incorrecta:

```text
Crear Daily Trading Activity e Intraday Trading Activity como Objetos separados, cuando probablemente son modelos o resoluciones temporales del mismo Objeto.
```

Riesgo de contamination:

```text
Incluir signed flow, aggressor imbalance u OFI sin decidir si pertenecen a Order Flow Pressure.
```

Riesgo temporal:

```text
Usar volumen diario final antes del market close.
```

Riesgo de seleccion:

```text
Confundir Attention Activity Candidate de 018 con actividad observable admitida.
```

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio tiene identidad semantica suficiente: preserva intensidad de participacion negociada.  No parece reducible a Price Movement, Liquidity, Microstructure, Order Flow, Quality ni Selection Surface.  Pero todavia necesita Representation Landscape antes de abrir Object Admission, porque debe decidir que modelos pertenecen al dominio y cuales deben moverse a dominios vecinos.
```

## Siguiente Paso

```text
Crear:  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\ 03_TABLES_feature_engineering\ 03_INFORMATION_OBJECTS\ DOMAIN_DEFINITIONS\ trading_activity_representation_landscape_v0_1.md
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\018\table_representation_audit_ES.md
```
