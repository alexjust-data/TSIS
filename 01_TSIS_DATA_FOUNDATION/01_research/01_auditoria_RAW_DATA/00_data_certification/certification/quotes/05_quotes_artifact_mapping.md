# Quotes Artifact Mapping

## Artefactos que si mandan

Para `quotes`, los artefactos que realmente importan para la certificacion son estos:

- dataset base
  - `quotes_current_cd_merged\quotes_current.parquet`
- builder
  - `auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py`
- metodologia
  - `auditoria\quotes\v2\04_quotes_full_C_D_methodology.md`
- closeout
  - `auditoria\quotes\v2\04_quotes_full_C_D_closeout.md`
- crosswalk
  - `auditoria\05_crosswalk_multidataset.md`

## Que sale ya de `auditoria`

- presencia observada
  - del parquet materializado
- criterio local de calidad
  - del `closeout`
- taxonomia y buckets
  - del flujo `v2`
- explicacion transversal
  - del `crosswalk` y de los bloques soporte

## Que no sale todavia listo

No existe todavia un artefacto unico y final de certificacion para `quotes` que una:

- cobertura esperada
- presencia observada
- calidad local
- explicacion transversal
- uso final

## Conclusion

El trabajo pendiente no es reauditar `quotes`.
Es ensamblar en una sola salida lo que ya esta repartido entre `auditoria\quotes\v2`, `01_auditoria_1B_general` y `05_crosswalk_multidataset`.
