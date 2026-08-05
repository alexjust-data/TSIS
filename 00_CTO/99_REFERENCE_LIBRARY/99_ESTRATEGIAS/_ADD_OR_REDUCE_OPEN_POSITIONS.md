**Añadir y reducir acciones es totalmente plausible**

Pero no debería formularse como:

```text
si sube, añado
si baja, añado más
si me asusto, reduzco
```

Eso abre un número enorme de grados de libertad y puede convertirse en una forma algorítmica de improvisación.

La formulación profesional es:

> En cada instante, el sistema calcula una **posición objetivo** y negocia la diferencia respecto a la posición actual.

$$
\Delta q_t = q_t^* - q_t
$$

Donde:

$$
q_t^*
=
Q_{\max}
\cdot
g(
\alpha_t,
P_{\text{survival},t},
P_{\text{termination},t},
liquidity_t,
execution_cost_t,
risk_t
)
$$

Por ejemplo:

```text
0%   = flat
25%  = evidencia inicial
50%  = frontside healthy
75%  = continuación confirmada
100% = máxima evidencia y capacidad
```

Y a la inversa:

```text
100% → 75%  frontside stressed
75%  → 50%  termination warning
50%  → 25%  termination risk high
25%  → 0%   termination detected
```

Empezaría con niveles discretos:

```text
0 / 25 / 50 / 75 / 100%
```

No con una función continua ni con RL.

Esto reduce drásticamente los grados de libertad y permite entender qué aporta cada transición.

La literatura profesional sobre ejecución y control de inventario plantea precisamente el problema como un equilibrio entre señal predictiva, impacto, costes, riesgo de inventario, liquidez y probabilidad de fill. [Almgren & Chriss, Optimal Liquidation](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501)

---

**Cuándo añadir en long**

Añadir debería significar:

> La evidencia de continuación ha aumentado.

No:

> El precio ha bajado y ahora está más barato.

Una política candidata:

```text
Añadir sólo si:

p_new_hod ↑
p_termination ↓
activity renewal ↑
bid resilience aceptable
spread/capacidad aceptables
posición todavía bajo máximo permitido
```

Ejemplos:

```text
wake-up confirmado
→ 25%

primer impulso aceptado
→ 50%

pullback saludable
→ mantener

rebreak con renovación del flujo
→ 75%

nuevo HOD aceptado
→ 100%
```

No añadiría automáticamente en un pullback profundo. Primero debe demostrar que sigue siendo un pullback y no una terminación.

---

**Cuándo reducir en long**

```text
buy response decay
→ reducir

bid resilience decay
→ reducir

termination warning
→ reducir más

failed reclaim
→ salir

backside confirmed
→ prohibir long
```

Esto puede producir más valor que encontrar mejores entradas porque reduce el *giveback*.

---

**Añadir y quitar en short**

También es plausible, pero aún más delicado.

```text
termination detected
→ todavía flat

backside confirmed
→ 25% short

failed reclaim
→ 50%

lower high + renewed sell pressure
→ 75%

support loss with acceptance
→ 100%
```

Y reducir:

```text
sell exhaustion
→ reducir

bid absorption
→ reducir

successful reclaim
→ cubrir

frontside reactivation
→ flat obligatorio
```

No añadiría al short simplemente porque el precio ha rebotado. Eso equivale a promediar contra un posible nuevo squeeze.


## El principal límite: `capacidad` y `ejecución`

En microcaps, 

```
una señal perfecta puede
≠  
una operación perfecta
```
No se puede comprar/vender cualquier número de acciones solo porque la señal diga “entra/sale”.   
El tamaño de la variación de posición $(|\Delta q_t|)$ está limitado por el más restrictivo de varios límites prácticos.  

La posición objetivo debe estar limitada por:

$$
|\Delta q_t|
\leq
\min
\begin{cases}
c_1 \cdot \text{recent executed volume}\\
c_2 \cdot \text{visible depth}\\
c_3 \cdot \text{risk budget}\\
c_4 \cdot \text{max impact budget}
\end{cases}
$$

Y debe considerar:

* Partial fills.
* Spread.
* Quote staleness.
* Halts.
* Slippage no lineal.
* Tamaño disponible.
* Coste de cruzar varias veces.
* Imposibilidad de salir simultáneamente con todos.

La SEC señala que las microcaps suelen tener menor liquidez y que operaciones relativamente pequeñas pueden producir variaciones porcentuales importantes; eso hace que el control de capacidad sea una parte central, no un detalle posterior. [SEC Microcap Investor Guide](https://www.sec.gov/about/reports-publications/investorpubsmicrocapstock)