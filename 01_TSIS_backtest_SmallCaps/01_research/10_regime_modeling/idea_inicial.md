Aquí ya empiezas a entrar en la zona “AlphaGo adaptado”.

Aquí sí usaría:

**Representación**
```sh
temporal transformers
TCNs
sequence encoders
contrastive learning
```

**Régimen**

```sh
HMM
switching models
clustering sobre embeddings
Bayesian regime inference
```

***Idea clave***


* Tu sistema no debe aprender: “qué es un breakout”
* Debe aprender: “en qué tipo de entorno este breakout tiene edge”

Eso cambia todo.


# 10_regime_modeling

## Objetivo

Detectar estados ocultos y cambios estructurales del mercado.

---

# Problema

Los mercados NO son estacionarios.

Los edges cambian con el tiempo.

---

# Técnicas posibles

- HMM
- clustering
- latent states
- embeddings
- switching models

---

# Objetivo

Inferir:

contexto oculto del mercado.

---

# Outputs

- regime labels
- hidden states
- transition probabilities

---

# Filosofía

El sistema debe adaptarse al régimen, no asumir estabilidad eterna.