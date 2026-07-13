# Bad Evidence and Rehabilitation - Modulo 01

## 1. Rol del documento

Este documento define el protocolo institucional para:

- acreditar;
- inspeccionar;
- justificar;
- y eventualmente rehabilitar

casos clasificados como `bad` dentro del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es evitar que `bad` se convierta en una etiqueta opaca, automatica o insuficientemente defendida.

## 2. Principio rector

Un caso `bad` no debe quedar cerrado solo porque un validador lo haya marcado.

Para que una exclusion relevante sea institucionalmente seria, TSIS debe poder:

- identificar el objeto afectado con precision;
- mostrar por que fallo;
- explicar por que la interpretacion correcta no permite consumo principal;
- y evaluar si existe una recuperacion defendible sin contaminar backtest ni ML.

## 3. Que significa un caso bad

En este protocolo, un caso `bad` es un objeto, subconjunto o unidad de analisis que:

- no debe entrar en los flujos principales permitidos;
- o cuya degradacion conocida invalida su uso para consumidores definidos.

`bad` no describe por si solo la calidad global del proveedor.

Describe una decision operacional de exclusión para un caso concreto.

## 4. Motivos validos para clasificar bad

Un caso solo debe cerrarse como `bad` cuando exista al menos uno de estos motivos:

- invalidez estructural dura;
- incoherencia economica imposible o no defendible;
- corrupcion de parseo;
- imposibilidad de mapearlo a un schema utilizable;
- incompatibilidad material con el consumidor relevante;
- o riesgo no aceptable de contaminar backtest, ML o inferencia institucional.

## 5. Evidencia minima exigida

Todo caso `bad` relevante debe poder documentarse, como minimo, con:

- identidad exacta del objeto afectado;
- dataset y contrato afectados;
- motivo primario de exclusion;
- bucket causal o interpretativo;
- evidencia estructural o numerica relevante;
- explicacion logica del fallo;
- y estado de recuperabilidad.

Cuando aplique, tambien debe existir:

- referencia a auditoria o closeout previo;
- evidencia visual de apoyo;
- y decision final de consumo permitido o prohibido.

## 6. Inspeccion visual obligatoria cuando sea viable

Cuando el tipo de objeto lo permita, el inspector debe poder cotejar visualmente cada caso `bad`.

Eso significa que debe existir una forma clara de revisar:

- el file afectado;
- el ticker;
- la fecha o rango temporal;
- y la anomalia observada.

La evidencia visual puede adoptar distintas formas segun el caso:

- tabla de filas problematicas;
- comparativa antes/despues;
- grafico del comportamiento anomalo;
- captura o render de columnas clave;
- o vista resumida del artefacto afectado.

Cuando el caso vaya a presentarse para revision humana final, la evidencia visual principal no debe quedar solo como archivo suelto.

Debe incrustarse dentro del `case_evidence_pack` o del `inspection_readout` correspondiente para que el inspector vea el fallo directamente en el documento.

La inspeccion visual no es decorativa.

Su funcion es permitir:

- comprender la exclusion;
- contrastarla con la regla;
- y detectar si la clasificacion esta sobrerreaccionando o subestimando el problema.

## 7. Explicacion logica obligatoria

Ningun caso `bad` importante debe quedar en:

- "el validador lo marco"

La justificacion correcta debe responder:

- que patron se observo;
- por que ese patron no es ruido aceptable;
- por que no se interpreta como edge case benigno;
- y por que su inclusion danaria el consumidor relevante.

## 8. Evaluacion obligatoria de rehabilitacion

Antes de cerrar un `bad` como exclusion definitiva, debe evaluarse si existe una recuperacion defendible.

La evaluacion de rehabilitacion debe preguntar:

- el problema es real o solo aparente;
- el problema puede aislarse sin contaminar el resto;
- existe una reinterpretacion logica y trazable;
- puede introducirse un flag en lugar de una exclusion total;
- y la recuperacion mantiene integridad suficiente para backtest o ML.

## 9. Regla de no dano operacional

La recuperacion solo es valida si no introduce deterioro material en:

- backtest defendible;
- ML gobernado;
- policies de consumo;
- o trazabilidad institucional.

Si la recuperacion exige supuestos debiles, heuristicas frágiles o ocultacion del problema, debe rechazarse.

## 10. Estados de cierre recomendados

Los casos `bad` deberian cerrar en uno de estos estados:

- `bad_confirmed`
- `bad_recoverable_rejected`
- `bad_rehabilitated_with_flag`
- `bad_reclassified`

Interpretacion:

- `bad_confirmed`
  - el caso sigue siendo `bad` y la exclusion queda acreditada
- `bad_recoverable_rejected`
  - se evaluo rehabilitacion pero no fue defendible
- `bad_rehabilitated_with_flag`
  - no entra como `good`, pero se permite consumo restringido con condicion explicita
- `bad_reclassified`
  - la exclusion inicial no se sostiene y el caso cambia de categoria

## 11. Relacion con proveedores de alta calidad

Un proveedor serio puede seguir produciendo:

- tails anomalos;
- casos limite;
- transiciones mal parseadas;
- o subconjuntos incompatibles con el uso concreto que TSIS exige.

Por tanto:

- un caso `bad` no invalida la calidad global del proveedor;
- pero tampoco puede ignorarse solo porque el proveedor sea reconocido.

La autoridad final de consumo en TSIS depende de la evidencia local y del contrato institucional, no del prestigio abstracto del vendor.

## 11.1 Regla de no backtestear artefactos como si fueran mercado

La presencia de un valor en el archivo no implica por si sola autorizacion para consumo en backtest, ML o uso institucional equivalente.

TSIS debe distinguir entre:

- dato presente en la fuente;
- y hecho de mercado defendible.

Un valor solo debe entrar en `backtest_core` cuando pueda sostenerse razonablemente como representacion interpretable de mercado, y no como:

- artefacto de parseo;
- placeholder;
- materializacion vacia;
- codificacion especial no resuelta del proveedor;
- o fila estructuralmente incoherente.

Por tanto:

- TSIS no debe backtestear artefactos como si fueran mercado;
- una fila puede existir y seguir siendo no apta para consumo principal;
- y su exclusión puede ser correcta aunque el proveedor global sea de alta calidad.

Esta regla es especialmente importante cuando aparecen casos como:

- `o = h = l = c = 0`
- campos criticos en cero
- `high < low`
- o contradicciones internas como `vw > high` con `high = 0`

En esos casos, la carga de la prueba no es demostrar por que excluir.

Es demostrar por que seria defendible incluir.

## 12. Relacion con forensic_only

Cuando un caso `bad` no sea consumible, puede seguir siendo valioso para:

- auditoria;
- diagnostico;
- reconciliacion;
- o estudio de causa raiz.

En esos casos, puede quedar en:

- `forensic_only`

Eso no lo convierte en dataset utilizable.

Lo preserva como evidencia y objeto de inspeccion.

## 13. Regla de preservacion

La acreditacion de un `bad` no debe destruir la evidencia original.

La forma correcta es:

- preservar el artefacto;
- anadir evidencia explicativa;
- documentar la decision;
- y, si procede, enlazar una posible ruta de rehabilitacion.

## 14. Regla final

En TSIS, excluir algo como `bad` exige mas que desconfianza.

Exige:

`evidencia trazable + explicacion logica + inspeccion revisable + evaluacion de rehabilitacion`
