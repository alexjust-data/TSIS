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