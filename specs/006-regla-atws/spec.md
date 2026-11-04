# Feature Specification: Regla determinista de ATWS (demanda de disparo sin caída de flujo)

**Feature Branch**: `006-regla-atws`

**Created**: 2026-11-03 (como `003-regla-atws`; renumerada a 006 el 2026-11-04 porque 003 ya era de otra funcionalidad)

**Status**: Draft

**Jira**: KAN-22 «Regla determinista de ATWS (demanda de disparo sin caída de flujo)» (responsable: Marcelo Acuña) · Fase 2

**Input**: User description: "Regla fija: si hay demanda de disparo y el flujo neutrónico (PWNT) sigue por encima de un umbral pasados 2 s, es ATWS. Definir la señal de demanda de disparo y calibrar el umbral con las corridas de ATWS y de disparo correcto (TRIP_OK) de PWR 3L. Meta: detectar ATWS en 3 s o menos. Usa las corridas de 002 y el reparto sin fuga de 004 (entrenamiento/validación/prueba)."

## Clarifications

### Session 2026-11-03

> Respuestas elegidas por el agente (Claude Code) por delegación del responsable, con la opción recomendada; quedan para revisión en el PR. La señal de demanda queda además pendiente de validar con la experta, como pide KAN-22.

- Q: ¿Qué retardo se asigna a un tipo de señal de disparo que no aparece en las corridas de entrenamiento? → A: El mayor retardo medido en entrenamiento entre todos los tipos (conservador: espera más antes de declarar ATWS, lo que evita falsas alarmas a costa de tiempo), y el reporte lo advierte.
  - *Nota tras implementar (2026-11-04)*: con la carpeta real, el tipo «turbine trip» queda sin ejemplo en entrenamiento y su retardo real (5 s) supera al mayor de entrenamiento (2.5 s): produce una falsa alarma en validación (R54). La respuesta no se cambia, porque se cambiaría mirando validación. La mejora queda propuesta para revisarla con la experta.
- Q: ¿Cómo se elige el umbral de flujo? → A: Si en entrenamiento todos los ATWS quedan por encima de todos los no-ATWS, el punto medio entre el mínimo ATWS y el máximo no-ATWS; si se solapan, el mayor umbral que no omite ningún ATWS de entrenamiento (se prioriza no omitir un ATWS) y se informan las falsas alarmas que eso produce en entrenamiento.
- Q: ¿Desde cuándo se mide la meta de 3 s? → A: Desde la demanda de disparo del reactor (instante en que el scram debía ocurrir). También se informa el tiempo desde la señal de disparo del anunciador, que en un disparo de turbina incluye los ~5 s de la lógica.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recomendación de ATWS en cada corrida (Priority: P1)

Un analista aplica la regla a cada corrida PWR 3L y obtiene, para cada una, si hubo demanda de disparo del reactor, en qué instante, el flujo neutrónico 2 s después de esa demanda y la recomendación: «posible ATWS» si el flujo sigue por encima del umbral, o «sin ATWS» en otro caso.

**Why this priority**: Es la regla que pide KAN-22. Un ATWS (el reactor no se apaga cuando debía) es el accidente más grave del alcance y una regla fija, explicable y sin entrenamiento es la primera barrera del diagnóstico rápido.

**Independent Test**: Aplicar la regla a corridas sintéticas con y sin caída del flujo tras una demanda y comprobar la recomendación, el instante de decisión y el tiempo de detección.

**Acceptance Scenarios**:

1. **Given** una corrida con demanda de disparo en la que el flujo cae a ~6 % (disparo correcto), **When** se aplica la regla, **Then** recomienda «sin ATWS».
2. **Given** una corrida con demanda de disparo en la que el flujo sigue alto 2 s después, **When** se aplica la regla, **Then** recomienda «posible ATWS» en un instante a no más de 3 s de la demanda.
3. **Given** una corrida sin demanda de disparo (operación normal, LOCA muy pequeño), **When** se aplica la regla, **Then** recomienda «sin ATWS» y lo dice («sin demanda»).
4. **Given** cualquier recomendación, **When** se presenta, **Then** está marcada como recomendación para el operador, no como acción.

---

### User Story 2 - Calibración solo con entrenamiento y evaluación en datos no vistos (Priority: P1)

El analista calibra el umbral de flujo y los retardos de la lógica de protección usando solo las corridas de entrenamiento del reparto de 004, y mide la regla en validación y prueba: ATWS detectados, ATWS omitidos, falsas alarmas y tiempos de detección.

**Why this priority**: Sin separar calibración y evaluación (principio II), las cifras del Hito 1 no valdrían nada.

**Independent Test**: Cambiar las corridas de validación o prueba y comprobar que el umbral y los retardos no cambian; comprobar que las cifras por conjunto cuadran con las recomendaciones por corrida.

**Acceptance Scenarios**:

1. **Given** el reparto de 004, **When** se calibra la regla, **Then** el umbral y los retardos dependen solo de corridas de entrenamiento.
2. **Given** la regla calibrada, **When** se evalúa, **Then** se obtiene por conjunto una tabla de ATWS detectados/omitidos y de falsas alarmas/rechazos correctos, y el tiempo de detección de cada ATWS detectado.
3. **Given** los mismos datos y configuración, **When** se repite, **Then** el resultado es idéntico.

---

### User Story 3 - Reporte para el Hito 1 (Priority: P2)

El analista recibe un reporte y archivos con la regla calibrada (umbral, retardos, margen), la evaluación por conjunto y por corrida, el cumplimiento de la meta de 3 s y las limitaciones.

**Why this priority**: Alimenta el Hito 1 (KAN-27: tiempos de detección frente a la meta de 3 s).

**Independent Test**: Generar el reporte y comprobar que cada corrida evaluada aparece una vez, que los totales cuadran y que la meta de 3 s se informa con su definición exacta.

**Acceptance Scenarios**:

1. **Given** la evaluación terminada, **When** se lee el reporte, **Then** muestra el umbral, el margen de separación en entrenamiento, la tabla por conjunto y la lista de ATWS con su tiempo de detección.
2. **Given** un ATWS omitido o una falsa alarma, **When** se lee el reporte, **Then** aparece nombrado con sus valores.

---

### Edge Cases

- Corridas ATWS en las que el simulador no registra ninguna señal de disparo (extracción de barras, R97): la demanda debe salir de una variable medible (flujo por encima del punto de disparo por alto flujo).
- Señal de disparo cuyo scram llega varios segundos después por diseño (disparo de turbina: unos 5 s): medir «2 s» desde la señal daría falsas alarmas en las corridas TRIP_OK.
- Señal de un tipo que no aparece en entrenamiento: recibe el mayor retardo medido en entrenamiento y el reporte lo advierte.
- Distribuciones de flujo de ATWS y no-ATWS que se solapen en entrenamiento: se toma el mayor umbral que no omite ningún ATWS de entrenamiento y se informan las falsas alarmas.
- Corrida cuyo instante de decisión cae fuera de los 300 s de la muestra: se recomienda «sin ATWS» con el motivo «decisión fuera de la ventana» y se advierte.
- Corrida sin registro de eventos (archivo `.dat`) o con un registro ilegible: la evaluación se detiene nombrando el archivo.
- Un ATWS sin demanda (ni señal ni alto flujo): no entra en la calibración y se cuenta como omisión, también en entrenamiento, con advertencia.
- Una corrida con PWNT inicial ≤ 0: la evaluación se detiene nombrando la corrida.
- Corridas que no aportan muestra en 002 (cortas, descartadas, OOD): no se evalúan, porque no están en ningún conjunto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST usar las corridas usables de 002 y el reparto entrenamiento/validación/prueba de 004 (misma semilla, verificado sin fuga), sin leer otras corridas ni mezclar datos de otra planta.
- **FR-002**: El sistema MUST definir la señal de disparo de cada corrida como la primera señal del sistema de protección en su registro de eventos (sin contar «Reactor Scram», que es el resultado) o el primer instante en que el flujo neutrónico alcanza el punto de disparo por alto flujo (118 %), lo que ocurra antes.
- **FR-003**: El sistema MUST definir la demanda de disparo del reactor como la señal de disparo más el retardo de la lógica de protección para ese tipo de señal, medido en las corridas de entrenamiento como el mayor tiempo entre la señal y «Reactor Scram»; un tipo no visto en entrenamiento recibe el mayor retardo de todos.
- **FR-004**: El sistema MUST recomendar «posible ATWS» cuando, en el primer paso a 2 s o más de la demanda, el flujo neutrónico relativo a su valor inicial está por encima del umbral; en otro caso, «sin ATWS» (con el motivo: sin demanda o flujo caído).
- **FR-005**: El sistema MUST calibrar el umbral solo con corridas de entrenamiento, como el punto medio entre el mínimo de los ATWS y el máximo de los no-ATWS si están separados, o el mayor umbral que no omite ningún ATWS de entrenamiento si se solapan, y MUST informar el margen de separación (o las falsas alarmas de entrenamiento).
- **FR-006**: El sistema MUST evaluar la regla en entrenamiento, validación y prueba, con ATWS detectados y omitidos, falsas alarmas y rechazos correctos por conjunto.
- **FR-007**: El sistema MUST medir el tiempo de detección de cada ATWS detectado desde la demanda de disparo y desde la señal de disparo, y MUST informar si cumple la meta de 3 s (definida desde la demanda).
- **FR-008**: Toda recomendación MUST presentarse como recomendación para el operador (principio I).
- **FR-009**: El sistema MUST detenerse con un error que nombre el archivo cuando falte o no se pueda leer el registro de eventos de una corrida evaluada, sin escribir resultados.
- **FR-010**: El sistema MUST producir el mismo resultado con los mismos datos y configuración, y regenerarlo con una sola ejecución documentada.

### Key Entities

- **Señal de disparo**: instante y tipo (p. ej. «low sg level», «turbine trip», «rcp-a trip», «scram lo rx press», «scram high flux»).
- **Retardo de la lógica de protección**: segundos entre la señal y el scram, por tipo de señal, medidos en entrenamiento.
- **Demanda de disparo**: señal + retardo; instante en que el reactor debía estar disparado.
- **Regla calibrada**: umbral de flujo relativo, retardos, espera de 2 s y margen de separación.
- **Evaluación por corrida**: corrida, clase, conjunto, señal, demanda, flujo en la decisión, recomendación, acierto y tiempos de detección.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El umbral y los retardos son idénticos si se cambian las corridas de validación o prueba.
- **SC-002**: El 100 % de las corridas usables de 002 aparece exactamente una vez en la evaluación, y los totales por conjunto cuadran.
- **SC-003**: Cada ATWS detectado tiene su tiempo de detección desde la demanda; la meta se cumple si es ≤ 3 s.
- **SC-004**: En validación y prueba se informan ATWS detectados/omitidos y falsas alarmas, con la lista nombrada de errores.
- **SC-005**: Dos ejecuciones idénticas dan resultados idénticos byte a byte.
- **SC-006**: Toda recomendación del reporte lleva la marca de recomendación para el operador.

## Assumptions

- PWNT es el flujo neutrónico en % del nominal y vale ~100 % en el estado inicial de todas las corridas; tras un scram cae a ~6 % en 1 s.
- El registro de eventos de PCTran (`transientlist.dat`) refleja las señales del anunciador; en las corridas ATWS el simulador puede omitir algunas señales de disparo (p. ej. R91 no registra «Scram High Prz Level», que sí aparece en su gemela).
- La espera de 2 s y el punto de disparo por alto flujo (118 %) vienen de KAN-22 y de la lógica de protección del simulador; la señal de demanda debe validarse con la experta.
- En los ATWS el simulador puede no registrar la señal real (R91 no registra la que sí aparece en su gemela R99): la demanda puede salir más tarde de lo real; el reporte lo declara como limitación.
- Con ~3 ATWS por conjunto de validación y prueba, las cifras tienen mucha incertidumbre.
