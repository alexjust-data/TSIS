# Price Location / Structure - Domain Definition v0.1

Status: `domain_definition_v0_1`
Date: `2026-07-20`
Scope: `cluster_3_pre_landscape_pre_admission`

Este documento define el dominio semantico `Price Location / Structure`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona modelos finales.
No autoriza variables para `Market State` ni `Event State`.
No modifica tablas, schemas, builders, contratos ni datasets.

## Nombre Del Dominio

```text
Price Location / Structure
```

## Que Informacion Intenta Preservar

```text
Donde esta situado el precio observable en t respecto a referencias estructurales legalmente conocidas.
```

El dominio intenta preservar informacion sobre:

```text
posicion contra VWAP, posicion contra HOD/LOD hasta t, posicion contra apertura, posicion contra prior close, posicion dentro del rango observado, y distancia a anchors relevantes de sesion o segmento.
```

La informacion central no es:

```text
como cambia el precio, cuanta volatilidad hay, cuanto volumen acompana, ni que retorno futuro ocurrio.
```

La informacion central es:

```text
localizacion contextual del precio.
```

## Por Que Este Dominio Merece Existir

```text
Porque un mismo precio absoluto no tiene significado estable sin saber donde esta ubicado respecto a referencias de sesion, historia reciente y estructura intradia.
```

En small caps y microcaps, el estado no se interpreta igual si el precio esta:

```text
cerca del high de sesion, lejos del VWAP, recuperando prior close, pegado al low, o en mitad de un rango observado.
```

Este dominio merece existir porque conserva una incertidumbre distinta:

```text
que posicion estructural ocupa el precio en t?
```

## Que Perderia TSIS Si Este Dominio Desapareciera  TSIS perderia capacidad para distinguir:

```text
movimiento alcista cerca de HOD vs lejos de HOD; precio sobre VWAP vs bajo VWAP; recuperacion de prior close vs rechazo bajo prior close; precio extendido vs precio central dentro del rango; pullback poco profundo vs perdida estructural; y evento cerca de una referencia critica vs evento sin referencia contextual.
```

## Que No Representa  Este dominio no representa:

```text
direccion del cambio como fenomeno principal, velocidad o aceleracion, amplitud/dispersion como volatilidad, participacion negociada, liquidez, order flow, noticias, fundamentales, outcomes futuros, ni calidad tecnica del dataset.
```

Distincion clave:

```text
return_vs_session_open puede ser Price Movement si se interpreta como cambio.  La misma magnitud puede ser Price Location si se interpreta como distancia actual a un anchor estructural.
```

El significado lo decide:

```text
Dominio -> Objeto -> Modelo -> Uso legal.
```

## Preguntas Cientificas Que Permite Formular

```text
Donde esta el precio respecto a VWAP en t?  Esta cerca de HOD o LOD observado hasta t?  Esta recuperando, perdiendo o alejandose de prior close?  Esta extendido respecto a apertura o segmento?  La respuesta a un evento cambia si ocurre cerca de referencias clave?  La probabilidad de continuation/failure cambia segun posicion estructural?
```

## Candidatos Incluidos  Detectados en la primera pasada:

```text
Intraday Position distance to VWAP distance to HOD distance to LOD distance to session open distance to prior close Overnight Dislocation
```

Lectura actual:

```text
Price Location / Structure = candidato principal a Objeto de Informacion.  Intraday Position = modelo intradia del mismo Objeto.  VWAP Distance = modelo de localizacion contra precio medio negociado.  HOD/LOD Distance = modelo de localizacion contra extremos observados hasta t.  Overnight Dislocation = frontera con Price Movement cuando mide gap; modelo de localizacion cuando mide distancia actual a prior close.
```

## Posibles Modelos De Representacion

```text
session anchor location model VWAP location model HOD/LOD proximity model range position model prior close recovery model pullback / retrace location model segment anchor location model
```

## Capacidades Derivables Relacionadas

### Capacidades Imprescindibles

```text
intraday__bar_close_price intraday__high_so_far intraday__low_so_far intraday__vwap_distance_ratio intraday__return_vs_session_open_ratio intraday__return_vs_prior_close_ratio
```

### Capacidades Complementarias

```text
intraday__return_vs_segment_open_ratio intraday__pullback_ratio_W intraday__retrace_ratio_W daily__open_price daily__prior_close
```

### Capacidades Pendientes O Fronterizas

```text
distance_to_session_hod distance_to_session_lod session_range_position anchored_vwap_distance final_daily_high_low_distance
```

Lectura:

```text
HOD/LOD final del dia no es legal intradia. Solo high_so_far/low_so_far hasta t puede ser decision-safe.
```

## Tablas Que Aportan Evidencia

```text
004_master_daily_table = referencias diarias: open, prior_close, high/low/close despues del cierre.  013_ohlcv_1m_quote_guarded = fuente 1m guarded para construir referencias intradia.  014_master_intraday_bar_table = barras cerradas, high_so_far, low_so_far, VWAP/distance candidates y anchors intradia.
```

## Fronteras Con Otros Dominios 

| Dominio vecino | Frontera |
| --- | --- |
| `Price Movement` | Movimiento mide cambio. Location mide posicion respecto a referencias. |
| `Volatility / Range State` | Volatility mide amplitud/dispersion. Location puede usar rango como coordenada, no como incertidumbre. |
| `Trading Activity` | Activity mide participacion negociada. Location no mide volumen. |
| `Liquidity` | Liquidity mide coste/facilidad de negociar. Location no mide spread/depth. |
| `Outcome Layer` | Future HOD/LOD, future returns y future extrema son outcomes, no location observable. |
| `Representation Quality State` | Cobertura y repair lineage condicionan confianza, pero no son localizacion. |

## Decision De Dominio

```text
decision = ready_for_representation_landscape
```

Motivo:

```text
El dominio tiene identidad semantica suficiente: preserva localizacion contextual del precio.  No queda absorbido por Price Movement ni Volatility. Pero necesita landscape para separar anchors, VWAP, HOD/LOD, range position y pullback/retrace.
```

## Siguiente Paso

```text
Crear:  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\ 03_TABLES_feature_engineering\ 03_INFORMATION_OBJECTS\ DOMAIN_DEFINITIONS\ price_location_structure_representation_landscape_v0_1.md
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
