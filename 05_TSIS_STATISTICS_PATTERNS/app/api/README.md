# Local Atlas API

FastAPI read-only sobre un run certificado del Atlas. `server_v2.py` es la
implementación vigente; `server.py` solo mantiene un import compatible. Los
Parquet permanecen inmutables y las notas humanas se guardan aparte en
`annotations.sqlite`.

La API elige el full más reciente solo cuando su certificación terminal es
`pass`; si no existe un full PASS, usa el probe PASS más reciente. Un run
incompleto, fallido o con certificación ilegible nunca alimenta los endpoints
de datos. `ATLAS_FINAL_ROOT` permite seleccionar explícitamente otro run,
pero también exige certificación terminal PASS.

Endpoints principales: `/api/meta`, `/api/labels`, `/api/cohorts`,
`/api/event-stats`, `/api/cases` y `/api/cases/{activation_case_id}`.
