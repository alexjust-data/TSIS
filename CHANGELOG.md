`CHANGELOG.md` es:

```text id="cl1"
la memoria histórica oficial del proyecto
```

Ahora mismo está vacío (“L”) 
y eso es normal al empezar.

---

# Lo MÁS importante

NO es:

```text id="cl2"
“un log técnico gigante”
```

NO es:

```text id="cl3"
“todos los commits pegados”
```

NO es:

```text id="cl4"
“historial Git duplicado”
```

---

# Entonces:

# ¿qué es realmente?

Es:

```text id="cl5"
historia semántica institucional
```

---

# Git ya guarda:

* líneas cambiadas
* commits
* archivos

---

# CHANGELOG guarda:

```text id="cl6"
qué cambió conceptualmente
```

---

# Ejemplo REAL

Git commit:

```text id="cl7"
feat: add universe active status filters
```

Eso está bien para Git.

---

# Pero CHANGELOG debe decir:

```text id="cl8"
v0.3.0
- Universe Builder formalized
- delisted handling introduced
- historical universe reconstruction stabilized
```

---

# Entonces:

# CHANGELOG responde:

```text id="cl9"
cómo evolucionó TSIS
```

NO:

```text id="cl10"
qué líneas cambiaron exactamente
```

---

# Qué pondría yo en tu caso

Ahora mismo probablemente:

```md id="cl11"
# TSIS Changelog

Todos los cambios institucionales relevantes del proyecto se registran aquí.

El objetivo NO es duplicar Git commits.

El objetivo es registrar:

- milestones arquitectónicos;
- cambios semánticos importantes;
- promotion states;
- breaking changes;
- releases institucionales;
- evolución conceptual del sistema.
```

---

# Luego:

---

# Primera release

```md id="cl12"
## v0.1.0 — Initial Institutional Foundation

### Added

- monorepo TSIS structure
- governance layer
- AGENTS.md institutional contract
- PROJECT_OPERATING_SYSTEM.md
- VERSIONING_STANDARDS.md
- RESEARCH_PHILOSOPHY.md
- institutional repository architecture

### Notes

This release establishes the foundational governance and research architecture of TSIS.
```

---

# Luego más adelante:

```md id="cl13"
## v0.2.0 — Data Governance Layer

### Added

- RAW data audit layer
- dataset quality policies
- dataset manifests
- schema governance
- historical reconstruction policies

### Changed

- canonical naming authority formalized
```

---

# Luego:

```md id="cl14"
## v0.3.0 — Universe Builder Institutionalization

### Added

- historical universe reconstruction
- active/inactive security tracking
- delisted support
- float filtering policies
- universe manifests

### Fixed

- timestamp normalization inconsistencies

### Breaking Changes

- universe schema updated
```

---

# Lo MÁS importante

NO registrar ruido.

---

# NO hacer esto:

```md id="cl15"
- fixed typo
- changed comment
- updated import
- changed variable name
```

Eso NO pertenece aquí.

Eso pertenece a Git.

---

# CHANGELOG debe registrar:

```text id="cl16"
cambios con importancia institucional
```

---

# Qué tipos de cosas sí van aquí

---

# Sí:

* nueva arquitectura
* nuevo pipeline
* nuevo schema
* nueva capa
* breaking changes
* promotion institutional
* nuevas policies
* cambios epistemológicos
* nuevo simulador
* nueva ontología
* nueva metodología

---

# NO:

* pequeños fixes
* imports
* cleanup trivial
* prints
* typo fixes
* experiments temporales

---

# Lo MÁS importante

Tu proyecto tiene:

* governance
* philosophy
* architecture
* reproducibility

Entonces tu changelog debe parecer:

```text id="cl17"
historia evolutiva del sistema
```

---

# NO:

```text id="cl18"
diario técnico caótico
```

---

# Cómo lo usarán agentes

MUY importante.

Los agentes leerán CHANGELOG para entender:

* qué evolucionó
* qué cambió conceptualmente
* qué es estable
* qué se rompió
* qué fue promocionado
* qué schemas cambiaron
* qué releases existen

---

# Mi recomendación REAL

Tu CHANGELOG debería ser:

* corto
* semántico
* institucional
* estable
* limpio
* milestone-oriented

---

# Sinceramente:

# probablemente deberías pensar en él como:

```text id="cl19"
historia constitucional de TSIS
```

NO como log técnico.

