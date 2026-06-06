# Price Semantics and Adjustment Policy - Modulo 01

## 1. Rol del documento

Este documento fija la politica transversal del modulo para tratar, comparar y consumir series de precio cuando existen varias escalas o semanticas validas del mismo instrumento.

Su objetivo es evitar errores conceptuales y operativos en:

- reconciliacion con plataformas externas;
- construccion de labels y features;
- backtests de research y de produccion;
- simulacion de ejecucion;
- y evidencia institucional de dossiers.

La tesis central es simple:

```text
en el modulo 01 no existe un "precio unico";
existen vistas de precio con semanticas distintas y usos distintos.
```

Companion compacto:

- `price_semantics_rules_line_by_line.md`

## 2. Problema institucional que resuelve

La experiencia acumulada en `daily` y `quotes` ya muestra tres fuentes sistematicas de confusion:

- `quotes raw` puede vivir en una escala distinta a `daily raw`;
- `daily raw` puede no coincidir con charts externos en modo `adjusted`;
- y una comparacion visual aparentemente trivial puede mezclar:
  - raw intradia;
  - raw diario vendor-normalized;
  - y una vista ajustada por dividendos, splits o continuidad historica.

Si estas capas no se separan explicitamente:

- el backtest mezcla series incompatibles;
- el ML aprende corporate actions como si fueran alpha;
- la simulacion de ejecucion hereda precios economicamente irreconciliables;
- y la evidencia de inspeccion pierde autoridad.

## 3. Principio rector

Toda serie de precio que entre en el modulo debe declararse por:

- `price_basis`
- `adjustment_policy`
- `corporate_action_scope`
- `time_scope`
- `consumer_intent`

Ninguna comparacion, feature, label o PnL debe construirse sin haber declarado antes esa semantica.

## 4. Vistas canonicas de precio

El modulo debe distinguir, como minimo, estas vistas:

### 4.1 `quotes_raw`

Representa el libro observado `bid/ask` tal como aparece en la fuente intradia.

Uso principal:

- microestructura;
- crossed diagnostics;
- slippage;
- ejecucion;
- calidad local del libro;
- halts y episodios intradia.

No debe tratarse como serie de retorno economico intertemporal por defecto.

### 4.2 `trades_raw`

Representa prints observados de trade intradia.

Uso principal:

- reconstruccion de actividad;
- precio de ejecucion;
- consolidacion microestructural;
- validacion cruzada con `quotes_raw`.

No debe tratarse como serie de portfolio valuation sin politica explicita de limpieza y consolidacion.

### 4.3 `daily_raw`

Representa barras `daily` del vendor en su escala operativa primaria.

Puede venir ya:

- split-normalized;
- vendor-normalized;
- o parcialmente armonizada;

pero no debe presumirse ajustada economicamente salvo declaracion expresa.

Uso principal:

- auditoria de vendor;
- integridad `OHLCV`;
- research diario raw;
- reconciliacion con tablas historicas raw;
- y evidencia institucional del bloque `daily`.

### 4.4 `split_normalized`

Vista diaria o intradia reexpresada a una base coherente de split para comparabilidad temporal.

Uso principal:

- reconciliacion entre `quotes_raw` y `daily_raw`;
- continuidad de series cuando el split explica diferencias de escala;
- y comparaciones entre datasets con distinta politica de split handling.

### 4.5 `adjusted`

Vista economica ajustada por corporate actions relevantes para retornos comparables.

En la practica puede implicar:

- dividends;
- splits;
- stock dividends;
- spin-offs si la politica lo soporta;
- remaps corporativos compatibles con continuidad economica.

Uso principal:

- retornos economicos;
- portfolio valuation de research;
- factor research;
- labels de ML;
- benchmark comparison;
- drawdowns y analytics cross-sectional.

### 4.6 `adjusted_proxy`

Vista aproximada construida internamente para explicar una discrepancia con una plataforma externa cuando no existe todavia una cadena institucional completa de ajuste.

Uso principal:

- evidencia forense;
- contraste visual;
- explicacion de diferencias `raw` vs `adjusted`;
- y reduccion de falsos positivos en inspeccion.

No sustituye la vista `adjusted` institucional.

## 5. Regla de uso por capa funcional

### 5.1 Backtest

Un backtest institucional debe separar al menos cuatro funciones:

- `signal_price_view`
- `execution_price_view`
- `valuation_price_view`
- `benchmark_price_view`

Regla recomendada:

- señales de retorno medio plazo:
  - `adjusted`
- ejecucion y friccion:
  - `quotes_raw` y/o `trades_raw`
- valoracion del portfolio:
  - `adjusted`
- reconciliacion contra vendor raw:
  - `daily_raw`

No es admisible un backtest donde:

- la señal salga de una serie ajustada;
- la ejecucion se simule sobre esa misma serie ajustada;
- y luego se afirme realismo microestructural.

### 5.2 ML

Un pipeline ML debe declarar por separado:

- `feature_price_view`
- `target_price_view`
- `execution_price_view` si existe evaluacion economica

Regla recomendada:

- features microestructurales:
  - `quotes_raw`
- features diarios de tendencia/factor:
  - preferentemente `adjusted`
- targets de retorno:
  - `adjusted`
- labels de calidad/ejecucion:
  - `quotes_raw` o `trades_raw`

Riesgo a evitar:

- usar `raw close-to-close returns` como target cuando dividendos o splits generan saltos no economicos.

Eso convierte corporate actions en senal espuria.

### 5.3 Dossiers e inspeccion

Cuando un dossier compare dos escalas de precio, debe explicitar:

- que vista se usa en cada imagen;
- que capa explica la discrepancia;
- si la discrepancia queda:
  - `explicada por split`
  - `explicada por dividendos`
  - `explicada por ajuste externo`
  - `parcialmente explicada`
  - `abierta`

## 6. Jerarquia de verdad de precio

La jerarquia institucional recomendada es:

1. `quotes_raw` y `trades_raw`
   - verdad primaria del hecho microestructural observado
2. `daily_raw`
   - verdad primaria del vendor diario
3. `split_normalized`
   - vista de reconciliacion de escala
4. `adjusted`
   - verdad primaria de retorno economico comparable
5. `adjusted_proxy`
   - evidencia auxiliar de contraste, no verdad primaria

## 7. Workflow obligatorio de reconciliacion

Toda discrepancia de precio con plataforma externa debe seguir esta secuencia:

1. identificar si la comparacion es:
   - `raw_vs_raw`
   - `raw_vs_adjusted`
   - `adjusted_proxy_vs_adjusted`
   - `external_series_not_fully_identified`
2. comprobar corporate actions posteriores y previas:
   - dividends
   - splits
   - ticker remaps
3. comprobar si `quotes_raw` y `daily_raw` viven en la misma escala
4. si no, construir `split_normalized`
5. si la plataforma externa esta ajustada, construir `adjusted` o `adjusted_proxy`
6. decidir si la discrepancia queda explicada o sigue abierta

## 8. Arquitectura operativa objetivo

El modulo debe evolucionar hacia una arquitectura de `price views`, no de un unico precio.

Minimo institucional recomendado:

- `price_identity_registry`
- `corporate_actions_service`
- `quotes_raw_view`
- `trades_raw_view`
- `daily_raw_view`
- `split_normalized_view`
- `adjusted_view`
- `external_adjusted_proxy_view`

## 9. Respaldo cientifico e institucional

La politica de este documento no es una convencion local arbitraria. Se apoya en tres familias de autoridad:

- metodologias institucionales de corporate actions y construccion de series comparables;
- literatura de asset pricing y machine learning aplicada a retornos;
- y practica cuantitativa institucional sobre costes de implementacion y separacion entre senal, ejecucion y valoracion.

### 9.1 Corporate actions, precio raw y precio adjusted

La referencia institucional mas importante para este modulo es CRSP.

CRSP distingue explicitamente:

- precio observado;
- precio ajustado por splits;
- y tratamiento diferenciado de distribuciones no ordinarias y otras corporate actions.

Esto respalda directamente nuestra separacion entre:

- `daily_raw`
- `split_normalized`
- `adjusted`
- `adjusted_proxy`

Referencias principales:

- CRSP, *US Stock & Indexes Databases Calculations & Index Methodologies*:
  - https://www.crsp.org/wp-content/uploads/guides/CRSP_Calculations_and_Index_Methodologies.pdf
- CRSP, *Market Indexes Methodology Guide*:
  - https://www.crsp.org/wp-content/uploads/guides/CRSP_Market_Indexes_Methodology_Guide-December_2025.pdf
- CRSP, *US Stock Databases* overview:
  - https://www.crsp.org/research/crsp-us-stock-databases/

Lectura institucional derivada:

- no debe presumirse que una serie `daily` y una serie `quotes` esten en la misma escala;
- no debe presumirse que una plataforma externa muestre `raw`;
- y la normalizacion por split y el ajuste economico deben ser vistas explicitas, no inferencias tacitas.

### 9.2 Asset pricing y construccion correcta de retornos

La literatura de asset pricing exige que los retornos usados en investigacion, cross-section y comparaciones economicas sean comparables en presencia de corporate actions.

Esto respalda que:

- las senales de retorno medio plazo se construyan preferentemente sobre `adjusted`;
- y que `raw` no se use de forma ingenua como target economico si incorpora saltos no economicos.

Referencias principales:

- Kenneth R. French Data Library:
  - https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- CRSP Historical Indexes overview:
  - https://www.crsp.org/research/crsp-historical-indexes/

Lectura institucional derivada:

- los retornos para research y benchmarking no deben confundirse con el precio observado de ejecucion;
- y la comparabilidad economica de una serie exige una politica explicita de corporate actions.

### 9.3 Machine learning financiero y riesgo de leakage semantico

La literatura moderna de ML financiero insiste en que la construccion de labels, features y validacion temporal debe ser semantica y economicamente coherente.

Esto respalda que:

- las features microestructurales salgan de `quotes_raw` o `trades_raw`;
- los targets de retorno salgan de `adjusted`;
- y que una mezcla no declarada entre raw y adjusted introduzca leakage conceptual y labels espurios.

Referencias principales:

- Marcos Lopez de Prado, *Beyond Econometrics: A Roadmap Towards Financial Machine Learning*:
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3365282
- Shihao Gu, Bryan Kelly, Dacheng Xiu, *Empirical Asset Pricing via Machine Learning*:
  - NBER: https://www.nber.org/papers/w25398
  - Review of Financial Studies: https://academic.oup.com/rfs/article/33/5/2223/5758276

Lectura institucional derivada:

- `raw close-to-close returns` no deben tratarse como target por defecto;
- un shock por dividendo o split no debe entrar al modelo como si fuera alpha;
- y la semantica del precio es parte de la especificacion del modelo, no un detalle de ETL.

### 9.4 Implementabilidad real y separacion entre senal y ejecucion

La practica cuantitativa institucional y la literatura sobre costes de implementacion respaldan que:

- la senal y la valoracion pueden vivir en una vista ajustada;
- mientras que la ejecucion y el coste deben evaluarse en vistas raw de mercado.

Eso justifica nuestra separacion entre:

- `signal_price_view`
- `execution_price_view`
- `valuation_price_view`
- `benchmark_price_view`

Referencias principales:

- Andrea Frazzini, Ronen Israel, Tobias Moskowitz, *Trading Costs of Asset Pricing Anomalies*:
  - AQR: https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs-of-Asset-Pricing-Anomalies?aqrPDF=1
  - SSRN: https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2294498_code753937.pdf?abstractid=2294498&mirid=1
- Cliff Asness, Tobias Moskowitz, Lasse Pedersen, *Value and Momentum Everywhere*:
  - https://www.aqr.com/Insights/Research/Journal-Article/Value-and-Momentum-Everywhere?aqrPDF=1

Lectura institucional derivada:

- no es defendible simular ejecucion sobre una serie ya ajustada para retornos;
- y tampoco es defendible valorar un portfolio estrategico solo con microdatos raw sin una vista economica comparable.

### 9.5 Marco de arquitectura cuantitativa adaptativa

La literatura de Andrew Lo y el marco de `Adaptive Markets` respaldan una lectura arquitectonica mas amplia:

- distintos usos del dato exigen distintas representaciones y controles;
- las restricciones de implementacion, liquidez y microestructura importan tanto como la teoria de retorno;
- y un stack institucional debe distinguir observacion, transformacion economica y uso final.

Referencias principales:

- Andrew W. Lo, *The Adaptive Markets Hypothesis*:
  - https://www.mit.edu/~alo/Papers/JPM2004.pdf
- MIT OpenCourseWare, *Adaptive Markets*:
  - https://ocw.mit.edu/courses/15-481x-adaptive-markets-financial-market-dynamics-and-human-behavior-fall-2022/

Lectura institucional derivada:

- la coexistencia de varias `price views` no es un defecto del stack;
- es la forma correcta de acomodar microestructura, corporate actions, valoracion y evidencia externa dentro de una sola arquitectura.

## 10. Norma de documentacion operativa

Todo documento futuro que fije una decision operativa sobre precio, ajuste, retorno, comparacion externa, backtest o ML debe incluir como minimo:

- problema institucional que resuelve;
- politica o regla que fija;
- implicaciones por consumidor o departamento;
- riesgos o errores que evita;
- y respaldo cientifico o institucional suficiente.

El nivel esperado no es solo descriptivo. Debe ser:

- conceptual;
- metodologico;
- y trazable a literatura o metodologia reconocida cuando la decision afecte semantica de dato, retorno, ejecucion o ajuste.

## 11. Conclusion

La politica del modulo 01 no trata el precio como un campo unico.

Lo trata como una familia de vistas semanticas que deben:

- declararse;
- construirse;
- validarse;
- y consumirse segun su uso economico y operativo.

La combinacion de CRSP, asset pricing empirico, ML financiero y practica cuantitativa institucional respalda esta arquitectura.

Documentos auxiliares de infraestructura:

- `data_storage_topology_and_target_state.md`
- `event_families_and_reference_inventory.md`
- `price_views_registry.md`
- `corporate_actions_adjustment_methodology.md`

Y cada pipeline downstream debe declarar que vista consume.

## 9. Implicaciones inmediatas para el modulo 01

### 9.1 `daily`

`daily` no debe presentarse como automaticamente comparable con TradingView o Yahoo sin declarar:

- si la plataforma externa esta en modo `adjusted`;
- y si nuestra comparacion esta usando `daily_raw` o una vista ajustada.

### 9.2 `quotes`

`quotes` puede vivir en una escala distinta a `daily_raw` o a una plataforma externa `adjusted`.

Eso no debe interpretarse automaticamente como error del libro.

Primero debe evaluarse si:

- la diferencia es de split normalization;
- la vista diaria ya esta vendor-normalized;
- o la plataforma externa esta mostrando `adjusted`.

### 9.3 Backtest institucional

No debe existir un solo `close` consumido indistintamente para:

- señal;
- ejecucion;
- valoracion;
- y contraste externo.

Esa simplificacion no es aceptable para una arquitectura de hedge fund rigurosa.

## 10. Base literaria y respaldo metodologico

### 10.1 CRSP - ajuste y corporate actions

La referencia metodologica mas importante para separar series `raw` y `adjusted` es la practica CRSP.

CRSP documenta explicitamente que:

- mantiene datos no ajustados;
- y proporciona factores para llevar precios y dividendos a una base comparable;
- incluyendo splits, stock dividends, spin-offs y otras distribuciones.

Esto respalda que:

- `raw` y `adjusted` son objetos distintos;
- y la comparabilidad temporal exige una politica de corporate actions.

Fuentes:

- CRSP, *CRSP Calculations and Index Methodologies*  
  https://www.crsp.org/wp-content/uploads/guides/CRSP_Calculations_and_Index_Methodologies.pdf
- CRSP, *Market Indexes Methodology Guide*  
  https://www.crsp.org/wp-content/uploads/guides/CRSP_Market_Indexes_Methodology_Guide-December_2025.pdf

### 10.2 Marcos Lopez de Prado - ML financiero y separacion de capas

Lopez de Prado insiste en que un stack de ML financiero serio debe distinguir:

- investigacion;
- leakage;
- labels;
- y uso economicamente defendible del dato.

Eso respalda nuestra politica de:

- declarar `feature_price_view`;
- declarar `target_price_view`;
- y no tratar corporate actions como si fueran alpha.

Fuentes:

- Lopez de Prado, *Machine Learning for Asset Managers*  
  https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3558728_code434076.pdf?abstractid=3558728&mirid=1
- Cornell ORIE profile  
  https://www.engineering.cornell.edu/orie/faculty-directory/marcos-lopez-de-prado

### 10.3 Gu, Kelly y Xiu - asset pricing con ML

La literatura moderna de asset pricing con ML trabaja sobre retornos economicamente comparables, no sobre shocks espurios generados por corporate actions mal tratadas.

Eso refuerza que:

- labels y retornos de ML deben vivir en `adjusted`;
- mientras la microestructura puede y debe vivir en `raw`.

Fuentes:

- Gu, Kelly, Xiu, *Empirical Asset Pricing via Machine Learning*  
  https://www.nber.org/papers/w25398
- Review of Financial Studies version  
  https://academic.oup.com/rfs/article/33/5/2223/5758276

### 10.4 AQR - implementabilidad, trading costs y realismo

La literatura aplicada de AQR muestra que la validez de una estrategia no descansa solo en el retorno bruto, sino en:

- costes de trading;
- implementabilidad;
- y portfolio construction realista.

Esto respalda nuestra separacion entre:

- vista de senal;
- vista de ejecucion;
- vista de valoracion.

Fuentes:

- Frazzini, Israel, Moskowitz, *Trading Costs of Asset Pricing Anomalies*  
  https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs-of-Asset-Pricing-Anomalies?aqrPDF=1
- Asness et al., *Value and Momentum Everywhere*  
  https://www.aqr.com/Insights/Research/Journal-Article/Value-and-Momentum-Everywhere

### 10.5 Andrew Lo - Adaptive Markets

Andrew Lo enfatiza una vision adaptativa y sistemica del mercado, donde la semantica del dato, el contexto institucional y la implementacion importan tanto como el modelo predictivo.

Esto encaja con la politica del modulo:

- no basta con "tener precios";
- hay que tener capas semanticas de precio gobernadas y trazables.

Fuentes:

- MIT OCW, *Adaptive Markets*  
  https://ocw.mit.edu/courses/15-481x-adaptive-markets-financial-market-dynamics-and-human-behavior-fall-2022/
- MIT Sloan, *Adaptive Markets* overview  
  https://mitsloan.mit.edu/press/can-market-be-both-rational-and-irrational

### 10.6 Fama-French - retornos comparables

La investigacion factorial clasica presupone retornos comparables y series coherentes.

Sin una politica correcta de corporate actions, los resultados de value, momentum o quality quedan contaminados en origen.

Fuente:

- Kenneth French Data Library  
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

## 11. Regla de excelencia documental

Toda decision operativa del modulo que:

- cambie consumo de datos;
- fije una politica de ajuste;
- defina consumers permitidos;
- o altere la semantica de una vista de precio

debe quedar explicada con:

- justificacion conceptual;
- implicacion operativa;
- riesgos evitados;
- y, cuando exista literatura relevante, respaldo metodologico explicito.

No basta con una regla corta o una preferencia local.

Debe quedar trazable por que esa decision mejora:

- rigor cientifico;
- defendibilidad de backtest;
- y robustez de ML.

## 12. Conclusion institucional

El modulo 01 no debe organizarse alrededor de un unico precio, sino alrededor de vistas de precio con semanticas bien definidas.

La politica correcta es:

- preservar el `raw`;
- construir vistas ajustadas cuando la tarea lo exija;
- separar senal, ejecucion y valoracion;
- y documentar toda comparacion externa con semantica explicita.

Esta politica es fundacional para una arquitectura de hedge fund rigurosa, reproducible y compatible con research, backtest y ML de nivel institucional.
