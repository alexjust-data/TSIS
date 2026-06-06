Aquí usaría:

* CatBoost
* LightGBM
* XGBoost

¿Por qué?

Porque son brutalmente buenos para:

* datos tabulares
* features heterogéneas
* relaciones no lineales
* interpretabilidad

Y además:

```sh
rápidos
robustos
difíciles de romper
Qué intentaría predecir
```

NO:

¿subirá mañana?

Sino:

```sh
P(+1R antes de -1R)
P(HOD break success)
P(parabolic extension)
Expected MAE
Expected MFE
Probability of halt
Probability of fade
```

Eso es muchísimo más útil.



# 09_edge_estadistico

## Objetivo

Analizar dónde y cuándo existe ventaja estadística.

---

# Preguntas clave

¿En qué contexto funciona el setup?

¿En qué régimen falla?

---

# Análisis típicos

- por float
- por market cap
- por hora
- por spread
- por volatilidad
- por época
- por catalyst

---

# Outputs

- edge maps
- conditional probabilities
- expectancy tables
- regime-conditioned analysis

---

# Filosofía

El edge NO es universal.

Depende del contexto.