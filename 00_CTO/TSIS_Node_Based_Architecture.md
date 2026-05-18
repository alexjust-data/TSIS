# TSIS.ai - Arquitectura Visual Basada en Nodos y Agentes

## Documento de Diseño v1.0 - Enero 2026

---

# ÍNDICE

1. [Visión del Producto](#1-visión-del-producto)
2. [Ejemplos de Apps Basadas en Nodos](#2-ejemplos-de-apps-basadas-en-nodos)
3. [Arquitectura de Backend para Tiempo Real + Agentes](#3-arquitectura-de-backend-para-tiempo-real--agentes)
4. [Stack Tecnológico Recomendado](#4-stack-tecnológico-recomendado)
5. [Flujo de un Grafo de Estrategia](#5-flujo-de-un-grafo-de-estrategia)
6. [Comunicación entre Agentes](#6-comunicación-entre-agentes)
7. [Resumen de Requisitos](#7-resumen-de-requisitos)

---

# 1. VISIÓN DEL PRODUCTO

## 1.1 Diferenciador Clave

TSIS.ai no será otro sistema de backtesting con código. Será una **plataforma visual** donde:

- Los usuarios construyen estrategias **arrastrando y conectando nodos**
- Cada nodo está **gobernado por un agente AI** especializado
- Los agentes **colaboran entre sí** para validar y ejecutar la estrategia
- El usuario ve **todo el pipeline de principio a fin** de forma visual
- La decisión final (GO/NO-GO a mercado) es el resultado de la **inteligencia colectiva** de los agentes

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PARADIGMA TRADICIONAL vs TSIS.ai                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║   TRADICIONAL (QuantConnect, TradeStation)      TSIS.ai                       ║
║   ════════════════════════════════════════      ═══════                       ║
║                                                                                ║
║   • Escribir código                             • Arrastrar nodos             ║
║   • Configuración por parámetros               • Hablar con agentes          ║
║   • El usuario interpreta resultados            • Agentes interpretan y       ║
║                                                   recomiendan                  ║
║   • Validación manual                           • Validación automática       ║
║                                                   por agente especializado    ║
║   • Decisión 100% humana                        • Decisión asistida por       ║
║                                                   consenso de agentes         ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 1.2 Modelo Mental

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         MODELO MENTAL TSIS.ai                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║                         ┌─────────────────────────────────────┐               ║
║                         │      CANVAS VISUAL (React Flow)      │               ║
║                         │                                      │               ║
║   Usuario arrastra      │   ┌─────┐    ┌─────┐    ┌─────┐    │               ║
║   nodos y los conecta   │   │ 🤖  │───►│ 🤖  │───►│ 🤖  │    │               ║
║   con aristas           │   └─────┘    └─────┘    └─────┘    │               ║
║                         │   Screener   Entry      Exit        │               ║
║                         │                                      │               ║
║                         │   Cada nodo tiene un agente AI      │               ║
║                         │   que puede ser consultado          │               ║
║                         │                                      │               ║
║                         └─────────────────────────────────────┘               ║
║                                        │                                       ║
║                                        ▼                                       ║
║                         ┌─────────────────────────────────────┐               ║
║                         │     ORQUESTADOR DE AGENTES          │               ║
║                         │     (LangGraph / CrewAI)            │               ║
║                         │                                      │               ║
║                         │  Los agentes se comunican entre sí  │               ║
║                         │  y llegan a una conclusión conjunta │               ║
║                         └─────────────────────────────────────┘               ║
║                                        │                                       ║
║                                        ▼                                       ║
║                         ┌─────────────────────────────────────┐               ║
║                         │         DECISIÓN FINAL              │               ║
║                         │                                      │               ║
║                         │  ✅ EJECUTAR A MERCADO              │               ║
║                         │  ❌ NO EJECUTAR (con razones)       │               ║
║                         │  ⚠️ EJECUTAR CON PRECAUCIÓN        │               ║
║                         └─────────────────────────────────────┘               ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

# 2. EJEMPLOS DE APPS BASADAS EN NODOS

## 2.1 Desarrollo/Programación Visual

| App | Creador | Descripción | Relevancia para TSIS |
|-----|---------|-------------|---------------------|
| **Node-RED** | IBM | Flujos de IoT y automatización | Conexión de datos en tiempo real |
| **Unreal Blueprints** | Epic Games | Programación visual de juegos | Lógica compleja sin código |
| **ComfyUI** | Community | Workflows de AI generativa (Stable Diffusion) | **MUY RELEVANTE** - cada nodo es un modelo/proceso |
| **n8n** | n8n.io | Automatización de workflows | Integración de APIs y servicios |
| **Zapier** | Zapier | Automatización no-code | UX simple para usuarios no técnicos |

## 2.2 Finanzas/Trading

| App | Descripción | Modelo de Nodos |
|-----|-------------|-----------------|
| **QuantConnect Algorithm Framework** | Pipeline estructurado | Universe → Alpha → Portfolio → Risk → Execution |
| **Wealth-Lab** | Strategy builder | Componentes arrastrables (entry, exit, sizing) |
| **MetaTrader Strategy Tester** | Visual backtesting | Inputs → Strategy → Outputs |
| **TradingView Strategy Builder** | Pine Script visual | Condiciones → Acciones |

## 2.3 AI/ML Workflows (Más Relevantes)

| App | Creador | Descripción | Relevancia |
|-----|---------|-------------|------------|
| **LangFlow** | Logspace | Workflows de LLMs visuales | **MUY RELEVANTE** - agentes conectados visualmente |
| **Flowise** | FlowiseAI | RAG y chatbots visuales | Agentes + bases de conocimiento |
| **Dify** | Dify.ai | Orquestación de agentes AI | Multi-agente con UI visual |
| **AutoGen Studio** | Microsoft | Equipos de agentes visuales | Agentes colaborativos |
| **CrewAI** | CrewAI | Framework multi-agente | Roles y tareas definidas |
| **LangGraph Studio** | LangChain | Grafos de agentes con estado | **IDEAL** para TSIS |

## 2.4 Análisis de Inspiración

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    INSPIRACIÓN PRINCIPAL: ComfyUI + LangFlow                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  DE COMFYUI TOMAMOS:                                                          ║
║  ══════════════════                                                           ║
║  • Canvas infinito con zoom/pan                                               ║
║  • Nodos con inputs/outputs tipados                                           ║
║  • Conexiones que validan compatibilidad                                      ║
║  • Ejecución visual (ver progreso nodo por nodo)                             ║
║  • Guardar/cargar workflows como JSON                                         ║
║                                                                                ║
║  DE LANGFLOW TOMAMOS:                                                         ║
║  ════════════════════                                                         ║
║  • Cada nodo puede ser un agente LLM                                          ║
║  • Chat embebido para interactuar con el flujo                               ║
║  • Playground para probar en tiempo real                                      ║
║  • Variables de estado que pasan entre nodos                                  ║
║                                                                                ║
║  RESULTADO TSIS.ai:                                                           ║
║  ══════════════════                                                           ║
║  Canvas visual donde cada nodo es un agente especializado en trading          ║
║  que puede ser consultado y que colabora con otros agentes                    ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

# 3. ARQUITECTURA DE BACKEND PARA TIEMPO REAL + AGENTES

## 3.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA TSIS.ai - NODOS + AGENTES                        │
└─────────────────────────────────────────────────────────────────────────────────┘

FRONTEND (React + React Flow)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    CANVAS DE NODOS (React Flow / XYFlow)                 │   │
│  │                                                                          │   │
│  │  • Drag & drop de nodos desde paleta                                    │   │
│  │  • Conexión visual de aristas (validación de tipos)                     │   │
│  │  • Estado visual de cada agente:                                        │   │
│  │    - 🔵 Idle (esperando)                                                │   │
│  │    - 🟡 Thinking (procesando)                                           │   │
│  │    - 🟢 Complete (terminado)                                            │   │
│  │    - 🔴 Error (falló)                                                   │   │
│  │  • Chat embebido por nodo para interactuar con el agente               │   │
│  │  • Panel de propiedades para configurar cada nodo                       │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │  MARKET DATA     │  │  AGENT CHAT      │  │  RESULTS PANEL   │             │
│  │  PANEL           │  │  PANEL           │  │                  │             │
│  │                  │  │                  │  │  Métricas        │             │
│  │  Precios live    │  │  Conversación    │  │  Equity curve    │             │
│  │  Noticias        │  │  con agentes     │  │  Trades          │             │
│  │  Alertas         │  │                  │  │  Validación      │             │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
API GATEWAY (FastAPI + WebSockets)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│  REST ENDPOINTS:                         WEBSOCKET ENDPOINTS:                   │
│  ════════════════                        ════════════════════                   │
│  POST   /api/graphs                      /ws/graph/{graph_id}                   │
│  GET    /api/graphs/{id}                 → Estado de agentes en tiempo real    │
│  PUT    /api/graphs/{id}                 → Mensajes entre agentes              │
│  DELETE /api/graphs/{id}                 → Progreso de ejecución               │
│                                                                                  │
│  POST   /api/graphs/{id}/execute         /ws/market                            │
│  POST   /api/graphs/{id}/backtest        → Precios en tiempo real              │
│  GET    /api/graphs/{id}/results         → Alertas de gaps                     │
│                                          → Noticias                             │
│  POST   /api/nodes/{id}/chat                                                    │
│  GET    /api/nodes/types                 /ws/agent/{agent_id}                  │
│                                          → Chat con agente específico          │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼

AGENT ORCHESTRATOR              MESSAGE BROKER                DATA SERVICE
(LangGraph / CrewAI)            (Redis Streams)               (Python + Rust)
┌─────────────────────┐         ┌─────────────────────┐       ┌─────────────────────┐
│                     │         │                     │       │                     │
│  ┌───────────────┐  │         │  CHANNELS:          │       │  POLYGON WEBSOCKET  │
│  │ 🤖 Agente     │  │         │  ═══════════════    │       │  ═════════════════  │
│  │    Screener   │  │◄───────►│  • node:events     │◄─────►│  • Trades (T&S)     │
│  └───────────────┘  │         │  • agent:messages  │       │  • Quotes (L1/L2)   │
│                     │         │  • market:data     │       │  • Bars (1m, 5m)    │
│  ┌───────────────┐  │         │  • graph:state     │       │  • News (Benzinga)  │
│  │ 🤖 Agente     │  │         │                     │       │                     │
│  │    Entry      │  │         │  FEATURES:          │       │  FEATURE ENGINE     │
│  └───────────────┘  │         │  ═══════════════    │       │  ═══════════════    │
│                     │         │  • Pub/Sub          │       │  • VWAP calculator  │
│  ┌───────────────┐  │         │  • Consumer groups  │       │  • Delta/VPIN       │
│  │ 🤖 Agente     │  │         │  • Message history  │       │  • Book imbalance   │
│  │    Exit       │  │         │                     │       │  • Tape speed       │
│  └───────────────┘  │         └─────────────────────┘       │                     │
│                     │                                        │  HISTORICAL DATA    │
│  ┌───────────────┐  │                                        │  ═══════════════    │
│  │ 🤖 Agente     │  │                                        │  • Parquet loader   │
│  │    Validator  │  │                                        │  • TimescaleDB      │
│  └───────────────┘  │                                        │                     │
│                     │                                        └─────────────────────┘
│  ┌───────────────┐  │                                                   │
│  │ 🤖 Agente     │  │                                                   │
│  │    Risk       │  │                                                   │
│  └───────────────┘  │                                                   │
│                     │                                                   │
│  ┌───────────────┐  │                                                   │
│  │ 🤖 Agente     │  │                                                   │
│  │    ML/Quality │  │                                                   │
│  └───────────────┘  │                                                   │
│                     │                                                   │
│  ┌───────────────┐  │                                                   │
│  │ 🤖 Agente     │  │                                                   │
│  │    Decision   │  │                                                   │
│  └───────────────┘  │                                                   │
│                     │                                                   │
└─────────────────────┘                                                   │
         │                                                                │
         ▼                                                                │
┌─────────────────────┐                                                   │
│  LLM BACKEND        │                                                   │
│  ═════════════════  │                                                   │
│                     │                                                   │
│  • Claude API       │  ◄── Recomendado para agentes complejos          │
│  • OpenAI API       │                                                   │
│  • Local (Ollama)   │  ◄── Para desarrollo/testing                     │
│  • Groq             │  ◄── Para respuestas rápidas                     │
│                     │                                                   │
└─────────────────────┘                                                   │
                                                                          │
                                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PERSISTENCE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐ │
│  │     PostgreSQL      │    │    TimescaleDB      │    │       Redis         │ │
│  │                     │    │                     │    │                     │ │
│  │  • Users            │    │  • Prices (OHLCV)   │    │  • Cache            │ │
│  │  • Graphs (JSON)    │    │  • Quotes           │    │  • Sessions         │ │
│  │  • Nodes config     │    │  • Features calc    │    │  • Pub/Sub          │ │
│  │  • Strategies       │    │  • Trades executed  │    │  • Agent state      │ │
│  │  • Backtest results │    │  • Equity curves    │    │  • Rate limiting    │ │
│  │  • Agent memory     │    │                     │    │                     │ │
│  │                     │    │                     │    │                     │ │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘ │
│                                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐                             │
│  │     S3 / MinIO      │    │      MLflow         │                             │
│  │                     │    │                     │                             │
│  │  • Parquet files    │    │  • ML models        │                             │
│  │  • Exported reports │    │  • Experiments      │                             │
│  │  • Agent artifacts  │    │  • Model registry   │                             │
│  │                     │    │                     │                             │
│  └─────────────────────┘    └─────────────────────┘                             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Flujo de Datos en Tiempo Real

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS EN TIEMPO REAL                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

                    POLYGON.IO
                        │
                        │ WebSocket (trades, quotes, bars)
                        ▼
              ┌─────────────────────┐
              │    DATA SERVICE     │
              │                     │
              │  1. Recibe datos    │
              │  2. Normaliza       │
              │  3. Calcula features│
              │  4. Publica         │
              └─────────────────────┘
                        │
                        │ Redis Pub/Sub
                        ▼
              ┌─────────────────────┐
              │   REDIS STREAMS     │
              │                     │
              │  market:AAPL        │
              │  market:TSLA        │
              │  features:realtime  │
              │  gaps:detected      │
              └─────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Agente  │    │ Agente  │    │ WebSocket│
    │Screener │    │ Entry   │    │ Server   │
    │         │    │         │    │          │
    │ Evalúa  │    │ Busca   │    │ Envía a  │
    │ gaps    │    │ señales │    │ frontend │
    └─────────┘    └─────────┘    └─────────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │      FRONTEND       │
              │                     │
              │  • Precios live     │
              │  • Estado agentes   │
              │  • Alertas          │
              │  • Señales          │
              └─────────────────────┘
```

---

# 4. STACK TECNOLÓGICO RECOMENDADO

## 4.1 Frontend - Canvas de Nodos

| Tecnología | Rol | Por Qué |
|------------|-----|---------|
| **React 18** | Framework | Ecosystem maduro, hooks, concurrent features |
| **React Flow (xyflow)** | Canvas de nodos | La mejor librería - usada por n8n, LangFlow, Flowise |
| **TypeScript** | Lenguaje | Type safety, mejor DX |
| **Zustand** | Estado global | Simple, performant, menos boilerplate que Redux |
| **TanStack Query** | Server state | Cache, invalidation, optimistic updates |
| **Socket.io-client** | WebSocket | Reconexión automática, fallback |
| **TailwindCSS** | Estilos | Utility-first, rápido |
| **shadcn/ui** | Componentes | Accesible, customizable, bonito |
| **Plotly.js** | Gráficos 3D | Superficies de optimización interactivas |
| **TradingView Lightweight** | Charts financieros | Profesional, performant |

## 4.2 Backend - API y Orquestación

| Tecnología | Rol | Por Qué |
|------------|-----|---------|
| **FastAPI** | Framework API | Async nativo, WebSocket, auto-docs, type hints |
| **Python 3.11+** | Lenguaje | Ecosystem ML/AI, async/await mejorado |
| **LangGraph** | Orquestación agentes | Grafos con estado, checkpoints, mejor que LangChain puro |
| **Pydantic v2** | Validación | Fast, integrado con FastAPI |
| **Celery** | Task queue | Backtests pesados, ML training |
| **Redis** | Broker + Cache | Pub/Sub, Streams, ultra rápido |

## 4.3 Agentes AI

| Tecnología | Rol | Por Qué |
|------------|-----|---------|
| **LangGraph** | Framework de agentes | Estado persistente, ciclos, bifurcaciones |
| **Claude API (Anthropic)** | LLM principal | Mejor razonamiento, tool use avanzado |
| **Ollama** | LLM local | Desarrollo, testing, sin costos |
| **LangSmith** | Observabilidad | Tracing, debugging de agentes |

## 4.4 Base de Datos

| Tecnología | Rol | Por Qué |
|------------|-----|---------|
| **PostgreSQL 16** | DB principal | JSONB para grafos, extensible |
| **TimescaleDB** | Time series | Hypertables, compression, built on Postgres |
| **Redis 7** | Cache + Pub/Sub | Sub-ms latency, Streams para eventos |
| **MinIO / S3** | Object storage | Parquet files, modelos ML, reportes |

## 4.5 ML/AI Pipeline

| Tecnología | Rol | Por Qué |
|------------|-----|---------|
| **MLflow** | Experiment tracking | Industry standard, model registry |
| **XGBoost** | Modelos tabulares | Rápido, interpretable |
| **PyTorch** | Deep learning | Quality predictor, embeddings |
| **Stable-Baselines3** | Reinforcement Learning | Position sizing con PPO/SAC |

## 4.6 Infrastructure

| Tecnología | Rol | Por Qué |
|------------|-----|---------|
| **Docker Compose** | Desarrollo | Ambiente consistente |
| **Kubernetes** | Producción | Scaling, auto-healing |
| **GitHub Actions** | CI/CD | Integrado, gratis para open source |
| **Prometheus + Grafana** | Monitoring | Industry standard |

---

# 5. FLUJO DE UN GRAFO DE ESTRATEGIA

## 5.1 Ejemplo: Estrategia Gap & Go

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    EJEMPLO: GRAFO DE ESTRATEGIA GAP & GO                         │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   📊 NODO 0     │
                              │   DATA SOURCE   │
                              │                 │
                              │  Polygon WS     │
                              │  + Historical   │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   🤖 NODO 1     │
                              │   SCREENER      │
                              │   AGENT         │
                              │                 │
                              │  "Filtra gaps   │
                              │   >15%, float   │
                              │   <10M, PM vol  │
                              │   >500K"        │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
           ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
           │  🤖 NODO 2A   │  │  🤖 NODO 2B   │  │  🤖 NODO 2C   │
           │  CATALYST     │  │  FUNDAMENTALS │  │  TECHNICALS   │
           │  AGENT        │  │  AGENT        │  │  AGENT        │
           │               │  │               │  │               │
           │  "¿Hay        │  │  "¿Tiene      │  │  "¿Estructura │
           │   catalizador │  │   dilution    │  │   técnica     │
           │   válido?"    │  │   risk?"      │  │   favorable?" │
           └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
                   │                  │                  │
                   └──────────────────┼──────────────────┘
                                      │
                                      ▼
                              ┌─────────────────┐
                              │   🤖 NODO 3     │
                              │   ENTRY AGENT   │
                              │                 │
                              │  "Detecta       │
                              │   breakout PM   │
                              │   high con      │
                              │   confirmación" │
                              └────────┬────────┘
                                       │
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
                │  🤖 NODO 4    │ │  🤖 NODO 5    │ │  🤖 NODO 6    │
                │  EXIT AGENT   │ │  RISK AGENT   │ │  ML QUALITY   │
                │               │ │               │ │  AGENT        │
                │  "Gestiona    │ │  "Calcula     │ │               │
                │   trailing,   │ │   position    │ │  "Predice     │
                │   targets,    │ │   size,       │ │   probabilidad│
                │   time stops" │ │   valida      │ │   de éxito:   │
                │               │ │   exposure"   │ │   78%"        │
                └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
                        │                 │                 │
                        └─────────────────┼─────────────────┘
                                          │
                                          ▼
                              ┌─────────────────┐
                              │   🤖 NODO 7     │
                              │   VALIDATOR     │
                              │   AGENT         │
                              │                 │
                              │  "Calcula DSR,  │
                              │   PBO, WFA.     │
                              │   Genera        │
                              │   certificado"  │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   🤖 NODO 8     │
                              │   DECISION      │
                              │   AGENT         │
                              │                 │
                              │  "Consenso de   │
                              │   todos los     │
                              │   agentes:      │
                              │                 │
                              │   ✅ GO         │
                              │   ❌ NO-GO      │
                              │   ⚠️ CAUTION   │
                              └─────────────────┘
```

## 5.2 Tipos de Nodos Disponibles

### Nodos de Datos
| Nodo | Descripción | Inputs | Outputs |
|------|-------------|--------|---------|
| **Data Source** | Fuente de datos (Polygon, Historical) | Config | Market Data |
| **Feature Calculator** | Calcula VWAP, Delta, etc. | Market Data | Features |
| **News Feed** | Noticias y catalizadores | Tickers | News Events |

### Nodos de Agentes
| Nodo | Agente | Responsabilidad |
|------|--------|-----------------|
| **Screener** | 🤖 Screener Agent | Filtrar universo de gaps |
| **Catalyst** | 🤖 Catalyst Agent | Validar catalizador |
| **Fundamentals** | 🤖 Fundamentals Agent | Evaluar riesgos fundamentales |
| **Technicals** | 🤖 Technicals Agent | Análisis técnico |
| **Entry** | 🤖 Entry Agent | Detectar señales de entrada |
| **Exit** | 🤖 Exit Agent | Gestionar salidas |
| **Risk** | 🤖 Risk Agent | Position sizing, exposure |
| **ML Quality** | 🤖 ML Agent | Predicción de calidad |
| **Validator** | 🤖 Validator Agent | Validación científica |
| **Decision** | 🤖 Decision Agent | Decisión final GO/NO-GO |

### Nodos de Utilidad
| Nodo | Descripción |
|------|-------------|
| **Merge** | Combina múltiples inputs |
| **Split** | Divide output en múltiples paths |
| **Filter** | Filtra basado en condición |
| **Logger** | Debug y logging |
| **Alert** | Envía notificación |

---

# 6. COMUNICACIÓN ENTRE AGENTES

## 6.1 Arquitectura de Comunicación

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    COMUNICACIÓN ENTRE AGENTES (LangGraph)                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────────────────┐
                         │         GRAPH STATE             │
                         │                                 │
                         │  {                              │
                         │    ticker: "ABCD",              │
                         │    gap_pct: 25.5,               │
                         │    screener_passed: true,       │
                         │    catalyst: "earnings",        │
                         │    entry_signal: {...},         │
                         │    ml_score: 0.78,              │
                         │    risk_approved: true,         │
                         │    validation: {...},           │
                         │    decision: "GO",              │
                         │    agent_messages: [...]        │
                         │  }                              │
                         │                                 │
                         └─────────────────────────────────┘
                                        ▲
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
           ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
           │ 🤖 Agente A   │   │ 🤖 Agente B   │   │ 🤖 Agente C   │
           │               │   │               │   │               │
           │ Lee estado    │   │ Lee estado    │   │ Lee estado    │
           │ Procesa       │   │ Procesa       │   │ Procesa       │
           │ Actualiza     │   │ Actualiza     │   │ Actualiza     │
           │ estado        │   │ estado        │   │ estado        │
           └───────────────┘   └───────────────┘   └───────────────┘
```

## 6.2 Ejemplo de Implementación con LangGraph

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

# Estado compartido entre todos los agentes
class TSISState(TypedDict):
    # Datos del ticker
    ticker: str
    date: str
    gap_pct: float
    gap_data: dict

    # Resultados de agentes
    screener_result: dict | None
    catalyst_result: dict | None
    fundamentals_result: dict | None
    entry_signal: dict | None
    exit_plan: dict | None
    risk_assessment: dict | None
    ml_prediction: dict | None
    validation_result: dict | None

    # Decisión final
    final_decision: Literal["GO", "NO_GO", "CAUTION"] | None
    decision_reasoning: str | None

    # Mensajes entre agentes
    agent_messages: list[dict]

# Agente Screener
def screener_agent(state: TSISState) -> TSISState:
    """Agente que evalúa si el gap pasa los filtros del screener"""
    llm = ChatAnthropic(model="claude-sonnet-4-20250514")

    prompt = f"""Eres el Agente Screener de TSIS.ai.

    Evalúa si este gap cumple con los criterios:
    - Gap: {state['gap_pct']}%
    - Float: {state['gap_data'].get('float', 'N/A')}
    - PM Volume: {state['gap_data'].get('pm_volume', 'N/A')}

    Criterios:
    - Gap > 15%
    - Float < 10M
    - PM Volume > 500K

    Responde con tu análisis y si PASA o NO PASA."""

    response = llm.invoke(prompt)

    return {
        **state,
        "screener_result": {
            "passed": True,  # Parseado de la respuesta
            "analysis": response.content,
            "agent": "screener"
        },
        "agent_messages": state["agent_messages"] + [{
            "from": "screener",
            "content": response.content
        }]
    }

# Agente Entry
def entry_agent(state: TSISState) -> TSISState:
    """Agente que detecta señales de entrada"""
    llm = ChatAnthropic(model="claude-sonnet-4-20250514")

    # Tiene acceso a los resultados previos
    screener_analysis = state["screener_result"]["analysis"]

    prompt = f"""Eres el Agente de Entry de TSIS.ai.

    El Agente Screener dijo: {screener_analysis}

    Analiza los datos técnicos y determina si hay señal de entrada:
    - PM High: {state['gap_data'].get('pm_high')}
    - Current Price: {state['gap_data'].get('current_price')}
    - VWAP: {state['gap_data'].get('vwap')}

    ¿Hay señal de BREAKOUT PM HIGH?"""

    response = llm.invoke(prompt)

    return {
        **state,
        "entry_signal": {
            "detected": True,
            "type": "BREAKOUT_PM_HIGH",
            "price": state['gap_data'].get('current_price'),
            "analysis": response.content
        }
    }

# Agente Decision (consenso final)
def decision_agent(state: TSISState) -> TSISState:
    """Agente que toma la decisión final basado en todos los inputs"""
    llm = ChatAnthropic(model="claude-sonnet-4-20250514")

    # Recopila todos los resultados de otros agentes
    all_results = {
        "screener": state.get("screener_result"),
        "catalyst": state.get("catalyst_result"),
        "fundamentals": state.get("fundamentals_result"),
        "entry": state.get("entry_signal"),
        "risk": state.get("risk_assessment"),
        "ml": state.get("ml_prediction"),
        "validation": state.get("validation_result")
    }

    prompt = f"""Eres el Agente de Decisión de TSIS.ai.

    Tu trabajo es analizar los reportes de todos los agentes y tomar
    una decisión final: GO, NO_GO, o CAUTION.

    Reportes de agentes:
    {all_results}

    Historial de mensajes entre agentes:
    {state['agent_messages']}

    Toma tu decisión y explica el razonamiento."""

    response = llm.invoke(prompt)

    # Parsear decisión
    decision = "GO" if "GO" in response.content.upper() else "NO_GO"

    return {
        **state,
        "final_decision": decision,
        "decision_reasoning": response.content
    }

# Construir el grafo
def build_tsis_graph():
    graph = StateGraph(TSISState)

    # Añadir nodos
    graph.add_node("screener", screener_agent)
    graph.add_node("catalyst", catalyst_agent)
    graph.add_node("fundamentals", fundamentals_agent)
    graph.add_node("entry", entry_agent)
    graph.add_node("exit", exit_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("ml", ml_agent)
    graph.add_node("validator", validator_agent)
    graph.add_node("decision", decision_agent)

    # Definir edges (flujo)
    graph.set_entry_point("screener")

    # Screener en paralelo evalúa catalyst y fundamentals
    graph.add_edge("screener", "catalyst")
    graph.add_edge("screener", "fundamentals")

    # Después de catalyst y fundamentals, va a entry
    graph.add_edge("catalyst", "entry")
    graph.add_edge("fundamentals", "entry")

    # Entry en paralelo evalúa exit, risk, ml
    graph.add_edge("entry", "exit")
    graph.add_edge("entry", "risk")
    graph.add_edge("entry", "ml")

    # Todo converge en validator
    graph.add_edge("exit", "validator")
    graph.add_edge("risk", "validator")
    graph.add_edge("ml", "validator")

    # Validator va a decision
    graph.add_edge("validator", "decision")

    # Decision es el final
    graph.add_edge("decision", END)

    return graph.compile()

# Ejecutar
async def run_strategy(ticker: str, gap_data: dict):
    graph = build_tsis_graph()

    initial_state = {
        "ticker": ticker,
        "date": "2026-01-15",
        "gap_pct": gap_data["gap_pct"],
        "gap_data": gap_data,
        "agent_messages": []
    }

    # Stream de resultados para actualizar UI en tiempo real
    async for event in graph.astream(initial_state):
        yield event  # Enviar a frontend via WebSocket
```

## 6.3 Comunicación en Tiempo Real con Frontend

```python
# backend/websocket_handler.py
from fastapi import WebSocket
from langgraph.graph import StateGraph

class GraphWebSocketHandler:
    def __init__(self, websocket: WebSocket, graph_id: str):
        self.ws = websocket
        self.graph_id = graph_id

    async def execute_and_stream(self, initial_state: dict):
        graph = build_tsis_graph()

        async for event in graph.astream(initial_state):
            # Cada vez que un agente termina, enviamos update al frontend
            await self.ws.send_json({
                "type": "agent_update",
                "graph_id": self.graph_id,
                "node": event.get("current_node"),
                "state": event.get("state"),
                "timestamp": datetime.now().isoformat()
            })

        # Enviar resultado final
        await self.ws.send_json({
            "type": "graph_complete",
            "graph_id": self.graph_id,
            "final_decision": event["state"]["final_decision"],
            "reasoning": event["state"]["decision_reasoning"]
        })
```

---

# 7. RESUMEN DE REQUISITOS

## 7.1 Requisitos Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Canvas Visual** | Arrastrar y soltar nodos desde paleta |
| **Canvas Visual** | Conectar nodos con aristas (validación de tipos) |
| **Canvas Visual** | Zoom, pan, minimap |
| **Canvas Visual** | Guardar/cargar grafos como JSON |
| **Agentes** | Cada nodo puede tener un agente AI |
| **Agentes** | Chat embebido para interactuar con cada agente |
| **Agentes** | Estado visual del agente (idle, thinking, done, error) |
| **Agentes** | Los agentes se comunican entre sí |
| **Tiempo Real** | Datos de mercado en vivo (Polygon) |
| **Tiempo Real** | Actualizaciones de estado de agentes |
| **Tiempo Real** | Alertas de gaps detectados |
| **Backtesting** | Ejecutar estrategia sobre datos históricos |
| **Backtesting** | Optimización de parámetros |
| **Backtesting** | Walk-Forward Analysis |
| **Validación** | DSR, PBO, certificado de robustez |

## 7.2 Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Canvas fluido con 50+ nodos |
| **Performance** | WebSocket latency < 100ms |
| **Performance** | Backtest de 5 años < 30 segundos |
| **Escalabilidad** | Soportar 100+ usuarios concurrentes |
| **Disponibilidad** | 99.9% uptime |
| **Seguridad** | Autenticación JWT |
| **Seguridad** | Datos encriptados en tránsito |

## 7.3 Stack Final Resumido

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         STACK TECNOLÓGICO TSIS.ai                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  FRONTEND                                                                       │
│  ════════                                                                       │
│  React 18 + TypeScript + React Flow + Zustand + TailwindCSS + shadcn/ui        │
│  TradingView Charts + Plotly.js + Socket.io                                     │
│                                                                                  │
│  BACKEND                                                                        │
│  ═══════                                                                        │
│  FastAPI + Python 3.11 + LangGraph + Celery + Redis                            │
│                                                                                  │
│  AGENTES AI                                                                     │
│  ══════════                                                                     │
│  LangGraph + Claude API + LangSmith (observabilidad)                           │
│                                                                                  │
│  DATOS                                                                          │
│  ═════                                                                          │
│  PostgreSQL + TimescaleDB + Redis + MinIO                                       │
│  Polygon.io (real-time) + Parquet (historical)                                 │
│                                                                                  │
│  ML/AI                                                                          │
│  ═════                                                                          │
│  MLflow + XGBoost + PyTorch + Stable-Baselines3                                │
│                                                                                  │
│  INFRA                                                                          │
│  ═════                                                                          │
│  Docker + Kubernetes + GitHub Actions + Prometheus + Grafana                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

**Documento Generado para TSIS.ai**
**Arquitectura Visual Basada en Nodos y Agentes v1.0**
**Enero 2026**
