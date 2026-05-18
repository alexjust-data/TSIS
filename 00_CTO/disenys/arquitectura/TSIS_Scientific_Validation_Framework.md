# TSIS.ai - Framework de Validación Científica
## Guía para Backtesting Replicable y Científicamente Riguroso

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Basado en:** Bailey & López de Prado (2014), Harvey et al. (2015), Pardo (2008)

---

## ÍNDICE

1. [Introducción: Por Qué Importa](#1-introducción)
2. [Los 7 Sesgos Mortales del Backtesting](#2-los-7-sesgos-mortales)
3. [Framework de Validación TSIS](#3-framework-de-validación)
4. [Implementación Técnica](#4-implementación-técnica)
5. [Métricas Científicas](#5-métricas-científicas)
6. [Checklist de Validación](#6-checklist-de-validación)
7. [Documentación y Auditoría](#7-documentación-y-auditoría)
8. [Comparación con TradeStation](#8-comparación-con-tradestation)

---

## 1. INTRODUCCIÓN

### 1.1 El Problema

> "With four parameters I can fit an elephant, and with five I can make him wiggle his trunk."
> — John von Neumann

In the field of mathematical finance, a "backtest" is the usage of historical market data to assess the performance of a proposed trading strategy. It is a relatively simple matter for a present-day computer system to explore thousands, millions or even billions of variations of a proposed strategy, and pick the best performing variant as the "optimal" strategy "in sample". Unfortunately, such an "optimal" strategy often performs very poorly "out of sample", because the parameters of the investment strategy have been overfit to the in-sample data.

### 1.2 Consecuencias de No Validar Correctamente

| Error | Consecuencia |
|-------|--------------|
| Survivorship bias | Sobreestimación de retornos ~2-4% anual |
| Look-ahead bias | Resultados irreproducibles en live trading |
| Overfitting | Estrategia "óptima" que pierde dinero en real |
| Selection bias | Falsos positivos por múltiples pruebas |
| Data snooping | Patrones espurios que no se repiten |

### 1.3 Objetivo de Este Framework

Garantizar que **cualquier científico, auditor o usuario** pueda:

1. **Replicar** exactamente los mismos resultados
2. **Validar** la significancia estadística
3. **Detectar** overfitting y sesgos
4. **Comparar** con otras plataformas (TradeStation, etc.)

---

## 2. LOS 7 SESGOS MORTALES DEL BACKTESTING

### 2.1 Survivorship Bias (Sesgo de Supervivencia)

**Definición:** Solo incluir activos que sobrevivieron hasta hoy, ignorando los que quebraron o fueron delisted.

Survivorship bias in backtesting can distort trading strategies by ignoring failed or delisted assets, leading to inflated returns and underestimated risks. For example, excluding defunct stocks from historical data can overstate annual returns by 1-4% and skew performance metrics like Sharpe ratios and drawdowns.

**Impacto en Small Caps:**
- Las small caps tienen mayor tasa de delisting/bancarrota
- El sesgo es **más severo** que en large caps
- From 1926 to 2015 only 42.1% of common stocks returned more than short-term Treasuries during their lifetime as a public company. A random common stock had a median life of only seven years.

**Solución TSIS:**
```sql
-- INCLUIR TODOS LOS TICKERS HISTÓRICOS
CREATE TABLE companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(200),
    status VARCHAR(20),  -- 'active', 'delisted', 'merged', 'bankrupt'
    delisting_date DATE,
    delisting_reason VARCHAR(100),
    -- Point-in-time tracking
    listing_date DATE,
    exchange_history JSONB  -- Historial de cambios de exchange
);

-- Índice para queries point-in-time
CREATE INDEX idx_companies_status_date ON companies(status, delisting_date);
```

### 2.2 Look-Ahead Bias (Sesgo de Anticipación)

**Definición:** Usar información que NO estaba disponible en el momento de la decisión.

Look-ahead bias emanates from the use of unavailable information by an investor during the historical periods over which a backtest is conducted. It is noteworthy that this is the most common mistake made when backtesting is conducted.

**Formas Comunes:**
1. **Reporting lag:** Usar datos de earnings antes de que se publicaran
2. **Data revisions:** Usar datos corregidos en vez de los originales
3. **Index additions:** Asumir que un stock estaba en el índice antes de añadirse

**Solución TSIS:**
```python
# POINT-IN-TIME DATA ACCESS
class PointInTimeDataLoader:
    """
    Solo retorna datos que estaban disponibles en la fecha especificada.
    """
    
    def get_fundamentals(self, ticker: str, as_of_date: date) -> dict:
        """
        Retorna fundamentales que estaban disponibles en as_of_date.
        Usa filing_date, NO period_end.
        """
        return db.query("""
            SELECT *
            FROM balance_sheets
            WHERE ticker = :ticker
              AND filing_date <= :as_of_date  -- Cuando se PUBLICÓ
              AND filing_date = (
                  SELECT MAX(filing_date)
                  FROM balance_sheets
                  WHERE ticker = :ticker
                    AND filing_date <= :as_of_date
              )
        """, ticker=ticker, as_of_date=as_of_date)
    
    def get_price(self, ticker: str, as_of_datetime: datetime) -> float:
        """
        Retorna el precio MÁS RECIENTE disponible en as_of_datetime.
        NO el precio de cierre del día (que no se conoce hasta después).
        """
        return db.query("""
            SELECT price
            FROM trades
            WHERE ticker = :ticker
              AND timestamp <= :as_of_datetime
            ORDER BY timestamp DESC
            LIMIT 1
        """, ticker=ticker, as_of_datetime=as_of_datetime)
    
    def was_listed(self, ticker: str, on_date: date) -> bool:
        """
        Verifica si el ticker estaba listado en esa fecha.
        """
        company = db.query("""
            SELECT listing_date, delisting_date
            FROM companies
            WHERE ticker = :ticker
        """, ticker=ticker)
        
        return (company.listing_date <= on_date and 
                (company.delisting_date is None or company.delisting_date > on_date))
```

### 2.3 Overfitting (Sobreajuste)

**Definición:** Optimizar parámetros hasta que "funcionen" en datos históricos, pero fallen en datos nuevos.

The most common mistake in backtesting involves overfitting or data snooping. Consequences: Strategies developed through overfitting are likely to fail in the future as random patterns that were captured during optimization do not repeat.

**Señales de Overfitting:**
- Sharpe ratio > 3 (casi siempre es overfit)
- Equity curve demasiado suave
- Muchos parámetros (>5-6)
- Resultados muy diferentes con pequeños cambios de parámetros

**Solución TSIS:**
```python
# MÉTRICAS ANTI-OVERFITTING

def calculate_overfitting_indicators(backtest_results: list) -> dict:
    """
    Calcula indicadores de posible overfitting.
    """
    returns = [r['return'] for r in backtest_results]
    
    # 1. Número efectivo de parámetros libres
    n_params = count_free_parameters(strategy)
    n_trades = len(backtest_results)
    params_per_trade = n_params / n_trades
    
    # 2. Sensibilidad a parámetros (alta = posible overfit)
    sensitivity = calculate_parameter_sensitivity(backtest_results)
    
    # 3. Comparación IS vs OOS
    is_sharpe = calculate_sharpe(in_sample_returns)
    oos_sharpe = calculate_sharpe(out_of_sample_returns)
    sharpe_degradation = (is_sharpe - oos_sharpe) / is_sharpe
    
    return {
        'params_per_trade': params_per_trade,  # < 0.01 es bueno
        'sensitivity_score': sensitivity,       # < 20% es bueno
        'sharpe_degradation': sharpe_degradation,  # < 30% es bueno
        'overfitting_probability': calculate_pbo(backtest_results)
    }
```

### 2.4 Selection Bias (Sesgo de Selección)

**Definición:** Reportar solo los resultados positivos de múltiples pruebas.

The problem of performance inflation extends beyond backtesting. More generally, researchers and investment managers tend to report only positive outcomes, a phenomenon known as selection bias. Not controlling for the number of trials involved in a particular discovery leads to false discoveries.

**El Problema del Multiple Testing:**
- Si pruebas 100 estrategias, esperarías ~5 con p < 0.05 por azar
- Si pruebas 1000, esperarías ~50 "significativas" por azar
- When datamining strategies, the more backtests computed the more likely a spurious strategy having high Sharpe ratio can be found.

**Solución TSIS:**
```python
# REGISTRO OBLIGATORIO DE TODOS LOS TRIALS

class OptimizationAuditLog:
    """
    Registra TODAS las combinaciones probadas, no solo las mejores.
    """
    
    def __init__(self, optimization_id: int):
        self.optimization_id = optimization_id
        self.trials = []
    
    def log_trial(self, params: dict, result: dict):
        """
        CADA trial debe ser registrado, sin excepción.
        """
        self.trials.append({
            'timestamp': datetime.now(),
            'params': params,
            'sharpe_ratio': result['sharpe'],
            'return': result['return'],
            'drawdown': result['drawdown'],
            'n_trades': result['n_trades']
        })
        
        # Guardar inmediatamente en BD (no en memoria)
        db.insert('optimization_trials', {
            'optimization_id': self.optimization_id,
            **self.trials[-1]
        })
    
    def get_trial_count(self) -> int:
        """
        Retorna el número TOTAL de trials ejecutados.
        Este número es CRÍTICO para calcular el Deflated Sharpe Ratio.
        """
        return len(self.trials)
    
    def get_sharpe_variance(self) -> float:
        """
        Varianza de los Sharpe ratios de todos los trials.
        Necesario para el DSR.
        """
        sharpes = [t['sharpe_ratio'] for t in self.trials]
        return np.var(sharpes)
```

### 2.5 Data Snooping (Espionaje de Datos)

**Definición:** Ajustar la estrategia después de ver los datos, inventando justificaciones post-hoc.

Storytelling bias creates ex-post narratives to explain random patterns discovered through data mining. When you find a pattern first and invent the economic rationale second, you're likely fooling yourself.

**Solución TSIS:**
```python
# HIPÓTESIS PRE-REGISTRADA

class HypothesisRegistry:
    """
    Registrar la hipótesis ANTES de ejecutar el backtest.
    Similar al pre-registro en estudios clínicos.
    """
    
    def register_hypothesis(
        self,
        user_id: int,
        hypothesis: str,
        expected_sharpe: float,
        rationale: str,
        strategy_params: dict
    ) -> int:
        """
        Registra hipótesis con timestamp inmutable.
        NO se puede modificar después.
        """
        hypothesis_id = db.insert('hypothesis_registry', {
            'user_id': user_id,
            'hypothesis': hypothesis,
            'expected_sharpe': expected_sharpe,
            'rationale': rationale,
            'strategy_params': json.dumps(strategy_params),
            'registered_at': datetime.now(),
            'hash': self._calculate_hash(hypothesis, strategy_params)
        })
        
        return hypothesis_id
    
    def validate_backtest(self, hypothesis_id: int, backtest_id: int) -> dict:
        """
        Valida que el backtest corresponde a la hipótesis pre-registrada.
        """
        hypothesis = db.get('hypothesis_registry', hypothesis_id)
        backtest = db.get('backtests', backtest_id)
        
        # Verificar que los parámetros coinciden
        params_match = json.loads(hypothesis['strategy_params']) == backtest['params']
        
        # Verificar que el backtest se ejecutó DESPUÉS del registro
        time_valid = backtest['executed_at'] > hypothesis['registered_at']
        
        return {
            'valid': params_match and time_valid,
            'params_match': params_match,
            'time_valid': time_valid,
            'hypothesis_hash': hypothesis['hash']
        }
```

### 2.6 Period Selection Bias (Sesgo de Selección de Período)

**Definición:** Solo testear en períodos favorables (bull markets, baja volatilidad).

Period selection bias occurs when backtesting only covers favorable market regimes, excluding major drawdowns or different volatility environments. Strategies tested only during bull markets or low-volatility periods show misleading resilience and return profiles.

**Solución TSIS:**
```python
# VALIDACIÓN MULTI-RÉGIMEN OBLIGATORIA

REQUIRED_MARKET_REGIMES = [
    {'name': 'Dot-com Crash', 'start': '2000-03-01', 'end': '2002-10-01'},
    {'name': 'Bull 2003-2007', 'start': '2003-01-01', 'end': '2007-10-01'},
    {'name': 'Financial Crisis', 'start': '2007-10-01', 'end': '2009-03-01'},
    {'name': 'Bull 2009-2020', 'start': '2009-03-01', 'end': '2020-02-01'},
    {'name': 'COVID Crash', 'start': '2020-02-01', 'end': '2020-04-01'},
    {'name': 'Post-COVID Bull', 'start': '2020-04-01', 'end': '2021-12-01'},
    {'name': '2022 Bear', 'start': '2022-01-01', 'end': '2022-10-01'},
    {'name': 'Recent', 'start': '2023-01-01', 'end': 'now'}
]

def validate_regime_coverage(backtest_config: dict) -> dict:
    """
    Verifica que el backtest cubre múltiples regímenes de mercado.
    """
    start_date = backtest_config['start_date']
    end_date = backtest_config['end_date']
    
    covered_regimes = []
    missing_regimes = []
    
    for regime in REQUIRED_MARKET_REGIMES:
        regime_start = parse_date(regime['start'])
        regime_end = parse_date(regime['end'])
        
        # ¿El backtest cubre este régimen?
        if start_date <= regime_start and end_date >= regime_end:
            covered_regimes.append(regime['name'])
        elif (start_date <= regime_end and end_date >= regime_start):
            covered_regimes.append(f"{regime['name']} (parcial)")
        else:
            missing_regimes.append(regime['name'])
    
    coverage_score = len(covered_regimes) / len(REQUIRED_MARKET_REGIMES) * 100
    
    return {
        'coverage_score': coverage_score,
        'covered_regimes': covered_regimes,
        'missing_regimes': missing_regimes,
        'passes_minimum': coverage_score >= 60,  # Mínimo 60% de regímenes
        'warning': "El backtest no incluye crisis financieras" if 'Financial Crisis' in missing_regimes else None
    }
```

### 2.7 Transaction Cost Bias

**Definición:** No modelar correctamente los costes de transacción reales.

**Componentes Ignorados Frecuentemente:**
- Spread bid-ask (especialmente en small caps ilíquidas)
- Slippage (impacto de mercado)
- Comisiones del broker
- Costes de borrowing para shorts
- Partial fills

**Solución TSIS:**
```python
# MODELO DE COSTES REALISTA

class RealisticCostModel:
    """
    Modelo de costes basado en datos reales de ejecución.
    """
    
    def __init__(self):
        # Costes base (ajustables por usuario)
        self.commission_per_share = 0.005  # $0.005/share
        self.min_commission = 1.00  # $1 mínimo
        self.sec_fee_rate = 0.0000278  # SEC fee
        self.finra_taf_rate = 0.000145  # FINRA TAF
    
    def calculate_spread_cost(
        self,
        ticker: str,
        trade_time: datetime,
        size: int
    ) -> float:
        """
        Calcula coste de spread basado en datos históricos reales.
        """
        # Obtener spread histórico real
        quote = db.query("""
            SELECT bid_price, ask_price, bid_size, ask_size
            FROM quotes
            WHERE ticker = :ticker
              AND timestamp <= :trade_time
            ORDER BY timestamp DESC
            LIMIT 1
        """, ticker=ticker, trade_time=trade_time)
        
        spread = quote['ask_price'] - quote['bid_price']
        spread_pct = spread / ((quote['ask_price'] + quote['bid_price']) / 2)
        
        # Ajustar por tamaño (más acciones = más slippage)
        avg_size = (quote['bid_size'] + quote['ask_size']) / 2
        size_ratio = size / avg_size
        
        # Modelo de impacto de mercado (square root model)
        market_impact = spread_pct * np.sqrt(size_ratio)
        
        return market_impact
    
    def calculate_slippage(
        self,
        ticker: str,
        order_type: str,  # 'market', 'limit'
        side: str,  # 'buy', 'sell'
        size: int,
        expected_price: float,
        trade_time: datetime
    ) -> float:
        """
        Simula slippage realista basado en volumen y volatilidad.
        """
        # Obtener volumen promedio
        avg_volume = db.query("""
            SELECT AVG(volume) as avg_vol
            FROM ohlcv_1m
            WHERE ticker = :ticker
              AND date BETWEEN :start AND :end
        """, ticker=ticker, start=trade_time - timedelta(days=20), end=trade_time)
        
        # Obtener volatilidad intraday
        volatility = self._get_intraday_volatility(ticker, trade_time)
        
        # Slippage = f(size/volume, volatility)
        participation_rate = size / (avg_volume['avg_vol'] / 390)  # minutos en día
        slippage_pct = volatility * np.sqrt(participation_rate) * 0.5
        
        return slippage_pct * expected_price * size
    
    def get_total_cost(
        self,
        ticker: str,
        side: str,
        size: int,
        price: float,
        trade_time: datetime
    ) -> dict:
        """
        Retorna todos los costes de una transacción.
        """
        trade_value = size * price
        
        commission = max(self.min_commission, size * self.commission_per_share)
        sec_fee = trade_value * self.sec_fee_rate if side == 'sell' else 0
        finra_taf = size * self.finra_taf_rate
        spread_cost = self.calculate_spread_cost(ticker, trade_time, size) * trade_value
        slippage = self.calculate_slippage(ticker, 'market', side, size, price, trade_time)
        
        total_cost = commission + sec_fee + finra_taf + spread_cost + slippage
        
        return {
            'commission': commission,
            'sec_fee': sec_fee,
            'finra_taf': finra_taf,
            'spread_cost': spread_cost,
            'slippage': slippage,
            'total_cost': total_cost,
            'cost_pct': total_cost / trade_value * 100
        }
```

---

## 3. FRAMEWORK DE VALIDACIÓN TSIS

### 3.1 Arquitectura de Validación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TSIS SCIENTIFIC VALIDATION FRAMEWORK                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐│
│  │   LAYER 1    │───▶│   LAYER 2    │───▶│   LAYER 3    │───▶│   LAYER 4  ││
│  │  Data        │    │  Execution   │    │  Statistics  │    │  Audit     ││
│  │  Integrity   │    │  Fidelity    │    │  Validation  │    │  Trail     ││
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘│
│                                                                              │
│  Checks:            Checks:            Checks:            Outputs:          │
│  • Survivorship     • Fill logic       • DSR              • Hash logs       │
│  • Point-in-time    • Cost model       • PBO              • Replication     │
│  • Completeness     • Timing           • Walk-Forward     • Certificates    │
│  • Consistency      • Order types      • Regime test      • Export CSV      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Layer 1: Data Integrity

```python
class DataIntegrityValidator:
    """
    Valida la integridad de los datos ANTES del backtest.
    """
    
    def validate_universe(self, start_date: date, end_date: date) -> ValidationReport:
        """
        Valida que el universo de stocks incluye delisted.
        """
        report = ValidationReport()
        
        # 1. Contar tickers activos vs delisted en el período
        active = db.count("""
            SELECT COUNT(DISTINCT ticker)
            FROM companies
            WHERE status = 'active'
              AND listing_date <= :end_date
        """, end_date=end_date)
        
        delisted = db.count("""
            SELECT COUNT(DISTINCT ticker)
            FROM companies
            WHERE status IN ('delisted', 'bankrupt', 'merged')
              AND listing_date <= :end_date
              AND delisting_date >= :start_date
        """, start_date=start_date, end_date=end_date)
        
        total = active + delisted
        delisted_ratio = delisted / total
        
        report.add_check(
            name="Survivorship Coverage",
            passed=delisted_ratio > 0.1,  # Al menos 10% delisted
            value=f"{delisted_ratio:.1%} delisted",
            warning="Possible survivorship bias" if delisted_ratio < 0.1 else None
        )
        
        # 2. Verificar gaps en datos de precios
        gaps = self._check_price_gaps(start_date, end_date)
        report.add_check(
            name="Price Data Completeness",
            passed=gaps['missing_pct'] < 5,
            value=f"{gaps['missing_pct']:.1%} missing",
            details=gaps['missing_tickers']
        )
        
        # 3. Verificar point-in-time consistency
        pit_issues = self._check_point_in_time(start_date, end_date)
        report.add_check(
            name="Point-in-Time Integrity",
            passed=len(pit_issues) == 0,
            value=f"{len(pit_issues)} issues found",
            details=pit_issues
        )
        
        return report
    
    def _check_point_in_time(self, start_date, end_date) -> list:
        """
        Detecta datos que violan point-in-time.
        """
        issues = []
        
        # Buscar fundamentales con filing_date después del uso
        bad_fundamentals = db.query("""
            SELECT ticker, period_end, filing_date
            FROM balance_sheets
            WHERE filing_date > period_end + INTERVAL '90 days'
              AND period_end BETWEEN :start AND :end
        """, start=start_date, end=end_date)
        
        for row in bad_fundamentals:
            issues.append({
                'type': 'late_filing',
                'ticker': row['ticker'],
                'period_end': row['period_end'],
                'filing_date': row['filing_date']
            })
        
        return issues
```

### 3.3 Layer 2: Execution Fidelity

```python
class ExecutionFidelityValidator:
    """
    Valida que la ejecución del backtest es realista.
    """
    
    def validate_fill_logic(self, trade: Trade, market_data: MarketData) -> ValidationReport:
        """
        Valida que el fill del trade es realista.
        """
        report = ValidationReport()
        
        # 1. ¿El precio de fill está dentro del rango OHLC?
        candle = market_data.get_candle(trade.ticker, trade.timestamp)
        price_valid = candle['low'] <= trade.fill_price <= candle['high']
        
        report.add_check(
            name="Fill Price Within Range",
            passed=price_valid,
            value=f"Fill: ${trade.fill_price}, Range: ${candle['low']}-${candle['high']}"
        )
        
        # 2. ¿El volumen es realista?
        max_participation = 0.10  # Máximo 10% del volumen del minuto
        minute_volume = market_data.get_minute_volume(trade.ticker, trade.timestamp)
        participation = trade.size / minute_volume if minute_volume > 0 else float('inf')
        
        report.add_check(
            name="Volume Participation",
            passed=participation <= max_participation,
            value=f"{participation:.1%} of minute volume",
            warning="Unrealistic fill - too large for liquidity" if participation > max_participation else None
        )
        
        # 3. ¿El slippage es realista?
        expected_slippage = self._estimate_realistic_slippage(trade, market_data)
        actual_slippage = abs(trade.fill_price - trade.expected_price) / trade.expected_price
        
        report.add_check(
            name="Slippage Realism",
            passed=actual_slippage >= expected_slippage * 0.5,  # Al menos 50% del esperado
            value=f"Actual: {actual_slippage:.2%}, Expected: {expected_slippage:.2%}",
            warning="Slippage too optimistic" if actual_slippage < expected_slippage * 0.5 else None
        )
        
        return report
    
    def validate_timing(self, trade: Trade) -> ValidationReport:
        """
        Valida que el timing del trade es realista.
        """
        report = ValidationReport()
        
        # 1. ¿El trade está dentro de horario de mercado?
        trade_time = trade.timestamp.time()
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        in_market_hours = market_open <= trade_time <= market_close
        
        report.add_check(
            name="Market Hours",
            passed=in_market_hours or trade.session == 'extended',
            value=f"Trade at {trade_time}, Session: {trade.session}"
        )
        
        # 2. ¿Hay latencia realista entre señal y ejecución?
        signal_to_fill = (trade.fill_timestamp - trade.signal_timestamp).total_seconds()
        
        report.add_check(
            name="Execution Latency",
            passed=signal_to_fill >= 0.1,  # Al menos 100ms
            value=f"{signal_to_fill:.3f} seconds",
            warning="Unrealistic zero-latency execution" if signal_to_fill < 0.1 else None
        )
        
        return report
```

### 3.4 Layer 3: Statistical Validation

```python
class StatisticalValidator:
    """
    Implementa métricas científicas de validación.
    Basado en Bailey & López de Prado (2014).
    """
    
    def calculate_deflated_sharpe_ratio(
        self,
        estimated_sharpe: float,
        sharpe_variance: float,
        n_trials: int,
        backtest_length: int,  # en días
        skewness: float,
        kurtosis: float
    ) -> dict:
        """
        Deflated Sharpe Ratio (DSR) - corrige por múltiples pruebas.
        
        Referencia: Bailey & López de Prado (2014)
        "The Deflated Sharpe Ratio: Correcting for Selection Bias,
        Backtest Overfitting and Non-Normality"
        """
        from scipy.stats import norm
        
        # Euler-Mascheroni constant
        gamma = 0.5772156649015328606
        e = np.exp(1)
        
        # Expected Maximum Sharpe Ratio (dado n_trials)
        # Esto es lo que esperarías por AZAR si probaste n_trials estrategias
        SR_0 = np.sqrt(sharpe_variance) * (
            (1 - gamma) * norm.ppf(1 - 1/n_trials) +
            gamma * norm.ppf(1 - 1/(n_trials * e))
        )
        
        # Standard deviation around SR_0
        sigma_SR = np.sqrt(
            (1 - skewness * SR_0 + ((kurtosis - 1) / 4) * SR_0**2) /
            (backtest_length - 1)
        )
        
        # Deflated Sharpe Ratio
        DSR = norm.cdf((estimated_sharpe - SR_0) / sigma_SR)
        
        return {
            'estimated_sharpe': estimated_sharpe,
            'expected_max_sharpe_by_chance': SR_0,
            'deflated_sharpe_ratio': DSR,
            'n_trials': n_trials,
            'interpretation': self._interpret_dsr(DSR),
            'is_significant': DSR > 0.95,  # 95% confidence
            'warning': f"Sharpe {estimated_sharpe:.2f} could be achieved by chance after {n_trials} trials" if DSR < 0.95 else None
        }
    
    def _interpret_dsr(self, dsr: float) -> str:
        if dsr >= 0.99:
            return "Highly significant (>99% confidence)"
        elif dsr >= 0.95:
            return "Significant (>95% confidence)"
        elif dsr >= 0.90:
            return "Marginally significant (>90% confidence)"
        elif dsr >= 0.50:
            return "Inconclusive - could be random"
        else:
            return "Likely overfitted - performance is WORSE than random"
    
    def calculate_probability_of_backtest_overfitting(
        self,
        optimization_results: list[dict]
    ) -> dict:
        """
        Probability of Backtest Overfitting (PBO) usando CSCV.
        
        Referencia: Bailey et al. (2014)
        "The Probability of Backtest Overfitting"
        """
        # Implementación de Combinatorially Symmetric Cross-Validation (CSCV)
        
        # 1. Crear matriz M de resultados
        # Filas = períodos de tiempo, Columnas = estrategias/parámetros
        M = self._create_performance_matrix(optimization_results)
        
        T, N = M.shape  # T períodos, N trials
        S = 16  # Número de particiones (recomendado por los autores)
        
        # 2. Dividir en S submatrices
        submatrices = self._partition_matrix(M, S)
        
        # 3. Generar todas las combinaciones de S/2 submatrices para IS
        from itertools import combinations
        
        logits = []
        
        for is_indices in combinations(range(S), S // 2):
            oos_indices = [i for i in range(S) if i not in is_indices]
            
            # Combinar submatrices para IS y OOS
            M_is = np.vstack([submatrices[i] for i in is_indices])
            M_oos = np.vstack([submatrices[i] for i in oos_indices])
            
            # Calcular Sharpe ratios
            SR_is = self._calculate_sharpes(M_is)
            SR_oos = self._calculate_sharpes(M_oos)
            
            # Encontrar mejor estrategia IS
            best_is_idx = np.argmax(SR_is)
            
            # ¿Cómo rinde OOS?
            rank_oos = self._get_rank(SR_oos, best_is_idx)
            
            # Calcular logit: log(rank / (N - rank))
            omega = rank_oos / N
            logit = np.log(omega / (1 - omega + 1e-10))
            logits.append(logit)
        
        # 4. PBO = proporción de logits < 0
        PBO = np.mean([1 if l < 0 else 0 for l in logits])
        
        return {
            'pbo': PBO,
            'interpretation': self._interpret_pbo(PBO),
            'is_overfit': PBO > 0.50,
            'logit_distribution': {
                'mean': np.mean(logits),
                'std': np.std(logits),
                'min': np.min(logits),
                'max': np.max(logits)
            },
            'recommendation': "Strategy likely overfit - use caution" if PBO > 0.50 else "Strategy shows robustness"
        }
    
    def _interpret_pbo(self, pbo: float) -> str:
        if pbo <= 0.10:
            return "Excellent - very low probability of overfitting"
        elif pbo <= 0.25:
            return "Good - low probability of overfitting"
        elif pbo <= 0.50:
            return "Acceptable - moderate risk of overfitting"
        elif pbo <= 0.75:
            return "Warning - high probability of overfitting"
        else:
            return "Critical - strategy is almost certainly overfit"
    
    def calculate_minimum_backtest_length(
        self,
        target_sharpe: float,
        skewness: float,
        kurtosis: float,
        confidence: float = 0.95
    ) -> int:
        """
        Calcula el mínimo número de observaciones necesarias.
        
        Referencia: Bailey & López de Prado (2014)
        "Minimum Backtest Length"
        """
        from scipy.stats import norm
        
        z = norm.ppf(confidence)
        
        # Fórmula de MinBTL
        min_length = 1 + (1 - skewness * target_sharpe + 
                         ((kurtosis - 1) / 4) * target_sharpe**2) * (z / target_sharpe)**2
        
        return {
            'minimum_days': int(np.ceil(min_length)),
            'minimum_years': min_length / 252,
            'confidence': confidence,
            'target_sharpe': target_sharpe,
            'interpretation': f"Need at least {int(min_length)} trading days ({min_length/252:.1f} years) to validate Sharpe={target_sharpe:.2f} at {confidence:.0%} confidence"
        }
```

### 3.5 Layer 4: Audit Trail

```python
class AuditTrailGenerator:
    """
    Genera documentación completa para replicación.
    """
    
    def generate_replication_package(
        self,
        backtest_id: int
    ) -> ReplicationPackage:
        """
        Genera un paquete completo para que terceros repliquen.
        """
        backtest = db.get('backtests', backtest_id)
        
        package = ReplicationPackage()
        
        # 1. Hash de datos de entrada
        package.data_hashes = self._generate_data_hashes(backtest)
        
        # 2. Configuración completa
        package.config = {
            'strategy_params': backtest['params'],
            'date_range': {
                'start': backtest['start_date'],
                'end': backtest['end_date']
            },
            'cost_model': backtest['cost_model_config'],
            'execution_model': backtest['execution_model_config'],
            'random_seed': backtest['random_seed']
        }
        
        # 3. Código/pseudocódigo de la estrategia
        package.strategy_code = self._extract_strategy_code(backtest['strategy_id'])
        
        # 4. Lista completa de trades
        package.trades = self._export_all_trades(backtest_id)
        
        # 5. Métricas de validación
        package.validation = {
            'dsr': self._get_dsr(backtest_id),
            'pbo': self._get_pbo(backtest_id),
            'regime_coverage': self._get_regime_coverage(backtest_id),
            'data_integrity': self._get_data_integrity_report(backtest_id)
        }
        
        # 6. Generar hash único del paquete
        package.package_hash = self._calculate_package_hash(package)
        
        return package
    
    def _generate_data_hashes(self, backtest: dict) -> dict:
        """
        Genera hashes SHA-256 de los datos de entrada.
        Permite verificar que se usan los mismos datos.
        """
        import hashlib
        
        hashes = {}
        
        # Hash del universo de tickers
        tickers = db.query("""
            SELECT ticker, status, listing_date, delisting_date
            FROM companies
            WHERE listing_date <= :end_date
            ORDER BY ticker
        """, end_date=backtest['end_date'])
        
        hashes['universe'] = hashlib.sha256(
            json.dumps(tickers, default=str).encode()
        ).hexdigest()
        
        # Hash de precios (muestra representativa)
        price_sample = db.query("""
            SELECT ticker, date, open, high, low, close, volume
            FROM ohlcv_daily
            WHERE date BETWEEN :start AND :end
            ORDER BY ticker, date
        """, start=backtest['start_date'], end=backtest['end_date'])
        
        hashes['prices'] = hashlib.sha256(
            json.dumps(price_sample, default=str).encode()
        ).hexdigest()
        
        # Hash de gaps usados
        gaps = db.query("""
            SELECT *
            FROM gaps
            WHERE gap_date BETWEEN :start AND :end
            ORDER BY ticker, gap_date
        """, start=backtest['start_date'], end=backtest['end_date'])
        
        hashes['gaps'] = hashlib.sha256(
            json.dumps(gaps, default=str).encode()
        ).hexdigest()
        
        return hashes
    
    def export_for_third_party_validation(
        self,
        backtest_id: int,
        format: str = 'csv'
    ) -> bytes:
        """
        Exporta datos en formato estándar para validación externa.
        """
        package = self.generate_replication_package(backtest_id)
        
        if format == 'csv':
            return self._export_csv(package)
        elif format == 'json':
            return self._export_json(package)
        elif format == 'excel':
            return self._export_excel(package)
    
    def _export_csv(self, package: ReplicationPackage) -> bytes:
        """
        Exporta múltiples CSVs en un ZIP.
        """
        import zipfile
        from io import BytesIO
        
        buffer = BytesIO()
        
        with zipfile.ZipFile(buffer, 'w') as zf:
            # 1. metadata.json
            zf.writestr('metadata.json', json.dumps({
                'package_hash': package.package_hash,
                'config': package.config,
                'data_hashes': package.data_hashes,
                'validation': package.validation
            }, default=str, indent=2))
            
            # 2. trades.csv
            trades_df = pd.DataFrame(package.trades)
            zf.writestr('trades.csv', trades_df.to_csv(index=False))
            
            # 3. daily_returns.csv
            returns_df = self._calculate_daily_returns(package.trades)
            zf.writestr('daily_returns.csv', returns_df.to_csv(index=False))
            
            # 4. strategy_definition.txt
            zf.writestr('strategy_definition.txt', package.strategy_code)
            
            # 5. validation_report.txt
            zf.writestr('validation_report.txt', self._format_validation_report(package.validation))
        
        return buffer.getvalue()
```

---

## 4. IMPLEMENTACIÓN TÉCNICA

### 4.1 Estructura de Tablas de Auditoría

```sql
-- Log de todas las optimizaciones (NUNCA borrar)
CREATE TABLE optimization_audit_log (
    id SERIAL PRIMARY KEY,
    optimization_id INT REFERENCES optimizations(id),
    trial_number INT NOT NULL,
    params JSONB NOT NULL,
    
    -- Resultados
    sharpe_ratio DECIMAL,
    total_return DECIMAL,
    max_drawdown DECIMAL,
    n_trades INT,
    
    -- Timestamp inmutable
    executed_at TIMESTAMP DEFAULT NOW(),
    
    -- Hash para verificación
    params_hash VARCHAR(64) NOT NULL,
    results_hash VARCHAR(64) NOT NULL
);

-- Índices para búsqueda rápida
CREATE INDEX idx_audit_optimization ON optimization_audit_log(optimization_id);
CREATE INDEX idx_audit_executed ON optimization_audit_log(executed_at);

-- Prevenir modificaciones
ALTER TABLE optimization_audit_log 
    ALTER COLUMN executed_at SET DEFAULT NOW(),
    ALTER COLUMN executed_at SET NOT NULL;

-- Trigger para prevenir updates/deletes
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit log cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_immutable
    BEFORE UPDATE OR DELETE ON optimization_audit_log
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_modification();


-- Registro de hipótesis pre-registradas
CREATE TABLE hypothesis_registry (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    
    -- Hipótesis
    hypothesis_name VARCHAR(200) NOT NULL,
    hypothesis_description TEXT NOT NULL,
    expected_sharpe DECIMAL,
    economic_rationale TEXT NOT NULL,
    
    -- Parámetros pre-especificados
    strategy_params JSONB NOT NULL,
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    
    -- Timestamp inmutable
    registered_at TIMESTAMP DEFAULT NOW(),
    
    -- Hash para verificación
    hypothesis_hash VARCHAR(64) NOT NULL,
    
    -- Estado
    backtest_executed BOOLEAN DEFAULT false,
    backtest_id INT REFERENCES backtests(id)
);

-- Trigger para prevenir modificaciones post-registro
CREATE TRIGGER hypothesis_immutable
    BEFORE UPDATE ON hypothesis_registry
    FOR EACH ROW
    WHEN (OLD.registered_at IS NOT NULL)
    EXECUTE FUNCTION prevent_audit_modification();


-- Certificados de validación
CREATE TABLE validation_certificates (
    id SERIAL PRIMARY KEY,
    backtest_id INT REFERENCES backtests(id),
    
    -- Métricas de validación
    dsr_value DECIMAL,
    dsr_significant BOOLEAN,
    pbo_value DECIMAL,
    pbo_passed BOOLEAN,
    regime_coverage_pct DECIMAL,
    data_integrity_score DECIMAL,
    
    -- Hashes de datos
    universe_hash VARCHAR(64),
    prices_hash VARCHAR(64),
    gaps_hash VARCHAR(64),
    
    -- Paquete de replicación
    replication_package_url VARCHAR(500),
    package_hash VARCHAR(64),
    
    -- Timestamp
    generated_at TIMESTAMP DEFAULT NOW(),
    
    -- Firma digital (opcional)
    digital_signature TEXT
);
```

### 4.2 API Endpoints de Validación

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/validation", tags=["Validation"])

@router.get("/backtest/{backtest_id}/integrity")
async def validate_data_integrity(backtest_id: int):
    """
    Ejecuta validación de integridad de datos.
    """
    validator = DataIntegrityValidator()
    backtest = await get_backtest(backtest_id)
    
    report = validator.validate_universe(
        backtest.start_date,
        backtest.end_date
    )
    
    return {
        'backtest_id': backtest_id,
        'passed': report.all_passed(),
        'checks': report.to_dict()
    }

@router.get("/backtest/{backtest_id}/dsr")
async def calculate_dsr(backtest_id: int):
    """
    Calcula Deflated Sharpe Ratio.
    """
    backtest = await get_backtest(backtest_id)
    optimization = await get_optimization(backtest.optimization_id)
    
    # Obtener estadísticas de todos los trials
    trial_stats = await get_trial_statistics(optimization.id)
    
    validator = StatisticalValidator()
    
    dsr = validator.calculate_deflated_sharpe_ratio(
        estimated_sharpe=backtest.sharpe_ratio,
        sharpe_variance=trial_stats['sharpe_variance'],
        n_trials=trial_stats['n_trials'],
        backtest_length=backtest.trading_days,
        skewness=backtest.returns_skewness,
        kurtosis=backtest.returns_kurtosis
    )
    
    return dsr

@router.get("/backtest/{backtest_id}/pbo")
async def calculate_pbo(backtest_id: int):
    """
    Calcula Probability of Backtest Overfitting.
    """
    backtest = await get_backtest(backtest_id)
    optimization = await get_optimization(backtest.optimization_id)
    
    # Obtener todos los resultados de la optimización
    all_results = await get_all_optimization_results(optimization.id)
    
    validator = StatisticalValidator()
    
    pbo = validator.calculate_probability_of_backtest_overfitting(all_results)
    
    return pbo

@router.get("/backtest/{backtest_id}/regime-coverage")
async def get_regime_coverage(backtest_id: int):
    """
    Verifica cobertura de regímenes de mercado.
    """
    backtest = await get_backtest(backtest_id)
    
    coverage = validate_regime_coverage({
        'start_date': backtest.start_date,
        'end_date': backtest.end_date
    })
    
    return coverage

@router.get("/backtest/{backtest_id}/certificate")
async def generate_validation_certificate(backtest_id: int):
    """
    Genera certificado de validación completo.
    """
    # Ejecutar todas las validaciones
    integrity = await validate_data_integrity(backtest_id)
    dsr = await calculate_dsr(backtest_id)
    pbo = await calculate_pbo(backtest_id)
    regime = await get_regime_coverage(backtest_id)
    
    # Generar paquete de replicación
    audit = AuditTrailGenerator()
    package = audit.generate_replication_package(backtest_id)
    
    # Guardar certificado
    certificate = await save_validation_certificate(
        backtest_id=backtest_id,
        dsr=dsr,
        pbo=pbo,
        regime=regime,
        integrity=integrity,
        package=package
    )
    
    return {
        'certificate_id': certificate.id,
        'backtest_id': backtest_id,
        'validation_passed': (
            integrity['passed'] and
            dsr['is_significant'] and
            not pbo['is_overfit'] and
            regime['passes_minimum']
        ),
        'details': {
            'data_integrity': integrity,
            'deflated_sharpe_ratio': dsr,
            'probability_of_overfitting': pbo,
            'regime_coverage': regime
        },
        'replication_package_hash': package.package_hash,
        'download_url': f"/api/v1/validation/backtest/{backtest_id}/replication-package"
    }

@router.get("/backtest/{backtest_id}/replication-package")
async def download_replication_package(
    backtest_id: int,
    format: str = "csv"
):
    """
    Descarga paquete de replicación para validación externa.
    """
    audit = AuditTrailGenerator()
    
    data = audit.export_for_third_party_validation(
        backtest_id=backtest_id,
        format=format
    )
    
    return Response(
        content=data,
        media_type="application/zip" if format == "csv" else "application/json",
        headers={
            "Content-Disposition": f"attachment; filename=replication_package_{backtest_id}.zip"
        }
    )

@router.post("/hypothesis/register")
async def register_hypothesis(
    hypothesis: HypothesisCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Pre-registra una hipótesis ANTES de ejecutar el backtest.
    """
    registry = HypothesisRegistry()
    
    hypothesis_id = registry.register_hypothesis(
        user_id=current_user.id,
        hypothesis=hypothesis.name,
        expected_sharpe=hypothesis.expected_sharpe,
        rationale=hypothesis.economic_rationale,
        strategy_params=hypothesis.params
    )
    
    return {
        'hypothesis_id': hypothesis_id,
        'registered_at': datetime.now(),
        'message': "Hypothesis registered. You can now run the backtest."
    }
```

---

## 5. MÉTRICAS CIENTÍFICAS

### 5.1 Tabla de Métricas Implementadas

| Métrica | Fórmula | Referencia | Uso |
|---------|---------|------------|-----|
| **Deflated Sharpe Ratio (DSR)** | Φ((SR* - SR₀) / σ_SR) | Bailey & López de Prado (2014) | Detectar si Sharpe es significativo tras múltiples pruebas |
| **Probability of Backtest Overfitting (PBO)** | CSCV method | Bailey et al. (2014) | Probabilidad de que el backtest esté sobreajustado |
| **Minimum Backtest Length (MinBTL)** | f(SR, skew, kurt, conf) | Bailey & López de Prado (2014) | Mínimo histórico necesario para validar |
| **Walk-Forward Efficiency (WFE)** | OOS_return / IS_return | Pardo (2008) | Robustez fuera de muestra |
| **Regime Degradation** | Δ performance entre regímenes | Custom | Consistencia en diferentes mercados |

### 5.2 Umbrales de Aceptación

```python
VALIDATION_THRESHOLDS = {
    # Deflated Sharpe Ratio
    'dsr': {
        'excellent': 0.99,    # >99% confidence
        'good': 0.95,         # >95% confidence
        'acceptable': 0.90,   # >90% confidence
        'minimum': 0.90       # Umbral para pasar
    },
    
    # Probability of Backtest Overfitting
    'pbo': {
        'excellent': 0.10,    # <10% prob overfitting
        'good': 0.25,         # <25%
        'acceptable': 0.50,   # <50%
        'maximum': 0.50       # Umbral para pasar
    },
    
    # Walk-Forward Efficiency
    'wfe': {
        'excellent': 0.80,    # >80% efficiency
        'good': 0.60,         # >60%
        'acceptable': 0.50,   # >50%
        'minimum': 0.50       # Umbral para pasar
    },
    
    # Regime Coverage
    'regime_coverage': {
        'excellent': 0.90,    # >90% de regímenes cubiertos
        'good': 0.70,         # >70%
        'acceptable': 0.60,   # >60%
        'minimum': 0.60       # Umbral para pasar
    },
    
    # Sharpe Ratio (raw) - WARNING levels
    'sharpe_warning': {
        'suspicious': 2.5,    # Sharpe > 2.5 es sospechoso
        'very_suspicious': 3.0,  # Sharpe > 3 casi seguro overfit
        'impossible': 4.0     # Sharpe > 4 es prácticamente imposible
    }
}
```

---

## 6. CHECKLIST DE VALIDACIÓN

### 6.1 Pre-Backtest Checklist

```markdown
## PRE-BACKTEST VALIDATION CHECKLIST

### Data Integrity
- [ ] Universe includes delisted/bankrupt stocks
- [ ] Point-in-time data verified (filing dates, not period ends)
- [ ] No forward-looking data leakage
- [ ] Price data completeness >95%
- [ ] Corporate actions adjusted (splits, dividends)

### Hypothesis Registration
- [ ] Strategy hypothesis documented BEFORE testing
- [ ] Economic rationale specified
- [ ] Expected performance range defined
- [ ] Parameters fixed before backtest

### Configuration
- [ ] Date range covers multiple market regimes
- [ ] Includes at least one major crisis (2008 or 2020)
- [ ] At least 5 years of data (preferably 10+)
- [ ] Cost model configured realistically
- [ ] Slippage model includes spread and market impact
```

### 6.2 Post-Backtest Checklist

```markdown
## POST-BACKTEST VALIDATION CHECKLIST

### Statistical Significance
- [ ] DSR > 0.90 (90% confidence)
- [ ] PBO < 0.50 (less than 50% overfitting probability)
- [ ] Sufficient sample size (MinBTL satisfied)
- [ ] Returns distribution analyzed (skew, kurtosis)

### Robustness
- [ ] Walk-Forward Efficiency > 50%
- [ ] Performance consistent across regimes
- [ ] No single trade dominates returns
- [ ] Drawdown within acceptable limits

### Replicability
- [ ] All parameters documented
- [ ] Random seed recorded (if applicable)
- [ ] Data hashes generated
- [ ] Replication package available
- [ ] Third-party validation possible

### Warnings Addressed
- [ ] Sharpe ratio < 2.5 (or justified if higher)
- [ ] No look-ahead bias detected
- [ ] Survivorship bias accounted for
- [ ] Transaction costs realistic
```

---

## 7. DOCUMENTACIÓN Y AUDITORÍA

### 7.1 Replication Package Contents

```
replication_package_[backtest_id].zip
├── metadata.json           # Config, hashes, validation results
├── strategy_definition.txt # Pseudocódigo de la estrategia
├── trades.csv              # Lista completa de trades
├── daily_returns.csv       # Retornos diarios
├── equity_curve.csv        # Curva de equity
├── universe.csv            # Tickers incluidos (con status)
├── validation_report.txt   # Reporte de validación completo
└── data_sample.csv         # Muestra de datos para verificación
```

### 7.2 Formato de Certificado de Validación

```json
{
  "certificate_id": "TSIS-VAL-2026-001234",
  "backtest_id": 12345,
  "generated_at": "2026-01-15T14:30:00Z",
  
  "strategy": {
    "name": "Gap Fade Strategy v2",
    "params_hash": "sha256:abc123..."
  },
  
  "validation_results": {
    "overall_passed": true,
    
    "data_integrity": {
      "passed": true,
      "survivorship_coverage": "15.2% delisted included",
      "point_in_time_verified": true,
      "data_completeness": "98.7%"
    },
    
    "statistical_significance": {
      "passed": true,
      "deflated_sharpe_ratio": 0.967,
      "interpretation": "Significant (>95% confidence)",
      "n_trials_recorded": 1260
    },
    
    "overfitting_assessment": {
      "passed": true,
      "pbo": 0.23,
      "interpretation": "Good - low probability of overfitting"
    },
    
    "robustness": {
      "passed": true,
      "walk_forward_efficiency": 0.68,
      "regime_coverage": "85% (6 of 7 regimes)",
      "includes_2008_crisis": true,
      "includes_2020_crash": true
    }
  },
  
  "data_hashes": {
    "universe": "sha256:def456...",
    "prices": "sha256:ghi789...",
    "gaps": "sha256:jkl012..."
  },
  
  "replication_package": {
    "url": "/api/v1/validation/backtest/12345/replication-package",
    "hash": "sha256:mno345..."
  }
}
```

---

## 8. COMPARACIÓN CON TRADESTATION

### 8.1 Paridad de Funcionalidades

| Funcionalidad | TradeStation | TSIS.ai | Notas |
|---------------|--------------|---------|-------|
| Walk-Forward Analysis | ✅ | ✅ | Rolling + Anchored |
| Cluster Analysis | ✅ | ✅ | Matrix de runs × OOS% |
| Sensitivity Analysis | ✅ | ✅ | Por parámetro |
| Genetic Optimization | ✅ | ✅ | DEAP library |
| Exhaustive Search | ✅ | ✅ | Grid search |
| **Deflated Sharpe Ratio** | ❌ | ✅ | **Ventaja TSIS** |
| **Probability of Overfitting** | ❌ | ✅ | **Ventaja TSIS** |
| **Pre-registro de hipótesis** | ❌ | ✅ | **Ventaja TSIS** |
| **Audit trail inmutable** | ❌ | ✅ | **Ventaja TSIS** |
| **Paquete de replicación** | ❌ | ✅ | **Ventaja TSIS** |

### 8.2 Garantía de Consistencia

Para garantizar que TSIS produce resultados consistentes con otras plataformas:

1. **Fórmulas Estándar:** Usar exactamente las mismas fórmulas que la industria
2. **Test Suite:** Suite de tests con resultados conocidos
3. **Validación Cruzada:** Comparar resultados con datasets públicos
4. **Documentación:** Documentar cualquier diferencia metodológica

```python
# TEST: Verificar que nuestro Sharpe coincide con estándar
def test_sharpe_ratio_calculation():
    returns = [0.01, -0.02, 0.015, 0.005, -0.01]  # Ejemplo
    
    # Nuestra implementación
    our_sharpe = calculate_sharpe(returns)
    
    # Implementación de referencia (empyrical library)
    import empyrical
    reference_sharpe = empyrical.sharpe_ratio(pd.Series(returns))
    
    assert abs(our_sharpe - reference_sharpe) < 0.001, \
        f"Sharpe mismatch: ours={our_sharpe}, reference={reference_sharpe}"
```

---

## CONCLUSIÓN

Este framework garantiza que TSIS.ai produce resultados:

1. **Científicamente rigurosos** - Basados en metodologías peer-reviewed
2. **Replicables** - Cualquiera puede reproducir los resultados
3. **Auditables** - Trail completo de todas las decisiones
4. **Defendibles** - Documentación para responder a cualquier cuestionamiento

Las ventajas competitivas sobre TradeStation son:

- **DSR y PBO** que detectan falsos positivos estadísticamente
- **Pre-registro de hipótesis** que previene data snooping
- **Paquetes de replicación** para validación externa
- **Audit trail inmutable** para transparencia total

---

**Referencias:**

1. Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio. Journal of Portfolio Management.
2. Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014). The Probability of Backtest Overfitting. Journal of Computational Finance.
3. Pardo, R. (2008). The Evaluation and Optimization of Trading Strategies. Wiley.
4. Harvey, C., & Liu, Y. (2014). Evaluating Trading Strategies. Journal of Portfolio Management.

---

*Documento generado para TSIS.ai*  
*Framework de Validación Científica v1.0*  
*Enero 2026*
