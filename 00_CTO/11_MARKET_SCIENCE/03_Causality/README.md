Si tu objetivo es:

```text
Aplicar causalidad a TSIS
sin cometer errores conceptuales
```

entonces NO debes estudiar solamente:

```text
Causality in Factor Investing
```

Porque ese paper es realmente la punta del iceberg.

Lo que López de Prado y Zoonekynd están haciendo es importar a finanzas una disciplina mucho más profunda:

```text
Causal Inference
```

La misma que usan:

* Medicina
* Epidemiología
* Economía
* Ciencias sociales
* IA moderna
* DeepMind
* Microsoft Research
* Schölkopf (MPI)
* Judea Pearl

([CFA Institute Research and Policy Center][1])

---

# Mi recomendación

Construiría una línea de estudio en 6 niveles.

```text
Nivel 0
Qué problema intenta resolver

Nivel 1
Fundamentos de causalidad

Nivel 2
Pearl

Nivel 3
Causal Discovery

Nivel 4
Causal ML

Nivel 5
Causal Finance

Nivel 6
TSIS
```

---

# NIVEL 0

# El problema

Empieza por leer varias veces:

### Causality and Factor Investing: A Primer

Es el manifiesto.

López de Prado introduce:

```text
Factor Mirage
Collider Bias
Confounder Bias
Causal Misspecification
```

y argumenta que muchos factores parecen funcionar estadísticamente pero están causalmente mal especificados. ([CFA Institute Research and Policy Center][2])

---

# NIVEL 1

# Aprender causalidad

Aquí NO empieces por Pearl.

Error típico.

---

## 1

### The Book of Why

The Book of Why

Objetivo:

```text
entender
```

NO demostrar.

---

## 2

### Causal Inference in Statistics: A Primer

Pearl

Éste es probablemente el mejor puente.

Pearl lo recomienda como entrada ligera a causalidad. ([Medium][3])

---

# NIVEL 2

# Judea Pearl

Ahora sí.

---

## Obligatorio

### Causality

Éste es el libro.

No hay otro.

Pearl convierte la causalidad en teoría matemática formal mediante SCMs, DAGs y do-calculus. ([Google Libros][4])

---

Objetivos:

```text
SCM

DAG

d-separation

Backdoor

Frontdoor

Do-Calculus

Counterfactuals
```

---

# NIVEL 3

# Causal Discovery

Aquí empieza lo realmente útil para TSIS.

---

Pregunta:

```text
¿Cómo descubro relaciones causales
a partir de datos?
```

---

## Libro

### Elements of Causal Inference

Muchos investigadores de IA consideran éste el puente moderno entre causalidad y machine learning. ([Brady Neal][5])

---

Éste lo estudiaría con muchísimo detalle.

---

# NIVEL 4

# Causality + Machine Learning

Aquí aparece el futuro.

---

## Obligatorio

### Causality for Machine Learning

Schölkopf

Paper fundamental.

Explica por qué muchos problemas difíciles de ML están ligados a causalidad. ([arXiv][6])

---

Pregunta:

```text
¿Por qué DeepMind
empieza a hablar tanto de causalidad?
```

---

Porque:

```text
correlación
≠
generalización
```

---

# NIVEL 5

# Causal Finance

Ahora sí.

---

## 1

### Causality and Factor Investing: A Primer

Leerlo muchas veces.

---

## 2

### Causal Factor Investing

Libro completo.

Cambridge University Press.

([Cambridge Assets][7])

---

## 3

### A Protocol for Causal Factor Investing

ADIA Lab.

Muy importante porque pasa de filosofía a protocolo de investigación. ([ADIA Lab][8])

---

## 4

### Correcting the Factor Mirage

Éste para mí es obligatorio.

Porque empieza a explicar:

```text
cómo hacerlo
```

([ADIA Lab][9])

---

# NIVEL 6

# Traducción a TSIS

Aquí ya no estudias causalidad.

La aplicas.

---

Yo crearía:

```text
11_MARKET_SCIENCE/

03_CAUSALITY/
```

---

Y dentro:

```text
01_Causal_Thinking.md

02_DAGs.md

03_Confounders.md

04_Colliders.md

05_Do_Calculus.md

06_Causal_Discovery.md

07_Causal_ML.md

08_Causal_Finance.md

09_TSIS_Causal_Framework.md
```

---

# La pregunta correcta para TSIS

NO es:

```text
¿Qué feature predice?
```

---

Es:

```text
¿Qué mecanismo genera
ese feature?
```

---

Ejemplo.

Un trader normal encuentra:

```text
RVOL > 10

↓

sube
```

---

TSIS debería preguntar:

```text
News
↓
Attention
↓
Aggressive Buying
↓
RVOL
↓
Price Move
```

---

Entonces:

```text
RVOL
```

es consecuencia.

---

Y:

```text
Attention Shock
```

es más cercano a la causa.

---

# Si yo tuviera que construir un programa doctoral para TSIS

Orden exacto:

```text
1. The Book of Why

2. Causal Inference in Statistics

3. Pearl - Causality

4. Elements of Causal Inference

5. Causality for Machine Learning

6. Causality and Factor Investing

7. A Protocol for Causal Factor Investing

8. Correcting the Factor Mirage

9. Aplicación a Market Microstructure

10. Aplicación a TSIS
```

---

Y la advertencia más importante:

No estudies causalidad para encontrar entradas.

Estúdiala para responder:

```text
¿Por qué existe este edge?
```

Porque eso es exactamente lo que diferencia un paper publicable en una revista seria, un equipo cuantitativo institucional o ADIA Lab de un simple proceso de minería de datos. López de Prado está intentando mover las finanzas desde:

```text
Encontrar patrones
```

hacia:

```text
Descubrir mecanismos
```

y ésa es probablemente una de las ideas más profundas que puedes incorporar a TSIS. ([CFA Institute Research and Policy Center][1])

[1]: https://rpc.cfainstitute.org/research/foundation/2025/causality-factor-investing?utm_source=chatgpt.com "Causality and Factor Investing: A Primer"
[2]: https://rpc.cfainstitute.org/sites/default/files/docs/research-reports/rf_lopezdeprado_causalityprimer_online.pdf?utm_source=chatgpt.com "Causality and Factor Investing: A Primer"
[3]: https://aleksander-molak.medium.com/yes-six-causality-books-that-will-get-you-from-zero-to-advanced-2023-f4d08718a2dd?utm_source=chatgpt.com "Yes! Six Causality Books That Will Get You From Zero to ..."
[4]: https://books.google.com/books/about/Causality.html?id=f4nuexsNVZIC&utm_source=chatgpt.com "Causality - Judea Pearl"
[5]: https://www.bradyneal.com/which-causal-inference-book?utm_source=chatgpt.com "Which causal inference book you should read"
[6]: https://arxiv.org/abs/1911.10500?utm_source=chatgpt.com "Causality for Machine Learning"
[7]: https://assets.cambridge.org/97810093/97292/frontmatter/9781009397292_frontmatter.pdf?utm_source=chatgpt.com "CAUSAL FACTOR INVESTING"
[8]: https://www.adialab.ae/research-series/a-protocol-for-causal-factor-investing?utm_source=chatgpt.com "A Protocol for Causal Factor Investing"
[9]: https://www.adialab.ae/research-series/correcting-the-factor-mirage-a-research-protocol-for-causal-factor-investing?utm_source=chatgpt.com "Correcting the Factor Mirage: A Research Protocol for ..."
