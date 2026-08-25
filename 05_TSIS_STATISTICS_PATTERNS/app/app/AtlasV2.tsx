'use client';

import { FormEvent, useEffect, useState } from 'react';
import TradingChart, { ContextCandle, ContextEvent } from './TradingChart';

const API = process.env.NEXT_PUBLIC_ATLAS_API ?? 'http://127.0.0.1:8765';
const DEFAULT_LABEL = 'gap_ge_30pct';

interface Meta {
  status: string;
  mode: string;
  counts: Record<string, number>;
}

interface LabelRow {
  activation_family: string;
  activation_label: string;
  label_rows: number;
  tickers: number;
}

interface CohortRow {
  activation_label: string;
  offset_session: number;
  observations: number;
  activation_cases: number;
  tickers: number;
  median_close_from_anchor_pct: number | null;
  p25_close_from_anchor_pct: number | null;
  p75_close_from_anchor_pct: number | null;
  observed_share_red_candle: number | null;
}

interface EventStatRow {
  activation_label: string;
  event_label: string;
  activation_cases: number;
  event_observed: number;
  median_offset: number | null;
  p25_offset: number | null;
  p75_offset: number | null;
}

interface CaseRow {
  activation_case_id: string;
  ticker: string;
  anchor_date: string;
  observed_sessions: number;
  complete_horizon: boolean;
  right_censored: boolean;
  activation_labels: string;
}

interface ActivationRow {
  activation_family: string;
  activation_label: string;
  observed_value: number;
  threshold: number;
}

interface AnnotationRow {
  id: number;
  note: string;
  created_at: string;
}

interface CaseDetail {
  episode: {
    episode_id: string;
    ticker: string;
    anchor_date: string;
    observed_sessions: number;
    complete_horizon: boolean;
    right_censored: boolean;
    horizon_peak_date: string;
    horizon_peak_offset: number;
  };
  context: ContextCandle[];
  trajectory: Array<ContextCandle & { offset_session: number }>;
  events: ContextEvent[];
  activations: ActivationRow[];
  annotations: AnnotationRow[];
}

const pct = (value: number | null | undefined): string =>
  value == null ? '—' : `${(Number(value) * 100).toFixed(1)}%`;
const count = (value: number | null | undefined): string =>
  value == null ? '—' : new Intl.NumberFormat('es-ES').format(Number(value));

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

export default function AtlasV2() {
  const [meta, setMeta] = useState<Meta>();
  const [labels, setLabels] = useState<LabelRow[]>([]);
  const [label, setLabel] = useState(DEFAULT_LABEL);
  const [stats, setStats] = useState<CohortRow[]>([]);
  const [eventStats, setEventStats] = useState<EventStatRow[]>([]);
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [detail, setDetail] = useState<CaseDetail>();
  const [note, setNote] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    void Promise.all([
      json<Meta>(`${API}/api/meta`),
      json<LabelRow[]>(`${API}/api/labels`),
    ])
      .then(([nextMeta, nextLabels]) => {
        setMeta(nextMeta);
        setLabels(nextLabels);
        if (!nextLabels.some((row) => row.activation_label === DEFAULT_LABEL) && nextLabels[0]) {
          setLabel(nextLabels[0].activation_label);
        }
      })
      .catch(() => setError('Inicia la API local del atlas para consultar los datos.'));
  }, []);

  useEffect(() => {
    if (!label) return;
    void Promise.all([
      json<CohortRow[]>(`${API}/api/cohorts?activation_label=${encodeURIComponent(label)}`),
      json<EventStatRow[]>(`${API}/api/event-stats?activation_label=${encodeURIComponent(label)}`),
      json<CaseRow[]>(`${API}/api/cases?activation_label=${encodeURIComponent(label)}&limit=90`),
    ])
      .then(([nextStats, nextEventStats, nextCases]) => {
        setStats(nextStats);
        setEventStats(nextEventStats);
        setCases(nextCases);
      })
      .catch(() => setError('No se pudo cargar la cohorte.'));
  }, [label]);

  const at = (offset: number): CohortRow | undefined =>
    stats.find((row) => row.offset_session === offset);
  const eventAt = (eventLabel: string): EventStatRow | undefined =>
    eventStats.find((row) => row.event_label === eventLabel);

  async function open(caseId: string): Promise<void> {
    setDetail(await json<CaseDetail>(`${API}/api/cases/${caseId}`));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function save(event: FormEvent): Promise<void> {
    event.preventDefault();
    if (!detail || !note.trim()) return;
    await json(`${API}/api/annotations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        episode_id: detail.episode.episode_id,
        note: note.trim(),
        tags: [],
      }),
    });
    setNote('');
    await open(detail.episode.episode_id);
  }

  return (
    <main>
      <header className="top">
        <div><span>TSIS · MÓDULO 05</span><b>Daily Pattern Atlas</b></div>
        <aside className={meta?.status === 'pass' ? 'ok' : ''}>
          <i />{meta ? `${meta.mode} · ${meta.status}` : 'conectando'}
        </aside>
      </header>
      <section className="hero">
        <div>
          <em>CENSO DESCRIPTIVO · 2005–2026</em>
          <h1>De cada cifra<br />a cada vela real.</h1>
          <p>Todas las activaciones daily, sus contextos y outcomes observados. Sin señales, PnL ni inferencia.</p>
        </div>
        <aside>
          <strong>{count(meta?.counts?.activation_case_index)}</strong>
          <b>sesiones activadas</b>
          <span>{count(meta?.counts?.session_observables)} sesiones censadas</span>
        </aside>
      </section>
      {error && <div className="error" role="alert">{error}</div>}
      <section className="shell">
        <nav>
          <b>ACTIVACIÓN</b>
          <select
            value={label}
            onChange={(event) => {
              setDetail(undefined);
              setLabel(event.target.value);
            }}
          >
            {labels.map((row) => (
              <option key={row.activation_label}>{row.activation_label}</option>
            ))}
          </select>
          <small>{labels.find((row) => row.activation_label === label)?.activation_family}</small>
          <b>LECTURA</b>
          <p>Las curvas usan todas las apariciones de la etiqueta, incluso cuando se solapan.</p>
          <ul>
            <li><i className="up" />vela verde</li>
            <li><i className="down" />vela roja</li>
            <li><i className="peak" />pico observado D0–D+20</li>
          </ul>
        </nav>
        <article>
          {!detail ? (
            <>
              <div className="title">
                <div><small>COHORTE ACTIVA · TODAS LAS APARICIONES</small><h2>{label}</h2></div>
                <span>{count(at(0)?.activation_cases)} casos · {count(at(0)?.tickers)} tickers</span>
              </div>
              <div className="metrics">
                <div><span>MEDIANA D+5</span><strong>{pct(at(5)?.median_close_from_anchor_pct)}</strong><small>P25 {pct(at(5)?.p25_close_from_anchor_pct)} · P75 {pct(at(5)?.p75_close_from_anchor_pct)}</small></div>
                <div><span>MEDIANA D+20</span><strong>{pct(at(20)?.median_close_from_anchor_pct)}</strong><small>offset de observación</small></div>
                <div><span>VELAS ROJAS D+5</span><strong>{pct(at(5)?.observed_share_red_candle)}</strong><small>frecuencia observada</small></div>
                <div><span>PICO OBSERVADO</span><strong>D+{eventAt('horizon_peak')?.median_offset ?? '—'}</strong><small>P25 D+{eventAt('horizon_peak')?.p25_offset ?? '—'} · P75 D+{eventAt('horizon_peak')?.p75_offset ?? '—'}</small></div>
                <div><span>PRIMER DÍA ROJO</span><strong>D+{eventAt('first_red_candle_after_d0')?.median_offset ?? '—'}</strong><small>{count(eventAt('first_red_candle_after_d0')?.event_observed)} casos observados</small></div>
              </div>
              <div className="path">
                <header><h3>Trayectoria mediana</h3><p>Cierre respecto a D0</p></header>
                <div>
                  {stats.map((row) => (
                    <i
                      key={row.offset_session}
                      style={{ height: `${Math.max(7, Math.min(90, 48 - Number(row.median_close_from_anchor_pct ?? 0) * 85))}%` }}
                      title={`D+${row.offset_session}: ${pct(row.median_close_from_anchor_pct)}`}
                    />
                  ))}
                </div>
              </div>
              <div className="sub"><h3>Casos que forman esta cifra</h3><span>{cases.length} recientes visibles</span></div>
              <div className="cards">
                {cases.map((row) => (
                  <button key={row.activation_case_id} onClick={() => void open(row.activation_case_id)}>
                    <header><strong>{row.ticker}</strong><small>D0 {row.anchor_date}</small></header>
                    <p>{row.activation_labels.split(',').slice(0, 3).join(' · ')}</p>
                    <footer>
                      <span>{row.observed_sessions} observaciones</span>
                      <b className={row.complete_horizon ? 'complete' : 'censored'}>
                        {row.complete_horizon ? '21 observaciones' : 'censurado'}
                      </b>
                    </footer>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <button className="back" onClick={() => setDetail(undefined)}>← Volver a la cohorte</button>
              <div className="caseTitle">
                <div><small>CASO DE ACTIVACIÓN</small><h2>{detail.episode.ticker} <span>D0 {detail.episode.anchor_date}</span></h2></div>
                <aside>{detail.activations.map((row) => <i key={row.activation_label}>{row.activation_label}</i>)}</aside>
              </div>
              <TradingChart rows={detail.context} events={detail.events} />
              <div className="event-strip">
                {detail.events.map((row) => (
                  <div key={`${row.event_label}-${row.offset_session}`}>
                    <b>D+{row.offset_session}</b><span>{row.event_label}</span>
                  </div>
                ))}
              </div>
              <div className="details">
                <section>
                  <h3>Lectura del caso</h3>
                  <dl>
                    <dt>Pico del horizonte</dt><dd>D+{detail.episode.horizon_peak_offset}</dd>
                    <dt>Observaciones</dt><dd>{detail.episode.observed_sessions}</dd>
                    <dt>Censura derecha</dt><dd>{String(detail.episode.right_censored)}</dd>
                  </dl>
                </section>
                <section>
                  <h3>Anotaciones humanas</h3>
                  <form onSubmit={(event) => void save(event)}>
                    <textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="La nota no altera los datos calculados." />
                    <button>Guardar nota</button>
                  </form>
                  {detail.annotations.map((row) => <p className="note" key={row.id}>{row.note}<small>{row.created_at}</small></p>)}
                </section>
              </div>
            </>
          )}
        </article>
      </section>
    </main>
  );
}
