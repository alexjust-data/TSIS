Tienes razón. La respuesta anterior exageraba inferencias y mezclaba hechos visibles con arquitectura inventada. Voy a rehacerla como una **lectura técnica forense de interfaz**, indicando qué puede afirmarse, qué puede inferirse y qué no sabemos.

# 1. Qué pantalla estamos viendo

Ruta visible:

```text
Operativa
└── Análisis
```

Submódulos hermanos:

```text
Cuenta & Performance
Ejecuciones
Posiciones
Locates
Análisis
```

Esto permite afirmar que la aplicación separa, al menos a nivel de interfaz:

* estado económico de cuenta;
* ejecuciones;
* posiciones;
* gestión de locates;
* análisis agregado.

No demuestra todavía que existan cinco servicios backend independientes. Solo demuestra cinco áreas funcionales.

---

# 2. Filtro por estrategia

Elementos visibles:

```text
Análisis por estrategia
Portfolio (todas las estrategias)
```

Conclusión sólida:

* el sistema soporta más de una estrategia;
* los resultados pueden agregarse en una vista de portfolio;
* el análisis puede filtrarse por una estrategia concreta.

Modelo de datos mínimo probable:

```text
strategy_id
strategy_name
portfolio_scope
```

Para replicarlo en TSIS necesitamos que cada operación conserve obligatoriamente:

```text
strategy_id
strategy_version
```

Sin eso no puede existir un selector fiable por estrategia.

---

# 3. Actualización y generación de informe

Botones:

```text
Refrescar
Informe
```

Mensaje:

```text
Informe HTML generado exitosamente: informe_q8.html
```

Conclusiones sólidas:

* la pantalla no es puramente estática;
* existe una acción de recarga;
* existe exportación o generación de un informe HTML;
* la lógica de informes está conectada al mismo conjunto de datos que alimenta la pantalla.

No podemos afirmar si el HTML lo genera un servicio separado o el mismo proceso GUI.

Contrato técnico mínimo para replicarlo:

```text
AnalyticsQuery
strategy_scope
date_range
return_base

AnalyticsResult
summary_metrics
trade_rows
metadata

ReportRenderer
AnalyticsResult → HTML
```

---

# 4. Filtros temporales

Controles visibles:

```text
Rango
Mensual
TOTAL
Hoy
```

Esto indica al menos cuatro modos de consulta temporal:

* intervalo personalizado;
* mes;
* histórico total;
* sesión actual.

La línea inferior muestra:

```text
Periodo: 2026-04-07T15:30:01-04:00 → 2026-05-07T15:30:02-04:00
```

Pistas técnicas importantes:

* usan timestamps ISO 8601;
* incluyen offset horario `-04:00`;
* la ventana temporal es explícita;
* las métricas dependen del periodo seleccionado.

Para TSIS esto requiere que todas las consultas se hagan con:

```text
start_timestamp
end_timestamp
timezone_basis
```

No bastaría con almacenar fechas sin zona horaria.

---

# 5. Base de retornos

Control visible:

```text
Base retornos: open_eq_periodo
```

Esta es una pista importante, pero debe interpretarse con cautela.

Lo observable:

* las métricas tienen una base de retorno configurable;
* el valor seleccionado se llama `open_eq_periodo`.

Interpretación razonable:

```text
open_eq_periodo
≈ equity al inicio del periodo
```

Podría significar que los retornos, porcentajes o ratios se normalizan respecto a la equity inicial del intervalo consultado.

No podemos saber qué otras opciones tiene el selector.

Para copiar esta capacidad necesitamos definir explícitamente:

```text
return_basis:
opening_equity_period
starting_capital
daily_opening_equity
closed_equity
```

pero las opciones concretas deberán decidirse, no inventarse a partir de la captura.

---

# 6. Métricas visibles

Se leen aproximadamente:

```text
Win Rate      66.7%
PF            2.11
DD Máx       -22.88
PnL Total     60.78
Sharpe         4.67
Sortino       12.31
```

Segunda fila:

```text
PnL bruto     63.05
% ganadoras   80.5%   [etiqueta parcialmente tapada; no segura]
...           12.8%   [etiqueta no legible]
Avg Win        3.60
Avg Loss      -3.41
Mejor Día      2.04%
```

Hay texto superpuesto del vídeo, por lo que no conviene afirmar nombres que no se leen.

Sí podemos asegurar que el sistema calcula:

* win rate;
* profit factor;
* drawdown máximo;
* P&L total;
* Sharpe;
* Sortino;
* ganancia media;
* pérdida media;
* mejor día.

Esto implica que hay datos suficientes para construir:

```text
trade-level returns
daily returns
equity series
drawdown series
gross and net PnL
```

El Sharpe y Sortino no pueden calcularse correctamente solo con una lista de operaciones sin definir una frecuencia de retornos. La presencia de `Base retornos` sugiere que sí existe una serie temporal o una política de construcción de retornos.

---

# 7. Tabla de operaciones cerradas

Columnas visibles:

```text
Entrada
Salida
Símbolo
Lado
Qty
P. Entrada
P. Salida
PnL
R
DD
Origen cierre
```

Esto nos permite reconstruir un esquema mínimo bastante fiable:

```text
trade_id
entry_timestamp
exit_timestamp
symbol
side
quantity
entry_price
exit_price
pnl
r_multiple
drawdown_or_adverse_excursion
close_origin
strategy_id
```

`strategy_id` no aparece en la tabla porque el filtro superior ya delimita la estrategia, pero debe existir en el backend.

---

# 8. Qué significa `R`

La columna `R` está presente, pero en las filas visibles parece vacía.

Podemos afirmar:

* el sistema contempla medir operaciones en unidades de riesgo;
* no todas las operaciones visibles tienen el valor poblado, o la resolución impide verlo.

Para calcular `R` se necesita algo equivalente a:

```text
initial_risk_amount
```

y una convención:

```text
R = pnl / initial_risk_amount
```

Por tanto, si queremos replicar esta función, cada trade debe conservar el riesgo inicial fijado cuando se abre, no recalcularlo después.

Campo necesario:

```text
initial_risk_usd
initial_stop_price
r_multiple
```

---

# 9. Qué puede significar `DD`

En las filas se ven valores como:

```text
0.00
-10.15
-9.65
-8.53
```

No podemos asegurar si es:

* drawdown de la operación;
* MAE monetario;
* drawdown acumulado en el momento del cierre;
* peor P&L flotante de la posición.

Por los valores y por aparecer a nivel de operación, la hipótesis más razonable es:

```text
máxima excursión adversa monetaria
```

o peor drawdown intraoperación.

Pero debe marcarse como inferencia, no hecho.

Para replicarlo correctamente necesitamos distinguir:

```text
mae_usd
mae_pct
mfe_usd
mfe_pct
portfolio_drawdown_at_exit
```

No usar una columna ambigua `DD`.

---

# 10. `Origen cierre`

Valores visibles:

```text
estrategia
orquestador
```

Esto sí es evidencia clara.

Significa que el sistema clasifica quién o qué originó el cierre.

La aplicación distingue al menos:

```text
strategy
orchestrator
```

Esto indica que una posición puede cerrarse:

* por lógica de estrategia;
* por lógica superior del sistema.

La línea superior derecha:

```text
Cierres orquestador: 5 / 48
```

refuerza esa interpretación.

Este dato permite deducir un requisito arquitectónico concreto:

```text
exit_initiator
exit_reason
```

Deben ser campos distintos.

Ejemplo:

```text
exit_initiator = orchestrator
exit_reason = end_of_session
```

o:

```text
exit_initiator = strategy
exit_reason = stop_loss
```

No debemos colapsarlos en una sola cadena.

Enumeración propuesta para TSIS:

```text
exit_initiator:
strategy
risk_engine
orchestrator
operator
broker
reconciliation

exit_reason:
target
stop
timeout
session_close
daily_loss_limit
emergency_stop
stale_data
disconnect
manual_close
```

---

# 11. Qué revela `Cierres orquestador: 5 / 48`

Esto confirma que el sistema contabiliza cierres por componente originador.

No demuestra el motivo exacto de esos cinco cierres.

El orquestador podría cerrar por:

* fin de sesión;
* parada general;
* límite de riesgo;
* reinicio;
* recuperación ante fallo.

La captura no permite elegir entre esas opciones.

Pero sí revela que el orquestador tiene capacidad operativa para iniciar cierres, no solo arrancar y parar procesos.

Eso afecta a la arquitectura:

```text
Strategy
└── puede solicitar cierre

Orchestrator
└── puede forzar cierre global o contextual
```

Ambos deben pasar por el mismo OMS y quedar auditados.

---

# 12. Qué componentes son necesarios para producir esta pantalla

La pantalla exige, como mínimo, estas capacidades backend:

```text
1. Trade Ledger
2. Strategy Registry
3. Analytics Query Layer
4. Metrics Calculator
5. Return Series Builder
6. Report Generator
7. Time-range Filter
8. Exit Attribution
```

No podemos afirmar que cada uno sea una clase o microservicio. Son responsabilidades lógicas.

Flujo mínimo:

```text
fills / positions / orders
    ↓
trade reconstruction
    ↓
closed-trade ledger
    ↓
analytics query
    ↓
metrics + rows
    ↓
GUI / HTML report
```

---

# 13. Qué tablas o artefactos necesita TSIS

Para construir una aplicación equivalente no basta con una tabla `trades`.

Necesitamos al menos:

```text
orders
order_events
fills
positions
closed_trades
account_snapshots
equity_snapshots
strategy_registry
exit_events
analytics_runs
```

Esquema mínimo de `closed_trades`:

```text
trade_id
strategy_id
symbol
side
entry_ts
exit_ts
qty
avg_entry_price
avg_exit_price
gross_pnl
fees
net_pnl
initial_risk_usd
r_multiple
mae_usd
mfe_usd
exit_initiator
exit_reason
orchestrator_action_id
```

Esquema mínimo de `equity_snapshots`:

```text
timestamp
cash
gross_position_value
net_liquidation
realized_pnl
unrealized_pnl
fees
strategy_id_nullable
portfolio_id
```

---

# 14. Qué copiaría de esta pantalla

Funcionalmente:

* filtro por estrategia y portfolio;
* filtros temporales;
* base configurable de retorno;
* métricas resumen;
* tabla de operaciones;
* atribución del cierre;
* informe HTML;
* contador de cierres del orquestador.

No copiaría sin revisar:

* nombres ambiguos como `DD`;
* cálculo de Sharpe sin conocer la frecuencia;
* agregación de operaciones con cantidades parciales;
* `R` si no conserva riesgo inicial;
* métricas de un solo mes presentadas sin tamaño de muestra y advertencias.

---

# 15. Deducción técnica principal

La pista más importante no es la interfaz ni el Sharpe. Es esta combinación:

```text
Origen cierre
+
Cierres orquestador: 5 / 48
```

Eso prueba que el sistema conserva **atribución causal operativa del cierre**.

Para construir algo equivalente, TSIS debe registrar la cadena completa:

```text
decision
→ signal
→ order
→ fill
→ position
→ exit request
→ exit initiator
→ exit reason
→ closing order
→ closing fills
→ reconstructed trade
```

Sin esa cadena, la pantalla puede mostrar P&L, pero no puede explicar correctamente quién cerró la posición ni por qué.

Esta es la lectura técnica defendible de la captura.
