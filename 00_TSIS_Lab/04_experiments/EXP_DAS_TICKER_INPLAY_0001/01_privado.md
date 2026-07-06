**No Solo Volumen**

No, humano y AlphaEvolve no deben investigar solo volumen. El volumen era un ejemplo de una familia de confirmación.

Lo que debe investigarse es la definición completa de strategy_inplay_gate.

Familias que deben entrar en el experimento:

price_structure:
first_push_high
dip_depth
rebreak_level
close_above_level
wick_break_vs_body_break
hold_above_level_n_bars

volume_confirmation:
volume vs previous 3/5/10 bars
volume vs dip volume
volume vs first push volume
cumulative volume
volume acceleration

time_structure:
minutes from scanner gate
minutes from push start
minutes from dip
premarket phase
near open vs early premarket

trend_context:
VWAP relation
EMA/Wilder regime
slope
compression/expansion

state_context:
market cap
price
float cuando exista
daily gap
prior volume
liquidity
spread/microstructure cuando exista

execution_context:
tradable range
spread
slippage proxy
volume available after in-play

La Gran Pregunta
La pregunta que te rompe la cabeza es exactamente la pregunta correcta:

¿Cuánto edge/profit existe antes de que la estrategia esté in-play
y cuánto existe después de que esté in-play?

Eso no se contesta con un backtest clásico primero. Primero se contesta con un experimento de descomposición.

Yo lo partiría así:

scanner_to_inplay_opportunity
= movimiento capturable desde scanner gate hasta in-play gate

post_inplay_opportunity
= movimiento capturable después del in-play gate

missed_move
= cuánto movimiento ya ocurrió antes de que la estrategia fuera válida

tradable_after_inplay
= cuánto queda realmente después de confirmar estructura

Luego mides:

MFE desde scanner gate
MAE desde scanner gate
MFE desde in-play gate
MAE desde in-play gate
return 1m/2m/5m/10m/30m después de in-play
failure rate después de in-play
fake breakout rate
continuation rate
time-to-failure
time-to-extension

Nuevo Experimento
La carpeta nueva tiene sentido:

C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_TICKER_INPLAY_0001

Yo crearía ahí documentos nuevos, no mezclaría esto con EXP_DAS_FRONTSIDE_DISCOVERY_0001.

Este experimento no busca “el mejor 50%”. Busca definir científicamente:

¿Cuándo un ticker escaneado pasa a estar in-play para DAS?

Y después:

¿Qué definición de in-play deja más oportunidad real y menos basura?

Orden Correcto

1. EXP_DAS_FRONTSIDE_DISCOVERY_0001
    Descubre/caza tickers frontside interesantes.

2. EXP_DAS_TICKER_INPLAY_0001
    Decide cuándo un ticker cazado por scanner pasa a estrategia in-play.

3. Luego sí:
    backtest clásico sobre reglas candidatas de entrada/salida.

4. Luego:
    AlphaEvolve puede mutar definiciones de in-play, confirmación, ventanas y políticas.

AlphaEvolve no debe empezar buscando una estrategia completa. Primero debe poder proponer variantes de:

qué significa in-play
qué confirma breakout real
qué descarta fake breakout
qué ventana tiene edge
qué estado previo explica continuidad/fallo

Ese es el puente correcto entre scanner, tablas de estado, experimentos y estrategia.