# DETERMINISTIC_FILL_SIMULATOR_V0_1 — IMPLEMENTATION AUTHORIZATION

## 1. Identificación

authorization_id: BT-GATE-009
capability_id: DETERMINISTIC_FILL_SIMULATOR_V0_1
status: AUTHORIZED_FOR_BOUNDED_IMPLEMENTATION
authorized_contract:
  EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1
contract_status:
  CLOSED_REVIEWED_READY_FOR_BOUNDED_IMPLEMENTATION_AUTHORIZATION
authorization_version: 0.1
authorization_date: 2026-07-29
current_gate_status: CLOSED_PASS_AUTHORIZATION_GRANTED
code_implementation_status: AUTHORIZED_FOR_DETERMINISTIC_FILL_SIMULATOR_V0_1_ONLY

## 2. Propósito

Este documento autoriza la implementación, prueba y validación de una primera
capacidad determinista de simulación de fills basada exclusivamente en el
contrato cerrado:

EXECUTION_SEMANTICS_AND_COST_MODEL_CONTRACT_V0_1.

La autorización permite convertir dicho contrato en código ejecutable y generar
evidencia reproducible de conformidad.

Esta autorización no modifica, amplía ni sustituye el contrato semántico
cerrado.

## 3. Capacidad autorizada

Se autoriza implementar un simulador determinista mínimo capaz de:

- recibir órdenes y datos de barras admitidos por el contrato;
- determinar la elegibilidad temporal de cada barra;
- evaluar las órdenes soportadas;
- producir resultados de evaluación y resultados terminales canónicos;
- calcular precios de ejecución, slippage y costes deterministas;
- aplicar expiración DAY;
- producir trazas, manifests y evidencia reproducible;
- fallar de forma cerrada ante inputs o configuraciones no admitidos.

## 4. Alcance funcional autorizado

La implementación V0.1 queda limitada a las capacidades definidas por el
contrato cerrado:

- MARKET_PROXY;
- LIMIT;
- STOP_MARKET_PROXY;
- FULL_FILL_ONLY;
- time_in_force = DAY;
- bar_based_execution_profile_v0_1;
- slippage determinista autorizado por el contrato;
- desglose determinista de costes autorizado por el contrato;
- política de tick declarada por el contrato;
- EVALUATION_OUTCOME canónico;
- TERMINAL_ORDER_OUTCOME canónico;
- política de barras ambiguas definida por el contrato;
- manejo contractual de gaps, precios ausentes e inputs inválidos.

La implementación debe reproducir las reglas del contrato sin introducir
semánticas alternativas.

## 5. Libertad de implementación

Dentro del alcance anterior, el agente está autorizado para:

- crear módulos, clases, funciones, tipos y adaptadores internos;
- crear esquemas y modelos de datos necesarios;
- crear fixtures y generadores de casos de prueba;
- crear utilidades de serialización, hashing, validación y comparación;
- crear CLI o entry points técnicos mínimos para ejecutar las pruebas y gates;
- refactorizar código nuevo de V0.1;
- modificar componentes existentes cuando sea necesario para integrar la
  capacidad autorizada, siempre que no cambie capacidades previamente cerradas;
- elegir la organización interna más adecuada;
- añadir validaciones defensivas y errores explícitos;
- añadir tests adicionales más allá del mínimo obligatorio;
- corregir defectos encontrados durante la implementación cuando la corrección
  no modifique el contrato ni amplíe el alcance autorizado.

La autorización se concede por capacidad y frontera funcional, no por una lista
cerrada de nombres de archivos.

## 6. Áreas del repositorio autorizadas

Pueden modificarse:

- el paquete o área del motor de ejecución;
- modelos y esquemas directamente necesarios para órdenes, fills, costes y
  outcomes;
- tests unitarios, de integración, determinismo y aceptación;
- fixtures y datos sintéticos de prueba;
- scripts de validación;
- configuración específica del simulador V0.1;
- documentación técnica del incremento;
- README, AGENTS.md y CHANGELOG aplicables;
- governance de 00_CTO/14_BACKTEST_ENGINE;
- manifests y artefactos de trazabilidad;
- directorios de runs o evidencias destinados a este gate.

Las modificaciones fuera de estas áreas solo están permitidas cuando sean
estrictamente necesarias para integrar la capacidad autorizada y no activen
capacidades actualmente cerradas.

Toda modificación incidental deberá declararse en el informe final.

## 7. Requisitos normativos

La implementación debe:

- ajustarse al contrato cerrado sin reinterpretaciones;
- producir el mismo resultado ante los mismos inputs y configuración;
- utilizar configuración explícita y versionada;
- evitar dependencias de reloj real, estado global no controlado o aleatoriedad
  no fijada;
- utilizar aritmética y redondeo definidos por el contrato;
- separar EVALUATION_OUTCOME de TERMINAL_ORDER_OUTCOME;
- conservar la evidencia de evaluaciones intermedias;
- fallar de forma cerrada ante órdenes, políticas o datos no autorizados;
- registrar las versiones de contrato, perfil, costes, slippage y política de
  tick utilizadas;
- generar outputs serializables y verificables mediante hash.

## 8. Tests obligatorios

Como mínimo deben existir pruebas para:

### 8.1 Elegibilidad temporal

- orden anterior al inicio de la barra;
- orden exactamente en source_bar.ts_start;
- orden posterior a source_bar.ts_start;
- prohibición de utilizar barras anteriores a la activación;
- expiración DAY.

### 8.2 MARKET_PROXY

- fill válido;
- precio requerido ausente;
- gap de replay;
- precio resultante no positivo;
- comportamiento de compra y venta.

### 8.3 LIMIT

- buy limit tocado;
- buy limit no tocado;
- sell limit tocado;
- sell limit no tocado;
- barra no elegible;
- gap y precio ausente;
- barra ambigua cuando sea aplicable.

### 8.4 STOP_MARKET_PROXY

- buy stop activado;
- sell stop activado;
- stop no activado;
- barra no elegible;
- gap y precio ausente;
- secuencia intrabar ambigua.

### 8.5 Outcomes

- FULL_FILL;
- NO_FILL_NOT_ELIGIBLE;
- NO_FILL_MISSING_PRICE;
- NO_FILL_GAP;
- FAIL_AMBIGUOUS_BAR;
- REJECTED_BY_CONTRACT;
- FILLED;
- EXPIRED_UNFILLED;
- conversión de FAIL_AMBIGUOUS_BAR a REJECTED_BY_CONTRACT;
- preservación de evaluaciones NoFill antes del resultado terminal.

### 8.6 Slippage, costes y redondeo

- cada modelo autorizado;
- ambos lados de la operación;
- cantidad y notional;
- secuencia de redondeo;
- desglose de componentes;
- coste total;
- fill_price <= 0;
- configuración desconocida o incompleta.

### 8.7 Determinismo

- ejecución repetida con inputs idénticos;
- igualdad byte a byte o igualdad canónica de outputs;
- igualdad de hashes;
- independencia del orden no significativo de mappings o serialización;
- ausencia de dependencia del reloj real;
- fallo cerrado ante configuraciones no versionadas.

### 8.8 Fuera de alcance

Deben existir pruebas negativas que demuestren el rechazo de:

- partial fills;
- time_in_force distinto de DAY;
- tipos de orden no autorizados;
- política PESSIMISTIC;
- políticas de tick no autorizadas;
- inputs que requieran StateReplayFeed;
- consumo de Market State o Event State.

## 9. Outputs y evidencia obligatorios

La implementación debe generar un run de aceptación con:

- run_manifest.json;
- configuration_snapshot.json;
- contract_and_policy_versions.json;
- input_case_manifest.json;
- evaluation_outcomes;
- terminal_order_outcomes;
- fill_records;
- cost_breakdowns;
- test_report;
- determinism_report;
- validation_report;
- hashes de los artefactos;
- inventario de casos ejecutados;
- inventario de limitaciones;
- referencia al commit o estado exacto del código evaluado.

Los nombres físicos pueden adaptarse a las convenciones existentes del
repositorio, siempre que la información requerida esté presente y sea
inequívoca.

## 10. Prohibiciones

Esta autorización no permite implementar ni activar:

- partial fills;
- asignación de volumen o prioridad de cola;
- modelos de liquidez o capacidad;
- participación máxima sobre volumen;
- fills basados en bid/ask o quotes;
- Market-By-Order o Market-By-Price;
- broker, venue o routing realism;
- latencia estocástica;
- borrow availability;
- locate workflow;
- hard-to-borrow fees no cubiertas por el contrato;
- SSR execution realism adicional;
- órdenes o time-in-force no admitidos por V0.1;
- PESSIMISTIC ambiguous-bar policy;
- StateReplayFeed;
- lectura física de StateBundles;
- consumo de Market State;
- consumo de Event State;
- ejecución de estrategias dependientes de estados;
- optimización de estrategias;
- estrategias nuevas;
- calibración usando resultados futuros;
- afirmaciones de edge, rentabilidad o validez económica.

## 11. Incidencias durante la implementación

No será necesaria una nueva autorización para:

- corregir bugs;
- añadir validaciones;
- reorganizar internamente el código;
- aumentar la cobertura de tests;
- mejorar mensajes de error;
- añadir evidencia reproducible;
- corregir documentación para que refleje la implementación autorizada.

La implementación deberá detenerse y volver a decisión cuando:

- el contrato resulte imposible de implementar sin reinterpretarlo;
- se descubra una contradicción semántica material;
- sea necesario introducir una nueva política de fill;
- sea necesario ampliar tipos de orden o time-in-force;
- se requiera una capacidad incluida en las prohibiciones;
- el cambio altere los outcomes canónicos;
- la evidencia revele no determinismo no resoluble dentro del alcance;
- sea necesario consumir State Provider, Market State o Event State.

En esos casos deberá registrarse:

IMPLEMENTATION_BLOCKED_CONTRACT_OR_SCOPE_DECISION_REQUIRED

## 12. Condiciones de cierre de BT-GATE-009

BT-GATE-009 podrá cerrarse como CLOSED_PASS_AUTHORIZATION_GRANTED cuando:

- este documento haya sido aprobado;
- la autorización esté sincronizada en governance;
- el contrato de referencia continúe cerrado;
- las restricciones externas permanezcan preservadas;
- PACKAGE_MANIFEST.json sea íntegro;
- no exista contradicción entre autorización, contrato, políticas y
  trazabilidad.

El cierre de BT-GATE-009 autoriza comenzar la implementación.

No certifica que la implementación exista ni que sea correcta.

## 13. Gate posterior de implementación

La implementación deberá evaluarse en un gate diferente, por ejemplo:

BT-GATE-010 =
DETERMINISTIC_FILL_SIMULATOR_V0_1_IMPLEMENTATION_AND_ACCEPTANCE

BT-GATE-010 solo podrá cerrarse cuando:

- el código autorizado esté implementado;
- todos los tests obligatorios pasen;
- el run de aceptación sea reproducible;
- la prueba de determinismo pase;
- los outputs cumplan los esquemas;
- los hashes y manifests sean íntegros;
- no se hayan activado capacidades prohibidas;
- governance represente el estado real.

## 14. Estado de autorizaciones externas

FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
state_bundle_physical_read = BLOCKED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
Market State consumption = NOT_AUTHORIZED
Event State consumption = NOT_AUTHORIZED
backtest_strategy_execution_with_states = false

## 15. Resultado de la decisión

BT-GATE-009 =
AUTHORIZED_FOR_BOUNDED_IMPLEMENTATION

CODE_IMPLEMENTATION =
AUTHORIZED_FOR_DETERMINISTIC_FILL_SIMULATOR_V0_1_ONLY

authorized_by: TSIS_OWNER
reviewed_by: EXTERNAL_FINAL_DOCUMENT_REVIEW
decision_timestamp: 2026-07-29T09:01:45Z
