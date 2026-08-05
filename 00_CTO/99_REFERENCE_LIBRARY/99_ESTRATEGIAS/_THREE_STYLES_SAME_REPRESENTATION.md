## Probabilidades a distintos horizontes

**¿Una arquitectura común para `HFT`, `scalping` y `frontside completo`?**

No construiría tres representaciones diferentes del mercado.  
Construiría un mismo sistema que produzca probabilidades a distintos horizontes:

$$
P(+U\text{ antes de }-D\mid S_{\leq t})
$$

$$
P(\text{nuevo HOD durante }H\mid S_{\leq t})
$$

$$
P(\text{terminación durante }H\mid S_{\leq t})
$$

$$
P(\text{backside confirmado durante }H\mid S_{\leq t})
$$

Para:

```text
H = 1 s, 3 s, 5 s, 15 s, 30 s, 60 s, 5 min
```

Entonces diferentes políticas consumen la misma superficie.

**Política microestructural de horizonte muy corto**

```text
H = 250 ms–5 s
```

Busca:

* Bursts de order flow.
* Queue imbalance.
* Cambio del bid/ask.
* Impacto inmediato.
* Micro-reversiones.

No la llamaría HFT estrictamente mientras no existan infraestructura, latencia y ejecución HFT. Sería:

```text
short_horizon_microstructure_policy
```

**Política scalping**

```text
H = 5–60 s
```

Busca:

* Primer impulso.
* Pausa breve.
* Renovación del flujo.
* Ruptura y aceptación.
* Salida rápida.

**Política estructural frontside**

```text
H = 1–15 min o episodio completo
```

Busca:

* Wake-up.
* Supervivencia del frontside.
* Pullbacks.
* Reaceleraciones.
* Terminación.

No son necesariamente tres estrategias incompatibles.   
Son **políticas diferentes sobre la misma representación**, pero deben tener:

* Strategy ID separado.
* P&L separado.
* Costes separados.
* Hipótesis separada.
* Validación separada.

Más adelante un router puede decidir cuál activar.