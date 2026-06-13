**prompt de inicio:**


Te tienes que poner al día con este proyecto:

C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\ARCHITECTURE_OVERVIEW.md
C:\TSIS_Data\CHANGELOG.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\README.md

Dentro hemos ido trabajando en la auditoría de la data descargada desde Polygon:

C:\TSIS_Data\01_TSIS_backtest_SmallCaps\README.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\AGENTS.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\LOCAL_RULES.md

Lee todos esos archivos completos y ponte al día antes de hacer cualquier otra cosa. Cuando los hayas leído y entendido, responde solo: ok.

IMPORTANTE SOBRE EL ENTORNO:
Los archivos están en C:\TSIS_Data, fuera del workspace principal C:\Users\AlexJ. En la sesión anterior, las lecturas normales dentro del sandbox
se quedaron colgadas incluso con pruebas mínimas como:

Test-Path -LiteralPath 'C:\TSIS_Data\PROJECT_RULES.md'

Esa misma prueba ejecutada con `sandbox_permissions: "require_escalated"` respondió en 0.3s con `True`.

Por tanto, no intentes leer esos archivos con comandos sandboxed normales porque puede parecer que estás “leyendo” durante muchos minutos, pero en
realidad el wrapper se queda bloqueado. Usa directamente comandos con `require_escalated` para las lecturas de C:\TSIS_Data. Hazlo de forma
eficiente, archivo por archivo o en bloques razonables, pero lee el contenido completo.


