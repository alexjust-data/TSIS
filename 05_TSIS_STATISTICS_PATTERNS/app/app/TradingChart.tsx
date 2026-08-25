'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type {
  CandlestickData,
  HistogramData,
  IChartApi,
  MouseEventParams,
  SeriesMarker,
  Time,
} from 'lightweight-charts';

export interface ContextCandle {
  date: string;
  o_split_normalized: number;
  h_split_normalized: number;
  l_split_normalized: number;
  c_split_normalized: number;
  v: number;
  analysis_eligible: boolean;
  quality_state: string;
  relative_offset: number;
}

export interface ContextEvent {
  event_date: string;
  event_label: string;
  offset_session: number;
}

export interface ActivationOccurrence {
  date: string;
  activation_family: string;
  activation_label: string;
  observed_value: number;
  threshold: number;
}

interface HoverState {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const shortEvent: Record<string, string> = {
  horizon_peak: 'PEAK',
  first_red_candle: 'FR',
  first_red_candle_after_d0: 'FR>D0',
  first_lower_close: 'LC',
  first_lower_high: 'LH',
  first_day_without_new_episode_high: 'NO HH',
};

const day = (value: string): Time => value.slice(0, 10) as Time;
const number = (value: number): string =>
  new Intl.NumberFormat('es-ES', { maximumFractionDigits: 4 }).format(value);
const count = (value: number): string => new Intl.NumberFormat('es-ES').format(value);

export default function TradingChart({
  rows,
  events,
  occurrences,
  selectedLabel,
  anchorDate,
}: {
  rows: ContextCandle[];
  events: ContextEvent[];
  occurrences: ActivationOccurrence[];
  selectedLabel: string;
  anchorDate: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [hover, setHover] = useState<HoverState | null>(null);
  const validRows = useMemo(() => rows.filter((row) => row.analysis_eligible), [rows]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || validRows.length === 0) return;
    let disposed = false;
    let observer: ResizeObserver | undefined;

    void import('lightweight-charts').then(
      ({ CandlestickSeries, HistogramSeries, createChart, createSeriesMarkers }) => {
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
        candles.priceScale().applyOptions({ scaleMargins: { top: 0.2, bottom: 0.14 } });

        const volume = chart.addSeries(
          HistogramSeries,
          { priceFormat: { type: 'volume' }, priceLineVisible: false },
          1,
        );
        volume.priceScale().applyOptions({ scaleMargins: { top: 0.12, bottom: 0 } });

        const candleData: CandlestickData<Time>[] = validRows.map((row) => ({
          time: day(row.date),
          open: Number(row.o_split_normalized),
          high: Number(row.h_split_normalized),
          low: Number(row.l_split_normalized),
          close: Number(row.c_split_normalized),
        }));
        const volumeData: HistogramData<Time>[] = validRows.map((row) => ({
          time: day(row.date),
          value: Number(row.v),
          color:
            row.c_split_normalized >= row.o_split_normalized
              ? 'rgba(49, 169, 130, 0.55)'
              : 'rgba(223, 103, 88, 0.55)',
        }));
        candles.setData(candleData);
        volume.setData(volumeData);

        const groupedEvents = new Map<string, string[]>();
        for (const event of events) {
          const key = event.event_date.slice(0, 10);
          groupedEvents.set(key, [
            ...(groupedEvents.get(key) ?? []),
            shortEvent[event.event_label] ?? event.event_label,
          ]);
        }
        const anchorDay = anchorDate.slice(0, 10);
        const occurrenceDays = new Set(occurrences.map((row) => row.date.slice(0, 10)));
        const markers: SeriesMarker<Time>[] = [
          ...[...occurrenceDays].map((date) => ({
            time: day(date),
            position: 'belowBar' as const,
            color: date === anchorDay ? '#4fa3d1' : '#4cc9b0',
            shape: date === anchorDay ? ('arrowUp' as const) : ('circle' as const),
            text: date === anchorDay ? 'D0' : '',
            size: date === anchorDay ? 1.2 : 0.55,
          })),
          ...(!occurrenceDays.has(anchorDay)
            ? [{
                time: day(anchorDay),
                position: 'belowBar' as const,
                color: '#4fa3d1',
                shape: 'arrowUp' as const,
                text: 'D0',
                size: 1.2,
              }]
            : []),
          ...[...groupedEvents.entries()].map(([date, labels]) => ({
            time: day(date),
            position: 'aboveBar' as const,
            color: labels.includes('PEAK') ? '#e1b642' : '#9b87df',
            shape: labels.includes('PEAK') ? ('arrowDown' as const) : ('circle' as const),
            text: labels.join(' · '),
            size: 1,
          })),
        ].sort((a, b) => String(a.time).localeCompare(String(b.time)));
        createSeriesMarkers(candles, markers, { autoScale: true });

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
  }, [anchorDate, events, occurrences, selectedLabel, validRows]);

  const centerD0 = () => {
    const anchorIndex = Math.max(
      0,
      validRows.findIndex((row) => row.date.slice(0, 10) === anchorDate.slice(0, 10)),
    );
    chartRef.current?.timeScale().setVisibleLogicalRange({
      from: Math.max(-0.5, anchorIndex - 55),
      to: Math.min(validRows.length - 0.5, anchorIndex + 30),
    });
  };

  const fitLifetime = () => chartRef.current?.timeScale().fitContent();

  return (
    <section className="trading-chart" aria-label="Gráfico daily interactivo de vida completa con volumen">
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
            <span>Mueve el ratón para consultar OHLCV · rueda para zoom · arrastra para desplazarte</span>
          )}
        </div>
        <aside>
          <button type="button" onClick={fitLifetime}>Vida completa</button>
          <button type="button" onClick={centerD0}>Centrar D0</button>
        </aside>
      </header>
      <div ref={containerRef} className="trading-chart-canvas" />
      <footer>
        {count(validRows.length)} velas elegibles · {validRows[0]?.date.slice(0, 10)}–{validRows.at(-1)?.date.slice(0, 10)} ·{' '}
        {count(occurrences.length)} marcas de {selectedLabel} · volumen inferior · Charts by TradingView Lightweight Charts™
      </footer>
    </section>
  );
}
