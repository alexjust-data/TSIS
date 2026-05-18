**Calculadora Inteligente de TSIS**. He unificado tu widget de cabecera, la página de control total y la **pantalla flotante (modal)**, que es la pieza clave para la velocidad en Small Caps.

Como bien dices, aunque ahora los datos de precio no sean en tiempo real, dejamos la interfaz "mapeada" para que, en cuanto conectes el bróker, el sistema empiece a "latir" automáticamente.

---

### 1. El Widget de Cabecera (Siempre visible)

Es tu monitor de estado. Responde a: *¿Puedo operar ahora y con cuánto?*

```text
[Total P&L]  [Win Rate]  [Profit Factor]  [Today]  
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Íconos Menú]  Total P&L: +$1,240  |  Win Rate: 62%  |  [🟢 RISK OK]  │  ⚡NEXT TRADE (F2) │
├────────────────────────────────────────────────────────────────────────┤  Ticker:[ NVDA ]   │
│                                                                        │  Entry: [2.51]     │
│                                                                        │  Stop : [1.89]     │
│                                                                        │  Side:  [LONG]     │
│                                                                        │  Shares:   ?       │
│  (Cuerpo del Dashboard: Gráficos, Actividad Reciente, etc.)            │  Risk $:   ?       │
│                                                                        │  [🟢 RISK OK]      │
│                                                                        │  [ CALCULAR ]      │
└────────────────────────────────────────────────────────────────────────┴────────────────────┘


```

---

### 2. La Pantalla Flotante / Modal (Acción Rápida)

Esta pantalla aparece al pulsar **F2** o el botón del widget. Se superpone al dashboard sin cerrarlo. Es pura entrada de datos rápida.

**Diseño de la Pantalla Flotante:**

```text
┌──────────────────────────────────────────────────────────┐
│  🧮 CALCULADORA DE POSICIÓN RÁPIDA          [ X ]        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  TICKER: [ AAPL ]      Precio Actual: $182.40 (Delay)    │
│                                                          │
│  ENTRADA: [ 183.00 ]      STOP: [ 181.50 ]               │
│                                                          │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  RESULTADO:                                              │
│  👉 [ 🟢 LONG ]   [ 100 SHARES ]  [ 📋 Copiar ]          │
│                                                          │
│  DETALLES:                                               │
│  Riesgo Total: $150 (0.6% cuenta)                        │
│  Exposición:   $18,300                                   │
│                                                          │
│  [⚠️ WARNING: Stop a 0.8% - Muy volátil ]                │
│                                                          │
└──────────────────────────────────────────────────────────┘

```

---

### 3. Página de Configuración (Menú Izquierda: /calculator)

Aquí es donde configuras las "reglas del juego". Lo que pongas aquí, manda sobre el widget y la pantalla flotante.

**Esquema de la Página:**

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  CONFIGURACIÓN MAESTRA DE RIESGO                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  COLUMNA A: PRESETS DE ESTRATEGIA            COLUMNA B: MATRIX DE VARIACIÓN                 │
│  ┌─────────────────────────────────────┐    ┌──────────────────────────────────────────┐    │
│  │ Seleccionar Perfil: [ Scalp ⚡ ]    │    │ "Si el precio cambia, no calcules:"      │    │
│  │                                     │    │                                          │    │
│  │ ⚙️ Ajustes del Perfil:               │    │ STOP TÉCNICO | DISTANCIA | SHARES        │    │
│  │ Risk per Trade: [$150]              │    │ ---------------------------------------- │    │
│  │ Max Position:   [$5,000]            │    │    181.70    |   1.30    |   115         │    │
│  │ Slippage Buffer: [ 0.02 ]           │    │    181.50    |   1.50    |   100 (Act)   │    │
│  │ Redondeo: [ Lotes de 10 ]           │    │    181.30    |   1.70    |    88         │    │
│  │                                     │    └──────────────────────────────────────────┘    │
│  │ [ GUARDAR CONFIGURACIÓN ]           │                                                    │
│  └─────────────────────────────────────┘    [ Historial de últimos 10 cálculos ]            │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

```

---

### Resumen de la Lógica "Cerebro-Cuerpo" (TSIS + Bróker)

Como el bróker es el que manda los datos de ejecución, el planteamiento queda así:

1. **Entrada de Ticker:** Tú pones el Ticker. Hoy el precio se queda fijo o lo pones tú; mañana TSIS lo traerá vía API del bróker.
2. **Cálculo:** TSIS calcula las acciones usando tus reglas (Risk, Max Position, Slippage).
3. **Validación (El Semáforo):**
* **Verde:** Todo OK.
* **Naranja:** El Stop está muy cerca del precio de entrada (peligro de ejecución).
* **Rojo:** El riesgo supera el máximo diario permitido en tu "Account Management".


4. **Sincronización:** * *Hoy:* Copias el número de acciones y lo pegas en tu plataforma de trading.
* *Mañana:* El bróker detecta que has abierto la posición y TSIS la importa automáticamente a tu Journal, comparando el riesgo que calculaste con el que realmente tomaste.



### Próximo paso recomendado:

Dile al programador que empiece por el **State de la Calculadora** (la lógica de los números) y que el Widget de la cabecera sea el primer elemento visual, ya que es el que usarás el 90% del tiempo.

---


Aquí tienes el contenido formateado y listo para copiar y pegar directamente en tu archivo Markdown. He optimizado el uso de bloques de código y sintaxis de tablas para que se visualice correctamente en cualquier lector (GitHub, Obsidian, VS Code, etc.).

---

# VERSIÓN DEFINITIVA: Calculadora Inteligente TSIS

## Arquitectura de 3 Capas

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAPA 1: ESTADO GLOBAL                               │
│  useCalculatorStore (Zustand) - Fuente única de verdad                      │
│  • ticker, entry, stop, side, lastResult, riskSettings, todayPnL            │
│  • isModalOpen, calculationHistory[]                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  CAPA 2: COMPONENTES UI                                                     │
│  • QuickCalculatorWidget (Dashboard) ← Lee/escribe estado                   │
│  • CalculatorModal (Global) ← Lee/escribe estado + F2 listener              │
│  • /calculator page ← Configuración completa                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  CAPA 3: BACKEND                                                            │
│  • GET /risk-settings → Configuración del usuario                           │
│  • GET /risk-settings/calculator → Cálculo con límites                      │
│  • GET /dashboard/metrics → today_pnl para semáforo                         │
│  • [NUEVO] POST /calculation-history → Guardar historial                    │
└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 1. Widget de Cabecera (Dashboard) - SIMPLIFICADO

> **Nota de Diseño:** El widget se ubica como la **primera tarjeta del Dashboard**, garantizando visibilidad inmediata sin saturar el Header global.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Dashboard                                               [🔄 Refresh]       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────┐  ┌──────────┐ ┌──────────┐    │
│  │  ⚡ PRÓXIMO TRADE                   [F2] │  │ Total    │ │ Win Rate │    │
│  │                                          │  │ P&L      │ │          │    │
│  │  Ticker: [NVDA    ]   Side: [LONG ▼]     │  │ +$1,240  │ │  62.5%   │    │
│  │  Entry:  [183.00  ]   Stop: [181.50 ]    │  └──────────┘ └──────────┘    │
│  │                                          │  ┌──────────┐ ┌──────────┐    │
│  │  ════════════════════════════════════    │  │ Profit   │ │ Today    │    │
│  │  📊 100 SHARES     Risk: $150 (0.6%)     │  │ Factor   │ │          │    │
│  │  [🟢 RISK OK]       [📋 Copy] [Expand ↗] │  │  1.85    │ │ +$89     │    │
│  └──────────────────────────────────────────┘  └──────────┘ └──────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

```

### 🚦 Lógica del Semáforo

```javascript
function getRiskStatus(result, settings, todayPnL) {
  const remainingDailyRisk = settings.max_loss_daily - Math.abs(todayPnL);

  if (result.risk_amount > remainingDailyRisk) {
    return { status: 'RED', message: 'Supera pérdida diaria máxima' };
  }

  if (result.risk_percent > 1.5) { // Stop muy lejos
    return { status: 'ORANGE', message: 'Stop a >1.5% - Riesgo elevado' };
  }

  if (result.risk_per_share / result.entry_price < 0.003) { // Stop muy cerca
    return { status: 'ORANGE', message: 'Stop a <0.3% - Riesgo de ejecución' };
  }

  return { status: 'GREEN', message: 'Risk OK' };
}

```

---

## 2. Modal Flotante (F2) - ACCIÓN RÁPIDA

Diseño optimizado para velocidad (Hotkey `F2`).

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  ⚡ CALCULADORA RÁPIDA                                     [ESC para cerrar] │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   TICKER               SIDE                PRECIO (futuro: live)         │
│   [  NVDA  ]           ○ LONG  ● SHORT       $182.40 (manual)            │
│                                                                          │
│   ENTRY PRICE                  STOP PRICE                                │
│   [ 183.00 ]                   [ 181.50 ]                                │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════════ │
│                                                                          │
│   RESULTADO                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │                                                                 │    │
│   │      🟢 LONG         ███  100 SHARES  ███       [📋 COPIAR]     │    │
│   │                                                                 │    │
│   │      Exposición: $18,300          Riesgo: $150 (0.60%)          │    │
│   │      Risk/Share: $1.50            P&L Target (2:1): $300        │    │
│   │                                                                 │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│   SEMÁFORO DE RIESGO                                                     │
│   [🟢] Risk OK - Dentro de parámetros                                    │
│                                                                          │
│   MATRIX DE VARIACIÓN (stops alternativos)                               │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │  STOP      │  DISTANCIA  │  SHARES  │  RIESGO   │                │    │
│   │  $181.80   │   $1.20     │   125    │  $150     │                │    │
│   │  $181.50   │   $1.50     │   100    │  $150     │  ◀── ACTUAL    │    │
│   │  $181.20   │   $1.80     │    83    │  $150     │                │    │
│   │  $181.00   │   $2.00     │    75    │  $150     │                │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│   [ ⚙️ Configuración ]                               [ CALCULAR ]          │
└──────────────────────────────────────────────────────────────────────────┘

```

**Shortcuts:**

* `F2` → Abrir/cerrar modal
* `ESC` → Cerrar
* `Enter` → Calcular
* `Ctrl+C` → Copiar shares (con resultado visible)

---

## 3. Página /calculator - CONFIGURACIÓN MAESTRA

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Configuración de Riesgo                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CUENTA                                 LÍMITES POR TRADE                   │
│  ┌───────────────────────────────────┐    ┌───────────────────────────────┐ │
│  │  Balance Actual                   │    │  Risk por Trade               │ │
│  │  [ $15,000 ]                      │    │  [ 1.00 ]%  = $150            │ │
│  │                                   │    │                               │ │
│  │  Pérdida Diaria Máxima            │    │  Max Shares por Trade         │ │
│  │  [ 2.00 ]%  = $300                │    │  [ 2000 ]                     │ │
│  │                                   │    │                               │ │
│  │  Trades por Día                   │    │  Max Posición                 │ │
│  │  [ 4 ]                            │    │  [ $5,000 ]                   │ │
│  │                                   │    │                               │ │
│  │  [🟡 Alerta 30%] [🟠 50%] [🔴 75%]│    │  Max Order                    │ │
│  └───────────────────────────────────┘    │  [ $3,000 ]                   │ │
│                                           └───────────────────────────────┘ │
│                                                                             │
│  CALCULADORA DE PRUEBA                   HISTORIAL (últimos 10)             │
│  ┌───────────────────────────────────┐    ┌───────────────────────────────┐ │
│  │  Entry: [___] Stop: [___] Side:[] │    │  14:32 NVDA L 100sh $150      │ │
│  │  [ CALCULAR ]                     │    │  14:15 AAPL S  50sh  $75      │ │
│  │                                   │    │  13:58 TSLA L 200sh $200      │ │
│  │  Resultado: -- shares             │    │  ...                          │ │
│  └───────────────────────────────────┘    └───────────────────────────────┘ │
│                                                                             │
│                                [ 💾 GUARDAR CONFIGURACIÓN ]                 │
└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 📂 Plan de Archivos

| Módulo | Archivo | Acción | Descripción |
| --- | --- | --- | --- |
| **Frontend** | `src/lib/calculator.ts` | **CREAR** | Zustand store para estado global |
|  | `src/components/calculator/QuickCalculatorWidget.tsx` | **CREAR** | Widget para Dashboard |
|  | `src/components/calculator/CalculatorModal.tsx` | **CREAR** | Modal flotante (F2) |
|  | `src/components/calculator/VariationMatrix.tsx` | **CREAR** | Tabla de stops alternativos |
|  | `src/app/calculator/page.tsx` | **CREAR** | Página de configuración |
|  | `src/components/layout/Sidebar.tsx` | MODIFICAR | Añadir Calculator al menú |
|  | `src/components/layout/AppLayout.tsx` | MODIFICAR | Añadir modal + F2 listener |
|  | `src/app/dashboard/page.tsx` | MODIFICAR | Integrar QuickCalculatorWidget |
| **Backend** | `app/api/v1/endpoints/risk_settings.py` | MODIFICAR | Añadir variation matrix endpoint |

---

## 🧠 Store de Calculadora (Zustand)

```typescript
interface CalculatorState {
  // Inputs
  ticker: string;
  entryPrice: string;
  stopPrice: string;
  side: 'long' | 'short';

  // Results
  lastResult: PositionCalculation | null;
  variationMatrix: VariationRow[];
  riskStatus: 'GREEN' | 'ORANGE' | 'RED';
  riskMessage: string;

  // Settings (cached from API)
  riskSettings: RiskSettings | null;
  todayPnL: number;

  // UI State
  isModalOpen: boolean;
  isCalculating: boolean;
  history: CalculationHistoryItem[];

  // Actions
  setInput: (field: string, value: string) => void;
  calculate: () => Promise<void>;
  copyToClipboard: () => void;
  openModal: () => void;
  closeModal: () => void;
  loadSettings: () => Promise<void>;
}

```

---

## 🛠️ Ajustes sobre Diseño Original

1. **Ubicación:** Del Header Global al **Dashboard Widget**. Mayor espacio y contexto.
2. **Estrategias:** Postergadas a Fase 2 para evitar cambios complejos en la base de datos actual.
3. **Backend:** El cálculo base se mantiene local para latencia cero, el backend valida y guarda historial.
4. **UX:** Inclusión de la **Matrix de Variación** para permitir ajustes rápidos de stop sin recalcular manualmente.
