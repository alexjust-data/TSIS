# Third-Party Evidence

Esta carpeta guarda evidencia externa cacheada para tests independientes.

La finalidad es evitar que los tests dependan de internet por defecto y, a la
vez, permitir comprobaciones contra fuentes externas.

## Ejemplos de evidencia

- SEC EDGAR submissions snapshot para una muestra de CIKs.
- NYSE/Nasdaq holiday or hours snapshot.
- OpenFIGI response snapshot.
- Documentacion de proveedor certificada.
- Hash, timestamp y URL de descarga.

## Reglas

- La evidencia debe ser pequena y trazable.
- Cada snapshot debe declarar fuente, fecha y metodo de captura.
- Los tests en vivo contra internet deben ser opt-in.
- Si una fuente cambia, crear nuevo snapshot versionado; no sobrescribir
  silenciosamente evidencia historica.

