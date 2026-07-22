# Trades Good Cases v0.1

## 1. Rol

`good` en `trades` existe, pero es extremadamente escaso. Por eso no debe sobrerrepresentarse.

Su valor no es estadistico. Su valor es semantico: demuestra como se ve un file cuando el flujo de trades:

- cabe dentro del rango diario;
- alinea con `1m`;
- no necesita narrativa correctiva de escala;
- y no presenta una cola outside material.

### Responde

- como se ve un file realmente limpio dentro de este ecosistema;
- que patron visual y metrico deberia aproximarse a `good`;
- por que `good` existe como referencia semantica aunque sea pequeno.

### No responde

- cuanta masa util total tiene `trades`;
- si todo lo no-`good` es inservible;
- ni si el bloque puede consumirse sin politicas de recuperacion.

## 2. Caso DMYS 2022-09-06

![DMYS good](../evidence_assets/historical_assets/13_good_dmys_2022_09_06.png)

### Que muestra la imagen

- los trades permanecen dentro del rango diario;
- no hay `outside_daily` material;
- el `trade_vwap` y `daily_vw` quedan muy proximos;
- la tabla resumen deja el file sin distancia ofensora real.

### Que pregunta responde

Responde a si `good` es una ficcion teorica o una firma observable. La imagen demuestra que es una firma real del tape limpio.

### Que conclusion debe sacar el lector

Este es el patron que justifica que `good` siga existiendo como estado separado y no como mera teoria. La imagen prueba que, aunque el bucket sea minimo, si hay files donde `trades` parece representar el dia de forma coherente.

### Que decision cambia

- este patron es apto para consumo relativamente limpio en ejecucion y referencias microestructurales;
- evita llamar `review` a casos donde el tape si parece sano.

### Que no debe concluir

- no debe concluir que esta cola representa la masa util total;
- no debe concluir que el bloque `trades` es sano en general;
- solo debe concluir que la referencia de limpieza existe y es observable.

### Que pipeline afecta

- ejecucion: apto como referencia limpia;
- ML microestructural: apto como ejemplo positivo;
- forensic: sirve como contraste de normalidad frente al resto del bloque.

## 3. Caso CLSN 2016-05-16

![CLSN good](../evidence_assets/historical_assets/14_good_clsn_2016_05_16.png)

### Lectura analitica

- la nube de prints sigue el entorno diario y el sobre `1m`;
- no aparece firma de escala extrema ni contaminacion outside relevante;
- la imagen ensena que `good` no significa perfeccion ideal, sino coherencia suficiente para uso limpio.

### Que pregunta responde

Responde a si la rareza de `good` invalida su valor. La respuesta es no: precisamente por ser raro sirve como patron de contraste frente a buckets recuperables o duros.

### Que error metodologico evita

Evita concluir que, como `good` es muy pequeno, todo `trades` esta condenado. La existencia de esta cola prueba que el tape puede ser semanticamente sano; lo que ocurre es que ese estado es raro en el bloque actual.

## 4. Que ensena la cola good

El hecho de que `good` sea tan pequeno no invalida el dataset. Lo que ensena es otra cosa:

- `trades` debe leerse como bloque de alta friccion y comparabilidad dificil, no como serie diaria simple;
- cuando aparece `good`, no hay que extrapolarlo a todo el universo;
- pero tampoco hay que negar su valor como referencia de como se ve un file sano en este ecosistema.

### Consecuencia

La consecuencia operativa es que `good` debe usarse como referencia positiva de QA y calibracion, no como estimador de masa util total. La masa util real del bloque depende de la rehabilitacion de `review`, no de la cola pristine.
