# Full Run Closeout v0.1

## Dictamen

`20260825_full_v0_1` termina con:

- operación: `pass`;
- certificación terminal: `pass`;
- auditoría independiente: `pass`;
- app/API smoke: `pass`;
- estado máximo concedido: `exploratory_report_ready`.

Este cierre autoriza el consumo descriptivo y visual del censo. No promociona
probabilidad, estrategia, señal, PnL ni conocimiento validado.

## Scope reconciliado

- tickers: 4.824;
- sesiones: 9.290.966;
- fechas: 2005-01-03 a 2026-03-06;
- ficheros raw distintos: 44.423;
- ticker-fecha ausentes: 0;
- ticker-fecha adicionales: 0.

## Outputs principales

- etiquetas de activación: 9.728.326;
- casos de activación distintos: 4.495.723;
- ciclos cooldown: 422.042;
- trayectorias de ciclos: 8.817.239;
- eventos de ciclos: 2.529.142;
- cohortes directas: 567 filas;
- estadísticas directas de eventos: 162 filas.

## Calidad

- outcomes o eventos sobre filas inválidas: 0;
- picos sobre filas inválidas: 0;
- mismatches de running high y peak: 0;
- variantes de schema por tabla: 1 en 4.824 parts;
- infinitos en outputs finales: 0;
- fórmulas independientes auditadas: 12/12 `pass`, error máximo 0;
- reconciliación D0 de cohortes directas: 0 mismatches;
- reconciliación de casos en eventos directos: 0 mismatches.

## Evidencia

- `runs/20260825_full_v0_1/operation_final_manifest.json`;
- `runs/20260825_full_v0_1/final/terminal_certification.json`;
- `runs/20260825_full_v0_1/final/probe_variable_audit_v0_1.json`;
- `FINAL_CENSUS_READOUT_v0_2.md` y `.json`.
## Cautela de trazabilidad

El premanifest histórico registró siete rutas dirty sin enumerarlas. Los hashes
de config, runner y upstream coinciden y el delta comprometido autorizado es
solo documental, pero la omisión reduce la evidencia forense del worktree.
`INC-20260825-011` lo declara; futuras ejecuciones ya persistirán entradas,
rutas y fingerprint porcelain. Esta limitación no eleva ni reduce el resultado
más allá de `exploratory_report_ready`.
