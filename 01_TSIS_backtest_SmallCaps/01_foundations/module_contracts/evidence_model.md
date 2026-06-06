# Evidence Model - Modulo 01

## 1. Rol del documento

Este documento define el modelo formal de evidencia del modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su objetivo es fijar que tipos de evidencia sustentan contratos, validaciones, promocion y decisiones de consumo.

## 2. Principio rector

La evidencia institucional no es opinion ni memoria conversacional.

Es soporte trazable para una afirmacion operativa.

Por tanto, toda promocion o decision relevante debe apoyarse en evidencia identificable y referenciable.

## 3. Que es evidencia en este modulo

En el contexto del modulo 01, evidencia es cualquier artefacto o resultado que permita sostener una afirmacion sobre:

- calidad;
- coverage;
- semantica;
- lineage;
- validacion;
- o aptitud para consumo.

## 4. Tipos de evidencia

### evidencia forense

Incluye:

- auditorias;
- notebooks de diagnostico;
- reconciliaciones;
- bucketizaciones;
- closeouts;
- analisis de excepciones.

Sirve para:

- descubrir problemas;
- justificar clasificaciones;
- y construir interpretacion operativa.

### evidencia de certificacion

Incluye:

- decisiones de calidad consolidadas;
- politicas `good/review/bad`;
- allowed consumers;
- metricas globales;
- y veredictos operativos por bloque.

Sirve para:

- traducir hallazgos forenses a politica utilizable.

### evidencia de validacion

Incluye:

- checks estructurales;
- validators;
- pruebas de consistencia;
- verificacion de schemas;
- y tests de compatibilidad contractual.

Sirve para:

- demostrar que un contrato o activo cumple requisitos definidos.

### evidencia de lineage

Incluye:

- referencias a fuentes upstream;
- grafos de transformacion;
- manifests;
- metadata de derivacion;
- y dependencias explicitadas.

Sirve para:

- sostener reproducibilidad y trazabilidad.

### evidencia de uso restringido

Incluye:

- justificaciones para `recoverable`;
- uso `ml_flagged`;
- analisis de sensibilidad;
- y razonamientos de cuarentena parcial.

Sirve para:

- habilitar consumo condicionado sin degradar la semantica principal.

## 5. Niveles de fuerza de evidencia

La evidencia no tiene toda la misma fuerza.

Como regla general:

### nivel 1

Observacion preliminar o hallazgo exploratorio.

### nivel 2

Analisis repetible con soporte suficiente para interpretacion provisional.

### nivel 3

Evidencia consolidada y suficiente para validacion o certificacion local.

### nivel 4

Evidencia suficiente para sostener contrato institucional y consumo gobernado.

## 6. Requisitos minimos para usar evidencia

Para que una evidencia soporte una decision institucional, debe ser posible responder:

- donde esta;
- que afirma;
- sobre que universo o ambito habla;
- con que metodo se genero;
- y que limitaciones tiene.

Si no puede responderse eso, la evidencia es demasiado debil para contrato serio.

## 7. Relacion entre evidencia y promocion

La promocion correcta sigue esta relacion:

- evidencia forense descubre y delimita;
- certificacion interpreta;
- validacion verifica;
- contrato institucional fija el uso permitido.

No debe invertirse ese orden.

## 8. Relacion con zonas preservadas

Las rutas congeladas del modulo contienen una parte esencial de la evidencia institucional:

- `01_research/01_auditoria_RAW_DATA/`
- `data/`
- `run/`
- `runs/`

Por eso se preservan.

No son ruido historico.

Son soporte de trazabilidad.

## 9. Regla de encapsulacion

Cuando una evidencia ya haya producido una conclusion estable:

- no hace falta copiar toda la evidencia dentro del contrato nuevo;
- si hace falta enlazarla, resumirla correctamente y mantener su referencia trazable.

La institucionalizacion correcta encapsula la evidencia.

No la borra y no la sustituye por memoria humana.

## 10. Regla final

Si una decision contractual importante no puede mostrar evidencia trazable, entonces la decision todavia no esta institucionalmente cerrada.
