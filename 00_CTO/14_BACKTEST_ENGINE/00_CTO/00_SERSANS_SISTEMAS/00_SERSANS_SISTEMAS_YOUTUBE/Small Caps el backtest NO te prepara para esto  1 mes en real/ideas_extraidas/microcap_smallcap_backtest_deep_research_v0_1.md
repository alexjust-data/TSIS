# Microcap / Smallcap Backtest Deep Research v0.1

Status: `source_note`
Owner layer: `00_CTO`
Target domain: `02_TSIS_BACKTEST_ENGINE`
Created date: 2026-07-23
Companion downloads: `sources_downloaded/`

## Scope

Este documento clona y preserva la respuesta operativa solicitada sobre fuentes especificas para construir backtests de small caps, microcaps, OTC y penny stocks.

No es un contrato promovido. Es una nota fuente para research y arquitectura del futuro backtest engine TSIS.

## Download Policy

Se pueden conservar snapshots de paginas publicas, paginas oficiales, abstracts, landing pages, metadata y documentos de libre acceso. No se deben descargar ni redistribuir libros completos, PDFs con copyright, articulos paywalled ni contenido que requiera licencia. Para esos casos, este paquete conserva URL, cita y razon de no descarga.

## Respuesta Clonada

Tienes razon: lo que buscas no son libros generales de backtesting, sino fuentes **especificas de small caps, microcaps, OTC, penny stocks, delistings, liquidez y ejecucion realista**.

**Core Obligatorio**

1. **Shumway, "The Delisting Bias in CRSP Data"**  
   Base para no inflar backtests de micro/small caps ignorando quiebras, delistings y retornos finales.  
   https://doi.org/10.1111/j.1540-6261.1997.tb03818.x

2. **Shumway & Warther, "The Delisting Bias in CRSP's NASDAQ Data..."**  
   Mas directo para Nasdaq small/micro caps. Recomienda tratar missing delisting returns como sesgo severo.  
   https://papers.ssrn.com/sol3/papers.cfm?abstract_id=11150

3. **Seguin & Smoller, "Share Price and Mortality: Newly Listed Nasdaq Stocks"**  
   Muy util para filtros de bajo precio, mortalidad, attrition y supervivencia.  
   https://doi.org/10.1016/S0304-405X(97)00019-6

4. **Panchapagesan & Werner, "From Pink Slips to Pink Sheets"**  
   Especifico de empresas que caen de Nasdaq a OTC/Pink Sheets. Clave para modelar delisting, spread y caida de volumen.  
   https://papers.ssrn.com/sol3/papers.cfm?abstract_id=565325

5. **Ang, Shtauber & Tetlock, "Asset Pricing in the Dark: The Cross Section of OTC Stocks"**  
   Probablemente el paper mas importante sobre retornos OTC: liquidez, disclosure, retail ownership, short-sale constraints.  
   https://www.nber.org/papers/w19309

6. **Eraker & Ready, "Do Investors Overpay for Stocks with Lottery-Like Payoffs?"**  
   Directo para OTC/penny stocks: skewness, perdidas medias, spreads enormes y lottery preference.  
   https://www.sciencedirect.com/science/article/pii/S0304405X14002372

7. **Joshua White, SEC DERA, "Outcomes of Investing in OTC Stocks"**  
   White paper institucional sobre OTC, promociones, disclosure y resultados reales de inversores.  
   https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2889360

**Small/Micro Cap Factors**

8. **Fama & French, "Dissecting Anomalies"**  
   Separa anomalias por micro, small y big stocks. Muy importante para saber si una senal solo funciona en microcaps iliquidos.  
   https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2008.01371.x

9. **Novy-Marx & Velikov, "A Taxonomy of Anomalies and Their Trading Costs"**  
   Para convertir cualquier backtest microcap en neto de costes.  
   https://www.nber.org/papers/w20721

10. **Muravyev, "Anomalies and Their Short-Sale Costs"**  
    Muy reciente y relevante: muchas anomalias en microcaps dependen de nombres caros o imposibles de shortear.  
    https://doi.org/10.1111/jofi.13501

11. **OSAM, "Microcaps: Factor Spreads, Structural Biases, and the Institutional Imperative"**  
    De las mejores piezas practicas sobre microcap factor investing: calidad, value, momentum, liquidez, capacidad.  
    https://canvas.osam.com/Commentary/BlogPost?Permalink=microcaps-factor-spreads-structural-biases-and-the-institutional-imperative

12. **Asness et al., "Size Matters, If You Control Your Junk"**  
    No es "microcap trading" puro, pero si esencial para small caps: el size premium sin controlar calidad puede ser basura/junk exposure.  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2632685

**Datos Y Mercado**

13. **CRSP US Stock Database / PERMNO / delisting data**  
    Fuente canonica para universo survivor-bias-free y delisting returns.  
    https://www.crsp.org/research/

14. **Kenneth French ME Breakpoints**  
    Para definir micro/small con breakpoints NYSE, no con umbrales arbitrarios.  
    https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/det_me_breakpoints.html

15. **SEC Microcap Stock Guide**  
    Documento regulatorio base: OTC, poca informacion, manipulacion, baja liquidez.  
    https://www.sec.gov/about/reports-publications/investorpubsmicrocapstock

16. **SEC Trading Suspensions**  
    Necesario para backtests event-driven en microcaps/penny stocks.  
    https://www.sec.gov/enforcement-litigation/trading-suspensions

17. **Nasdaq Trading Halt Codes / Halt Search**  
    Para modelar halts, LULD, news pending, compliance halts.  
    https://nasdaqtrader.com/Trader.aspx?id=TradeHaltCodes

18. **FINRA OTC Transparency / Short Sale Volume**  
    Util para OTC volume, off-exchange activity y restricciones short.  
    https://www.finra.org/filing-reporting/otc-transparency  
    https://www.finra.org/finra-data/browse-catalog/short-sale-volume

**Libro Que Si Mantendria**

- **James O'Shaughnessy, _What Works on Wall Street_**  
  No es exclusivo de microcaps, pero si tiene backtests de small/micro cap y advertencias sobre que gran parte del exceso historico viene de nombres demasiado pequenos para ejecutar.  
  https://www.mheducation.com/highered/mhp/product/what-works-wall-street.html

Conclusion practica: para microcaps/smallcaps no hay un "libro de arquitectura de backtester" especifico. La base seria es papers + documentos regulatorios + data vendor docs. Si vas a construir el backtester, estos son los modulos obligatorios: `point-in-time universe`, `delisting engine`, `halt/suspension engine`, `corporate actions`, `spread/slippage`, `participation/capacity`, `shortability/borrow cost`, `OTC tier/disclosure state`, y `promotion/fraud-risk flags`.

## TSIS Implications

Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta

- `point-in-time universe` -> CRSP/PERMNO, Shumway, Shumway & Warther -> incluir securities muertos, cambios de ticker, delistings y retornos finales -> acceso/licencia CRSP puede limitar reconstruccion completa.
- `delisting engine` -> Shumway, Seguin & Smoller, Panchapagesan & Werner -> modelar retorno de salida, transicion a OTC/Pink, suspension y falta de liquidez posterior -> retornos faltantes requieren policy explicita.
- `execution realism` -> Novy-Marx & Velikov, Ang/Shtauber/Tetlock, Eraker & Ready, FINRA/SEC -> penalizar spreads, slippage, volumen utilizable, no fills y capacidad -> quotes historicas completas pueden requerir TAQ/licencias.
- `shortability constraints` -> Muravyev, FINRA short sale volume, Reg SHO/threshold data -> long-short microcap no puede asumir borrow infinito ni coste cero -> borrow fees historicos suelen requerir vendors.
- `OTC disclosure/tier state` -> SEC microcap guide, Rule 15c2-11, OTC Markets tier structure -> estado de disclosure/tier debe ser observable as-of -> datos historicos de tiers pueden requerir licencia OTC Markets.
- `halt/suspension engine` -> SEC trading suspensions, Nasdaq halt codes/search -> backtest intradia debe conocer halts, resumption y no-trade windows -> historico completo de halts puede variar por venue/licencia.

## Sources Download Manifest

Los snapshots locales, cuando existan, viven en:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_SERSANS_SISTEMAS/02_DEEP_RESEACH/sources_downloaded/
```

Archivos de control:

- `sources_downloaded/SOURCE_DOWNLOAD_MANIFEST.md`
- `sources_downloaded/source_download_manifest.json`
- `sources_downloaded/BLOCKED_SOURCE_METADATA_SNAPSHOTS.md`

El manifest generado por descarga debe registrar:

- fuente;
- URL;
- estado: `downloaded_landing_or_public_page`, `metadata_only`, `failed_or_blocked`, `paywalled_or_copyright_limited`;
- ruta local cuando aplique;
- razon de exclusion cuando aplique.

