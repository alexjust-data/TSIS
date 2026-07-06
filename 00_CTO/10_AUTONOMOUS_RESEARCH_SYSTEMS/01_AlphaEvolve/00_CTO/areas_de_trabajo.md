# Nota De Autoridad v3

Fecha: 2026-07-05
Estado: nota_exploratoria_subordinada

Este documento contiene ideas previas sobre OpenEvolve/AlphaEvolve y areas de trabajo. Las rutas tipo `04_EVOLUTION_LAB/` o experimentos directos deben leerse ahora como historicas o conceptuales.

La estructura operativa vigente para experimentos es:

```text
C:/TSIS_Data/00_TSIS_Lab
```

AlphaEvolve no crea un laboratorio paralelo. Debe producir `candidate research experiments` compatibles con `00_TSIS_Lab`.

---
SÃ­. Ahora sÃ­ he revisado la estructura real del repo.

La raÃ­z de OpenEvolve estÃ¡ organizada asÃ­:

```text
openevolve/
â”œâ”€â”€ configs/
â”œâ”€â”€ examples/
â”œâ”€â”€ openevolve/        # cÃ³digo fuente del framework
â”œâ”€â”€ scripts/
â”œâ”€â”€ tests/
â”œâ”€â”€ openevolve-run.py
â”œâ”€â”€ pyproject.toml
â”œâ”€â”€ setup.py
â”œâ”€â”€ Dockerfile
â””â”€â”€ README.md
```

El uso bÃ¡sico no exige copiar esa estructura dentro de TSIS: puedes instalarlo con `pip install openevolve`, o clonarlo en modo desarrollo con `git clone ...` y `pip install -e ".[dev]"`. Su ejecuciÃ³n tÃ­pica necesita tres piezas: `initial_program.py`, `evaluator.py` y `config.yaml`. ([GitHub][1])

Para TSIS, por tanto, **no tienes que adaptar tu proyecto a la estructura interna de OpenEvolve**. Tienes que crear experimentos TSIS que le den esas tres piezas:

```text
04_EVOLUTION_LAB/
â”œâ”€â”€ experiments/
â”‚   â””â”€â”€ 001_pm_squeeze_detector/
â”‚       â”œâ”€â”€ initial_program.py
â”‚       â”œâ”€â”€ evaluator.py
â”‚       â”œâ”€â”€ config.yaml
â”‚       â””â”€â”€ output/
```

OpenEvolve modifica el cÃ³digo candidato, lo evalÃºa con tu `evaluator.py`, guarda poblaciones/resultados y usa mecanismos como MAP-Elites, islands, LLM ensemble y artifact feedback para ir mejorando candidatos. ([GitHub][2])

Mi lectura: **sÃ­ parece implementable para TSIS**, pero no todavÃ­a como â€œTSIS Evolve completoâ€. Primero Ãºsalo en un experimento pequeÃ±o:

```text
001_pm_squeeze_detector
```

Objetivo:

```text
Evolucionar una funciÃ³n que detecte eventos PM_Squeeze
sobre una event_table ya creada.
```

No empezarÃ­a con entradas/salidas/ticks. EmpezarÃ­a con detectores de eventos o filtros, porque son mÃ¡s fÃ¡ciles de evaluar y menos peligrosos contra sobreoptimizaciÃ³n.

[1]: https://github.com/algorithmicsuperintelligence/openevolve "GitHub - algorithmicsuperintelligence/openevolve: Open-source implementation of AlphaEvolve Â· GitHub"
[2]: https://github.com/algorithmicsuperintelligence/openevolve/blob/main/README.md "openevolve/README.md at main Â· algorithmicsuperintelligence/openevolve Â· GitHub"


# Pregunta

```sh
o sea, que podrÃ­amos aplicar alphaevelve a cada evento sobre toda la data? entiendo que antes hay que crear toda la estructura para el evolve , pero la pregunta es que una vez se ha codificado cada uno de los eventos que buscarmos (aunque estÃ¡ mÃ¡s o menos no muy bien codificado) el propio proceso evolve puede encontrar eventos inesperados o mejorados porcada uno de ellos?
```

Si. Y de hecho has llegado al punto donde AlphaEvolve/OpenEvolve empieza a ser realmente interesante para TSIS.

Pero hay dos niveles muy distintos:

---

# Nivel 1: Evolucionar un evento que tÃº ya definiste

Ejemplo.

TÃº defines:

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
Â¿Los eventos detectados
terminan produciendo grandes squeezes?
```

---

Entonces empieza a mutar:

```python
gap > 20
```

â†“

```python
gap > 35
```

---

o

```python
float < 20M
```

â†“

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
La definiciÃ³n original
capturaba demasiada basura.

La nueva definiciÃ³n
captura mejor los runners.
```

---

Esto sÃ­.

Y es probablemente la primera aplicaciÃ³n real de OpenEvolve en TSIS.

---

# Nivel 2: Descubrir variantes inesperadas

AquÃ­ es donde se pone interesante.

Imagina:

```text
PM_Squeeze_Event
```

---

TÃº crees que importa:

```text
Gap
Float
PM Volume
```

---

Pero OpenEvolve empieza a experimentar.

Y descubre:

```text
La variable mÃ¡s predictiva
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
NÃºmero de intentos al HOD
```

---

AquÃ­ ya no estÃ¡ optimizando solamente.

EstÃ¡ generando hipÃ³tesis.

---

# Nivel 3: Descubrir subfamilias

Esto es lo que mÃ¡s me interesa para TSIS.

Supongamos que hoy tienes:

```text
PM_Squeeze
```

como un Ãºnico evento.

---

OpenEvolve podrÃ­a descubrir:

```text
PM_Squeeze_A
```

---

CaracterÃ­sticas:

```text
Gap 30-60%

Float 2-5M

Pullback corto

Rebreak rÃ¡pido
```

---

Y ademÃ¡s:

```text
PM_Squeeze_B
```

---

CaracterÃ­sticas:

```text
Gap >100%

Float <1M

Pullback profundo

Spread ancho
```

---

Y descubre:

```text
B gana mucho mÃ¡s.
```

---

Eso ya es casi clustering guiado por resultados.

---

# Nivel 4: Descubrir eventos completamente nuevos

AquÃ­ es donde hay que tener cuidado.

Mucha gente piensa:

```text
AlphaEvolve encontrarÃ¡
el Santo Grial.
```

---

No necesariamente.

Porque OpenEvolve no observa el mercado como un humano.

Observa:

```text
Datos
+
CÃ³digo
+
MÃ©trica
```

---

Por tanto necesita un espacio de bÃºsqueda.

---

Si solo le das:

```python
PM_Squeeze
```

mutarÃ¡ PM_Squeeze.

---

No inventarÃ¡ mÃ¡gicamente:

```text
SSR Liquidity Compression Event
```

si jamÃ¡s le diste variables relacionadas.

---

Por eso yo veo:

```text
Pattern Mining
â†“
OpenEvolve
```

---

y no:

```text
OpenEvolve
â†“
Pattern Mining
```

---

# Lo que realmente podrÃ­a pasar en TSIS

Y esto sÃ­ creo que es muy potente.

Imagina:

```text
2005-2026

150.000 eventos
```

---

OpenEvolve prueba miles de variantes.

---

DespuÃ©s de semanas descubre:

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

TÃº nunca programaste eso.

---

Simplemente definiste:

```text
score =
capturar runners grandes
```

---

Y el sistema evolucionÃ³ hacia esa definiciÃ³n.

---

# Lo mÃ¡s importante

Tu intuiciÃ³n inicial era:

```text
AlphaEvolve analizarÃ¡
20 aÃ±os de datos
y encontrarÃ¡ cosas.
```

---

La versiÃ³n correcta serÃ­a:

```text
AlphaEvolve analizarÃ¡
20 aÃ±os de datos

dentro de un espacio
de bÃºsqueda bien definido

y encontrarÃ¡ variantes
que un humano
probablemente no habrÃ­a probado.
```

Eso sÃ­ lo veo completamente realista para TSIS.

De hecho, si consigues construir:

```text
event_table
outcome_table
strategy_evaluator
```

yo dirÃ­a que una de las aplicaciones mÃ¡s valiosas de OpenEvolve no serÃ¡ optimizar entradas o salidas, sino **descubrir mejores definiciones de eventos y mejores filtros contextuales** para los fenÃ³menos que ya conoces (PM Squeeze, Gap & Go, Red to Green, First Green Day, etc.). AhÃ­ es donde tienes una combinaciÃ³n muy rara: 20 aÃ±os de datos de microcaps + conocimiento discrecional profundo + un motor evolutivo. Esa combinaciÃ³n sÃ­ tiene potencial para producir hallazgos interesantes.

