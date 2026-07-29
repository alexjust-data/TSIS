No hacemos primero “la guía completa” y después el backtester.

Tampoco programamos a ciegas y dejamos la documentación para el final.

Hacemos dos artefactos vivos, pero el que manda es el backtester.
```
BACKTEST_VERTICAL_SLICE_V0_1
    = lo que vamos construyendo y probando en codigo

TSIS_PROFESSIONAL_TRADING_SYSTEMS_GUIDE
    = el cuaderno estructurado donde queda explicado lo que ya hemos decidido,
    de donde sale, que estado tiene y que queda pendiente
```
Ejemplo concreto:

Si vamos a implementar OrderIntent:
```
1. Miramos qué dicen Sersan, QuantStart/SAT, Pardo, Chan, Harris.
2. Tomamos una decisión mínima TSIS:

    Signal != Decision != OrderIntent != Order != Fill

3. Lo implementamos en el vertical slice.
4. Hacemos un test.
5. En la guía viva queda una sección corta:

    Estado: TSIS_VALIDATED_CONTRACT
    Decision: separar Signal, Decision, OrderIntent, Order y Fill
    Evidencia: Sersan + SAT + Harris + test TSIS
    Archivo/test: ...
```
Pero si hablamos de locates para shorts y todavía no lo implementamos:
```
Estado: TSIS_DECISION_PENDING
Fuente: Sersan small caps + Harris/Chan
Motivo: en small caps short una señal no implica disponibilidad
Decision TSIS: pendiente
Implementacion: no incluida en v0.1
```
Así evitamos dos errores:
```
Error 1:
escribir una biblia antes de tener un backtest funcionando

Error 2:
programar sin dejar rastro de por qué se tomó cada decisión
```


####


He cerrado el incremento de contabilidad mínima.

  Estado actual:

  DATA = PASS
  REPLAY_FEED = PASS
  MECHANICAL_TRADE_PATH = PASS
  ACCOUNTING_MINIMUM = PASS
  BACKTEST_VERTICAL_SLICE = ACCOUNTING_VERTICAL_SLICE_CLOSED
  BROKER_COST_REALISM = NOT_CLAIMED
  FILL_REALISM = NOT_CLAIMED
  SHORT_TRADABILITY = NOT_EVALUATED
  EDGE = NOT_EVALUATED

  Implementado:

  C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/accounting/

  Artefactos reales generados:

  C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/accounting_abat_short_open_close_v0_1/

  Resultado ABAT:

  quantity = 100
  entry_price = 3.87
  exit_price = 4.665
  gross_pnl = -79.50
  total_costs = 2.00
  realized_net_pnl = -81.50
  ending_equity = 9918.50
  final_position_quantity = 0

  Verificación:

  Ran 61 tests
  OK

  También corregí un detalle importante: CostModel.to_dict() ahora conserva tasas sub-cent como
  commission_per_share = 0.005 en el manifest, en vez de redondearlas a 0.01.

  Documentación actualizada:

  C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/08_ACCOUNTING.md
  C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/README.md
  C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/AGENT.md
  C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/CHANGELOG.md
  C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/README.md
  C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/AGENTS.md
  C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/CHANGELOG.md

  Limpiado:

  script temporal eliminado
  6 __pycache__ eliminados

  Siguiente paso razonable: elegir un incremento acotado: varios símbolos del fixture, primer
  contrato de execution semantics/cost realism, o un manifest único que encadene preflight ->
  replay -> mechanics -> accounting.