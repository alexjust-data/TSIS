
# TSIS.ai v2.0: Arquitectura Basada en Nodos y Agentes Autónomos

## 1. Visión del Proyecto
La evolución de **TSIS.ai** busca transformar una plataforma de trading tradicional en un "cerebro colectivo" visual. A diferencia de otros programas de backtesting, TSIS utilizará **Programación Basada en Nodos** (Node-Based Programming) integrada con una **Arquitectura Multi-Agente**.

En este modelo, cada nodo no es solo una función lógica, sino un **agente autónomo** que analiza una parte específica del mercado y se comunica con otros agentes para llegar a un consenso de ejecución.

---

## 2. Referencias de Aplicaciones (Benchmarks)

Para la UX/UI de "enchufar" nodos y la lógica de agentes, estas son las mejores referencias actuales:

1.  **[n8n.io](https://n8n.io/):** Automatización de flujos donde cada nodo realiza una acción API o lógica compleja (if/else, bucles). Es "fair-code" y auto-alojable.
2.  **[Zapier Interfaces](https://zapier.com/platform/interfaces):** Solución para crear aplicaciones personalizadas con componentes visuales que se conectan a automatizaciones.
3.  **[LangFlow](https://www.langflow.org/) / [FlowiseAI](https://flowiseai.com/):** Específicamente diseñados para IA. Permiten conectar LLMs, memorias y herramientas para crear agentes. Es lo más parecido a la visión de TSIS.
4.  **[Unreal Engine (Blueprints)](https://www.unrealengine.com/es-ES/blueprints-visual-scripting):** El estándar de oro en programación visual de alto rendimiento y ejecución de eventos en tiempo real.
5.  **[Tuned.com](https://www.tuned.com/) / [Luna Trading](https://lunatrading.com/):** Plataformas de trading que utilizan nodos para definir lógica de entrada/salida y backtesting.

---

## 3. Arquitectura del Backend: "The Agentic Orchestrator"

Para soportar datos en tiempo real y agentes que "hablan" entre sí, el backend debe ser concurrente y basado en eventos.



### Componentes Clave:
* **Motor de Grafo (Execution Engine):** Traducción del diagrama visual (JSON de nodos y aristas) en un grafo dirigido acíclico (**DAG**).
    * *Tecnología:* **NetworkX** (lógica) o **LangGraph** (orquestación de agentes).
* **Capa de Agentes (Agent Layer):** Cada nodo es un hilo o micro-servicio con un agente especializado (Rol, Herramientas, Memoria).
    * *Tecnología:* **PydanticAI** o **CrewAI**.
* **Transporte de Datos en Tiempo Real:** Sistema de mensajería ultrarrápido para que los agentes intercambien datos de mercado al milisegundo.
    * *Tecnología:* **NATS** o **Redis Pub/Sub**.
* **Backend de Alta Velocidad:** API en **FastAPI (Python)** con núcleos de cálculo críticos escritos en **Rust**.

---

## 4. Ejemplo de Flujo de Trabajo (La Tesis)

| Tipo de Nodo | Rol del Agente | Función |
| :--- | :--- | :--- |
| **Screener Node** | *The Scout* | Filtra SmallCaps con Gaps > 4% en tiempo real. |
| **Order Flow Node** | *The Tape Reader* | Analiza el DOM y el Tape; busca absorción en el bid. |
| **ML Predictor Node** | *The Analyst* | Ejecuta modelos (XGBoost) y da probabilidad de éxito. |
| **Risk Node** | *The Controller* | Valida Stop Loss y límites de pérdida diaria (Max Daily Loss). |
| **Terminal Node** | *The Executioner* | Recibe el consenso total y envía la orden a mercado (Alpaca/IBKR). |

---

## 5. Stack Tecnológico Sugerido

* **Frontend (El Lienzo):** [React Flow](https://reactflow.dev/) o **SvelteFlow**. Es la librería que permite crear el editor de nodos con drag-and-drop.
* **Orquestación:** **LangGraph**. Ideal para flujos de agentes que requieren ciclos de retroalimentación (ej. el agente de riesgo pidiendo ajustes al agente de estrategia).
* **Comunicación Interna:** **gRPC** para asegurar una latencia mínima entre los agentes y el motor de datos.
