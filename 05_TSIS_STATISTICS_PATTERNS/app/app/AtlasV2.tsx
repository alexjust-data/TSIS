'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import TradingChart, {
  ActivationOccurrence,
  ContextCandle,
  ContextEvent,
} from './TradingChart';

const API = process.env.NEXT_PUBLIC_ATLAS_API ?? 'http://127.0.0.1:8765';
const DEFAULT_LABEL = 'gap_ge_30pct';
const CASE_PAGE_SIZE = 90;

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

interface FamilyDefinition {
  family: string;
  title: string;
  definition: string;
  formula: string;
  labels: string[];
  caveat: string;
}

interface ActivationCatalog {
  families: FamilyDefinition[];
  family_count: number;
  label_count: number;
  semantics: string;
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
  lifetime_summary: {
    first_observed_date: string | null;
    last_observed_date: string | null;
    observed_sessions: number;
    eligible_sessions: number;
  };
  trajectory: Array<ContextCandle & { offset_session: number }>;
  events: ContextEvent[];
  activations: ActivationRow[];
  selected_activation_label: string;
  occurrences: ActivationOccurrence[];
  annotations: AnnotationRow[];
}

const pct = (value: number | null | undefined): string =>
  value == null ? '—' : `${(Number(value) * 100).toFixed(1)}%`;
const count = (value: number | null | undefined): string =>
  value == null ? '—' : new Intl.NumberFormat('es-ES').format(Number(value));
const isoDay = (value: string | null | undefined): string => value?.slice(0, 10) ?? '—';

const formatActivation = (value: string): string => {
  const threshold = value.match(/_(\d+)(pct|x)$/)?.[1];
  if (value.startsWith('close_advance_ge_')) return `Subida al cierre ≥ ${threshold}%`;
  if (value.startsWith('gap_ge_')) return `Gap de apertura ≥ ${threshold}%`;
  if (value.startsWith('range_ge_')) return `Rango diario ≥ ${threshold}%`;
  if (value.startsWith('relative_volume_ge_')) return `Volumen relativo ≥ ${threshold}×`;
  const breakout: Record<string, string> = {
    high_breakout_previous_day: 'Ruptura del máximo del día previo',
    high_breakout_previous_week: 'Ruptura del máximo de 5 sesiones',
    high_breakout_previous_month: 'Ruptura del máximo de 21 sesiones',
    high_breakout_previous_quarter: 'Ruptura del máximo de 63 sesiones',
    high_breakout_previous_half_year: 'Ruptura del máximo de 126 sesiones',
    high_breakout_previous_year: 'Ruptura del máximo de 252 sesiones',
  };
  return breakout[value] ?? value;
};

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

export default function AtlasV2() {
  const [meta, setMeta] = useState<Meta>();
  const [labels, setLabels] = useState<LabelRow[]>([]);
  const [catalog, setCatalog] = useState<ActivationCatalog>();
  const [label, setLabel] = useState(DEFAULT_LABEL);
  const [stats, setStats] = useState<CohortRow[]>([]);
  const [eventStats, setEventStats] = useState<EventStatRow[]>([]);
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [detail, setDetail] = useState<CaseDetail>();
  const [note, setNote] = useState('');
  const [error, setError] = useState('');
  const [cohortLoading, setCohortLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [moreLoading, setMoreLoading] = useState(false);
  const detailRequest = useRef(0);

  useEffect(() => {
    void Promise.all([
      json<Meta>(`${API}/api/meta`),
      json<LabelRow[]>(`${API}/api/labels`),
      json<ActivationCatalog>(`${API}/api/activation-catalog`),
    ])
      .then(([nextMeta, nextLabels, nextCatalog]) => {
        setMeta(nextMeta);
        setLabels(nextLabels);
        setCatalog(nextCatalog);
        setError('');
        if (!nextLabels.some((row) => row.activation_label === DEFAULT_LABEL) && nextLabels[0]) {
          setCohortLoading(true);
          setLabel(nextLabels[0].activation_label);
        }
      })
      .catch(() => setError('Inicia la API local del atlas para consultar los datos.'));
  }, []);

  useEffect(() => {
    if (!label) return;
    let active = true;
    void Promise.all([
      json<CohortRow[]>(`${API}/api/cohorts?activation_label=${encodeURIComponent(label)}`),
      json<EventStatRow[]>(`${API}/api/event-stats?activation_label=${encodeURIComponent(label)}`),
      json<CaseRow[]>(
        `${API}/api/cases?activation_label=${encodeURIComponent(label)}&limit=${CASE_PAGE_SIZE}&offset=0`,
      ),
    ])
      .then(([nextStats, nextEventStats, nextCases]) => {
        if (!active) return;
        setStats(nextStats);
        setEventStats(nextEventStats);
        setCases(nextCases);
        setError('');
      })
      .catch(() => {
        if (active) setError('No se pudo cargar la cohorte.');
      })
      .finally(() => {
        if (active) setCohortLoading(false);
      });
    return () => {
      active = false;
    };
  }, [label]);

  const at = (offset: number): CohortRow | undefined =>
    stats.find((row) => row.offset_session === offset);
  const eventAt = (eventLabel: string): EventStatRow | undefined =>
    eventStats.find((row) => row.event_label === eventLabel);
  const totalCases = Number(at(0)?.activation_cases ?? 0);

  const currentFamily = useMemo(
    () => catalog?.families.find((family) => family.labels.includes(label)),
    [catalog, label],
  );
  const cataloguedLabels = useMemo(
    () => new Set(catalog?.families.flatMap((family) => family.labels) ?? []),
    [catalog],
  );
  const uncataloguedLabels = labels.filter((row) => !cataloguedLabels.has(row.activation_label));

  function chooseLabel(nextLabel: string, keepDetail: boolean): void {
    setCohortLoading(true);
    setLabel(nextLabel);
    setStats([]);
    setEventStats([]);
    setCases([]);
    if (!keepDetail) setDetail(undefined);
  }

  async function loadDetail(caseId: string, selectedLabel: string): Promise<void> {
    const requestId = ++detailRequest.current;
    setDetailLoading(true);
    try {
      const nextDetail = await json<CaseDetail>(
        `${API}/api/cases/${caseId}?activation_label=${encodeURIComponent(selectedLabel)}`,
      );
      if (requestId !== detailRequest.current) return;
      setDetail(nextDetail);
      setError('');
    } catch {
      if (requestId === detailRequest.current) {
        setError('No se pudo cargar la vida completa de este ticker.');
      }
    } finally {
      if (requestId === detailRequest.current) setDetailLoading(false);
    }
  }

  async function open(caseId: string): Promise<void> {
    await loadDetail(caseId, label);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function selectCaseActivation(nextLabel: string): Promise<void> {
    if (!detail) return;
    chooseLabel(nextLabel, true);
    await loadDetail(detail.episode.episode_id, nextLabel);
  }

  async function loadMore(): Promise<void> {
    if (!label || moreLoading || cases.length >= totalCases) return;
    setMoreLoading(true);
    try {
      const nextCases = await json<CaseRow[]>(
        `${API}/api/cases?activation_label=${encodeURIComponent(label)}&limit=${CASE_PAGE_SIZE}&offset=${cases.length}`,
      );
      setCases((current) => [
        ...current,
        ...nextCases.filter(
          (next) => !current.some((row) => row.activation_case_id === next.activation_case_id),
        ),
      ]);
      setError('');
    } catch {
      setError('No se pudieron cargar más casos.');
    } finally {
      setMoreLoading(false);
    }
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
    await loadDetail(detail.episode.episode_id, detail.selected_activation_label);
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
          <h1>De cada cifra, a cada vela real.</h1>
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
            aria-label="Activación estadística"
            onChange={(event) => chooseLabel(event.target.value, false)}
          >
            {catalog?.families.map((family) => {
              const familyLabels = family.labels
                .map((key) => labels.find((row) => row.activation_label === key))
                .filter((row): row is LabelRow => Boolean(row));
              if (familyLabels.length === 0) return null;
              return (
                <optgroup key={family.family} label={`${family.title} (${familyLabels.length})`}>
                  {familyLabels.map((row) => (
                    <option key={row.activation_label} value={row.activation_label}>
                      {formatActivation(row.activation_label)}
                    </option>
                  ))}
                </optgroup>
              );
            })}
            {uncataloguedLabels.length > 0 && (
              <optgroup label="Sin catalogar">
                {uncataloguedLabels.map((row) => (
                  <option key={row.activation_label} value={row.activation_label}>
                    {formatActivation(row.activation_label)}
                  </option>
                ))}
              </optgroup>
            )}
          </select>
          <small className="technical-label">{label}</small>
          <small>
            {labels.length} de {catalog?.label_count ?? '—'} etiquetas materializadas ·{' '}
            {catalog?.family_count ?? '—'} familias
          </small>

          <b>QUÉ SIGNIFICA</b>
          {currentFamily && (
            <section className="family-definition active-family">
              <strong>{currentFamily.title}</strong>
              <p>{currentFamily.definition}</p>
              <code>{currentFamily.formula}</code>
              <small>{currentFamily.caveat}</small>
            </section>
          )}
          <details className="family-guide">
            <summary>Ver las 5 familias</summary>
            {catalog?.families.map((family) => (
              <section key={family.family} className="family-definition">
                <strong>{family.title}</strong>
                <p>{family.definition}</p>
                <code>{family.formula}</code>
                <small>{family.caveat}</small>
              </section>
            ))}
          </details>

          <b>LECTURA</b>
          <p>{catalog?.semantics}</p>
          <ul>
            <li><i className="up" />vela verde</li>
            <li><i className="down" />vela roja</li>
            <li><i className="occurrence" />ocurrencia de la activación elegida</li>
            <li><i className="peak" />pico observado D0–D+20</li>
          </ul>
        </nav>
        <article aria-busy={cohortLoading || detailLoading}>
          {!detail ? (
            <>
              <div className="title cohort-title">
                <div>
                  <small>COHORTE ACTIVA · TODAS LAS APARICIONES</small>
                  <h2>
                    {formatActivation(label)}
                    <span>{count(at(0)?.activation_cases)} casos · {count(at(0)?.tickers)} tickers</span>
                  </h2>
                  <code>{label}</code>
                </div>
              </div>
              <div className="metrics">
                <div><span>MEDIANA D+5</span><strong>{pct(at(5)?.median_close_from_anchor_pct)}</strong><small>P25 {pct(at(5)?.p25_close_from_anchor_pct)} · P75 {pct(at(5)?.p75_close_from_anchor_pct)}</small></div>
                <div><span>MEDIANA D+20</span><strong>{pct(at(20)?.median_close_from_anchor_pct)}</strong><small>offset de observación</small></div>
                <div><span>VELAS ROJAS D+5</span><strong>{pct(at(5)?.observed_share_red_candle)}</strong><small>frecuencia observada</small></div>
                <div><span>PICO OBSERVADO</span><strong>D+{eventAt('horizon_peak')?.median_offset ?? '—'}</strong><small>P25 D+{eventAt('horizon_peak')?.p25_offset ?? '—'} · P75 D+{eventAt('horizon_peak')?.p75_offset ?? '—'}</small></div>
                <div><span>PRIMER DÍA ROJO</span><strong>D+{eventAt('first_red_candle_after_d0')?.median_offset ?? '—'}</strong><small>{count(eventAt('first_red_candle_after_d0')?.event_observed)} casos observados</small></div>
              </div>
              <div className="sub">
                <h3>Casos que forman esta cifra</h3>
                <span>
                  Mostrando {count(cases.length)} casos más recientes de {count(totalCases)} · orden D0 descendente
                </span>
              </div>
              <div className="cards">
                {cases.map((row) => (
                  <button key={row.activation_case_id} onClick={() => void open(row.activation_case_id)}>
                    <header><strong>{row.ticker}</strong><small>D0 {isoDay(row.anchor_date)}</small></header>
                    <p>{row.activation_labels.split(',').slice(0, 3).map(formatActivation).join(' · ')}</p>
                    <footer>
                      <span>{row.observed_sessions} observaciones</span>
                      <b className={row.complete_horizon ? 'complete' : 'censored'}>
                        {row.complete_horizon ? '21 observaciones' : 'censurado'}
                      </b>
                    </footer>
                  </button>
                ))}
              </div>
              {cases.length < totalCases && (
                <button className="load-more" type="button" onClick={() => void loadMore()} disabled={moreLoading}>
                  {moreLoading ? 'Cargando…' : `Cargar ${Math.min(CASE_PAGE_SIZE, totalCases - cases.length)} casos más`}
                </button>
              )}
            </>
          ) : (
            <>
              <button className="back" onClick={() => setDetail(undefined)}>← Volver a la cohorte</button>
              <div className="caseTitle">
                <div>
                  <small>CASO DE ACTIVACIÓN · VIDA COMPLETA DEL TICKER</small>
                  <h2>{detail.episode.ticker} <span>D0 {isoDay(detail.episode.anchor_date)}</span></h2>
                </div>
                <aside aria-label="Activaciones de esta sesión">
                  {detail.activations.map((row) => (
                    <button
                      type="button"
                      className={row.activation_label === detail.selected_activation_label ? 'selected' : ''}
                      aria-pressed={row.activation_label === detail.selected_activation_label}
                      title={row.activation_label}
                      key={row.activation_label}
                      onClick={() => void selectCaseActivation(row.activation_label)}
                    >
                      {formatActivation(row.activation_label)}
                    </button>
                  ))}
                </aside>
              </div>
              <p className="chart-selection">
                Marcando {count(detail.occurrences.length)} ocurrencias de{' '}
                <strong>{formatActivation(detail.selected_activation_label)}</strong> entre{' '}
                {isoDay(detail.lifetime_summary.first_observed_date)} y{' '}
                {isoDay(detail.lifetime_summary.last_observed_date)}.
              </p>
              <TradingChart
                rows={detail.context}
                events={detail.events}
                occurrences={detail.occurrences}
                selectedLabel={detail.selected_activation_label}
                anchorDate={detail.episode.anchor_date}
              />
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
                    <dt>Horizonte observado</dt><dd>{detail.episode.observed_sessions} sesiones</dd>
                    <dt>Vida disponible</dt><dd>{count(detail.lifetime_summary.observed_sessions)} sesiones</dd>
                    <dt>Sesiones elegibles</dt><dd>{count(detail.lifetime_summary.eligible_sessions)}</dd>
                    <dt>Censura derecha D+20</dt><dd>{detail.episode.right_censored ? 'sí' : 'no'}</dd>
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
