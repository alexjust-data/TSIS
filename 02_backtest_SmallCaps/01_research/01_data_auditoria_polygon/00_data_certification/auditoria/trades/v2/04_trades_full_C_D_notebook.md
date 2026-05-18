`04_trades_root_cause_audit_notebook.ipynb` funciona como notebook de descubrimiento y diseño analítico. Explora el problema, prueba hipótesis, compara versiones del validador, construye taxonomías, decide qué señales importan y empuja a crear helpers, builders y caches. `04_trades_full_C_D_audit.ipynb` es la cristalización de ese trabajo. Ya no investiga desde cero, consume el resultado estructural de esa fase anterior, se centra en el `current` final `C + D` y presenta el análisis final de forma estable, ligera y reproducible. Dicho con más precisión, el primero no alimenta directamente al segundo como dependencia de datos brutos del notebook, sino que guía la arquitectura, la semántica y los artefactos que luego el segundo usa. En una fórmula corta: `root_cause_audit_notebook = cuaderno de I+D y formulación` y `full_C_D_audit = cuaderno final de lectura operativa sobre el dataset consolidado`.

`Notebook de referencia:` [04_trades_full_C_D_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/04_trades_full_C_D_audit.ipynb). `Fecha del readout:` 2026-04-14. `Dataset auditado:` `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet`. Este documento deja constancia compacta, celda por celda a nivel visual, de lo que calcula cada bloque del notebook, qué salida produce y qué lectura técnica aporta sobre la data auditada `C + D`.

**Imagen 14. Snapshot ejecutivo de severidad del full C+D**

![14](img/14.png)

Esta figura corresponde al bloque inicial de snapshot y resume la distribución global de severidades del `current` final. La motivación es fijar primero la foto macro del dataset antes de entrar en causas, concentración temporal o taxonomías de ruptura.

**resultado**

La salida muestra una población claramente dominada por `SOFT_FAIL` y `HARD_FAIL`, con `PASS` como fracción minoritaria. La lectura correcta no es “hay algunos errores”, sino “la parte problemática domina el materializado final”. Eso obliga a interpretar todo el notebook como una auditoría de una data estructuralmente tensionada frente a referencias, no como una revisión de residuo pequeño.

**Imagen 15. Evolución por batch y deriva de severidad**

![15](img/15.png)

Esta imagen analiza si la severidad se mantiene estable o deriva al recorrer el materializado por batches. La motivación es detectar si el problema depende del tramo de procesamiento, del orden de materialización o de algún subconjunto del dataset.

**resultado**

La salida enseña tasas por batch y su suavizado temporal, lo que permite ver si `PASS`, `SOFT_FAIL` y `HARD_FAIL` cambian de forma sistemática. El resultado figurativo es una deriva visible y no completamente plana, lo que sugiere heterogeneidad temporal o poblacional en el full. Su lectura es importante porque indica que no basta con una sola métrica global: el residuo cambia según el tramo y eso apunta a concentración temporal o por cohortes.

**Imagen 16. Conteo de issues y warns dominantes**

![16](img/16.png)

Este gráfico abre la raíz causal primaria del `current` ya materializado. La motivación es transformar el reparto de severidades en causas observables y ver qué reglas del validador están explicando realmente la masa de files problemáticos.

**resultado**

La salida enseña que el `issue` duro dominante es `trade_price_outside_daily_range`, mientras que entre los `warns` destacan `trade_price_outside_1m_range`, `duplicate_exact_trade_rows_present` y `off_session_trades_present`. La lectura inteligente aquí es que el problema no es genérico ni difuso: está articulado alrededor de ruptura contra referencias de precio y, además, viene acompañado por duplicados y actividad fuera de sesión como contaminantes estructurales.

**Imagen 17. Evidencia agregada por issue dominante**

![17](img/17.png)

Esta figura complementa la anterior midiendo para cada `issue` cuántos files, cuántos tickers y cuántas fechas quedan afectados. La motivación es distinguir si una causa grande está inflada por repetirse muchas veces en pocos activos o si realmente atraviesa el universo.

**resultado**

La salida muestra que el `issue` dominante no vive en un puñado de nombres, sino que alcanza miles de tickers y miles de fechas. Eso que la anomalía principal tiene extensión horizontal sobre el universo y profundidad vertical en el tiempo. En términos de calidad de data, esto refuerza la idea de que no estamos ante un edge case operativo, sino ante una patología sistémica del dataset o de su alineación con referencias.

**Imagen 18. Concentración temporal de problemas**

![18](img/18.png)

Esta imagen mide dónde se concentran los problemas por mes y por año. La motivación es detectar si la severidad es homogénea a lo largo del histórico o si existen ventanas temporales especialmente deterioradas.

**resultado**

La salida muestra variaciones temporales visibles, no una estructura plana. Eso quiere decir que el residuo tiene régimen temporal y que hay épocas donde la presión de `SOFT_FAIL` y `HARD_FAIL` sube con claridad. La lectura correcta es que la data no debe tratarse como una sola población estable; conviene pensarla por tramos temporales, porque la intensidad del problema cambia.

**Imagen 19. Tickers con mayor carga de HARD_FAIL**

![19](img/19.png)

Aquí el notebook cambia la dimensión temporal por la dimensión ticker. La motivación es identificar si el problema, además de masivo en agregado, se concentra de forma extrema en ciertos nombres.

**resultado**

La salida da un ranking de tickers donde la tasa de `HARD_FAIL` es extraordinariamente alta, con casos cercanos al `100%`. Eso que dentro del full hay subconjuntos de activos donde la data está prácticamente tomada por la anomalía. La consecuencia es importante: aunque el problema sea general, también hay clústeres de severidad extrema que merecen lectura diferenciada y no deben diluirse en el promedio global.

**Imagen 20. Diagnóstico de escala y duplicados**

![20](img/20.png)

Esta figura combina dos diagnósticos quirúrgicos: posible desalineación de escala frente a referencias y distribución del exceso de duplicados por severidad. La motivación es separar una explicación por `scale mismatch` de una explicación por contaminación de prints duplicados.

**resultado**

La salida sugiere que los casos de escala existen, pero no dominan la población. En cambio, la distribución de `duplicate_excess_ratio_pct` castiga mucho más a `HARD_FAIL` que a `PASS`. La lectura técnica es que la duplicación pesa más como estructura del residuo que la escala. Eso no elimina el problema de escala, pero sí lo relega como explicación parcial, no central.

**Imagen 21. Vista general de ruptura daily por lado y magnitud**

![21](img/21.png)

Esta imagen inaugura el bloque específico de `trade_price_outside_daily_range`. La motivación es descomponer la ruptura en `below_only`, `above_only` y `both`, y visualizar la magnitud del corte por lado.

**resultado**

La salida muestra una dominancia muy clara de `below_only` frente a `above_only` y `both`. Eso que la ruptura contra `daily` no es simétrica. La forma del problema no parece compatible con ruido aleatorio alrededor del rango diario, sino con una estructura donde el corte por abajo tiene hegemonía estadística.

**Imagen 22. Concentración temporal de la ruptura contra daily**

![22](img/22.png)

Este gráfico lleva la ruptura daily a la dimensión temporal. La motivación es ver si `outside_daily_range` aparece de manera uniforme o si se agrupa por épocas del histórico.

**resultado**

La salida dibuja una serie temporal y resúmenes anuales donde la carga de ruptura cambia de forma visible. La lectura es que el problema `outside_daily_range` tampoco es estacionario. Hay pulsos temporales y fases más cargadas, lo que puede reflejar cambios de calidad de referencia, composición del universo o patrones de microestructura que no se repiten igual en todo el histórico.

**Imagen 23. Dispersión corte por abajo frente a corte por arriba**

![23](img/23.png)

Aquí se baja a un plano de dispersión entre magnitud de ruptura por abajo y por arriba. La motivación es ver si ambos tipos de corte coexisten de forma equilibrada o si una dirección domina la geometría del problema.

**resultado**

La salida muestra una nube claramente sesgada y poco compatible con simetría. La mayor parte de la masa no se reparte de forma equivalente entre ambos lados. La lectura correcta es que la ruptura tiene dirección dominante y que `below_only` no es un artefacto visual de otra tabla, sino una propiedad geométrica del residuo.

**Imagen 24. Distribuciones capadas al p99 de las rupturas**

![24](img/24.png)

La motivación de esta imagen es quitar el efecto de los outliers más violentos y observar la masa central del problema. Por eso las distribuciones se capan al `p99`.

**resultado**

La salida enseña que, incluso eliminando el 1% más extremo, las colas siguen siendo pesadas. Eso que la anomalía no depende solo de unos pocos casos gigantes. La población central ya viene dañada y mantiene ruptura material en magnitud absoluta o relativa. En términos de auditoría, esto refuerza que el problema es poblacional, no anecdótico.

**Imagen 25. Vista anual de side y magnitud de rupturas**

![25](img/25.png)

Esta figura resume cómo se reparte el lado de la ruptura y su tamaño a lo largo de los años. La motivación es unir dirección y magnitud en una lectura temporal más compacta.

**resultado**

La salida deja ver que ni la composición por lado ni la magnitud de la ruptura se comportan igual en todo el histórico. La lectura inteligente es que el régimen de `outside_daily_range` cambia con el tiempo. Eso vuelve a apoyar la idea de que el dataset no debe leerse como una sola población homogénea, sino como varias cohortes temporales con comportamiento distinto.

**Imagen 26. Conteo por bandas absolutas y relativas**

![26](img/26.png)

Esta imagen bucketiza la ruptura en bandas absolutas y porcentuales. La motivación es convertir una variable continua en una estructura más legible y comprobar si el problema es grande en dinero absoluto o sobre todo en proporción al rango diario.

**resultado**

La salida muestra mucha masa cerca de cero en magnitud absoluta, pero una distribución muy desplazada hacia bandas altas cuando la ruptura se expresa como porcentaje del rango diario. La lectura técnica es fuerte: muchas rupturas son pequeñas en términos monetarios, pero gigantescas respecto al `daily span`. Eso sugiere que la referencia diaria puede ser demasiado estrecha para acomodar el universo de trades observado, o que hay un desacople serio entre ambos mundos.

**Imagen 27. Cruce entre bandas y lado de la ruptura**

![27](img/27.png)

Esta figura cruza las bandas absolutas y relativas con `break_side`. La motivación es ver qué lado domina dentro de cada bucket y no solo en agregado total.

**resultado**

La salida confirma que `below_only` gana peso en gran parte de las bandas relevantes, especialmente donde se acumula mucha masa de files. Eso refuerza que el sesgo direccional no es local a una sola escala. Cambia la magnitud, pero la dirección dominante del residuo persiste.

**Imagen 28. Porcentaje interno por bucket y lado**

![28](img/28.png)

La motivación aquí ya no es contar files brutos, sino medir la composición interna de cada bucket. Es una lectura de mezcla, no de volumen absoluto.

**resultado**

La salida convierte el cruce anterior en porcentajes internos y enseña que la dominancia relativa por lado se mantiene bastante estable a través de buckets. La lectura correcta es que la forma del problema no depende solo de cuánto rompe, sino también de un patrón estructural persistente en la dirección de la ruptura. Eso hace el residuo más coherente y menos compatible con simple ruido.

**Imagen 29. Taxonomía agregada del residuo**

![29](img/29.png)

Esta es una de las figuras más importantes del notebook porque resume el universo de `outside_daily_range` en familias operativas. La motivación es pasar de métricas sueltas a taxonomías interpretables.

**resultado**

La salida muestra que dominan familias como `confirmed_by_1m_and_not_scale` y `confirmed_by_1m_and_dup_heavy`. La lectura fuerte aquí es que el residuo principal queda confirmado por `1m`, por lo que no parece mero artefacto de `daily` ni simple `scale mismatch`. Esto endurece claramente la interpretación: una parte muy grande del problema parece real frente a referencia intradía.

**Imagen 30. Taxonomía cruzada con lado de la ruptura**

![30](img/30.png)

Esta imagen abre la taxonomía por `break_side`. La motivación es ver si las familias principales cambian de anatomía al separar ruptura por abajo, por arriba o por ambos lados.

**resultado**

La salida enseña para cada taxonomía cuánto pesa cada lado y cuál es su magnitud mediana. El significado es que las familias no son equivalentes entre sí: unas están mucho más cargadas hacia `below_only`, otras combinan lados o vienen asociadas a mayor magnitud. Eso permite separar subpoblaciones más plausibles y estructurales de otras más ambiguas o mixtas.

**Imagen 31. Señal por banda absoluta y relativa**

![31](img/31.png)

Esta figura relaciona las bandas de ruptura con tres señales: confirmación por `1m`, advertencia de escala y actividad fuera de sesión. La motivación es medir qué explicación gana peso cuando cambia la magnitud.

**resultado**

La salida muestra porcentajes muy altos de confirmación por `1m` a lo largo de gran parte de las bandas, mientras que la advertencia de escala se mantiene residual. La actividad fuera de sesión aparece, pero no desplaza la señal principal. La lectura es que, a distintas escalas de ruptura, la explicación dominante sigue siendo “la rotura queda refrendada por la referencia intradía”.

**Imagen 32. Señal por lado de ruptura**

![32](img/32.png)

La última imagen condensa la explicación por `break_side`. La motivación es ver si `above_only`, `below_only` y `both` difieren en confirmación por `1m`, en aviso de escala o en presencia de trades fuera de sesión.

**resultado**

La salida muestra que la confirmación por `1m` sigue siendo muy alta en todos los lados, mientras que `scale mismatch` permanece bajo y `off-session` actúa más como contexto que como causa dominante. La lectura final del notebook queda reforzada: el residuo principal parece amplio, real y confirmado por referencia intradía, no una ilusión creada por unos pocos errores de escala o por actividad periférica aislada.

### Lectura rápida de problemas por orden descendente

`trade_price_outside_daily_range`:  
es el problema más importante del dataset. que una parte enorme de los trades queda fuera del rango `daily`, y por tanto el conflicto principal está entre la cinta de trades y la referencia OHLCV diaria.   
Imágenes : `16`, `17`, `21`, `22`, `26`, `29`.

`trade_price_outside_1m_range`:  
es la segunda señal más grave porque confirma el problema contra una referencia intradía más fina. Cuando aparece junto con `outside_daily_range`, el caso deja de parecer simple estrechez del `daily` y pasa a parecer ruptura más real. 
Imágenes : `16`, `29`, `31`, `32`.

`confirmed_by_1m_and_not_scale`:    
no es un `issue` raw, pero sí la taxonomía más importante del residuo. que el problema principal queda confirmado por `1m` y no se explica por desalineación de escala. Es la señal más fuerte de que el residuo duro probablemente es real. 
Imágenes : `29`, `31`, `32`.

`duplicate_exact_trade_rows_present` y `duplicate_excess_ratio_gt_hard_cap`:    
significan contaminación por repetición de prints. No hablan solo de precios fuera de rango, sino de una cinta que además puede venir inflada o distorsionada por duplicación. Eso degrada volumen, intensidad y cualquier lectura microestructural derivada.  
Imágenes : `16`, `20`, `29`.

`off_session_trades_present`:  
que una parte relevante del residuo vive o se apoya en trades fuera de sesión regular. No implica por sí solo dato incorrecto, pero sí un contexto donde la microestructura es más frágil y las referencias agregadas pueden encajar peor. 
Imágenes : `16`, `31`, `32`.

`below_only`: es el lado dominante de la ruptura y por eso debe tratarse como una señal importante en sí misma. que el problema no es simétrico; el residuo rompe mucho más por abajo que por arriba. Eso hace menos verosímil una explicación de ruido aleatorio.   
Imágenes : `21`, `23`, `27`, `28`, `30`, `32`.

`scale mismatch`: existe, pero no parece la explicación dominante. Su significado es que en ciertos casos trades y referencias parecen vivir en escalas distintas, pero el notebook sugiere que esa familia explica solo una parte menor del residuo.   
Imágenes : `20`, `29`, `31`, `32`.

`concentración extrema por ticker`: que, además del problema sistémico global, hay nombres concretos donde la anomalía prácticamente coloniza toda la historia disponible. Es importante para priorización, porque esos tickers requieren lectura específica y no deben quedar diluidos en el promedio del universo.   
Imágenes : `17`, `19`.

`heterogeneidad temporal del residuo`: que la severidad no se comporta igual en todo el histórico. Hay periodos más deteriorados que otros, lo que apunta a cohortes temporales, cambios de régimen o fases del pipeline donde la fricción con referencias se vuelve más intensa.   
Imágenes : `15`, `18`, `22`, `25`.
