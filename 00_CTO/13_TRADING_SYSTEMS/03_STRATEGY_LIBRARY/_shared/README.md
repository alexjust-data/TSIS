# Strategy Library Shared Utilities

Estado: infraestructura neutral exploratoria.

Esta carpeta existe para evitar dependencias laterales entre estrategias.

Regla:

```text
Las estrategias no importan codigo desde otras estrategias.
```

Si `LONG/DAS`, `LONG/gap&go`, `LONG/Breakout`, `SHORT/*` u otra estrategia
necesitan una utilidad comun, esa utilidad debe vivir aqui o en otra capa
neutral equivalente, no dentro de una estrategia concreta.

Permitido aqui:

- lectura comun de datos;
- helpers de referencia;
- helpers de universo;
- formateo de comandos;
- utilidades de charts;
- utilidades de runs;
- exportacion comun de imagenes.

Prohibido aqui:

- reglas operativas propias de una estrategia;
- thresholds semanticos de una estrategia;
- nombres de eventos propios de una estrategia;
- defaults que solo tengan sentido para una estrategia;
- salidas o runs de una estrategia.

Contrato principal:

```text
03_STRATEGY_LIBRARY/README.md
```
