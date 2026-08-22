# Core Market RAW Alignment Audit Schema Contract v0.1

Fecha: 2026-08-21  
Estado: `PROVISIONAL_EXECUTABLE_CONTRACT`  
Grain de tarea: `family × target_ticker`

Este contrato gobierna los outputs del auditor físico read-only. No gobierna
el schema económico de los cuatro RAW.

## Inventario Parquet

Una fila por Parquet fuente:

```text
family                         string not null
ticker                         string not null
absolute_path                  string not null
relative_path                  string not null
file_exists                    bool not null
file_size_bytes                int64 not null
magic_header_ok                bool not null
magic_footer_ok                bool not null
parquet_openable               bool not null
metadata_readable              bool not null
metadata_num_rows              int64 not null
row_group_count                int32 not null
schema_readable                bool not null
schema_fingerprint             string nullable
schema_columns_json            string not null
missing_required_columns_json  string not null
extra_columns_json             string not null
required_schema_complete       bool not null
date_extraction_method         string not null
observed_date_count            int32 not null
first_observed_date            date32 nullable
last_observed_date             date32 nullable
out_of_scope_date_count        int32 not null
error_class                    string nullable
error_message                  string nullable
```

## Ticker-date Parquet

Grain único: `family × ticker × observed_date`.

```text
family         string not null
ticker         string not null
observed_date  date32 not null
```

## Ticker-family coverage Parquet

Grain único: un ticker objetivo. Para cada familia se conservan:

```text
<family>_directory_exists
<family>_file_count
<family>_date_count
<family>_first_date
<family>_last_date
<family>_error_file_count
```

Campos terminales:

```text
all_target_directories_present  bool
all_families_have_dates         bool
first_date_equal                bool
last_date_equal                 bool
window_equal                    bool
observed_date_set_equal         bool
```

`window_equal` y `observed_date_set_equal` solo pueden ser `true` si las cuatro
familias tienen fechas.

## Diferencias ticker-date

Grain único: `ticker × observed_date` cuando la presencia no coincide:

```text
ticker                     string
observed_date              date32
present_in_ohlcv_daily     bool
present_in_ohlcv_1m        bool
present_in_quotes          bool
present_in_trades          bool
present_family_count       int8
missing_family_count       int8
```

## Compatibilidad

Un cambio de nombre, tipo, nulabilidad, grain o interpretación requiere nueva
versión del contrato, tests, probe production-equivalent y manifest distinto.
Añadir una familia nueva también es breaking para este contrato de cuatro
familias.
