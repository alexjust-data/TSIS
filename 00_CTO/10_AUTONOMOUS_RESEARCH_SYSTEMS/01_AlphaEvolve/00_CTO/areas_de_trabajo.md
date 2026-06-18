Sí. Ahora sí he revisado la estructura real del repo.

La raíz de OpenEvolve está organizada así:

```text
openevolve/
├── configs/
├── examples/
├── openevolve/        # código fuente del framework
├── scripts/
├── tests/
├── openevolve-run.py
├── pyproject.toml
├── setup.py
├── Dockerfile
└── README.md
```

El uso básico no exige copiar esa estructura dentro de TSIS: puedes instalarlo con `pip install openevolve`, o clonarlo en modo desarrollo con `git clone ...` y `pip install -e ".[dev]"`. Su ejecución típica necesita tres piezas: `initial_program.py`, `evaluator.py` y `config.yaml`. ([GitHub][1])

Para TSIS, por tanto, **no tienes que adaptar tu proyecto a la estructura interna de OpenEvolve**. Tienes que crear experimentos TSIS que le den esas tres piezas:

```text
04_EVOLUTION_LAB/
├── experiments/
│   └── 001_pm_squeeze_detector/
│       ├── initial_program.py
│       ├── evaluator.py
│       ├── config.yaml
│       └── output/
```

OpenEvolve modifica el código candidato, lo evalúa con tu `evaluator.py`, guarda poblaciones/resultados y usa mecanismos como MAP-Elites, islands, LLM ensemble y artifact feedback para ir mejorando candidatos. ([GitHub][2])

Mi lectura: **sí parece implementable para TSIS**, pero no todavía como “TSIS Evolve completo”. Primero úsalo en un experimento pequeño:

```text
001_pm_squeeze_detector
```

Objetivo:

```text
Evolucionar una función que detecte eventos PM_Squeeze
sobre una event_table ya creada.
```

No empezaría con entradas/salidas/ticks. Empezaría con detectores de eventos o filtros, porque son más fáciles de evaluar y menos peligrosos contra sobreoptimización.

[1]: https://github.com/algorithmicsuperintelligence/openevolve "GitHub - algorithmicsuperintelligence/openevolve: Open-source implementation of AlphaEvolve · GitHub"
[2]: https://github.com/algorithmicsuperintelligence/openevolve/blob/main/README.md "openevolve/README.md at main · algorithmicsuperintelligence/openevolve · GitHub"


# Pregunta

```sh
o sea, que podríamos aplicar alphaevelve a cada evento sobre toda la data? entiendo que antes hay que crear toda la estructura para el evolve , pero la pregunta es que una vez se ha codificado cada uno de los eventos que buscarmos (aunque está más o menos no muy bien codificado) el propio proceso evolve puede encontrar eventos inesperados o mejorados porcada uno de ellos?
```

Si. Y de hecho has llegado al punto donde AlphaEvolve/OpenEvolve empieza a ser realmente interesante para TSIS.

Pero hay dos niveles muy distintos:

---

# Nivel 1: Evolucionar un evento que tú ya definiste

Ejemplo.

Tú defines:

```python
def is_pm_squeeze(event):

    return (
        event.gap > 20
        and event.float < 20_000_000
        and event.pm_volume > 500_000
        and event.first_push > 15
    )
```

---

OpenEvolve recibe:

```text
32.000 eventos
2005-2026
```

y un evaluador:

```text
¿Los eventos detectados
terminan produciendo grandes squeezes?
```

---

Entonces empieza a mutar:

```python
gap > 20
```

↓

```python
gap > 35
```

---

o

```python
float < 20M
```

↓

```python
float < 8M
```

---

o incluso:

```python
gap > 35
and pm_volume > 2M
and float < 5M
```

---

Y descubre:

```text
La definición original
capturaba demasiada basura.

La nueva definición
captura mejor los runners.
```

---

Esto sí.

Y es probablemente la primera aplicación real de OpenEvolve en TSIS.

---

# Nivel 2: Descubrir variantes inesperadas

Aquí es donde se pone interesante.

Imagina:

```text
PM_Squeeze_Event
```

---

Tú crees que importa:

```text
Gap
Float
PM Volume
```

---

Pero OpenEvolve empieza a experimentar.

Y descubre:

```text
La variable más predictiva
no es Gap.
```

---

Sino:

```text
PM Volume / Float
```

---

o

```text
Velocidad del primer push
```

---

o

```text
Distancia a VWAP
```

---

o

```text
Número de intentos al HOD
```

---

Aquí ya no está optimizando solamente.

Está generando hipótesis.

---

# Nivel 3: Descubrir subfamilias

Esto es lo que más me interesa para TSIS.

Supongamos que hoy tienes:

```text
PM_Squeeze
```

como un único evento.

---

OpenEvolve podría descubrir:

```text
PM_Squeeze_A
```

---

Características:

```text
Gap 30-60%

Float 2-5M

Pullback corto

Rebreak rápido
```

---

Y además:

```text
PM_Squeeze_B
```

---

Características:

```text
Gap >100%

Float <1M

Pullback profundo

Spread ancho
```

---

Y descubre:

```text
B gana mucho más.
```

---

Eso ya es casi clustering guiado por resultados.

---

# Nivel 4: Descubrir eventos completamente nuevos

Aquí es donde hay que tener cuidado.

Mucha gente piensa:

```text
AlphaEvolve encontrará
el Santo Grial.
```

---

No necesariamente.

Porque OpenEvolve no observa el mercado como un humano.

Observa:

```text
Datos
+
Código
+
Métrica
```

---

Por tanto necesita un espacio de búsqueda.

---

Si solo le das:

```python
PM_Squeeze
```

mutará PM_Squeeze.

---

No inventará mágicamente:

```text
SSR Liquidity Compression Event
```

si jamás le diste variables relacionadas.

---

Por eso yo veo:

```text
Pattern Mining
↓
OpenEvolve
```

---

y no:

```text
OpenEvolve
↓
Pattern Mining
```

---

# Lo que realmente podría pasar en TSIS

Y esto sí creo que es muy potente.

Imagina:

```text
2005-2026

150.000 eventos
```

---

OpenEvolve prueba miles de variantes.

---

Después de semanas descubre:

```text
Los mejores runners
tienen esta firma:

Gap > 45%

Float < 3M

PM Volume > 4M

Pullback 4%-8%

Primer push > 25%
```

---

Tú nunca programaste eso.

---

Simplemente definiste:

```text
score =
capturar runners grandes
```

---

Y el sistema evolucionó hacia esa definición.

---

# Lo más importante

Tu intuición inicial era:

```text
AlphaEvolve analizará
20 años de datos
y encontrará cosas.
```

---

La versión correcta sería:

```text
AlphaEvolve analizará
20 años de datos

dentro de un espacio
de búsqueda bien definido

y encontrará variantes
que un humano
probablemente no habría probado.
```

Eso sí lo veo completamente realista para TSIS.

De hecho, si consigues construir:

```text
event_table
outcome_table
strategy_evaluator
```

yo diría que una de las aplicaciones más valiosas de OpenEvolve no será optimizar entradas o salidas, sino **descubrir mejores definiciones de eventos y mejores filtros contextuales** para los fenómenos que ya conoces (PM Squeeze, Gap & Go, Red to Green, First Green Day, etc.). Ahí es donde tienes una combinación muy rara: 20 años de datos de microcaps + conocimiento discrecional profundo + un motor evolutivo. Esa combinación sí tiene potencial para producir hallazgos interesantes.
