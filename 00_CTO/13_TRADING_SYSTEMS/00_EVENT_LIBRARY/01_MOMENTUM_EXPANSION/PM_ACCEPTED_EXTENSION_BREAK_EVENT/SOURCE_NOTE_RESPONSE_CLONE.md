Sí. Esta era la respuesta completa, reconstruida limpia:

**Evento Base**

Yo lo definiría como una familia distinta al simple `First_3Bar_Push`.

Aquí el evento no es solo el push, sino la secuencia:

```text
primera extensión -> aceptación/meseta -> ruptura violenta
```

**Versión 1: PM_Shelf_Breakout_Event**

Fenómeno: en premarket el ticker hace una primera extensión, no la devuelve entera, construye una base o meseta, y luego rompe esa zona con varias velas consecutivas.

Condiciones base:

- `session_segment = premarket`
- primera extensión previa desde low/precio inicial PM hasta primer high relevante: `>= 20%`
- duración mínima de meseta: `>= 20 min`
- el precio no pierde más de `35%-45%` de la primera extensión
- lows sostienen una zona relativamente estable
- rango comprimido respecto a la extensión inicial
- pendiente plana o ligeramente positiva
- ruptura con `3-4` velas 1m consecutivas
- highs crecientes
- closes fuertes
- nuevo high sobre la meseta
- push adicional `>= 20%`

Crítica: esta versión es fácil de detectar, pero puede ser demasiado rígida. Si exigimos “meseta” perfecta, perderemos casos reales donde la base es irregular.

**Versión 2: PM_Extension_Hold_And_Impulse_Event**

Fenómeno: el mercado demuestra primero interés real, después aceptación, y finalmente expansión agresiva.

Esta versión separa el evento en fases:

Fase A: `initial_extension`

- ocurre antes del push principal
- subida mínima: `>= 15%-25%`
- volumen visible
- marca un primer high

Fase B: `hold_acceptance`

- el precio se mantiene por encima de una zona de aceptación
- no hay colapso completo de la primera extensión
- duración mínima: `15-90 min`
- puede tener inclinación positiva ligera

Fase C: `impulse_break`

- ruptura de la parte alta de la base
- `3-4` velas consecutivas
- highs ascendentes
- close de cada vela fuerte respecto a su rango
- volumen de ruptura superior al volumen medio de la meseta

Crítica: esta es conceptualmente mejor, porque describe lo que ocurre. Pero tiene más parámetros: cuánto es aceptación, cuánto es meseta, cuánto volumen confirma. Riesgo: si la hacemos demasiado flexible, se convierte en “cualquier consolidación antes de subir”.

**Versión 3: PM_Accepted_Extension_Break_Event**

Esta sería mi candidata preferida.

Definición:

Evento de premarket donde un ticker hace una primera expansión, el mercado acepta precios elevados durante un periodo suficiente sin revertir la extensión, y posteriormente rompe la zona de aceptación con un impulso vertical de varias velas consecutivas.

Condiciones conceptuales:

1. `premarket_initial_extension`
   - primera subida relevante del día
   - no necesariamente el máximo definitivo
   - demuestra atención temprana

2. `accepted_price_shelf`
   - el precio sostiene una zona elevada
   - la base dura lo suficiente para distinguirla de un simple spike
   - el rango se comprime o deriva suavemente hacia arriba

3. `violent_shelf_break`
   - ruptura de la parte alta de la meseta
   - `3-4` velas 1m consecutivas
   - highs crecientes
   - closes cerca de máximos
   - volumen expansivo

4. `event_timestamp`
   - primera vela de la ruptura violenta, no la primera extensión

Crítica final: esta versión es la más limpia porque evita confundir el “evento completo” con el “trigger visual”. La primera extensión no es el evento final; es una condición previa. La meseta es la aceptación. El push violento es la materialización.

Yo lo nombraría provisionalmente:

```text
PM_Accepted_Extension_Break_Event
```

Y no lo definiría como estrategia. No dice comprar, vender, entrar, salir ni stop. Solo dice:

```text
Este ticker extendió, aceptó precio elevado y rompió violentamente esa aceptación en premarket.
```
