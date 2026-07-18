# TDI Event Schema v0.1. 

**Objetivo:** definir la estructura única de todos los eventos generados.   

**Principios:** event first, inmutabilidad, todo cambio es un nuevo evento.  

**Tipos de evento:** inicio de sesión, premarket, idea, entrada, gestión, salida, observación, cierre. 

**Campos comunes:** id, timestamp, ticker, estrategia, confianza, emoción, notas. Eventos específicos amplían estos campos.   

**Fuente de verdad:** todos los informes derivan exclusivamente de estos eventos.  