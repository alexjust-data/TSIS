# Layer Validation Standard v0.1

## 1. Rol del documento

Este documento define el estandar transversal minimo para declarar que una nueva capa, dataset derivado o vista de precio esta:

- semanticamente validada;
- tecnicamente bien implementada;
- auditada de forma visible;
- y suficientemente cerrada para ser usada por un consumidor real.

Aplica a capas como:

- `daily_adjusted`
- `ohlcv_1m_split_normalized`
- `intraday_regime_features`
- y cualquier otra capa futura con transformacion no trivial.

## 2. Principio rector

Una capa no queda validada porque:

- el script corra;
- el output exista;
- o unos pocos casos "parezcan correctos".

Una capa solo puede considerarse institucionalmente cerrada cuando supera varias capas independientes de comprobacion.

La validacion correcta debe demostrar, de forma acumulativa, que:

- la semantica definida por contrato es precisa;
- la implementacion sigue esa semantica;
- los controles negativos no la contradicen;
- la evidencia visual la hace inspeccionable;
- y un consumidor real deja de sufrir exactamente el error que la capa pretendia corregir.

## 3. Regla general

Ninguna nueva capa debe declararse "bien hecha", "promovida" o "lista para consumo" si no supera explicitamente, como minimo:

1. validacion semantica;
2. validacion de implementacion;
3. negative controls;
4. validacion visual o inspectiva;
5. validacion por consumidor real o por prueba de uso equivalente;
6. reproducibilidad;
7. trazabilidad documental.

## 4. Validacion semantica

La validacion semantica responde a:

- que significa exactamente la capa;
- que transforma;
- que no transforma;
- y bajo que definicion matematica o logica debe comportarse.

Debe existir, por contrato, una declaracion explicita de:

- formula o transformacion aplicada;
- unidad semantica del output;
- variables afectadas;
- variables que deben permanecer invariantes;
- casos frontera esperados;
- y observaciones que falsarian la semantica si aparecieran.

Ejemplos:

- `daily_adjusted` debe explicar por que corrige splits y dividendos;
- `ohlcv_1m_split_normalized` debe explicar por que corrige splits, pero no pretende ser una serie economica completa ajustada por dividendos;
- `intraday_regime_features` debe explicar cuando una feature usa `1m raw` y cuando usa `1m_split_normalized`.

## 5. Validacion de implementacion

La validacion de implementacion responde a:

- si el codigo ejecuta la semantica correcta sin bugs operativos obvios.

Debe comprobar, como minimo:

- columnas esperadas presentes;
- conteos escritos coherentes;
- tipos y layout correctos;
- reruns reproducibles;
- y comportamiento correcto en fechas frontera o ventanas con evento.

Una implementacion no queda validada solo porque genere archivos.

Debe demostrar que:

- no omite filas relevantes;
- no cambia ventanas que no debe cambiar;
- y no produce outputs distintos sin explicacion en ejecuciones equivalentes.

## 6. Negative controls

Toda capa nueva debe incluir controles negativos explicitos.

La pregunta no es solo:

- cambia donde debe?

Tambien es:

- permanece neutra donde no debe actuar?

Los controles negativos deben incluir, cuando apliquen:

- tickers sin evento;
- ventanas post-evento neutras;
- casos sin corporate actions;
- months o days control;
- y series donde la capa deberia permanecer identica al input.

Una capa que "mejora" tambien en controles donde no deberia tocar nada no queda validada.

## 7. Validacion visual o inspectiva

La capa debe poder auditarse sin depender de fe en el codigo.

Eso exige:

- readout visual;
- casos representativos;
- ejemplos frontera;
- y explicacion tecnica de lo que se ve.

La evidencia visual debe permitir contestar:

- si la transformacion actua donde debe;
- si desaparece la discontinuidad o error que queriamos corregir;
- si el control negativo queda neutro;
- y si algun edge case aparentemente raro es en realidad una consecuencia necesaria del contrato.

La politica de presentacion de esa evidencia sigue:

- `01_foundations/module_contracts/inspection_dossier_model.md`

## 8. Validacion por consumidor real

La validacion fuerte no termina en la capa aislada.

Debe existir, cuando sea viable, un consumidor real que use la capa y permita verificar que el problema objetivo queda efectivamente corregido.

Preguntas clave:

- que consumidor usa esta capa?
- que error sufria antes?
- que cambia al usar esta capa?
- y por que ese cambio es exactamente el que buscabamos?

Ejemplos:

- `daily_adjusted` queda mucho mas validado cuando alimenta `daily_return_labels`;
- `ohlcv_1m_split_normalized` quedara mas validado aun cuando un consumidor cross-session deje de ver falsos gaps por split.

## 9. Reproducibilidad

Una capa no esta institucionalmente cerrada si solo el autor original sabe rehacerla.

Debe existir:

- script reproducible;
- manifest o plan de muestreo cuando aplique;
- layout de salida;
- documentacion de ejecucion;
- y posibilidad de rerun por otro agente sin depender de memoria oral.

La reproducibilidad correcta exige que:

- el mismo input produzca el mismo output salvo cambios declarados;
- los resultados puedan recomputarse;
- y la logica no quede escondida en notebooks manuales o pasos no trazados.

## 10. Trazabilidad documental

Toda capa nueva debe quedar enlazada, al menos, en:

- contrato de dataset o vista;
- schema o layout si aplica;
- plan incremental u operacional;
- manifest piloto si existe;
- resultados del piloto;
- readout visual si existe;
- consumidor real o contrato de consumidor;
- y `CHANGELOG.md`.

La evidencia no debe quedar repartida sin mapa.

Debe poder seguirse una cadena clara:

`contrato -> implementacion -> piloto -> evidencia -> consumidor -> conclusion`

## 11. Invariantes

Cuando una capa tenga reglas invariantes, estas deben escribirse explicitamente.

Ejemplos:

- `future_split_factor > 0`
- si no existe split futuro relevante, entonces `future_split_factor = 1`
- si un ticker control no tiene eventos en ventana, la capa debe permanecer neutra
- una feature cross-session no debe usar `1m raw` si el riesgo de split contamination es material

Los invariantes no son solo notas pedagogicas.

Son criterios falsables de auditoria.

## 12. Niveles de madurez

Para evitar lenguaje ambiguo, una capa deberia poder declararse en uno de estos niveles:

### Nivel 1 - Definida

- existe contrato o politica;
- aun no hay piloto real.

### Nivel 2 - Implementada

- existe script materializador o builder;
- aun no hay evidencia semantica suficiente.

### Nivel 3 - Pilotada

- existe piloto semantico;
- hay controles;
- y la capa parece correcta en casos elegidos.

### Nivel 4 - Auditada

- existe readout visual o inspectivo;
- los edge cases estan explicados;
- y la capa ya no depende solo de tablas o narrativa abstracta.

### Nivel 5 - Consumida

- existe al menos un consumidor real conectado;
- y el error objetivo queda mitigado de forma demostrable.

### Nivel 6 - Promovida

- la capa ya no es solo piloto;
- tiene expansion operacional estable;
- y su uso institucional ya no depende de aprobacion ad hoc caso por caso.

## 13. Regla de prudencia

Hasta alcanzar al menos:

- `Nivel 4 - Auditada`

ninguna capa debe presentarse como si estuviera plenamente cerrada.

Y hasta alcanzar al menos:

- `Nivel 5 - Consumida`

ninguna capa debe presentarse como si ya hubiera demostrado valor real para downstream.

## 14. Veredicto final

La pregunta correcta no es:

- parece bien?

La pregunta correcta es:

- la semantica esta bien definida?
- la implementacion la respeta?
- los controles no la contradicen?
- la evidencia visual la hace inspeccionable?
- y un consumidor real confirma que corrige el problema objetivo?

Solo cuando la respuesta acumulada sea si, una capa puede considerarse:

- suficientemente validada;
- institucionalmente defendible;
- y lista para promocion operacional.
