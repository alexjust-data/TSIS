Este es el **Documento de Especificación Técnica Maestra (v3.0)** para el equipo de desarrollo de **TSIS.ai**. Este documento fusiona el rigor matemático de los sistemas tipo QuantConnect con la arquitectura visual de vanguardia (Unreal Engine Style).

---

# 🛸 TSIS.ai v2.0: Technical Architecture & Implementation Blueprint

**Status:** High-Level Specification (No Code)

**Objective:** Gold Standard in Multi-Agent Node-Based Trading Systems.

---

## 1. Arquitectura del Motor Visual: "The Canvas Engine"

Para superar la estética de herramientas genéricas, el equipo debe construir un motor de renderizado basado en **GPU** y no en el DOM de la web.

### 1.1 Renderizado de Alta Fidelidad

* **Tecnología Base:** [WebGPU](https://gpuweb.github.io/gpuweb/) o [WebGL 2.0](https://www.khronos.org/webgl/). Se debe usar para manejar el "grid" infinito y el flujo de partículas en las aristas.
* **Framework Sugerido:** [Rete.js v2](https://retejs.org/) (Altamente modular y orientado a programación visual) o un motor propio sobre [PixiJS](https://pixijs.com/).
* **Estándar de Interfaz:** Se debe replicar el sistema de **Sub-grafos (Macros)** de [Unreal Blueprints](https://www.google.com/search?q=https://docs.unrealengine.com/5.0/en-US/blueprints-visual-scripting-in-unreal-engine/). Esto permite que una estrategia compleja de 50 nodos se colapse en 1 solo nodo maestro de "Tesis".

### 1.2 Comportamiento de los Conectores (Control Flow vs Data Flow)

Inspirado en los papers de [Visual Programming Languages (VPL)](https://www.google.com/search?q=https://ieeexplore.ieee.org/document/751061), implementaremos dos tipos de cables:

1. **Cables de Ejecución (Execution Tracks):** Color **Oro/Blanco**. Indican el orden de disparo. Sin este pulso, el nodo no procesa nada.
2. **Cables de Datos (Data Tracks):** Colores específicos por tipo (Cian para precios, Violeta para IA, Rojo para Riesgo).

---

## 2. El Agente de Nodos: "Agentic Intelligence Layer"

Cada nodo no es una función; es un agente autónomo que utiliza **Small Language Models (SLMs)** o modelos de ML específicos para Small Caps.

### 2.1 Orquestación de Agentes

* **Framework de Referencia:** [LangGraph (por LangChain)](https://www.langchain.com/langgraph). Es el estándar para grafos de agentes con ciclos y estados persistentes.
* **Consenso de Tesis:** El nodo final debe implementar una lógica de **Votación Ponderada** (Weighted Consensus). Si el agente de "Order Flow" da un score de 0.9 pero el de "Noticias" da 0.2, el motor de tesis debe decidir basándose en el [Bayesian Inference](https://www.google.com/search?q=https://towardsdatascience.com/introduction-to-bayesian-networks-81067e312162).

---

## 3. Integración con el Motor de Backtesting (Rigor Científico)

Basado en la comparativa con QuantConnect, TSIS debe evitar el "look-ahead bias" y el "overfitting".

### 3.1 Point-in-Time Data & Survivorship Bias

* **Fuente de Datos:** Integración vía [Polygon.io Stocks API](https://polygon.io/docs/stocks/get_v3_reference_tickers) usando el parámetro `date` para asegurar datos *point-in-time*.
* **Corrección de Sesgo:** El nodo "Screener" debe consultar una base de datos de tickers que incluya empresas *delisted*. Referencia: [Journal of Financial Economics - Survivorship Bias in Performance Studies](https://www.google.com/search?q=https://www.sciencedirect.com/science/article/abs/pii/0304405X89900220).

### 3.2 Métricas de Validación (Anti-Overfitting)

Cada estrategia diseñada con nodos debe pasar por:

* **DSR (Deflated Sharpe Ratio):** Para ajustar el Sharpe según cuántos nodos/variaciones el usuario intentó. [Paper original de Marcos López de Prado](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551).
* **PBO (Probability of Backtest Overfitting):** [Referencia de laboratorio (QuantResearch.org)](https://www.google.com/search?q=https://www.quantresearch.org/Library.htm).

---

## 4. "The Time-Machine Debugger"

Esta es la pieza clave para la confianza del trader.

### 4.1 Snapshotting & State Replay

* **Arquitectura de Eventos:** Cada cambio en un nodo debe ser guardado como un evento en una base de datos de series temporales como [TimescaleDB](https://www.timescale.com/).
* **Visual Debugging:** Al pausar el timeline, los cables deben mostrar el "Last Known Value". Si el usuario cambia un parámetro de un nodo en pausa, el sistema debe proyectar el "What-If" instantáneamente en los nodos siguientes.

---

## 5. Infraestructura y Despliegue (Backend)

El sistema debe procesar miles de eventos por segundo (Ticks de Small Caps).

* **Mensajería de Baja Latencia:** Usar [NATS.io](https://nats.io/) para la comunicación entre el motor de ejecución (en la nube) y la interfaz visual del usuario.
* **Multithreading:** La app local (Electron) debe delegar el renderizado a la GPU y el cálculo de agentes a hilos de [Web Workers](https://developer.mozilla.org/es/docs/Web/API/Web_Workers_API/Using_web_workers).
* **Seguridad:** Implementar un **Sandboxing** para los nodos-agentes, de modo que un agente no pueda bloquear el flujo principal de ejecución de la orden a mercado.

---

## 6. Checklist de Implementación para el Equipo

1. **Hito 1:** Lienzo infinito con soporte para 100+ nodos a 60 FPS (PixiJS + WebGL).
2. **Hito 2:** Serialización de estrategias en JSONB (PostgreSQL) para clonar/compartir tesis.
3. **Hito 3:** Integración del "Maestro de Tesis" con el informe justificado (TSIS Brief).
4. **Hito 4:** Modo Replay con sincronización de gráficos de precios (TradingView) y el estado de los nodos.

---

**Conclusión:** TSIS.ai no solo replica la potencia de QuantConnect, sino que la envuelve en una interfaz que permite la **Ingeniería de Tesis Visual**, reduciendo el error humano y acelerando la validación científica de estrategias en el mercado de Small Caps.