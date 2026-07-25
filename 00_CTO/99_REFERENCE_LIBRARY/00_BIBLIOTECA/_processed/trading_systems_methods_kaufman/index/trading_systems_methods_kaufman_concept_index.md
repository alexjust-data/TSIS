# Concept Index - Trading Systems and Methods - Perry J. Kaufman

Indice orientado a agentes. Las paginas son aproximadas segun TOC/OCR local.

## Menu

- [Arquitectura de investigacion](#arquitectura-de-investigacion)
- [Indicadores y familias de sistemas](#indicadores-y-familias-de-sistemas)
- [Eventos, patrones e intradia](#eventos-patrones-e-intradia)
- [Testing y optimizacion](#testing-y-optimizacion)
- [Costes, liquidez y riesgo](#costes-liquidez-y-riesgo)
- [Uso recomendado en TSIS](#uso-recomendado-en-tsis)

## Arquitectura de investigacion

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Primero idea, despues herramienta | 1-8 | `hypothesis_id` antes de indicador |
| Perfil de trading system | 6-8 | Define expectativas antes del test |
| Datos, muestras y error | 9-20 | Base de `DataQualityGate` y significancia |
| Estandarizacion de retornos/riesgo | 20-23 | Comparacion entre estrategias |
| Supply and demand / equilibrium | 29-34 | Fundamento economico de modelos |
| Regresion y correlacion | 30-60 | Features, spreads, modelos explicativos |
| ARIMA / series temporales | 55-60 | Research avanzado, no v0.1 |

## Indicadores y familias de sistemas

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Moving averages | 65-81 | Trend features y smoothing |
| Lag, lead y timing | 75-90 | Cuidado con senales no ejecutables |
| Trend systems | 89-125 | Familia `trend_following` |
| Breakouts | 89-125, 281-305 | Familia `breakout` |
| Momentum | 126-133 | Familia `momentum` |
| Oscillators | 133-158 | Familia `countertrend/timing` |
| Momentum con volumen | 144-152 | Feature compuesta precio-volumen |
| Seasonality | 160-188 | Filtros calendario/regimen |
| Cycles | 189-212 | Detrending, spectral/Fourier |
| Charting | 213-236 | Patrones visuales traducibles a reglas |
| Volume/open interest/breadth | 237-255 | Confirmacion y filtros |
| Point-and-figure | 256-280 | Event/bar abstraction, sensitivity |
| Charting systems | 281-304 | Canales, swing, thrust, complex patterns |
| Spreads/arbitrage | 305-333 | Relacion entre activos, carrying charges |

## Eventos, patrones e intradia

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Measuring the news | 334-338 | `EventState` y timestamp de noticia |
| Event trading | 338-344 | Eventos como ciclo, no como columna final |
| Opinion / contrary opinion | 346-350 | Inputs externos con riesgo de data snooping |
| Gaps | 225-226, 394-400, 419-428 | Small caps, opening gap, scanner |
| Time of day | 384-394 | Intraday state y session clock |
| Pattern recognition | 382-418 | Reglas programables vs subjetividad |
| Computer-based pattern recognition | 416-418 | Riesgo de overfitting por combinatoria |
| Day trading | 419-435 | Costes, liquidez, rapidez y disciplina |
| Opening range breakout | 428-435 | Estrategia benchmark para TSIS intradia |

## Testing y optimizacion

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Expectations antes del test | 503-505 | `expected_profile` obligatorio |
| Objetivo de test | 504-505 | No optimizar solo por net profit |
| Identificacion de parametros | 505-506 | `ParameterSpaceRegistry` |
| Parametros continuos/discretos/codificados | 505-506 | Tratamiento distinto en grid search |
| Seleccion de test data | 506-508 | Data contracts y series continuas |
| Busqueda del optimo | 508-510 | Riesgo de picos aislados |
| Visualizar mapas de resultados | 510-517 | Robustez por superficies/mesetas |
| Step-forward testing | 517-519 | Validacion temporal mas realista |
| Out-of-sample | 517-519 | Separar seleccion y verificacion |
| Cambiar reglas tras resultados | 519-520 | Contamina validacion |
| Valid test results | 520-525 | Una prueba/caso no valida sistema |
| Comparar dos sistemas | 527-530 | Evaluacion por perfil, no solo beneficio |
| Retesting | 531-533 | Revalidar al anadir datos |
| Comprehensive studies | 533-546 | Comparacion amplia de familias |
| Price shocks | 546-548, 562-565 | Riesgo de eventos no anticipables |
| Data mining / overoptimization | 548-554 | Registrar variantes y selection path |

## Costes, liquidez y riesgo

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Use/abuse of computer | 555-562 | No confundir potencia con validez |
| Theory of runs | 565-572 | Losing streaks y supervivencia |
| Selective trading | 572-574 | Filtros pueden reducir trades hasta inutilidad |
| System trade-offs | 574-579 | Trend vs countertrend profiles |
| Trading limits | 579-582 | Ejecucion limitada por reglas de mercado |
| Similarity of systems | 583-586 | Diversificacion falsa si sistemas son equivalentes |
| Risk aversion | 587-589 | Perfil del operador/cuenta |
| Liquidity | 589-591 | Crucial para small caps y day trading |
| Measuring risk | 591-596 | Risk metrics de sistema y portfolio |
| Leverage | 596-598 | Capitalizacion y margin-to-equity |
| Diversification | 598-603 | Riesgo conjunto y correlacion |
| Individual trade risk | 603-609 | Stop/risk per trade |
| Market ranking / CSI | 609-614 | Seleccion por oportunidad/riesgo |
| Probability of success and ruin | 614-617 | Ruin analysis |
| Compounding / optimal f | 617-626 | Position sizing agresivo y peligroso |
| Comparing expected and actual results | 626-630 | Live monitoring vs expectativas |

## Uso recomendado en TSIS

| Tarea de agente | Consultar |
|---|---|
| Crear catalogo inicial de estrategias benchmark | Caps. 5, 6, 12, 16 |
| Definir parametro y rango de una estrategia | Cap. 21 |
| Disenar grid search sin sesgo obvio | Cap. 21 |
| Revisar una estrategia sobreoptimizada | Cap. 21 y Cap. 20 advanced methods |
| Crear pruebas walk-forward | Cap. 21 |
| Implementar perfil de performance | Cap. 21-23 |
| Revisar small caps intradia | Cap. 16, 22, 23 |
| Disenar filtros de liquidez/costes | Cap. 16 y 23 |
| Disenar stress por price shocks | Cap. 21-22 |
| Revisar diversificacion real entre estrategias | Cap. 23 similarity/diversification |

