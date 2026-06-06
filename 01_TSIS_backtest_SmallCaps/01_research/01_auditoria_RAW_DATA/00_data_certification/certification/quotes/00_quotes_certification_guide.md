# Quotes Certification Guide

## Regla de esta carpeta

Esta carpeta no reaudita `quotes`.
Tampoco redefine criterios ya cerrados en `auditoria`.

Su funcion es solo esta:

- tomar la auditoria ya cerrada
- identificar que artefactos son canonicos
- y preparar el ensamblado final de certificacion

## Fuentes maestras

Para `quotes`, la verdad documental ya vive aqui:

- `auditoria\00_que_proyecto_estamos_construyendo.md`
- `auditoria\00_auditoria_general.md`
- `auditoria\01_auditoria_1B_general.md`
- `auditoria\05_crosswalk_multidataset.md`
- `auditoria\quotes\v2\04_quotes_full_C_D_methodology.md`
- `auditoria\quotes\v2\04_quotes_full_C_D_closeout.md`

## Que ya esta hecho

En `auditoria\quotes\v2` ya estan resueltos:

- el dataset base `quotes_current_cd_merged\quotes_current.parquet`
- el filtro al universo `<1B>`
- el merge `C + D`
- la taxonomia local
- la lectura economica del crossed
- el corte `ask = 0` vs `ask > 0`
- la politica local `good / review / bad`
- la implicacion general para `backtesting` y `ML/IA`

## Que no debe rehacerse aqui

En `certification\quotes` no debemos:

- rehacer la auditoria local
- inventar una taxonomia nueva
- cambiar la politica `good / review / bad`
- construir ahora una malla sintetica diaria completa sin necesidad

## Que si queda por hacer

Solo quedan piezas de ensamblado:

- fijar que artefactos de `auditoria` se reutilizan tal cual
- decidir que falta de verdad para la certificacion final
- y enlazar `quotes` con el cierre global del proyecto

## Nota operativa

Las conclusiones materiales que queden aqui deberan apoyarse despues con imagenes y graficos exportados desde artefactos reproducibles, pero eso se hara al final, no ahora.
