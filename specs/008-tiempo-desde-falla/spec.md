# Feature Specification: Tiempo de detección desde la falla (PWR 3L)

**Feature Branch**: `008-tiempo-desde-falla`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "Medir el tiempo de detección desde la falla (KAN-25, responsable Abner Arboleda) en PWR 3L. Evaluación causal segundo a segundo del diagnóstico rápido (clasificador de Etapa 1 de 005 y regla de ATWS de 006) con la regla de confianza sostenida, contando el tiempo desde el instante de la falla tomado del Transient Report de PCTran (registro de eventos de cada corrida), no desde el inicio de la ventana ni desde el inicio detectado por el validador. Metas: diagnóstico de la familia del evento en 10 s o menos; ATWS en 3 s o menos. Reportar por corrida y en resumen, con las falsas alarmas, sin reentrenar ni ajustar nada con las corridas de prueba. Salida consultiva."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saber cuándo ocurrió la falla en cada corrida (Priority: P1)

Un analista obtiene, para cada corrida de evento, el instante en que ocurrió la falla según el registro de eventos del simulador (Transient Report), junto con la fuente de ese dato y su diferencia con el inicio que detectó el validador. Las corridas en que el instante no se puede establecer con confianza quedan marcadas y no se usan para las metas.

**Why this priority**: Todo tiempo de detección se mide desde este instante. Si está mal, las métricas no significan nada; la medición anterior (005) usó el inicio detectado por el validador, que en algunas corridas difiere decenas de segundos de la falla real.

**Independent Test**: Determinar el instante de la falla en corridas con registros conocidos y comprobar que coincide con la línea del registro (o con la regla acordada cuando el registro no la tiene), que se informa la fuente y que las corridas inciertas quedan marcadas.

**Acceptance Scenarios**:

1. **Given** una corrida cuyo registro anota la acción que inicia la falla (cierre de válvulas de agua de alimentación, disparo de una bomba del refrigerante, disparo de la turbina, pérdida de energía), **When** se determina el instante de la falla, **Then** es el instante de esa primera línea del registro y la fuente es «registro».
2. **Given** una corrida de LOCA, cuyo registro no anota el instante de la rotura, **When** se determina el instante de la falla, **Then** se aplica la regla acordada en FR-002 y se informa su fuente.
3. **Given** una corrida en la que la planta ya cambia (según el validador) más de 2 s antes del instante de la falla determinado, **When** se determina el instante, **Then** la corrida queda marcada como «incierta», se informa y no cuenta para las metas.
4. **Given** cualquier corrida de evento, **When** se informa su instante de falla, **Then** aparece también el inicio detectado por el validador y la diferencia entre ambos.

---

### User Story 2 - Medir segundo a segundo cuánto tarda el diagnóstico desde la falla (Priority: P1)

El analista reproduce las corridas de prueba segundo a segundo, como si llegaran en tiempo real. En cada segundo, el diagnóstico rápido decide solo con los datos recibidos hasta ese momento, y se aplica la regla de confianza sostenida. Así obtiene, para cada corrida, cuánto tardó en confirmarse la familia correcta desde la falla y cuánto tardó la regla en reconocer un ATWS, y los compara con las metas de 10 s y 3 s, junto con las falsas alarmas.

**Why this priority**: Es lo que pide la tarea. Las metas de tiempo son las del plan del proyecto, y el informe del Hito 1 (007) las espera medidas desde la falla.

**Independent Test**: Reproducir corridas con probabilidades y decisiones conocidas y comprobar el instante de confirmación, el tiempo desde la falla, la decisión de ATWS y las falsas alarmas.

**Acceptance Scenarios**:

1. **Given** una corrida de prueba, **When** se reproduce segundo a segundo, **Then** la decisión de cada segundo usa solo datos hasta ese segundo.
2. **Given** una corrida de evento, **When** la familia correcta alcanza la confianza mínima durante 2 segundos seguidos después de la falla, **Then** el tiempo de diagnóstico es el segundo de confirmación menos el instante de la falla; si nunca ocurre, «no detectado».
3. **Given** una corrida de ATWS, **When** la regla de ATWS recomienda «posible ATWS», **Then** el tiempo de ATWS se mide según FR-006.
4. **Given** las corridas de prueba, **When** termina la evaluación, **Then** el resumen indica qué fracción cumple la meta de 10 s (por familia y, en LOCA, por tamaño de rotura) y qué fracción de ATWS cumple la de 3 s.
5. **Given** una corrida de operación normal, o el tramo previo a la falla, **When** el diagnóstico confirma una familia de evento o la regla recomienda «posible ATWS» sin que lo sea, **Then** se cuenta como falsa alarma.

---

### User Story 3 - Comparar con la medición anterior y conservar la línea de tiempo (Priority: P2)

El analista ve, para cada corrida, el tiempo medido desde la falla junto al que se medía antes (desde el inicio del validador, en 005) y obtiene la línea de tiempo segundo a segundo de cada corrida, para el informe del Hito 1 y las demostraciones.

**Why this priority**: Muestra cuánto cambia la conclusión al medir bien y deja los datos listos para el informe, pero la tarea se cumple con la historia 2.

**Independent Test**: Evaluar corridas conocidas y comprobar que la comparación muestra ambos tiempos y su diferencia, y que la línea de tiempo tiene una fila por segundo con la decisión de ese segundo.

**Acceptance Scenarios**:

1. **Given** una corrida de evento de prueba, **When** se genera el reporte, **Then** aparecen el tiempo desde la falla, el tiempo desde el inicio del validador y su diferencia.
2. **Given** una corrida evaluada, **When** se exporta su línea de tiempo, **Then** hay una fila por segundo con las probabilidades de cada familia, la familia confirmada (o ninguna) y la decisión de la regla de ATWS cuando la hay.

---

### Edge Cases

- La falla ocurre antes del primer segundo que el diagnóstico puede evaluar (5 s): el tiempo se mide igual desde la falla, y puede ser mayor por esa espera mínima.
- El registro no tiene ninguna línea del iniciador (LOCA, extracción de barras): se aplica la regla de FR-002.
- La planta cambia antes del instante de falla determinado (por ejemplo, la falla programada se activó antes): la corrida es «incierta».
- Una corrida de ATWS en la que la regla no encuentra demanda de disparo: «ATWS no detectado», con el motivo.
- El diagnóstico confirma la familia correcta y después cambia: cuenta la primera confirmación; los cambios posteriores se informan en la línea de tiempo.
- El modelo guardado de la Etapa 1 no corresponde al reparto actual (otra semilla u otras corridas): la evaluación se detiene con un error, para no evaluar con corridas que el modelo vio.
- Una familia sin corridas de prueba: aparece con cero y sin metas inventadas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST determinar, para cada corrida de evento usable, el instante de la falla a partir de su registro de eventos (Transient Report): el instante de la primera línea que corresponde a la acción iniciadora de la falla.
- **FR-002**: Cuando el registro no anota el instante de la falla (LOCA y otros casos sin línea del iniciador), el sistema MUST usar: [NEEDS CLARIFICATION: ¿de dónde se toma el instante de la falla cuando el Transient Report no lo registra, por ejemplo en las LOCA?]
- **FR-003**: El sistema MUST informar para cada corrida la fuente del instante de la falla, el inicio detectado por el validador y su diferencia; MUST marcar como «incierta» toda corrida en que el validador detecte cambios más de 2 s antes del instante de la falla, y MUST excluirla de las metas, informándola aparte.
- **FR-004**: El sistema MUST evaluar cada corrida segundo a segundo de forma causal: la decisión de cada segundo usa solo datos hasta ese segundo.
- **FR-005**: El sistema MUST aplicar la regla de confianza sostenida: una familia se confirma cuando su probabilidad es de al menos 0,80 en 2 segundos seguidos. El tiempo de diagnóstico es el primer segundo de confirmación de la familia correcta (con ambos segundos posteriores a la falla) menos el instante de la falla, o «no detectado».
- **FR-006**: El sistema MUST medir el tiempo de ATWS con la regla de ATWS de 006 como: [NEEDS CLARIFICATION: ¿desde qué instante se cuenta la meta de 3 s del ATWS: desde la demanda de disparo registrada (cuando el disparo debía ocurrir y falló) o desde el evento iniciador?]
- **FR-007**: El sistema MUST NOT reentrenar ni ajustar nada: MUST usar el clasificador de Etapa 1 guardado por 005 y la regla de ATWS calibrada solo con entrenamiento (006), y MUST detenerse con un error si el clasificador guardado no corresponde al reparto sin fuga actual.
- **FR-008**: El sistema MUST informar, sobre las corridas de prueba, la fracción de corridas de evento con diagnóstico en 10 s o menos (en total, por familia y, en LOCA, por tamaño de rotura) y la fracción de ATWS reconocidos en 3 s o menos, con su definición exacta y si se cumple la meta, o «sin datos».
- **FR-009**: El sistema MUST contar las falsas alarmas: confirmaciones de una familia de evento en corridas de operación normal o antes de la falla, y recomendaciones «posible ATWS» en corridas que no son ATWS.
- **FR-010**: El sistema MUST producir un reporte por corrida con: identificador, clase, conjunto, instante de la falla y su fuente, inicio del validador, tiempo de diagnóstico, tiempo de ATWS (si aplica), falsas alarmas y si es incierta.
- **FR-011**: El sistema MUST comparar, para cada corrida de evento, el tiempo de diagnóstico desde la falla con el tiempo medido desde el inicio del validador.
- **FR-012**: El sistema MUST exportar la línea de tiempo de cada corrida evaluada, con una fila por segundo: probabilidades de cada familia, familia confirmada o ninguna, y decisión de la regla de ATWS en su segundo de decisión.
- **FR-013**: El sistema MUST generar todo con una sola ejecución documentada, reproducible con la misma semilla, publicar sus resultados todos juntos o ninguno, e identificar toda salida como consultiva.
- **FR-014**: El sistema MUST evaluar las corridas de prueba para las metas y MUST informar también las de validación, marcadas como referencia, porque el clasificador las usó para elegir su época.
- **FR-015**: El sistema MUST NOT modificar los datos de origen ni usar datos de NPPAD.

### Key Entities

- **Instante de la falla**: segundos desde el inicio de la corrida en que ocurre la falla; con su fuente (línea del registro u otra según FR-002) y su estado (confiable o incierto).
- **Inicio del validador**: el primer cambio de la planta que detectó el validador del proyecto (usado en 005).
- **Línea de tiempo**: una fila por segundo con las probabilidades de cada familia, la familia confirmada y la decisión de la regla de ATWS.
- **Tiempo de diagnóstico**: segundos desde la falla hasta la confirmación de la familia correcta.
- **Tiempo de ATWS**: segundos hasta que la regla reconoce el ATWS, según FR-006.
- **Falsa alarma**: confirmación de una familia de evento sin evento, o «posible ATWS» sin ATWS.
- **Reporte**: tiempos por corrida, resumen frente a las metas, falsas alarmas, corridas inciertas y comparación con la medición anterior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las corridas de evento tiene un instante de falla con su fuente, o está marcada como incierta con su motivo.
- **SC-002**: En las corridas de prueba no inciertas, la familia del evento se confirma en 10 s o menos desde la falla en el 100 % de las corridas de evento (meta del proyecto; se informa el resultado tal como salga).
- **SC-003**: En las corridas de prueba y de validación, el 100 % de los ATWS se reconoce en 3 s o menos según FR-006 (meta del proyecto; se informa tal como salga).
- **SC-004**: 0 falsas alarmas del diagnóstico en las corridas de operación normal de prueba y 0 recomendaciones «posible ATWS» en corridas de prueba que no son ATWS.
- **SC-005**: Dos ejecuciones con los mismos datos y la misma semilla producen resultados idénticos.
- **SC-006**: La evaluación completa termina en menos de 5 minutos en una computadora portátil sin aceleración gráfica.
- **SC-007**: El clasificador y la regla usados son exactamente los de 005 y 006: ninguna cifra se obtiene ajustando con las corridas de prueba.

## Assumptions

- El clasificador de Etapa 1 es el modelo guardado por `entrenar-etapa1` (005) con la semilla 42; la regla de ATWS es la de `evaluar-regla-atws` (006), calibrada con las corridas de entrenamiento. Esta funcionalidad no los cambia.
- La regla de confianza sostenida es la de 005 (probabilidad ≥ 0,80 en 2 segundos seguidos); la regla de ATWS decide según 006 (2 s después de la demanda).
- Medición de datos reales: el registro anota el iniciador en las ATWS y TRIP_OK por pérdida de agua de alimentación (cierre de válvulas), por disparo de bomba («RCP-A trip»), por disparo de turbina y por pérdida de energía (válvula de la turbina del agua auxiliar). En las LOCA solo anota la falla insertada en t = 0 con un retardo que el registro no muestra. En cuatro corridas (falla 9: R47, R48, R54 y R99) el retardo programado no se cumplió y la planta cambia desde ~1 s.
- Las metas (10 s para el diagnóstico y 3 s para el ATWS) vienen del plan del proyecto; si no se alcanzan, se informa el resultado tal como sale.
- El conjunto de prueba es el del reparto de 004 (13 corridas); las cifras tienen mucha incertidumbre.
- El informe del Hito 1 (007) podrá usar estas cifras; generarlo queda fuera de esta funcionalidad.
