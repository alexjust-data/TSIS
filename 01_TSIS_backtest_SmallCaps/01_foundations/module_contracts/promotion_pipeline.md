# Promotion Pipeline - Modulo 01

## 1. Rol del documento

Este documento define el pipeline de promocion para activos del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es formalizar como algo pasa de evidencia o trabajo exploratorio a activo institucional consumible.

## 2. Principio rector

Nada debe convertirse en activo consumible por costumbre, cercania o repeticion de uso.

La promocion correcta exige:

- evidencia;
- interpretacion estable;
- contrato explicito;
- y capacidad de validacion.

## 3. Estados base del pipeline

El pipeline base del modulo es:

`exploratory -> provisional -> validated -> institutional -> deprecated -> archived`

No todos los objetos recorreran todos los estados del mismo modo, pero ningun activo debe saltar a `institutional` sin pasar por validacion suficiente.

## 4. Exploratory

Estado para:

- notebooks;
- pruebas locales;
- outputs de analisis;
- hipotesis;
- builders tempranos;
- resultados no cerrados.

Requisitos minimos:

- contexto identificable;
- owner o autor responsable;
- alcance limitado;
- no presentarse como source of truth institucional.

Permitido:

- experimentar;
- iterar;
- descubrir problemas;
- producir evidencia inicial.

No permitido:

- declararlo canonico;
- usarlo como dependencia silenciosa de multiples capas.

## 5. Provisional

Estado para objetos que ya tienen utilidad repetible pero aun no cierran su semantica final.

Requisitos minimos:

- objetivo explicito;
- descripcion operativa;
- naming estable;
- evidencia enlazada;
- criterio de salida hacia validacion.

Permitido:

- uso controlado en research;
- consumo acotado por personas o pipelines experimentales.

No permitido:

- presentarlo como contrato final;
- ocultar limitaciones de cobertura o calidad.

## 6. Validated

Estado para objetos que ya tienen verificacion suficiente para uso gobernado, aunque aun no sean autoridad institucional total.

Requisitos minimos:

- schema suficientemente estable;
- policy o uso permitido definido;
- evidencia de validacion;
- lineage minimo;
- compatibilidad con contratos locales.

Permitido:

- uso sistematico controlado;
- integracion en builders o research programado;
- consumo por capas downstream acotadas.

No permitido:

- asumir que ya es autoridad global si falta cierre institucional.

## 7. Institutional

Estado para activos que ya forman parte del sistema operativo del modulo.

Requisitos minimos:

- contrato explicito;
- schema canonico si aplica;
- policy de consumo definida si aplica;
- naming estable;
- version logica;
- manifest o metadata de trazabilidad;
- lineage suficiente;
- validacion documentada;
- owner claro;
- ubicacion coherente con la arquitectura institucional.

Permitido:

- consumo regular por multiples componentes;
- referencia como source of truth local del modulo;
- uso como base para capas downstream.

No permitido:

- cambios silenciosos de semantica;
- breaking changes no declarados;
- redefiniciones impulsadas por necesidades locales ad hoc.

## 8. Deprecated

Estado para activos que ya no deben promoverse como opcion preferida, pero siguen existiendo por compatibilidad, trazabilidad o transicion.

Requisitos minimos:

- motivo de deprecacion;
- sustituto recomendado si existe;
- horizonte o criterio de salida;
- riesgo de uso residual documentado.

## 9. Archived

Estado para activos retirados del circuito operativo principal pero preservados por valor historico, cientifico o de auditoria.

No deben presentarse como activos vigentes.

Su preservacion puede seguir siendo critica para:

- lineage;
- reproducibilidad;
- revisiones futuras;
- comparacion historica.

## 10. Requisitos transversales de promocion

Para promocionar un activo hacia estados altos, el modulo debe poder responder, como minimo:

- que es;
- para que sirve;
- quien lo mantiene;
- de que evidencia nace;
- que version logica tiene;
- que policy de consumo lo gobierna;
- que schema lo describe;
- que lineage tiene;
- y como se valida.

Si no puede responderse eso, la promocion no esta cerrada.

## 11. Relacion con auditoria y certificacion

En este modulo, la promocion de datasets y contratos debe apoyarse en:

- auditoria como evidencia;
- certificacion como interpretacion operativa;
- y foundations como cierre institucional.

La evidencia historica no se borra al promocionar.

Se referencia y se encapsula.

## 12. Reglas de cuarentena

Si un activo presenta dudas materiales de semantica, coverage, quality o compatibility, debe permanecer en un estado inferior o pasar a cuarentena operacional.

No debe promocionarse por presion de agenda.

## 13. Regla final

La promocion institucional correcta no es:

- uso repetido;
- costumbre;
- ni confianza subjetiva.

Es:

`evidencia + contrato + validacion + trazabilidad`
