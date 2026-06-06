# Inspection Dossier Model - Modulo 01

## 1. Rol del documento

Este documento define el modelo canonico de inspeccion institucional para el modulo:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps`

Su funcion es establecer como debe presentarse la evidencia de un dataset o bloque auditado para que:

- humanos;
- agentes;
- revisores tecnicos;
- e inspectores metodologicos

puedan entender el resultado sin depender de memoria conversacional ni de notebooks abiertos en directo.

## 2. Principio rector

La evidencia institucional no debe quedar encerrada solo en notebooks historicos.

Tampoco debe reducirse a un markdown narrativo sin soporte reproducible.

La forma correcta es:

`evidencia historica preservada -> artefactos reproducibles de inspeccion -> inspection readout -> contrato institucional`

Regla transversal complementaria:

- toda politica operativa importante debe tener, ademas de su capa formal, una capa explicativa;
- esa regla vive en `01_foundations/module_contracts/policy_explanation_standard.md`.
- toda nueva capa o dataset derivado debe superar ademas una validacion transversal explicita;
- esa regla vive en `01_foundations/module_contracts/layer_validation_standard_v0_1.md`.

## 3. Relacion entre notebooks, scripts y markdown

### Notebooks

Sirven para:

- exploracion;
- diagnostico;
- apertura de casos;
- generacion inicial de tablas e imagenes;
- inspeccion interactiva;
- y prueba de hipotesis o rehabilitaciones.

### Scripts o builders

Sirven para:

- reproducir evidence packs;
- exportar tablas;
- generar imagenes estables;
- materializar readouts repetibles;
- y reducir dependencia de ejecucion manual.

### Markdown institucional

Sirve para:

- fijar la interpretacion;
- presentar el resultado a un inspector;
- enlazar evidencia persistida;
- y cerrar la decision operacional.

Un markdown no sustituye la ejecucion.

La encapsula y la explica.

Cuando el dossier vaya dirigido a inspeccion humana final, el markdown no debe limitarse a enlazar assets.

Debe, siempre que sea viable, incrustar imagenes clave directamente en el propio documento para que el lector pueda:

- ver el caso;
- entender el fallo;
- y revisar la justificacion sin abandonar la lectura principal.

Cuando exista contraste con una plataforma externa de precios, el dossier debe declarar tambien:

- si la vista interna usada es `raw` o `adjusted_proxy`
- si la serie externa es `adjusted` o no identificada con certeza
- y si la discrepancia queda explicada por ajustes, solo parcialmente explicada o abierta

La politica transversal que gobierna esto vive en:

- `01_foundations/module_contracts/external_price_comparison_caveats.md`
- `01_foundations/module_contracts/price_semantics_and_adjustment_policy.md`

## 4. Estructura general esperada

Cada dataset o bloque institucional deberia poder tener, cuando aplique:

- `inspection_readout`
- `good_justification`
- `flagged_case_evidence_packs`
- `bad_case_evidence_packs`
- `coverage_case_evidence_packs`
- `evidence_assets`
- `build_inspection_pack` notebook o script

## 5. inspection_readout

El `inspection_readout` es el documento principal para lectura humana.

Debe responder, como minimo:

- cual es el veredicto del bloque;
- que estados existen;
- por que una parte es `good`;
- por que otra queda `flagged`, `review` o `recoverable`;
- por que ciertos casos quedan `bad`;
- que evidencia visual o tabular soporta esas decisiones;
- y que partes pueden reabrirse o rehabilitarse.

No debe copiar toda la auditoria historica.

Debe resumirla y enlazarla correctamente.

## 6. good justification

No todo `good` necesita evidencia por file.

Pero si necesita justificacion institucional.

La justificacion de `good` debe explicar:

- que bucket o familias entran en `good`;
- por que el residuo restante no invalida su uso;
- que estadistica agregada lo sostiene;
- y que ejemplos representativos apoyan la decision.

## 7. flagged case evidence packs

Aplican a casos:

- `recoverable_with_flag`
- `review`
- `review_not_rehabilitated`
- o equivalentes

Su objetivo es explicar:

- por que no son `good`;
- por que no son `bad`;
- que condicion o flag exigen;
- y para que consumidores siguen siendo aceptables.

## 8. bad case evidence packs

Aplican a casos `bad`.

Deben seguir el protocolo de:

- `01_foundations/module_contracts/bad_evidence_and_rehabilitation.md`

Su objetivo es:

- acreditar el caso;
- mostrarlo;
- explicarlo;
- y evaluar rehabilitacion.

## 9. coverage case evidence packs

Aplican cuando el problema no es principalmente calidad del dato, sino:

- cobertura;
- continuidad;
- frontera temporal;
- gap interpretable;
- o desalineacion frente al universo esperado.

Estos packs son especialmente importantes para:

- `daily`
- `1m`
- `quotes`
- `trades`

cuando la lectura correcta no sea binaria entre "presente" y "roto".

## 10. evidence assets

Cada dossier debe apoyarse en artefactos persistidos y revisables.

Ejemplos:

- imagenes;
- tablas csv/parquet;
- capturas de filas problematicas;
- resúmenes por bucket;
- exports por ticker o file;
- y vistas comparativas cross-dataset.

Los assets deben ser:

- trazables;
- reusables;
- y enlazables desde el markdown institucional.

Para documentacion de presentacion y justificacion final, los assets visuales mas importantes deben aparecer:

- incrustados inline en el `inspection_readout`;
- o incrustados dentro del `case_evidence_pack` correspondiente.

## 10.1 Regla de "preguntas que responde"

Todo ejemplo, grafico, tabla, bloque visual o capa de evidencia debe declarar explicitamente:

- a que preguntas responde;
- y, cuando sea importante, que preguntas no responde.

No basta con describir visualmente lo que aparece en pantalla.

La forma institucional correcta es:

### `Que muestra`

Describe el contenido visual o tabular sin interpretacion excesiva.

### `Responde`

Enumera las preguntas concretas que esa pieza de evidencia permite contestar.

Ejemplos validos:

- cuanta masa hay;
- como se reparte;
- que buckets dominan;
- que firma global tiene el problema;
- como se ve visualmente una familia ya interpretada;
- que prueba un caso representativo;
- que decision cambia;
- que vio exactamente el notebook historico al recalcular raw files;
- como se distribuyen los casos reales de una muestra estratificada;
- si una familia se sostiene mas alla de dos o tres ejemplos bonitos.

### `No responde`

Aclara los limites de esa pieza cuando exista riesgo de sobrelectura.

Ejemplos validos:

- no ensena files individuales del universo;
- no expresa estados finales de certificacion;
- no sustituye el conteo poblacional;
- no prueba por si sola que el tape este roto;
- no absuelve un bucket entero.

### `Consecuencia`

Explica que error metodologico evita y que decision operacional o institucional cambia.

Regla:

- ninguna imagen debe quedar como decoracion muda;
- ninguna tabla debe presentarse como si se explicara sola;
- y ningun bucket debe apoyarse solo en nombres tecnicos o atributos sin traducirlos a preguntas respondidas.

## 10.2 Regla de lectura visual real

La explicacion de una imagen no puede salir solo de:

- el nombre del bucket;
- una plantilla generica;
- o una lista de metricas del caso.

Debe salir de la lectura visual real de la propia imagen.

Eso obliga a responder, cuando aplique:

- donde se ve exactamente el problema en el panel;
- si el tape realmente aparece o queda visualmente oculto;
- si el fallo principal vive en precio, escala, rango, tiempo, volumen o integridad estructural;
- y si el panel actual demuestra bien la causa del rechazo o se queda corto.

Reglas obligatorias:

- si el motivo real del caso es visible en la imagen, el texto debe nombrar la zona visual concreta donde se ve;
- si el motivo real no se ve bien, el texto debe decirlo explicitamente;
- si el panel no demuestra la causalidad principal, el dossier debe pedir una visualizacion complementaria en vez de fingir que la prueba ya existe;
- queda prohibido presentar como "evidencia visual suficiente" una imagen que no ensena el fenomeno que supuestamente justifica el bucket.

Ejemplo de mala practica:

- decir que un caso es `bad_data` por integridad del tape cuando la imagen solo ensena una trayectoria de precio aparentemente normal y no hay visualizacion de `size <= 0`, duplicados o filas invalidas.

Ejemplo de buena practica:

- distinguir que un caso de `bad_data` por colapso de escala si queda probado por el panel de precio;
- pero que un caso de `bad_data` por integridad estructural requiere un panel adicional de sizes, duplicados o filas invalidas.

## 11. build inspection pack

Cada dossier relevante deberia indicar como se generan los assets que usa.

Puede ser mediante:

- notebook;
- script;
- o pipeline reproducible equivalente.

Mientras el formato este estabilizandose, un notebook puede ser aceptable.

Cuando la estructura ya sea estable, debe priorizarse un script o builder institucional.

## 12. Regla de higiene de artefactos

Toda carpeta, asset o file derivado que haya sido usado de forma transitoria y ya no forme parte del flujo activo debe tratarse como ruido operacional.

Regla:

- si ya no esta en uso, debe eliminarse;
- si conserva valor historico o metodologico, debe archivarse;
- y ese archivado debe quedar explicitamente anotado en su lugar, para que humanos y agentes no lo confundan con outputs activos.

No deben mantenerse en paralelo:

- carpetas viejas y nuevas que cumplan el mismo rol;
- manifests obsoletos mezclados con manifests activos;
- ni exports historicos que ya no correspondan a la politica vigente.

La carpeta activa debe reflejar solo:

- outputs vigentes;
- manifests vigentes;
- y assets realmente consumidos por los dossiers institucionales actuales.

## 13. Relacion con contratos institucionales

El dossier de inspeccion no reemplaza:

- dataset contract;
- policy contract;
- schema contract;
- validators;
- o registry entry.

Su funcion es hacerlos inteligibles y auditables para inspeccion humana.

La relacion correcta es:

- el contrato dice que vale;
- el dossier muestra por que vale;
- y los assets permiten comprobarlo.

La unidad final de inspeccion no debe ser:

- una imagen aislada;
- ni un csv aislado;
- ni un notebook historico aislado.

Debe ser:

`caso = imagen incrustada + explicacion + decision + trazabilidad`

## 14. Estructura minima recomendada por dataset

Formato recomendado:

```text
01_foundations/inspection_dossiers/<dataset>/
├── <dataset>_inspection_readout_v0_1.md
├── good_justification/
├── flagged_case_evidence_packs/
├── bad_case_evidence_packs/
├── coverage_case_evidence_packs/
├── evidence_assets/
└── build_<dataset>_inspection_pack.md
```

El builder puede empezar como:

- `build_<dataset>_inspection_pack.ipynb`

y mas adelante migrar a:

- `build_<dataset>_inspection_pack.py`

## 15. Regla de preservacion

Los dossiers no deben borrar ni sustituir:

- auditoria historica;
- notebooks originales;
- imagenes previas utiles;
- ni artefactos ya existentes que sostengan la interpretacion.

La institucionalizacion correcta:

- preserva;
- reorganiza la lectura;
- y hace la evidencia inspeccionable.

## 16. Regla final

Un bloque institucionalmente maduro no solo tiene contratos.

Tambien puede:

- mostrar su evidencia;
- explicar sus decisiones;
- y permitir inspeccion humana de sus casos relevantes.
