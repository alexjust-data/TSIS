# TSIS.ai - Motor de Backtesting para Small Caps

## Guía Conceptual y Especificación de Procesos v2.0

**Fecha:** Enero 2026
**Propósito:** Documento maestro para desarrollo del motor de backtesting

---

# ÍNDICE

1. El Problema Fundamental
2. Inventario de Datos Disponibles
3. Anatomía de un Gap en Small Caps
4. Arquitectura Conceptual del Motor
5. El Universo Dinámico: Tabla de Gaps Históricos
6. Experiencia del Usuario: El Wizard de 6 Pasos
7. Motor de Ejecución de Estrategias
8. Sistema de Optimización Multi-Parámetro
9. Walk-Forward Analysis (WFA)
10. Cluster Analysis y Mapas de Estabilidad 3D
11. Sensitivity Analysis
12. Validación Científica Anti-Overfitting
13. Resultados y Visualizaciones
14. Plan de Tests por Etapa de Ingeniería
15. Preparación para Streaming Real-Time
16. Glosario de Términos

---

# 1. EL PROBLEMA FUNDAMENTAL

## 1.1 ¿Por Qué Small Caps Es Diferente?

Cuando trabajas en TradeStation con el ES (E-mini S&P 500), aplicas tu estrategia a **UN SOLO instrumento**. En small caps, **el universo de instrumentos cambia CADA DÍA**.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     COMPARACIÓN: TRADESTATION vs TSIS.ai                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║   TRADESTATION (ES/NQ)                    TSIS.ai (SMALL CAPS)                ║
║   ════════════════════                    ════════════════════                 ║
║                                                                                ║
║   ┌─────────────────────┐                 Día 1: [ABCD, XYZ]                  ║
║   │                     │                 Día 2: [EFGH, IJKL, MNOP]           ║
║   │    ES FUTURES       │                 Día 3: [QRST]                       ║
║   │                     │                 Día 4: [UVWX, YZAB]                 ║
║   │    (siempre el      │                 Día 5: [CDEF, GHIJ, KLMN, OPQR]     ║
║   │     mismo ticker)   │                 ...                                  ║
║   │                     │                 Día N: [diferentes cada día]        ║
║   └─────────────────────┘                                                     ║
║                                                                                ║
║   El screener NO existe                   El SCREENER es PARTE de la          ║
║                                           estrategia y es OPTIMIZABLE         ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 1.2 El Insight Clave

> **"En small caps, el SCREENER es parte de la estrategia."**
>
> Los parámetros del screener (gap mínimo, float máximo, volumen premarket) son TAN OPTIMIZABLES como los parámetros de entrada y salida.

## 1.3 Modelo Mental Correcto

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         MODELO CONCEPTUAL TSIS.ai                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║                    ┌─────────────────────────────────────────────────┐        ║
║                    │                                                  │        ║
║   ┌──────────┐     │    ┌──────────────────┐    ┌────────────────┐  │        ║
║   │ SCREENER │────►│    │ Universo Diario  │───►│   ESTRATEGIA   │  │        ║
║   │ CONFIG   │     │    │ (tickers que     │    │   (Entry/Exit) │  │        ║
║   └──────────┘     │    │  cumplen filtros)│    └────────────────┘  │        ║
║        │           │    └──────────────────┘             │          │        ║
║        │           │             │                       │          │        ║
║        │           │             ▼                       ▼          │        ║
║        │           │    Para cada ticker ──────► Evaluar señales    │        ║
║        │           │                                     │          │        ║
║        │           │                                     ▼          │        ║
║        │           │                            Simular trades      │        ║
║        │           │                                     │          │        ║
║        │           └─────────────────────────────────────┼──────────┘        ║
║        │                                                 │                    ║
║        │              ES PARTE DE LA                     │                    ║
║        └──────────────► ESTRATEGIA ◄─────────────────────┘                    ║
║                                                                                ║
║                                     │                                          ║
║                                     ▼                                          ║
║                              ┌─────────────┐                                   ║
║                              │ RESULTADOS  │                                   ║
║                              │  AGREGADOS  │                                   ║
║                              └─────────────┘                                   ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 1.4 Implicaciones Prácticas

| Aspecto                  | TradeStation    | TSIS.ai                                     |
| ------------------------ | --------------- | ------------------------------------------- |
| Universo de backtest     | Fijo (1 ticker) | Dinámico (reconstruido cada día)          |
| Parámetros optimizables | Solo entry/exit | Screener + Entry + Exit                     |
| Survivorship bias        | Menor riesgo    | **CRÍTICO** - Incluir delisted       |
| Point-in-time data       | Importante      | **CRÍTICO** - Solo datos disponibles |
| Liquidez                 | Alta (futuros)  | Variable (validar ejecutabilidad)           |

---

# 2. INVENTARIO DE DATOS DISPONIBLES

## 2.1 Ubicación y Estructura

Todos los datos están en `C:\TSIS_Data\` en formato Parquet.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        ESTRUCTURA DE DATOS EN DISCO                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  C:\TSIS_Data\                                                                 ║
║  │                                                                             ║
║  ├── fundamentals/                      ◄─── 5,622 empresas                   ║
║  │   ├── balance_sheets/                     33 columnas por empresa          ║
║  │   ├── income_statements/                  30 columnas por empresa          ║
║  │   ├── cash_flow_statements/               Trimestral/Anual                 ║
║  │   └── smallcap_ratios/               ◄─── FLAGS DE RIESGO (crítico)       ║
║  │                                           • bankruptcy_risk_flag           ║
║  │                                           • dilution_risk_flag             ║
║  │                                           • high_leverage_flag             ║
║  │                                                                             ║
║  ├── ohlcv_intraday_1m/                 ◄─── DATOS INTRADAY 1 MINUTO         ║
║  │   ├── 2004_2018/                          (crítico para backtesting)       ║
║  │   └── 2019_2025/                                                           ║
║  │                                                                             ║
║  ├── quotes_p95_2004_2018/              ◄─── Quotes históricos (bid/ask)     ║
║  ├── quotes_p95_2019_2025/                                                    ║
║  │                                                                             ║
║  ├── additional/                                                               ║
║  │   ├── corporate_actions/             ◄─── Splits, cambios de ticker       ║
║  │   ├── ipos/                          ◄─── 5,247 IPOs                      ║
║  │   └── news/                          ◄─── Noticias por batch              ║
║  │                                                                             ║
║  ├── short_data/                                                               ║
║  │   ├── short_interest/                ◄─── % de float en short             ║
║  │   └── short_volume/                                                        ║
║  │                                                                             ║
║  └── regime_indicators/                 ◄─── Para filtrar por régimen        ║
║      ├── etfs/                               SPY, QQQ, IWM, VIX               ║
║      └── indices/                            NDX, SOX, COMP                   ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 2.2 Resumen de Datos Disponibles

| Dataset                    | Cantidad              | Rango Temporal | Uso Principal            |
| -------------------------- | --------------------- | -------------- | ------------------------ |
| Empresas con fundamentales | 5,622                 | Multi-anual    | Filtros fundamentales    |
| OHLCV Intraday 1 min       | Millones de registros | 2004-2025      | **Backtesting**    |
| Quotes (bid/ask)           | Millones              | 2004-2025      | Spread, slippage         |
| IPOs                       | 5,247                 | Histórico     | Detectar nuevas empresas |
| Noticias                   | 5,244+                | Reciente       | Catalizadores            |
| Short Interest             | Por ticker            | Histórico     | Short squeeze detection  |
| ETFs/Índices              | 35                    | 2003-2025      | Régimen de mercado      |

## 2.3 Campos Críticos: Smallcap Ratios

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMALLCAP RATIOS - 19 COLUMNAS                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Identificación:                                                 │
│  • ticker, fiscal_period, fiscal_year, end_date                 │
│                                                                  │
│  Liquidez:                                                       │
│  • current_ratio, quick_ratio, cash_ratio                       │
│                                                                  │
│  Burn Rate (crítico para small caps):                           │
│  • quarterly_burn_rate                                           │
│  • cash_runway_quarters  ◄── ¿Cuántos trimestres de vida?       │
│                                                                  │
│  Apalancamiento:                                                 │
│  • debt_to_equity, debt_to_assets                               │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              ⚠️  FLAGS DE RIESGO (ÚNICOS)  ⚠️              │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • bankruptcy_risk_flag    ◄── Riesgo de quiebra          │  │
│  │  • dilution_risk_flag      ◄── Riesgo de dilución         │  │
│  │  • high_leverage_flag      ◄── Alto apalancamiento        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Estos flags son VENTAJA COMPETITIVA vs Flash Research          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# 3. ANATOMÍA DE UN GAP EN SMALL CAPS

## 3.1 ¿Qué Es un Gap?

Un gap ocurre cuando el precio de apertura es significativamente diferente al cierre del día anterior.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          ANATOMÍA DE UN GAP UP                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Precio ($)                                                                    ║
║     │                                                                          ║
║  32 ┤                                              ╭────╮ HOD                  ║
║     │                                             ╱      ╲                     ║
║  28 ┤                                    ╭───────╯        ╲                    ║
║     │                                   ╱                   ╲                  ║
║  24 ┤                          PM High ╱                     ╲────────────     ║
║     │                              ╭──╯                                        ║
║  20 ┤                     OPEN ───╯  ◄─── GAP (+25%)                          ║
║     │           ═══════════════════════════════════════════                   ║
║  16 ┤   ────────╯  PREV CLOSE                                                 ║
║     │                                                                          ║
║     └────────────┬──────────────┬────────────────┬─────────────────────────   ║
║              Prev Day       Pre-Market      Market Open    Trading Day        ║
║                            4:00-9:30         9:30            9:30-16:00       ║
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                      MÉTRICAS DEL GAP                                    │  ║
║  ├─────────────────────────────────────────────────────────────────────────┤  ║
│  │  Gap % = (Open - Prev Close) / Prev Close × 100                         │  ║
║  │         = ($20 - $16) / $16 × 100 = +25%                                │  ║
║  │                                                                          │  ║
║  │  Return = (Current - Open) / Open × 100                                 │  ║
║  │  Change % = (Current - Prev Close) / Prev Close × 100                   │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 3.2 Niveles Clave de un Gap Day

| Nivel      | Descripción                          | Uso en Estrategias            |
| ---------- | ------------------------------------- | ----------------------------- |
| PREV CLOSE | Cierre del día anterior              | Referencia para Gap %         |
| PM LOW     | Mínimo del premarket                 | Soporte, Stop loss            |
| PM HIGH    | Máximo del premarket                 | Breakout target               |
| OPEN       | Precio de apertura (9:30)             | Gap & Go, Red to Green        |
| VWAP       | Precio promedio ponderado por volumen | Soporte/Resistencia dinámico |
| HOD        | High of Day                           | Breakout, Profit target       |
| LOD        | Low of Day                            | Stop loss, Support            |

## 3.3 Estrategias Principales

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                 ESTRATEGIAS IMPLEMENTADAS EN TSIS.ai                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                         ESTRATEGIAS LONG                                 │  ║
║  ├─────────────────────────────────────────────────────────────────────────┤  ║
║  │                                                                          │  ║
║  │  BREAKOUT PM HIGH                    GAP AND GO                         │  ║
║  │  ══════════════════                  ═══════════                        │  ║
║  │  Entrada: Ruptura del               Entrada: Primera hora,              │  ║
║  │  máximo de premarket                gap >15%, sin sobreextensión        │  ║
║  │  con confirmación (+5%)             consolidación bajo PM High          │  ║
║  │                                                                          │  ║
║  │  VWAP BOUNCE                         RED TO GREEN                       │  ║
║  │  ═══════════                         ════════════                       │  ║
║  │  Entrada: Primer dip a VWAP         Entrada: Rompe open después        │  ║
║  │  en acción con volumen alto         de estar rojo                       │  ║
║  │                                                                          │  ║
║  │  VWAP RECLAIM                        FIRST PULLBACK                     │  ║
║  │  ═══════════                         ══════════════                     │  ║
║  │  Entrada: Recupera VWAP             Entrada: Primer retroceso          │  ║
║  │  con volumen                        en runner activo                    │  ║
║  │                                                                          │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                         ESTRATEGIAS SHORT                                │  ║
║  ├─────────────────────────────────────────────────────────────────────────┤  ║
║  │                                                                          │  ║
║  │  GREEN TO RED                        GAP AND CRAP                       │  ║
║  │  ════════════                        ════════════                       │  ║
║  │  Entrada: Rompe open hacia           Entrada: Sobreextensión en PM,    │  ║
║  │  abajo después de estar verde        dilución, resistencia arriba       │  ║
║  │                                                                          │  ║
║  │  VWAP REJECTION                      LATE DAY FADE                      │  ║
║  │  ══════════════                      ═════════════                      │  ║
║  │  Entrada: Rechaza VWAP               Entrada: Última hora y media,     │  ║
║  │  con poco volumen                    rompe niveles clave               │  ║
║  │                                                                          │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

# 4. ARQUITECTURA CONCEPTUAL DEL MOTOR

## 4.1 Vista de Alto Nivel (4 Capas)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ARQUITECTURA DEL MOTOR DE BACKTESTING                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                         CAPA 0: DATOS CRUDOS                             │  ║
║  │                         (C:\TSIS_Data\)                                  │  ║
║  │  Parquet files: OHLCV, Quotes, Fundamentales, News, Short Data          │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                         ║
║                                      ▼ ETL (una vez)                          ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                    CAPA 1: GAP UNIVERSE PRE-COMPUTADO                    │  ║
║  │                    (PostgreSQL/TimescaleDB)                              │  ║
║  │                                                                          │  ║
║  │  Tabla: historical_gaps                                                  │  ║
║  │  - Todos los gaps desde 2004-2025 (~500,000+ registros)                 │  ║
║  │  - Point-in-time data (solo lo disponible en ese momento)               │  ║
║  │  - Incluye tickers DELISTED (evitar survivorship bias)                  │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                         ║
║                                      ▼ Query con filtros                      ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                    CAPA 2: SCREENER ENGINE                               │  ║
║  │                                                                          │  ║
║  │  Input: Configuración del usuario (gap%, float, volume, etc.)           │  ║
║  │  Output: Universo diario filtrado                                        │  ║
║  │  Día 1: [AAPL, TSLA] | Día 2: [AMD, NVDA] | Día 3: [BBBY, AMC]         │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                         ║
║                                      ▼ Para cada ticker/día                   ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                    CAPA 3: STRATEGY EXECUTOR                             │  ║
║  │                                                                          │  ║
║  │  1. Cargar datos intraday (OHLCV 1 min)                                 │  ║
║  │  2. Calcular indicadores (VWAP, HOD, LOD, etc.)                         │  ║
║  │  3. Evaluar condiciones de ENTRADA                                       │  ║
║  │  4. Si hay señal → Simular ejecución                                    │  ║
║  │  5. Evaluar condiciones de SALIDA                                        │  ║
║  │  6. Calcular P&L con costos realistas                                   │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                         ║
║                                      ▼ Agregar resultados                     ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                    CAPA 4: METRICS & VALIDATION                          │  ║
║  │                                                                          │  ║
║  │  Métricas estándar:                 Métricas científicas:               │  ║
║  │  • Total Return, Sharpe Ratio       • Deflated Sharpe Ratio (DSR)       │  ║
║  │  • Profit Factor, Max Drawdown      • Probability of Overfitting (PBO)  │  ║
║  │  • Win Rate                         • Walk-Forward Efficiency           │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 4.2 Flujo de Datos del Backtest

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         FLUJO DE DATOS DEL BACKTEST                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Usuario configura estrategia en Wizard                                       ║
║                    │                                                           ║
║                    ▼                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │  PASO 1: Filtrar Universo                                                │  ║
║  │  Query historical_gaps con filtros del screener                          │  ║
║  │  Resultado: 45,230 gaps en 1,826 días                                    │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                    │                                                           ║
║                    ▼                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │  PASO 2: Para Cada Día                                                   │  ║
║  │                                                                          │  ║
║  │  Día 2020-03-15: [PLUG, NIO, WKHS]                                      │  ║
║  │       │                                                                  │  ║
║  │       ├── PLUG: Cargar OHLCV → Calcular VWAP → Evaluar Entry → Trade?  │  ║
║  │       ├── NIO:  Cargar OHLCV → Calcular VWAP → Evaluar Entry → Trade?  │  ║
║  │       └── WKHS: Cargar OHLCV → Calcular VWAP → Evaluar Entry → Trade?  │  ║
║  │                                                                          │  ║
║  │  Si hay señal válida → Simular Trade → Calcular P&L                     │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                    │                                                           ║
║                    ▼                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │  PASO 3: Calcular Métricas Agregadas                                     │  ║
║  │                                                                          │  ║
║  │  Total trades: 2,847  |  Win rate: 58.3%  |  Profit factor: 1.87        │  ║
║  │  Total return: +127.4%  |  Max drawdown: -18.2%  |  Sharpe: 1.42        │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

# 5. EL UNIVERSO DINÁMICO: TABLA DE GAPS HISTÓRICOS

## 5.1 Por Qué Pre-Computar

Calcular todos los gaps en tiempo real durante cada backtest sería extremadamente lento. Pre-computamos una tabla con **TODOS** los gaps históricos.

## 5.2 Estructura de la Tabla historical_gaps

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ESTRUCTURA: TABLA historical_gaps                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  IDENTIFICADORES                                                               ║
║  • date (DATE)         → Fecha del gap                                        ║
║  • ticker (VARCHAR)    → Símbolo de la acción                                 ║
║                                                                                ║
║  MÉTRICAS DEL GAP (disponibles a las 9:30)                                    ║
║  • gap_pct             → % del gap vs prev close                              ║
║  • prev_close          → Cierre del día anterior                              ║
║  • open_price          → Precio de apertura                                   ║
║                                                                                ║
║  DATOS PREMARKET (disponibles antes de 9:30)                                  ║
║  • pm_high, pm_low     → Rango del premarket                                  ║
║  • pm_volume           → Volumen del premarket                                ║
║  • pm_vwap             → VWAP del premarket                                   ║
║                                                                                ║
║  CARACTERÍSTICAS DEL TICKER (POINT-IN-TIME) ⚠️                                ║
║  • float_shares        → Float EN ESE MOMENTO                                 ║
║  • market_cap          → Market cap EN ESE MOMENTO                            ║
║  • avg_volume_20d      → Volumen promedio 20 días                             ║
║  • short_interest_pct  → % de float en short                                  ║
║                                                                                ║
║  CATALIZADOR                                                                   ║
║  • has_news            → ¿Había noticia ese día?                              ║
║  • catalyst_type       → 'earnings', 'fda', 'contract', 'offering'...         ║
║                                                                                ║
║  MÉTRICAS DEL DÍA (para análisis, NO para señales de entrada)                 ║
║  • day_high, day_low, day_close, day_volume                                   ║
║  • hod_time            → Hora del high of day                                 ║
║  ⚠️ Estos datos se usan para análisis POSTERIOR, nunca para señales          ║
║                                                                                ║
║  STATUS DEL TICKER (CRÍTICO PARA SURVIVORSHIP BIAS)                           ║
║  • ticker_status       → 'active', 'delisted', 'bankrupt', 'merged'           ║
║  • delisting_date      → Fecha de delisting (si aplica)                       ║
║  ⚠️ NUNCA filtrar por status='active' en backtests                            ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 5.3 Proceso de Construcción (ETL)

| Etapa | Descripción                        | Fuente                                 |
| ----- | ----------------------------------- | -------------------------------------- |
| 1     | Extraer OHLCV, calcular gaps        | ohlcv_intraday_1m                      |
| 2     | Añadir datos premarket             | ohlcv (4:00-9:30)                      |
| 3     | Añadir fundamentales point-in-time | fundamentals (filing_date <= gap_date) |
| 4     | Añadir catalizadores               | news (published < 9:30)                |
| 5     | Añadir métricas del día          | ohlcv (9:30-16:00)                     |
| 6     | Añadir status del ticker           | corporate_actions                      |

---

# 6. EXPERIENCIA DEL USUARIO: EL WIZARD DE 6 PASOS

## 6.1 Visión General

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         WIZARD DE BACKTESTING - 6 PASOS                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐              ║
║  │  1  │───►│  2  │───►│  3  │───►│  4  │───►│  5  │───►│  6  │              ║
║  │SCRN │    │ENTRY│    │EXIT │    │DATE │    │SIZE │    │ RUN │              ║
║  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘    └─────┘              ║
║                                                                                ║
║  Screener   Entry      Exit       Date       Sizing     Run &                 ║
║  Filters    Rules      Rules      Range      & Costs    Validate              ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 6.2 PASO 1: Screener Configuration

**Lo que configura el usuario:**

| Sección         | Parámetros                                   |
| ---------------- | --------------------------------------------- |
| Gap Filters      | Gap % min/max, Gap direction                  |
| Stock Filters    | Float min/max, Market cap max, Price min/max  |
| Volume Filters   | PM Volume min, Relative volume min            |
| Catalyst Filters | Require catalyst, Types (earnings, FDA, etc.) |
| Exclusions       | Exclude ADRs, ETFs, OTC                       |
| Survivorship     | Include delisted (SIEMPRE recomendado)        |

**Preview en tiempo real:**

- Número de gaps que cumplen los filtros
- Número de días de trading
- Número de tickers únicos
- % de tickers ahora delisted

## 6.3 PASO 2: Entry Configuration

**Entry Types disponibles:**

- Breakout PM High
- VWAP Bounce
- VWAP Reclaim
- Red to Green
- First Pullback
- Opening Range Breakout

**Entry Conditions Builder:**

- Groups (AND logic between groups)
- Conditions (OR logic within group)
- Properties: Price, VWAP, Open, HOD, LOD, PM High, PM Low, Volume, Time
- Operators: >, <, =, crosses above, crosses below

**Time Window:**

- Start time (ej: 09:30)
- End time (ej: 11:30)

## 6.4 PASO 3: Exit Configuration

**Profit Target:**

- Enable/disable
- Reference price: Entry, Open, VWAP, HOD, PM High
- Offset: +X%
- Partial exit: X% at +Y%

**Stop Loss:**

- Enable/disable
- Reference price: Entry, Open, VWAP, LOD, PM Low
- Offset: -X%
- Trailing stop: Trail by X%, activate at +Y%

**Time-Based Exit:**

- Time stop (ej: 15:45)
- Max hold time (ej: 120 minutos)

## 6.5 PASO 4: Date Range & Validation

**Date Range:**

- Start/End date
- Quick select: Last year, Last 3 years, Last 5 years, All data

**Market Regime Filters:**

- Bull market, Bear market, Neutral, High volatility
- Include 2008 Crisis, 2020 COVID, 2022 Bear Market

**Walk-Forward Settings:**

- Enable Walk-Forward Analysis
- Number of runs (10 recomendado)
- OOS % (20% típico)
- Type: Rolling o Anchored

## 6.6 PASO 5: Sizing & Costs

**Capital:**

- Starting capital

**Position Sizing:**

- Method: Fixed risk, Fixed dollar, Fixed shares, Kelly
- Risk per trade %
- Max position %
- Max shares

**Transaction Costs:**

- Commission per share
- Spread estimate %
- Slippage estimate %
- SEC fee, TAF fee

**Costo típico small caps:** ~0.50% round trip

## 6.7 PASO 6: Review & Run

**Resumen de configuración completa**

**Acciones disponibles:**

- Save Strategy
- Run Backtest
- Run Optimization
- Run Walk-Forward
- Run Cluster Analysis

---

# 7. MOTOR DE EJECUCIÓN DE ESTRATEGIAS

## 7.1 Proceso de Simulación de un Trade

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PROCESO DE SIMULACIÓN DE UN TRADE                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  FASE 1: CARGAR DATOS                                                         ║
║  ════════════════════                                                         ║
║  • Cargar OHLCV intraday 1-min del ticker para la fecha                       ║
║  • 390 barras (9:30 - 16:00)                                                  ║
║  • Calcular VWAP running, tracking de HOD, LOD                                ║
║                                                                                ║
║  FASE 2: BUSCAR SEÑAL DE ENTRADA                                              ║
║  ═══════════════════════════════                                              ║
║  Para cada barra en la ventana de entrada (ej: 09:30-11:30):                  ║
║  • Evaluar condiciones de entrada                                              ║
║  • Si TODAS las condiciones se cumplen → SEÑAL VÁLIDA                         ║
║                                                                                ║
║  FASE 3: CALCULAR POSITION SIZE                                               ║
║  ══════════════════════════════                                               ║
║  Ejemplo Fixed Risk:                                                          ║
║  • Capital: $100,000, Risk: 1%, Stop: 5%                                      ║
║  • Risk per trade: $1,000                                                     ║
║  • Entry price: $5.20, Stop price: $4.94                                      ║
║  • Risk per share: $0.26                                                      ║
║  • Shares = $1,000 / $0.26 = 3,846 shares                                     ║
║                                                                                ║
║  FASE 4: SIMULAR EJECUCIÓN DE ENTRADA                                         ║
║  ═══════════════════════════════════                                          ║
║  • Limit order: buscar si precio toca el límite                               ║
║  • Aplicar slippage                                                            ║
║  • Registrar entry price, time, shares                                        ║
║                                                                                ║
║  FASE 5: MONITOREAR Y BUSCAR SALIDA                                           ║
║  ═══════════════════════════════════                                          ║
║  Para cada barra después de la entrada:                                       ║
║  • ¿Tocó stop loss? → EXIT                                                    ║
║  • ¿Tocó profit target? → EXIT (o partial)                                    ║
║  • ¿Activar trailing? → Ajustar stop                                          ║
║  • ¿Time stop? → EXIT                                                         ║
║                                                                                ║
║  FASE 6: CALCULAR P&L                                                         ║
║  ════════════════════                                                         ║
║  • Gross P&L = (Exit - Entry) × Shares                                        ║
║  • Costs = Spread + Slippage + SEC + TAF                                      ║
║  • Net P&L = Gross - Costs                                                    ║
║  • R-Multiple = Net P&L / Initial Risk                                        ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 7.2 Costos Realistas para Small Caps

| Costo                      | Valor Típico    | Descripción                  |
| -------------------------- | ---------------- | ----------------------------- |
| Commission                 | $0.00            | La mayoría de brokers gratis |
| Spread                     | 0.30%            | Mayor que large caps          |
| Slippage                   | 0.20%            | Por falta de liquidez         |
| SEC Fee                    | 0.00278%         | Solo en ventas                |
| TAF Fee                    | $0.000166/share  | Muy pequeño                  |
| **Total round trip** | **~0.50%** | Por trade                     |

---

# 8. SISTEMA DE OPTIMIZACIÓN MULTI-PARÁMETRO

## 8.1 ¿Qué Es la Optimización?

Busca los mejores valores para los parámetros:

- **Parámetros del Screener**: Gap mínimo, float máximo, volumen
- **Parámetros de Entry**: Hora de entrada, confirmación %
- **Parámetros de Exit**: Profit target %, stop loss %

## 8.2 Exhaustive Search (Grid Search)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         EXHAUSTIVE SEARCH (GRID SEARCH)                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Prueba TODAS las combinaciones posibles                                      ║
║                                                                                ║
║  Ejemplo: 2 parámetros                                                        ║
║  • Gap mínimo = [10%, 20%, 30%, 40%, 50%]    → 5 valores                     ║
║  • Float máximo = [5M, 10M, 15M, 20M]        → 4 valores                     ║
║  • Total combinaciones: 5 × 4 = 20 backtests                                  ║
║                                                                                ║
║         Float ▲                                                                ║
║          20M  │  ○      ○      ●      ○      ○                                ║
║          15M  │  ○      ●      ●      ●      ○                                ║
║          10M  │  ○      ●      ★      ●      ○      ★ = Mejor resultado       ║
║           5M  │  ○      ○      ●      ○      ○      ● = Buenos resultados    ║
║               └──────┬──────┬──────┬──────┬──────▶ Gap%                       ║
║                     10%    20%    30%    40%    50%                            ║
║                                                                                ║
║  VENTAJAS:                              DESVENTAJAS:                          ║
║  ✓ Garantiza encontrar el óptimo        ✗ Tiempo crece exponencialmente      ║
║  ✓ Resultados reproducibles             ✗ 6 params × 10 valores = 1,000,000  ║
║                                                                                ║
║  RECOMENDACIÓN: Usar cuando total combinaciones < 10,000                      ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 8.3 Genetic Optimization

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          GENETIC OPTIMIZATION                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Usa algoritmos evolutivos (inspirado en evolución natural)                   ║
║                                                                                ║
║  GENERACIÓN 1: Población inicial aleatoria (100 individuos)                   ║
║       │                                                                        ║
║       ▼ Selección (los mejores sobreviven)                                    ║
║       │                                                                        ║
║       ▼ Crossover (combinan genes)                                            ║
║       │                                                                        ║
║       ▼ Mutación (pequeños cambios aleatorios)                                ║
║       │                                                                        ║
║  GENERACIÓN 2: Nueva población (hijos de los mejores)                         ║
║       │                                                                        ║
║       ▼ Repetir por N generaciones                                            ║
║       │                                                                        ║
║  GENERACIÓN 50: Mejor individuo encontrado                                    ║
║                                                                                ║
║  VENTAJAS:                              DESVENTAJAS:                          ║
║  ✓ Mucho más rápido                     ✗ No garantiza el óptimo global      ║
║  ✓ Escala bien con muchos parámetros    ✗ Resultados pueden variar           ║
║                                                                                ║
║  RECOMENDACIÓN: Usar cuando total combinaciones > 10,000                      ║
║                 Population: 100, Generations: 50                              ║
║                 Guardar random seed para reproducibilidad                     ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 8.4 Fitness Functions

| Función               | Cuándo Usar                                   |
| ---------------------- | ---------------------------------------------- |
| Net Profit             | Simple, pero puede sobreajustar                |
| **Sharpe Ratio** | **RECOMENDADO** - Balance riesgo/retorno |
| Profit Factor          | Estrategias con alto win rate                  |
| Calmar Ratio           | Cuando drawdown es prioritario                 |
| Custom Combined        | Múltiples objetivos                           |

⚠️ **IMPORTANTE**: Siempre incluir slippage y comisiones DURANTE la optimización.

---

# 9. WALK-FORWARD ANALYSIS (WFA)

## 9.1 El Problema del Overfitting

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          EL PROBLEMA DEL OVERFITTING                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  IN-SAMPLE (2010-2020)                    OUT-OF-SAMPLE (2021-2024)           ║
║  Sharpe: 2.5, Return: +340%               Sharpe: 0.3, Return: -15%           ║
║                                                                                ║
║  Equity                                   Equity                               ║
║    ▲           ╱                            ▲                                  ║
║    │         ╱                              │  ────────                        ║
║    │       ╱                                │          ╲                       ║
║    │     ╱                                  │           ╲                      ║
║    │   ╱                                    │            ╲────                 ║
║    │ ╱                                      │                                  ║
║    └────────────▶                           └────────────▶                    ║
║                                                                                ║
║  "¡Funciona increíble!"                   "¿Qué pasó?"                        ║
║                                                                                ║
║  ESTO ES OVERFITTING: La estrategia se ajustó a patrones específicos del     ║
║  pasado que NO se repiten en el futuro.                                       ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 9.2 Cómo Funciona Walk-Forward Analysis

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     WALK-FORWARD ANALYSIS - ROLLING                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Datos totales: 2015 ────────────────────────────────────────── 2024          ║
║                                                                                ║
║  Run 1: [████████ IN-SAMPLE (80%) ████████][▓▓ OOS (20%) ▓▓]                  ║
║         │         2015-2016               ││    2017      │                    ║
║                                                                                ║
║  Run 2:       [████████ IN-SAMPLE ████████][▓▓ OOS ▓▓]                        ║
║               │         2016-2017         ││   2018  │                         ║
║                                                                                ║
║  Run 3:             [████████ IN-SAMPLE ████████][▓▓ OOS ▓▓]                  ║
║                     │         2017-2018         ││   2019  │                   ║
║  ...                                                                           ║
║                                                                                ║
║  EQUITY WALK-FORWARD (concatenación de todos los OOS):                        ║
║  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]         ║
║   2017    2018    2019    2020    2021    2022    2023    2024                ║
║                                                                                ║
║  ^ Esta curva representa cómo hubiera funcionado la estrategia                ║
║    si hubieras re-optimizado periódicamente                                   ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 9.3 Walk-Forward Efficiency (WFE)

```
                  Average OOS Performance
  WFE  =  ─────────────────────────────────  ×  100%
                  Average IS Performance

  INTERPRETACIÓN:
  ───────────────
  WFE > 100%    │  OOS mejor que IS (raro, posible suerte)
  WFE 70-100%   │  EXCELENTE - Muy robusta
  WFE 50-70%    │  ACEPTABLE - Robusta
  WFE < 50%     │  ⚠️ POSIBLE OVERFITTING
```

## 9.4 Criterios de PASS/FAIL (TradeStation)

Para PASAR el Walk-Forward Analysis:

- [✓] Profitable overall (P&L positivo en OOS concatenado)
- [✓] Walk-Forward Efficiency >= 50%
- [✓] Maximum Drawdown < 40%

Si FALLA cualquiera → La estrategia NO es apta para trading real

## 9.5 Tipos de Walk-Forward

| Tipo               | Descripción                      | Cuándo Usar                            |
| ------------------ | --------------------------------- | --------------------------------------- |
| **Rolling**  | Ventana IS "rueda" (tamaño fijo) | Cuando el mercado cambia frecuentemente |
| **Anchored** | IS siempre desde inicio, crece    | Cuando quieres dar peso a históricos   |

---

# 10. CLUSTER ANALYSIS Y MAPAS DE ESTABILIDAD 3D

## 10.1 Cluster Analysis

Ejecuta MÚLTIPLES Walk-Forward Analysis con diferentes configuraciones para encontrar la más robusta.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                            CLUSTER ANALYSIS                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Variables a probar:                                                          ║
║  • Número de runs: 5, 10, 15, 20, 25                                          ║
║  • % Out-of-Sample: 10%, 15%, 20%, 25%, 30%                                   ║
║                                                                                ║
║  Total combinaciones: 5 × 5 = 25 Walk-Forward Analysis                        ║
║                                                                                ║
║              MATRIZ DE CLUSTER (Walk-Forward Efficiency)                      ║
║                                                                                ║
║       OOS%     10%    15%    20%    25%    30%                                ║
║      Runs  ┌──────┬──────┬──────┬──────┬──────┐                               ║
║        5   │  52% │  48% │  45% │  42% │  38% │                               ║
║       10   │  58% │  62% │  65% │  61% │  55% │                               ║
║       15   │  55% │  68% │ ★72% │  69% │  60% │   ★ = ÓPTIMO                 ║
║       20   │  51% │  65% │  70% │  67% │  58% │                               ║
║       25   │  48% │  60% │  64% │  62% │  54% │                               ║
║            └──────┴──────┴──────┴──────┴──────┘                               ║
║                                                                                ║
║  El óptimo está en Runs=15, OOS=20% con WFE=72%                               ║
║  HAY UNA "MESETA" de buenos resultados → ROBUSTEZ                             ║
║                                                                                ║
║  ⚠️ Si ves un "pico" aislado = probable OVERFITTING                          ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 10.2 Mapa de Estabilidad 3D de Parámetros

Visualiza cómo el performance varía con cambios en los parámetros de la ESTRATEGIA.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     MAPA DE ESTABILIDAD 3D DE PARÁMETROS                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Eje X: Gap mínimo (10% - 50%)                                                ║
║  Eje Y: Float máximo (5M - 20M)                                               ║
║  Eje Z: Sharpe Ratio                                                          ║
║                                                                                ║
║     Sharpe ▲                                                                   ║
║        2.0 ┤            ╭───────╮                                              ║
║            │           ╱  ★     ╲    ★ = Punto óptimo                         ║
║        1.5 ┤    ╭─────╯          ╲                                             ║
║            │   ╱   "MESETA"       ╲                                            ║
║        1.0 ┤  ╱   (zona estable)   ╲────╮                                      ║
║            │ ╱                           ╲                                     ║
║        0.5 ┼────────────────────────────────▶ Gap%                            ║
║                                                                                ║
║  SUPERFICIE BUENA (ROBUSTA):         SUPERFICIE MALA (FRÁGIL):                ║
║                                                                                ║
║      ╭───────────╮                         ╱╲                                  ║
║     ╱   Meseta    ╲                       ╱  ╲  ← Pico aislado                ║
║    ╱    suave      ╲                     ╱    ╲                                 ║
║                                                                                ║
║  = Pequeños cambios NO               = Pequeños cambios causan                ║
║    afectan mucho el resultado          grandes cambios = OVERFITTING          ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Lo que ve el usuario:**

- Gráfico 3D interactivo (Plotly.js)
- Puede rotar, zoom, ver desde diferentes ángulos
- Score de estabilidad: 0-100%
- Advertencias si detecta picos aislados

---

# 11. SENSITIVITY ANALYSIS

Muestra cómo cada parámetro individual afecta el performance.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           SENSITIVITY ANALYSIS                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  PARÁMETRO: Gap Mínimo (Sensibilidad BAJA ✓)                                  ║
║  ═══════════════════════════════════════════                                  ║
║                                                                                ║
║  Sharpe ▲                                                                      ║
║     2.0 ┤               ●     ★                                               ║
║         │         ●           ●     ●                                         ║
║     1.5 ┤    ●                      ●                                         ║
║         │●                               ●                                    ║
║     1.0 └────┬────┬────┬────┬────┬────┬────▶ Gap%                             ║
║            10%  15%  20%  25%  30%  35%  40%                                   ║
║                                                                                ║
║  Curva suave = Cambios pequeños no afectan mucho                              ║
║                                                                                ║
║  ────────────────────────────────────────────────────────────────────────     ║
║                                                                                ║
║  PARÁMETRO: Profit Target (Sensibilidad ALTA ⚠️)                              ║
║  ═══════════════════════════════════════════════                              ║
║                                                                                ║
║  Sharpe ▲                                                                      ║
║     2.0 ┤                      ★                                              ║
║         │                    ●                                                ║
║     1.5 ┤           ●                     ●                                   ║
║         │      ●                              ●                               ║
║     1.0 ┤ ●                                        ●                          ║
║         │●                                              ●                     ║
║     0.5 └────┬────┬────┬────┬────┬────┬────┬────▶ Target%                    ║
║             5%   7%  10%  12%  15%  17%  20%  22%                              ║
║                                                                                ║
║  Solo funciona bien entre 12-17% = Posible overfitting                        ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

  INTERPRETACIÓN DE SENSIBILIDAD:
  ───────────────────────────────
  Score < 10%   │  Muy estable - bajo riesgo de overfitting
  Score 10-20%  │  Estable - aceptable
  Score 20-30%  │  Moderado - monitorear de cerca
  Score > 30%   │  ALTO - riesgo de overfitting
```

---

# 12. VALIDACIÓN CIENTÍFICA ANTI-OVERFITTING

## 12.1 Deflated Sharpe Ratio (DSR)

**Problema**: Si pruebas 1,000 estrategias, ALGUNAS tendrán buen Sharpe solo por AZAR.

**Solución**: Ajustar el Sharpe por el número de estrategias probadas.

```
                    Sharpe observado - E[max(Sharpe bajo H0)]
  DSR  =  ───────────────────────────────────────────────────
                         σ[max(Sharpe)]

  INTERPRETACIÓN:
  • DSR > 1.96 → Significativo al 95% (bueno)
  • DSR > 2.58 → Significativo al 99% (muy bueno)
  • DSR < 1.64 → NO significativo (posible suerte)
```

## 12.2 Probability of Backtest Overfitting (PBO)

**Pregunta**: ¿Cuál es la probabilidad de que la "mejor" estrategia sea en realidad la mejor, y no solo parezca buena por overfitting?

```
  INTERPRETACIÓN:
  • PBO < 0.10 → Excelente (muy baja probabilidad de overfit)
  • PBO 0.10-0.30 → Bueno
  • PBO 0.30-0.50 → Moderado (precaución)
  • PBO > 0.50 → ALTO RIESGO de overfitting
```

## 12.3 Ventaja Competitiva vs TradeStation

| Funcionalidad               | TradeStation | TSIS.ai             |
| --------------------------- | ------------ | ------------------- |
| Walk-Forward Analysis       | ✓           | ✓                  |
| Cluster Analysis            | ✓           | ✓                  |
| Sensitivity Analysis        | ✓           | ✓                  |
| Deflated Sharpe Ratio       | ✗           | **✓ ÚNICO** |
| Probability of Overfitting  | ✗           | **✓ ÚNICO** |
| Audit Trail de todos trials | ✗           | **✓ ÚNICO** |
| Paquete de replicación     | ✗           | **✓ ÚNICO** |

## 12.4 Certificado de Validación

Lo que ve el usuario al finalizar un backtest validado:

```
╔══════════════════════════════════════════════════════════════════╗
║          TSIS.ai VALIDATION CERTIFICATE                           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Certificate ID: TSIS-VAL-2026-0123456                           ║
║  Strategy: "VWAP Reclaim - Low Float Gappers"                    ║
║  Period: 2020-01-01 to 2024-12-31 (5 years)                      ║
║                                                                   ║
║  VALIDATION RESULTS                         OVERALL: PASS ✓      ║
║  ────────────────────────────────────────────────────────────    ║
║                                                                   ║
║  Data Integrity                                                   ║
║  [✓] Survivorship coverage: 14.2% delisted included              ║
║  [✓] Point-in-time data verified                                 ║
║                                                                   ║
║  Statistical Validation                                           ║
║  [✓] Deflated Sharpe Ratio: 2.14 (p < 0.05)                     ║
║  [✓] Probability of Overfitting: 0.18 (LOW)                     ║
║  [✓] Walk-Forward Efficiency: 68% (>50%)                        ║
║                                                                   ║
║  Robustness                                                       ║
║  [✓] Parameter stability score: 0.82/1.00                       ║
║  [✓] Max drawdown: 18.2% (<40%)                                 ║
║                                                                   ║
║  [ Download Certificate PDF ]  [ Download Replication Package ]  ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 13. RESULTADOS Y VISUALIZACIONES

## 13.1 Pantalla de Resultados

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         BACKTEST RESULTS                                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Strategy: VWAP Reclaim - Low Float Gappers                                   ║
║  Period: 2020-01-01 to 2024-12-31 | Duration: 5 years                         ║
║                                                                                ║
║  [Overview] [Equity Curve] [Trades] [Calendar] [Monthly] [Validation]         ║
║                                                                                ║
║  ┌────────────────────────────┐  ┌────────────────────────────────────────┐  ║
║  │  GENERAL METRICS           │  │  TRADE METRICS                         │  ║
║  │                            │  │                                        │  ║
║  │  Starting Balance:         │  │  Total Trades:    2,847               │  ║
║  │  $100,000                  │  │  Win Rate:        58.3%               │  ║
║  │                            │  │  Avg Win:         +$412               │  ║
║  │  Ending Balance:           │  │  Avg Loss:        -$289               │  ║
║  │  $227,400  (+127.4%)       │  │  Profit Factor:   1.87                │  ║
║  │                            │  │  R:R Ratio:       1.43:1              │  ║
║  │  Max Drawdown:             │  │                                        │  ║
║  │  -$18,200  (-18.2%)        │  │                                        │  ║
║  │                            │  │                                        │  ║
║  │  Sharpe Ratio: 1.42        │  │                                        │  ║
║  └────────────────────────────┘  └────────────────────────────────────────┘  ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 13.2 Visualizaciones Disponibles

| Tab                    | Contenido                                  |
| ---------------------- | ------------------------------------------ |
| **Overview**     | Métricas generales, winning/losing trades |
| **Equity Curve** | Gráfico de balance + drawdown             |
| **Trades**       | Tabla con todos los trades (paginated)     |
| **Calendar**     | P&L por día en formato calendario         |
| **Monthly**      | Tabla de retornos mensuales por año       |
| **Validation**   | DSR, PBO, WFE, Certificado                 |

## 13.3 Exports Disponibles

| Formato         | Contenido                                                               |
| --------------- | ----------------------------------------------------------------------- |
| **Excel** | Summary, Trades, Daily Returns, Monthly, Equity, Parameters, Validation |
| **CSV**   | Trades individuales                                                     |
| **PDF**   | Certificado de validación                                              |
| **ZIP**   | Paquete de replicación completo                                        |

---

# 14. PLAN DE TESTS POR ETAPA DE INGENIERÍA

## 14.1 Filosofía

**Cada etapa debe pasar TODOS sus tests antes de avanzar a la siguiente.**

## 14.2 ETAPA 1: ETL y Base de Datos

| Test                   | Descripción                               | Criterio                |
| ---------------------- | ------------------------------------------ | ----------------------- |
| test_parquet_reader    | Lee archivos OHLCV de C:\TSIS_Data         | Carga sin errores       |
| test_gap_calculation   | gap = (open - prev_close) / prev_close     | Precisión 0.01%        |
| test_point_in_time     | Solo usa datos con filing_date <= gap_date | No look-ahead           |
| test_premarket_data    | pm_high, pm_low, pm_volume                 | Calculados de 4:00-9:30 |
| test_delisted_included | Tickers delisted en la tabla               | >= 10% delisted         |

**Criterios de Aceptación:**

- [✓] Tabla historical_gaps > 400,000 registros
- [✓] Cubre período 2004-2025
- [✓] Queries de screener < 500ms

## 14.3 ETAPA 2: Screener Engine

| Test                    | Descripción                    |
| ----------------------- | ------------------------------- |
| test_gap_filter_min_max | Gap entre min y max             |
| test_float_filter       | Float <= max                    |
| test_catalyst_filter    | Solo gaps con catalizador       |
| test_survivorship_off   | Incluye delisted                |
| test_combined_filters   | Múltiples filtros simultáneos |

**Criterios de Aceptación:**

- [✓] Todos los filtros funcionan correctamente
- [✓] Performance < 2 segundos

## 14.4 ETAPA 3: Strategy Executor

| Test                    | Descripción                      |
| ----------------------- | --------------------------------- |
| test_vwap_calculation   | VWAP = Σ(price × vol) / Σ(vol) |
| test_entry_signals      | Cada tipo de entrada              |
| test_entry_time_window  | Solo señales en ventana          |
| test_position_sizing    | Fixed risk cálculo correcto      |
| test_exit_profit_target | Exit en target                    |
| test_exit_stop_loss     | Exit en stop                      |
| test_exit_trailing      | Trailing se ajusta correctamente  |
| test_cost_calculation   | Spread + slippage + fees          |
| test_no_look_ahead_bias | Solo datos disponibles            |

**Criterios de Aceptación:**

- [✓] Todas las estrategias de entrada funcionan
- [✓] Todas las estrategias de salida funcionan
- [✓] No hay look-ahead bias

## 14.5 ETAPA 4: Metrics Engine

| Test               | Descripción                   |
| ------------------ | ------------------------------ |
| test_total_return  | (ending - starting) / starting |
| test_win_rate      | winning / total × 100         |
| test_profit_factor | gross_profit / gross_loss      |
| test_sharpe_ratio  | avg_return / std_dev           |
| test_max_drawdown  | Max caída desde pico          |

## 14.6 ETAPA 5: Optimization Engine

| Test                             | Descripción                 |
| -------------------------------- | ---------------------------- |
| test_exhaustive_all_combinations | Prueba todas                 |
| test_genetic_bounds              | Dentro de rangos             |
| test_genetic_improves            | Mejora por generación       |
| test_all_trials_saved            | Audit trail completo         |
| test_reproducibility             | Mismo seed = mismo resultado |

## 14.7 ETAPA 6: Walk-Forward Analysis

| Test                        | Descripción             |
| --------------------------- | ------------------------ |
| test_rolling_window_splits  | Ventanas correctas       |
| test_anchored_window_splits | IS desde inicio          |
| test_wfe_calculation        | WFE = avg(OOS) / avg(IS) |
| test_pass_fail_criteria     | Criterios TradeStation   |
| test_cluster_analysis       | Matriz de resultados     |

## 14.8 ETAPA 7: Validación Científica

| Test                        | Descripción                     |
| --------------------------- | -------------------------------- |
| test_deflated_sharpe        | DSR con datos conocidos          |
| test_pbo                    | Escenario overfitted → PBO alto |
| test_sensitivity_analysis   | Sensibilidad de parámetros      |
| test_certificate_generation | Certificado completo             |
| test_replication_package    | ZIP descargable                  |

## 14.9 ETAPA 8: Frontend

| Test                     | Descripción           |
| ------------------------ | ---------------------- |
| test_wizard_navigation   | 6 pasos navegables     |
| test_wizard_saves_config | Config persistida      |
| test_screener_preview    | Preview en tiempo real |
| test_backtest_execution  | Run funciona           |
| test_results_display     | Resultados correctos   |
| test_3d_surface          | Gráfico interactivo   |
| test_export_to_excel     | Descarga funciona      |

---

# 15. PREPARACIÓN PARA STREAMING REAL-TIME

## 15.1 Arquitectura Preparada

El diseño usa una **INTERFAZ abstracta** para obtener datos:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ABSTRACCIÓN DE FUENTE DE DATOS                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║                        IDataSource (interfaz)                                  ║
║                               │                                                ║
║               ┌───────────────┴───────────────┐                               ║
║               ▼                               ▼                                ║
║  ┌─────────────────────┐         ┌─────────────────────┐                      ║
║  │  ParquetDataSource  │         │  StreamDataSource   │                      ║
║  │  (actual - offline) │         │  (futuro - real-time)│                     ║
║  └─────────────────────┘         └─────────────────────┘                      ║
║           │                               │                                    ║
║           ▼                               ▼                                    ║
║   Lee de C:\TSIS_Data            Conecta a WebSocket                          ║
║   archivos Parquet               recibe datos en vivo                         ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Beneficio**: Cambiar de Parquet a Streaming solo requiere implementar una nueva clase. El resto del motor NO cambia.

---

# 16. GLOSARIO DE TÉRMINOS

## Términos de Trading

| Término    | Descripción                                |
| ----------- | ------------------------------------------- |
| Gap         | Diferencia entre cierre anterior y apertura |
| Float       | Acciones disponibles para trading público  |
| VWAP        | Volume Weighted Average Price               |
| HOD/LOD     | High/Low of Day                             |
| PM High/Low | Premarket High/Low (4:00-9:30)              |
| R/G         | Red to Green (pasa de negativo a positivo)  |
| Runner      | Acción con momentum fuerte                 |
| Squeeze     | Short squeeze (shorts forzados a cubrir)    |

## Términos de Backtesting

| Término            | Descripción                                        |
| ------------------- | --------------------------------------------------- |
| In-Sample (IS)      | Datos usados para optimizar                         |
| Out-of-Sample (OOS) | Datos para validación (no usados en optimización) |
| Walk-Forward        | Método de validación rolling IS→OOS              |
| WFE                 | Walk-Forward Efficiency (robustez)                  |
| Overfitting         | Sobreajuste a datos históricos                     |
| Survivorship Bias   | Sesgo por excluir activos que ya no existen         |
| Look-Ahead Bias     | Usar datos que no estaban disponibles               |
| Point-in-Time       | Datos como estaban en ese momento exacto            |

## Métricas

| Término      | Descripción                                |
| ------------- | ------------------------------------------- |
| Sharpe Ratio  | Return ajustado por riesgo                  |
| Profit Factor | Gross Profit / Gross Loss                   |
| Max Drawdown  | Máxima caída desde un pico                |
| Win Rate      | % de trades ganadores                       |
| R-Multiple    | P&L expresado en unidades de riesgo         |
| DSR           | Deflated Sharpe Ratio (ajustado por trials) |
| PBO           | Probability of Backtest Overfitting         |

---

# RESUMEN EJECUTIVO - 10 PUNTOS CLAVE

1. **El Screener ES Parte de la Estrategia**: Sus parámetros son optimizables.
2. **Survivorship Bias es CRÍTICO**: SIEMPRE incluir tickers delisted/bankrupt.
3. **Point-in-Time**: Solo usar datos disponibles en el momento de la decisión.
4. **Walk-Forward es el Gold Standard**: Mínimo 10 runs, WFE >= 50% para PASS.
5. **Mapas 3D**: Buscar mesetas (robusto), evitar picos (overfitting).
6. **DSR y PBO**: Métricas científicas exclusivas de TSIS.ai.
7. **Costos Realistas**: Small caps tienen ~0.50% round trip.
8. **Tests Antes de Avanzar**: Cada etapa debe pasar todos sus tests.
9. **Audit Trail**: Guardar TODOS los trials, no solo los mejores.
10. **Preparado para Streaming**: Arquitectura con interfaces abstractas.

---

**Documento Generado para TSIS.ai**
**Especificación Conceptual del Motor de Backtesting v2.0**
**Enero 2026**
