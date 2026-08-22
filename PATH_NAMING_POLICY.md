# TSIS Path and Naming Policy

Estado: `ACTIVE_ROOT_POLICY`

Fecha de adopcion: `2026-08-17`

## 1. Proposito

Esta policy separa dos responsabilidades que antes se estaban intentando
resolver con un unico nombre fisico:

```text
nombre y ruta fisica
= navegacion humana breve y compatibilidad operativa

titulo interno, manifest y contrato
= significado cientifico completo
```

Un nombre largo no garantiza mejor semantica. Cuando se combina con varios
niveles descriptivos puede impedir checkout, copia, movimiento, borrado,
materializacion, certificacion o lectura desde herramientas de Windows.

El objetivo no es convertir TSIS en un arbol de siglas. El objetivo es que un
humano pueda reconocer la carpeta a primera vista y que la ruta completa siga
siendo segura para Windows, Git, PowerShell, Python y herramientas auxiliares.

## 2. Problema comprobado

En la maquina TSIS de referencia se comprobo:

```text
canonical repository root = C:\TSIS_Data
Windows LongPathsEnabled  = 0
PowerShell                = 5.1
Git core.longpaths        = not configured
```

La API Win32 mantiene por defecto `MAX_PATH = 260` caracteres, incluyendo el
terminador nulo. El soporte ampliado requiere simultaneamente configuracion de
Windows y que cada aplicacion sea `longPathAware`; no es una garantia
transversal. Git for Windows tambien evita por defecto checkout de paths que
superan 260 caracteres.

El filesystem puede admitir componentes individuales mucho mayores, pero eso
no resuelve el problema: el riesgo real depende de la suma de raiz, carpetas,
separadores, nombre de archivo, extension y sufijos temporales.

Referencias primarias:

- Microsoft, Maximum Path Length Limitation:
  https://learn.microsoft.com/windows/win32/fileio/maximum-file-path-limitation
- Microsoft, Naming Files, Paths, and Namespaces:
  https://learn.microsoft.com/windows/win32/fileio/naming-a-file
- Git for Windows, release notes and known long-path limitation:
  https://github.com/git-for-windows/build-extra/blob/master/ReleaseNotes.md

El incidente interno de referencia es:

```text
00_CTO/04_MARKET_STATES_CREATION/
02_INFORMATION_OBJECTS/TRADING_ACTIVITY/MODEL_01_MARKED_ACTIVITY/
BINDING_A/03_AUDIT/
TRADING_ACTIVITY_BINDING_A_LONG_PATH_INCIDENT_READOUT_v0_1.md
```

## 3. Presupuesto obligatorio

Para nuevos paths bajo la raiz canonica `C:\TSIS_Data`:

```text
absolute path preferred maximum = 235 characters
absolute path hard maximum      = 240 characters
repository-relative maximum     = 220 characters
directory component maximum     = 40 characters
new file component preferred    = 72 characters
new file component hard maximum = 96 characters
```

El limite operativo de 240 deja margen frente a `MAX_PATH` para terminadores,
sufijos atomicos y diferencias de herramientas. No autoriza a consumir ese
margen sin necesidad; 235 es el objetivo preferido.

El preflight debe medir la ruta final real, no estimar solo el nombre de la
ultima carpeta. Debe incluir los sufijos que el proceso pueda crear, por
ejemplo:

```text
.tmp
.partial
.lock
.checkpoint
```

## 4. Regla de legibilidad

Una ruta primaria debe permitir que un humano identifique, sin descifrar un
jeroglifico:

```text
dominio o capa
Information Object
Representation Model
binding o etapa
tipo de artefacto
```

Se prefieren palabras completas:

```text
TRADING_ACTIVITY
MODEL_01_MARKED_ACTIVITY
BINDING_A
02_MATERIALIZATION
```

No se aceptan como navegacion primaria cadenas como:

```text
TA/RM/MAT
MMS/PLS/OFP
DEV_CERT/IMPL_PROBES
```

Las abreviaturas solo pueden usarse cuando son convenciones de dominio
estables o cuando el README local registra su expansion completa. Una nueva
abreviatura no registrada se considera naming ambiguo.

## 5. Regla para carpetas

Cada segmento nuevo debe:

- describir una sola responsabilidad;
- usar palabras reconocibles;
- evitar repetir palabras ya expresadas por el padre;
- respetar 40 caracteres como maximo;
- evitar wrappers que solo alarguen la ruta;
- utilizar prefijo numerico solo para orden semantico estable.

El prefijo `00_`, `01_`, `02_` no forma parte de la identidad cientifica. Solo
ordena la navegacion dentro de un mismo nivel.

## 6. Regla para archivos

Los archivos nuevos deben usar un nombre compacto y un titulo interno completo.
El nombre fisico no debe intentar contener todo el resumen, estado, metodo,
scope y resultado del documento.

Ejemplo recomendado:

```text
archivo = BINDING_A_PERCENTILE_REPLAY_v0_1.md
titulo interno = Trading Activity Binding A Independent Percentile Replay,
                 Full Execution and Certification Readout v0.1
```

Los IDs exactos, estados de promocion, hashes, scope y lineage deben vivir en
el contenido o manifest, no todos concatenados en el filename.

Los archivos historicos largos quedan `grandfathered`: no se renombran
silenciosamente porque sus nombres pueden estar citados, hasheados o incluidos
en handoffs. Cualquier renombrado futuro exige mapa de migracion y revision de
referencias.

## 7. No depender de configuracion local

Activar `LongPathsEnabled=1` o `core.longpaths=true` puede servir como defensa
secundaria, pero no convierte una ruta larga en portable. Un artefacto TSIS
debe cumplir esta policy sin depender de que cada editor, shell, libreria,
agente o maquina haya realizado ese opt-in.

## 8. Gate obligatorio antes de crear o mover

Toda operacion estructural debe comprobar:

```text
all source paths mapped
all targets unique
no pre-existing collisions
all targets remain under the governed root
maximum final path <= 240
maximum directory component <= 40
new file component <= 96
hash preservation when content is not meant to change
```

Si un path supera el presupuesto, se rediseña la jerarquia. No se resuelve
transformando toda la navegacion en siglas opacas.

## 9. Excepciones

Una excepcion necesita:

- justificacion explicita;
- path y longitud exactos;
- herramientas consumidoras verificadas;
- riesgo downstream;
- owner;
- plazo de correccion o estado `grandfathered`;
- registro en manifest o changelog.

No existe excepcion implicita por el mero hecho de que una herramienta concreta
consiga abrir el archivo.

## 10. Primera aplicacion gobernada

La reorganizacion de:

```text
00_CTO/04_MARKET_STATES_CREATION
```

es la primera aplicacion formal. Su mapa y manifest viven en:

```text
00_CTO/04_MARKET_STATES_CREATION/00_CTO/PATH_MAP_v0_1.csv
00_CTO/04_MARKET_STATES_CREATION/00_CTO/MIGRATION_v0_1.json
```

La fase de traslado preservo nombres y SHA-256. Despues del traslado se
actualizaron de forma intencional los tres entrypoints raiz (`AGENTS.md`,
`README.md` y `CHANGELOG.md`) para que apunten al arbol nuevo.
