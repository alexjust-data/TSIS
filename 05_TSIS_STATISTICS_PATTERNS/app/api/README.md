# Local Atlas API

FastAPI read-only sobre un run certificado del Atlas. `server_v2.py` es la
implementación vigente; `server.py` solo mantiene un import compatible. Los
Parquet permanecen inmutables y las notas humanas se guardan aparte en
`annotations.sqlite`.

La API elige el full corregido si existe y, en su defecto, el probe corregido.
`ATLAS_FINAL_ROOT` permite inspeccionar explícitamente otro run.

Endpoints principales: `/api/meta`, `/api/labels`, `/api/cohorts`,
`/api/event-stats`, `/api/cases` y `/api/cases/{activation_case_id}`.
