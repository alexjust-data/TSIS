Realizado

1. Definimos el mercado y el universo PIT.
2. Definimos el fenómeno observable completo:
    Dormancy -> activación -> In-Play -> Frontside -> termination -> Backside.

3. Formulamos la pregunta científica general y la particular de Wake-up.
4. Definimos las necesidades de información.
5. Identificamos el perfil candidato de Information Objects.
6. Definimos un Representation Model candidato para cada objeto.
7. Establecimos los hard gates y el protocolo de admisión.
8. Definimos Wake-up como Event Type candidato, separado de detector, estrategia y outcome.
9. Elegimos Trading Activity como primer objeto para implementación física.
10. Auditamos la fuente física legacy de trades.
11. Limitamos provisionalmente el experimento a RTH research-only.
12. Definimos coverage, elegibilidad, temporalidad, missingness, latencia y baseline PIT.
13. Especificamos las variables de Binding A.
14. Implementamos y probamos su kernel.
15. Ejecutamos un smoke físico de una partición.
16. Documentamos estado, hitos, handoff y roadmap completo.

Pendiente: Trading Activity

1. Diseñar el piloto multisesión.
2. Ejecutar la materialización symbol-second.
3. Emitir el readout y cerrar el source gate legacy.
4. Ampliar a una muestra estratificada.
5. Implementar Binding B.
6. Justificar e implementar Binding C, si aporta información.
7. Comparar A/B/C con el mismo presupuesto de falsas alarmas.
8. Ejecutar validación temporal OOS.
9. Admitir o rechazar el modelo.
10. Promover las variables ganadoras, si procede.
11. Definir tablas, builders, validators y lineage.
12. Revalidar tras el backfill completo de Massive.

Pendiente: demás objetos CORE

Para cada objeto habrá que repetir auditoría física, variables, bindings, piloto, comparación, OOS,
admisión y mapping:

1. Market Microstructure State
2. Price Movement
3. Liquidity

Pendiente: SUPPORTING CONTEXT

1. Volatility / Range State
2. Price Location / Structure

Para cada uno:

source audit
-> physical bindings
-> tests and pilot
-> validation
-> admission
-> table mapping and lineage

Pendiente: CONDITIONAL CONTEXT

1. Fundamental Context
2. News / Catalyst Context
3. Halt Context

Además habrá que definir cuándo están disponibles, cuándo son obligatorios y cómo propagan unknown,
unavailable y stale.

Pendiente: DEFERRED EXTENSION

1. Order Flow Pressure

Solo avanzará cuando estén validados:

trade classification
trade/quote alignment
classification confidence
classifiable coverage

Cierre de todos los Objects

Trading Activity
+ Market Microstructure State
+ Price Movement
+ Liquidity
+ Volatility / Range State
+ Price Location / Structure
+ Fundamental Context
+ News / Catalyst Context
+ Halt Context
+ Order Flow Pressure, si se admite
=
WAKE_UP INFORMATION OBJECT PROFILE IMPLEMENTED

Después de cerrar todos los Objects todavía faltará:

integración de representaciones
-> Wake-up Detector
-> calibración
-> evaluación OOS
-> Episode Instance
-> promoción operacional

Ahora seguimos con el piloto multisesión de Trading Activity.


====================================

====================================


El siguiente orden correcto es:

1. Congelar la arquitectura de 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/_00_CTO/00_apuntes_Q_ES_WAKE_UP.md:
    - onset mínimo = transición de Trading Activity;
    - Wake-up compuesto = evidencia multiobjeto;
    - In-Play y decisión estratégica = capas posteriores.

2. Crear el perfil experimental Wake-up RTH para A/B, incluyendo LEFT_CENSORED_ACTIVE_AT_SCOPE_START cuando el despertar ocurrió
    antes de las 09:30.

3. Construir un panel ciego y estratificado de positivos, negativos, ambiguos y artefactos para resolver WUL-D01…D08. Los
    gráficos orientan la semántica, pero no bastan para fijar umbrales.

4. Congelar D07: definición numérica del label, episodios, matching y presupuesto de falsas activaciones.
5. Materializar labels y denominador de development; después cerrar y sellar D12.
6. Auditar y congelar B-02. Solo entonces implementar Binding B, ejecutar probes por shard, materializarlo y comparar A/B.

Objeción concreta: el contrato D07 actual parece definir únicamente el onset de Trading Activity. Debe nombrarlo explícitamente
como ACTIVITY_TRANSITION_DETECTED, evitando presentarlo como el Wake-up compuesto completo.

---

## 1. Sí: actualizar documentos

No crear uno nuevo. Actualizar estos dos existentes:

1. 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/01_DEFINITION/01_WAKE_UP_EVENT_DEFINITION.md

    Convertir en contrato formal lo definido en tus apuntes:
    - transición mínima de Trading Activity;
    - Wake-up compuesto multiobjeto;
    - In-Play y estrategia como capas posteriores.

2. 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/00_WAKE_UP_END_to_END.md

    Reflejar esa secuencia completa. El archivo permanece exactamente donde lo has colocado.

No modificaría la nota fuente:

C:\TSIS_Data\00_CTO\04_MARKET_STATES_CREATION\04_EVENTS\WAKE_UP\_00_CTO\00_apuntes_Q_ES_WAKE_UP.md

## 2. Qué significa el perfil RTH

A y B actuales solo observan aproximadamente:

09:30–16:00

Por tanto:

- pueden estudiar Wake-ups que empiezan durante RTH;
- no pueden localizar un Wake-up ocurrido en premarket;
- si el ticker ya llega despierto a las 09:30, debe marcarse LEFT_CENSORED_ACTIVE_AT_SCOPE_START, no inventar un Wake-up a las
09:30.

No es otro tipo de Wake-up. Es el mismo evento bajo una cobertura temporal limitada.

## 3. Panel y WUL-D01…D08

Un panel es una muestra controlada de casos reales:

Wake-ups claros
activaciones progresivas
one-print/dust
actividad alta pero normal
datos defectuosos
casos ambiguos
tickers ya activos al abrir RTH

Se revisan sin mostrar resultados de Binding A o B, para fijar justamente las reglas del label.

Los gráficos a los que me refería son los ejemplos visuales que aportaste anteriormente: TIVC, LOBO, AZTR, POAI, VERO, NKGN,
GPUS, etc. Sirven para entender el fenómeno, pero no para calcular por sí solos los umbrales.

WUL-D01…D08 son las ocho decisiones pendientes del contrato:

- WUL-D01: horizonte de confirmación.
- WUL-D02: cómo medir el régimen dormido anterior.
- WUL-D03: cuánto cambio relativo constituye anomalía.
- WUL-D04: actividad económica mínima antirruido.
- WUL-D05: mínimo de eventos/timestamps distintos.
- WUL-D06: cobertura y resolución mínima de los datos.
- WUL-D07: cierre, reset y reactivación del episodio.
- WUL-D08: oracle automático o adjudicación humana.

## 4. Qué significa cerrar D07

Después del panel se fijan esos valores y se actualizan:

- 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/03_LABELS/WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md
- 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/03_LABELS/TRADING_ACTIVITY_FALSE_ACTIVATION_COUNTING_CONTRACT_v0_1.md
- 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/03_LABELS/WAKE_UP_LABEL_AND_DENOMINATOR_MATERIALIZATION_CONTRACT_v0_1.md

Entonces se solicita tu aprobación explícita. Solo después se materializan los labels.











###################################



un conjunto controlado de casos RTH para convertir tu definición cualitativa de Wake-up en reglas medibles.

PANEL
=
casos ticker-sesión dentro de RTH
con evidencia raw alrededor de una posible transición

Incluye deliberadamente:

POSITIVOS   → estaba dormida y realmente despertó
NEGATIVOS   → print aislado o actividad normal
AMBIGUOS    → la evidencia no permite decidir
ARTEFACTOS  → duplicados, errores o problemas de fuente

“Ciego” significa que los revisores no ven Binding A/B, sus scores, rebreak, retornos ni PnL. “Estratificado” significa que se incluyen casos de
distintos horarios, intensidades y morfologías, no solo ejemplos evidentes.

WUL-D01…D08 son las ocho decisiones numéricas pendientes:

- D01: cuánto tiempo observar para confirmar el despertar.
- D02: cuánto historial previo demuestra que estaba dormida.
- D03: cuán anómala debe ser la nueva actividad.
- D04: actividad económica mínima antirruido.
- D05: mínimo de trades/clusters independientes.
- D06: calidad y cobertura mínima de los datos.
- D07: cuándo termina un episodio y puede producirse otro Wake-up.
- D08: si decide una regla automática, humanos o una combinación.

Los gráficos que mostraste ayudan a identificar casos, pero el panel debe comprobarlos usando trades, timestamps, dollar volume y calidad de
fuente. Su finalidad es elegir y congelar esas ocho reglas antes de crear los labels con los que competirán A y B.

Está descrito en 00_CTO/04_MARKET_STATES_CREATION/04_EVENTS/WAKE_UP/03_LABELS/WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md:182.

Referencia de navegación utilizada: C:/Users/AlexJ/.codex/skills/graphify/SKILL.md.

─ Worked for 1m 07s ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› pero como se hace eso? hay que usar los datos y encontrar casos?


• Sí. Hay que utilizar los datos históricos y construir una muestra de casos, pero de forma controlada y sin usar Binding A ni B para encontrarlos.

El proceso sería:

1. Usar únicamente el periodo development y el universo diario elegible RTH.
2. Recorrer los trades raw buscando candidatos muy amplios:

actividad baja observada después de las 09:30
→
incremento claro de trades, clusters y dollar volume

El buscador debe priorizar recall: recoger muchos posibles despertares aunque incluya falsos casos.

3. Añadir controles que el buscador no elegiría espontáneamente:

periodos que permanecen dormidos
un único print grande
bursts que no reúnen corroboración mínima
actividad elevada pero normal para ese ticker
duplicados y anomalías de datos

4. Para cada caso crear una ficha basada en evidencia raw:

trades y timestamp clusters
share/dollar volume
actividad anterior
actividad posterior
calidad y cobertura de la fuente

Sin mostrar:

variables o scores de A/B
rebreak
retornos posteriores
PnL

5. Dos revisores clasifican independientemente cada caso como positivo, negativo, ambiguo, unavailable o artefacto, y sitúan el intervalo probable
    de inicio.

6. Comparando esas adjudicaciones con distintas configuraciones se resuelven WUL-D01…D08: duración previa de dormancia, horizonte de confirmación,
    anomalía mínima, suelo económico, clusters mínimos, etc.

7. Una vez congeladas esas reglas, se ejecuta el oracle sobre todo el denominator de development y se generan los labels oficiales para comparar A
    contra B.

Los gráficos que ya tienes sirven como ejemplos iniciales, pero están seleccionados por un scanner y contienen información de precio/rebreak. No
pueden constituir por sí solos el panel neutral.















