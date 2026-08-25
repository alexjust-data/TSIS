'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type {
  CandlestickData,
  HistogramData,
  IChartApi,
  MouseEventParams,
  Time,
} from 'lightweight-charts';

export interface AdjustedCandle {
  ticker: string;
  date: string;
  o_adjusted: number;
  h_adjusted: number;
  l_adjusted: number;
  c_adjusted: number;
  v: number;
  materialized_price_view: string;
  chart_eligible: boolean;
}

interface HoverState {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const day = (value: string): Time => value.slice(0, 10) as Time;
const number = (value: number): string =>
  new Intl.NumberFormat('es-ES', { maximumFractionDigits: 4 }).format(value);
const count = (value: number): string => new Intl.NumberFormat('es-ES').format(value);

export default function AdjustedTradingChart({ rows }: { rows: AdjustedCandle[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [hover, setHover] = useState<HoverState | null>(null);
  const validRows = useMemo(() => rows.filter((row) => row.chart_eligible), [rows]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || validRows.length === 0) return;
    let disposed = false;
    let observer: ResizeObserver | undefined;

    void import('lightweight-charts').then(
      ({ CandlestickSeries, HistogramSeries, createChart }) => {
        if (disposed) return;
        const chart = createChart(container, {
          width: container.clientWidth,
          height: 620,
          layout: {
            background: { type: 'solid', color: '#12181d' },
            textColor: '#96a0a8',
            panes: {
              separatorColor: '#303a42',
              separatorHoverColor: '#596771',
              enableResize: true,
            },
          },
          grid: {
            vertLines: { color: 'rgba(105, 119, 128, 0.11)' },
            horzLines: { color: 'rgba(105, 119, 128, 0.11)' },
          },
          crosshair: {
            vertLine: { color: '#9ca7ae', labelBackgroundColor: '#36424a' },
            horzLine: { color: '#9ca7ae', labelBackgroundColor: '#36424a' },
          },
          timeScale: {
            borderColor: '#3a444b',
            timeVisible: false,
            secondsVisible: false,
            rightOffset: 6,
            barSpacing: 8,
            minBarSpacing: 0.5,
            lockVisibleTimeRangeOnResize: true,
          },
          rightPriceScale: { borderColor: '#3a444b' },
          handleScale: { axisPressedMouseMove: true, mouseWheel: true, pinch: true },
          handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true },
        });
        chartRef.current = chart;

        const candles = chart.addSeries(CandlestickSeries, {
          upColor: '#31a982',
          downColor: '#df6758',
          wickUpColor: '#31a982',
          wickDownColor: '#df6758',
          borderVisible: false,
          priceLineVisible: false,
        });
        candles.priceScale().applyOptions({ scaleMargins: { top: 0.12, bottom: 0.08 } });

        const volume = chart.addSeries(
          HistogramSeries,
          { priceFormat: { type: 'volume' }, priceLineVisible: false },
          1,
        );
        volume.priceScale().applyOptions({ scaleMargins: { top: 0.12, bottom: 0 } });

        const candleData: CandlestickData<Time>[] = validRows.map((row) => ({
          time: day(row.date),
          open: Number(row.o_adjusted),
          high: Number(row.h_adjusted),
          low: Number(row.l_adjusted),
          close: Number(row.c_adjusted),
        }));
        const volumeData: HistogramData<Time>[] = validRows.map((row) => ({
          time: day(row.date),
          value: Number(row.v),
          color:
            row.c_adjusted >= row.o_adjusted
              ? 'rgba(49, 169, 130, 0.55)'
              : 'rgba(223, 103, 88, 0.55)',
        }));
        candles.setData(candleData);
        volume.setData(volumeData);

        const volumeByDate = new Map(validRows.map((row) => [row.date.slice(0, 10), Number(row.v)]));
        chart.subscribeCrosshairMove((param: MouseEventParams<Time>) => {
          if (!param.time) {
            setHover(null);
            return;
          }
          const candle = param.seriesData.get(candles) as CandlestickData<Time> | undefined;
          if (!candle || !('open' in candle)) return;
          const date = String(param.time);
          setHover({
            date,
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
            volume: volumeByDate.get(date) ?? 0,
          });
        });

        chart.timeScale().fitContent();
        requestAnimationFrame(() => {
          const panes = chart.panes();
          if (panes[0]) panes[0].setHeight(470);
          if (panes[1]) panes[1].setHeight(150);
        });

        observer = new ResizeObserver(([entry]) => {
          chart.applyOptions({ width: Math.floor(entry.contentRect.width) });
        });
        observer.observe(container);
      },
    );

    return () => {
      disposed = true;
      observer?.disconnect();
      chartRef.current?.remove();
      chartRef.current = null;
    };
  }, [validRows]);

  const fitLifetime = () => chartRef.current?.timeScale().fitContent();

  return (
    <section className="trading-chart adjusted-chart" aria-label="Gráfico daily adjusted interactivo sin estadísticas">
      <header className="chart-toolbar">
        <div aria-live="polite">
          {hover ? (
            <>
              <b>{hover.date}</b>
              <span>O {number(hover.open)}</span>
              <span>H {number(hover.high)}</span>
              <span>L {number(hover.low)}</span>
              <span>C {number(hover.close)}</span>
              <span>V {new Intl.NumberFormat('es-ES', { notation: 'compact' }).format(hover.volume)}</span>
            </>
          ) : (
            <span>Precio adjusted · mueve el ratón para OHLCV · rueda para zoom · arrastra para desplazarte</span>
          )}
        </div>
        <aside><button type="button" onClick={fitLifetime}>Vida completa</button></aside>
      </header>
      <div ref={containerRef} className="trading-chart-canvas" />
      <footer>
        {count(validRows.length)} velas ajustadas · {validRows[0]?.date.slice(0, 10)}–{validRows.at(-1)?.date.slice(0, 10)} ·{' '}
        {validRows[0]?.materialized_price_view ?? 'daily_adjusted'} · sin activaciones ni estadísticas
      </footer>
    </section>
  );
}