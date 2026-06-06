# TSIS Project Rules

## 1. Rol de este documento

`PROJECT_RULES.md` es el reglamento transversal de conducta técnica e institucional de TSIS.

No es un documento filosófico profundo.
No es un manual de Git.
No es un mapa de arquitectura.
No es un contrato específico para agentes.

Su función es definir qué conducta es obligatoria, aceptable e institucionalmente correcta dentro del proyecto.

Si `RESEARCH_PHILOSOPHY.md` define cómo piensa TSIS, y `PROJECT_OPERATING_SYSTEM.md` define cómo funciona TSIS, este documento define cómo debe trabajarse dentro de TSIS.

---

## 2. Principio rector

TSIS no se gobierna por conveniencia local, velocidad momentánea o resultados visualmente atractivos.

TSIS se gobierna por:

- reproducibilidad;
- claridad semántica;
- disciplina estructural;
- robustez;
- trazabilidad;
- y realismo operativo.

Cuando exista conflicto entre rapidez y rigor, manda el rigor.
Cuando exista conflicto entre comodidad local y coherencia institucional, manda la coherencia institucional.

---

## 3. Prioridades institucionales

Las prioridades transversales de TSIS son estas:

- `reproducibilidad > velocidad`
- `robustez > optimización puntual`
- `claridad > complejidad innecesaria`
- `trazabilidad > conveniencia local`
- `ejecución realista > equity curve bonita`
- `semántica explícita > convenciones implícitas`
- `disciplina institucional > atajos personales`

Estas prioridades deben gobernar decisiones humanas y decisiones de agentes.

---

## 4. Reglas fundamentales del proyecto

### 4.1. Ningún resultado importante puede depender de memoria humana

No se acepta como institucionalmente válido ningún resultado que solo pueda explicarse por:

- memoria verbal;
- contexto de conversación;
- prompts pasados;
- conocimiento tácito no documentado;
- parámetros no versionados.

### 4.2. Ningún módulo define su propia source of truth

La verdad operativa del sistema no puede fragmentarse en verdades locales incompatibles.

Todo módulo debe alinearse con:

- contracts institucionales;
- manifests oficiales;
- versionado lógico de datasets;
- semántica canónica del repositorio.

### 4.3. Ningún output importante vale sin contexto

Un output sin:

- origen;
- config;
- dataset version;
- commit;
- manifest o metadata suficiente;

no debe usarse como evidencia institucional.

### 4.4. Ningún resultado bonito equivale por sí mismo a edge real

Una equity curve atractiva no es una prueba.
Un experimento prometedor no es promoción.
Un notebook convincente no es evidencia institucional suficiente.

---

## 5. Reglas de promoción

Nada debe promocionarse dentro de TSIS solo por entusiasmo, intuición o resultados superficiales.

### 5.1. Nada se considera serio si no puede reconstruirse

Ninguna estrategia, dataset, modelo, simulador o pipeline debe considerarse institucionalmente serio si no puede reconstruirse sin ambigüedad.

### 5.2. Nada promoted sin estructura mínima

Nada debe pasar a estado fuerte sin:

- `manifest`;
- `owner` explícito;
- naming estable;
- validación documentada;
- versionado suficiente;
- y trazabilidad de inputs/outputs.

### 5.3. Nada institutional por default

El estado `institutional` debe ser excepcional y ganado.
Nunca debe ser el estado implícito por defecto de algo nuevo.

---

## 6. Reglas de calidad del trabajo

### 6.1. La claridad es una obligación

Toda pieza importante del sistema debe poder explicarse de forma precisa.
Si algo no puede describirse con claridad, probablemente aún no está suficientemente bien definido.

### 6.2. La semántica manda sobre el nombre técnico

No basta con que algo “funcione”.
Debe significar exactamente lo que dice significar.

Los nombres institucionales son contratos semánticos.
Por tanto, está prohibido sostener entidades ambiguas solo porque el código todavía las tolera.

### 6.3. Las decisiones arquitectónicas deben dejar rastro

Toda decisión arquitectónica relevante debe documentarse.
No debe vivir solo en la cabeza de una persona ni en una conversación puntual.

### 6.4. La deuda técnica debe declararse

La deuda técnica no es una vergüenza.
La deuda técnica invisible sí lo es.

Todo compromiso provisional importante debe quedar documentado como tal.

---

## 7. Reglas de investigación

### 7.1. La ausencia de evidencia no es evidencia de edge

Si una hipótesis no ha sido refutada todavía, eso no la convierte en válida.
Si un setup no ha sido suficientemente degradado, eso no lo convierte en robusto.

### 7.2. La simulación realista tiene prioridad sobre el optimismo

Cuando un conflicto entre un resultado atractivo y una simulación más realista obligue a elegir, manda la simulación más realista.

### 7.3. Ninguna hipótesis debe protegerse del escrutinio

Una hipótesis no merece privilegio por:

- sofisticación técnica;
- intuición fuerte;
- tradición del trader;
- pasado reciente;
- complejidad del modelo.

Toda hipótesis relevante debe poder degradarse, falsarse o ponerse en cuarentena.

### 7.4. La robustez importa más que el máximo local

TSIS no persigue el mejor resultado aislado.
Persigue mecanismos suficientemente sólidos como para sobrevivir a validación, fricción y cambio de régimen.

---

## 8. Reglas sobre módulos y capas

### 8.1. Los límites entre capas deben respetarse

Las fronteras entre:

- datos;
- features;
- eventos;
- estados;
- estrategias;
- ejecución;
- reporting;
- ML/RL;

no son decorativas.

Son una protección estructural del sistema.

### 8.2. Ninguna capa debe absorber silenciosamente responsabilidades de otra

Si una capa empieza a redefinir el rol de otra, eso debe ser una decisión explícita, no una deriva informal.

### 8.3. Los contratos compartidos deben tratarse como infraestructura

Todo contrato compartido entre módulos o capas debe considerarse infraestructura institucional y no detalle accidental de implementación.

---

## 9. Reglas de documentación

### 9.1. Documentar no es opcional

Cuando una pieza del sistema cambia su semántica operativa, la documentación relevante debe actualizarse.

### 9.2. La documentación institucional no debe duplicarse sin necesidad

Cada documento raíz debe tener función propia.
No se debe convertir un archivo en duplicado parcial de otro.

### 9.3. Si un conocimiento es importante, debe ser persistente

Todo conocimiento estructural relevante debe vivir en el repositorio de forma:

- versionada;
- trazable;
- legible;
- persistente.

---

## 10. Reglas para humanos

### 10.1. No existe vía rápida humana por encima del sistema

Ninguna persona está autorizada a degradar la disciplina estructural solo porque entiende el contexto actual del proyecto.

### 10.2. El contexto verbal no sustituye el contrato escrito

Lo que “sabemos” de palabra no sustituye:

- manifests;
- changelogs;
- versionado;
- naming canónico;
- policies institucionales.

### 10.3. La autoridad humana implica más responsabilidad, no menos disciplina

Quien toma decisiones finales dentro del proyecto debe aumentar el nivel de trazabilidad, no relajarlo.

---

## 11. Reglas para agentes

Los agentes deben tratar este documento como norma de conducta transversal.

Si existe conflicto entre:

- producir rápido;
- dejar trazabilidad;
- respetar semántica institucional;
- mantener separación entre capas;

el agente debe elegir la opción que preserve la estructura del sistema.

Los agentes no deben optimizar localmente a costa del orden global del proyecto.

---

## 12. Regla final

TSIS no debe convertirse en:

- una colección de scripts;
- un laboratorio de notebooks desconectados;
- una suma de hallazgos difíciles de reconstruir;
- un repositorio dependiente de personas concretas;
- una arquitectura que solo funciona mientras sus creadores recuerdan cómo opera.

TSIS debe evolucionar como:

- sistema cuantitativo modular;
- infraestructura reproducible;
- laboratorio audit-ready;
- stack compatible con agentes;
- y proyecto capaz de crecer durante años sin colapsar estructuralmente.

Toda regla de este documento existe para defender esa dirección.
