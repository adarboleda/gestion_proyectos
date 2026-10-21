# Feature Specification: Diagnóstico de accidentes sobre NPPAD (canal lento, Fases 1–2)

**Feature Branch**: `001-diagnostico-lento-nppad`

**Created**: 2026-10-18

**Status**: Implementada (con limitaciones declaradas)

**Input**: User description: "Preparar los datos del dataset NPPAD (Tsinghua/PCTRAN) y construir un diagnóstico de accidentes que distinga operación normal, LOCA (con su rama caliente/fría) y ATWS a partir de la evolución temporal de las variables de planta, indicando incertidumbre cuando la información no alcance."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Datos de NPPAD listos y sin fuga (Priority: P1)

Un analista del proyecto necesita convertir las simulaciones crudas del dataset NPPAD en conjuntos de entrenamiento, validación y prueba, con las variables de planta ya escaladas y los márgenes térmicos de referencia alineados, de modo que cualquier evaluación posterior mida generalización real y no memorización.

**Why this priority**: Todo lo demás (diagnóstico, margen térmico, EOP) depende de que los datos estén bien preparados; un error aquí invalida todas las cifras.

**Independent Test**: Ejecutar la preparación y comprobar que ninguna corrida aparece en más de un conjunto, que los escaladores se ajustaron solo con entrenamiento y que el reporte declara explícitamente las clases con pocas muestras.

**Acceptance Scenarios**:

1. **Given** las 202 simulaciones de NORM, LOCA, LOCAC y ATWS, **When** se prepara el dataset, **Then** cada corrida de LOCA/LOCAC cae completa en un solo conjunto (70/15/15) y se informa el conteo de muestras por clase y conjunto.
2. **Given** una clase con una sola simulación (NORM, ATWS), **When** no se puede formar un conjunto de prueba independiente, **Then** el sistema genera bloques de tiempo disjuntos y declara en la metadata que esas métricas son orientativas.
3. **Given** el conjunto de entrenamiento, **When** se escalan las variables, **Then** los coeficientes de escala se guardan para reutilizarlos sin recalcularlos con datos nuevos.

---

### User Story 2 - Diagnóstico NORM / LOCA / ATWS con abstención (Priority: P1)

Un operador (o el evaluador del sistema) recibe, a partir de los primeros 1500 s de un transitorio, un diagnóstico entre operación normal, LOCA o ATWS, con la confianza asociada; cuando la confianza no alcanza el umbral, el sistema responde "INCIERTO" en lugar de forzar una respuesta.

**Why this priority**: Es la función central del sistema y la meta de seguridad más importante (no dejar pasar accidentes reales).

**Independent Test**: Evaluar el diagnóstico sobre las muestras de prueba y verificar la matriz de confusión, la tasa de falsos negativos y la tasa de INCIERTO.

**Acceptance Scenarios**:

1. **Given** una secuencia de LOCA o LOCAC, **When** se diagnostica, **Then** el resultado es "familia LOCA" o "INCIERTO", nunca NORM ni ATWS.
2. **Given** una secuencia de ATWS, **When** se diagnostica, **Then** el resultado es ATWS.
3. **Given** una predicción con confianza menor a 0.80, **When** se emite el resultado, **Then** se reporta INCIERTO.

---

### User Story 3 - Rama afectada del LOCA: caliente o fría (Priority: P2)

Cuando el diagnóstico es LOCA, el sistema indica si la rotura está en la rama caliente o en la fría, porque cambia el procedimiento y la evolución del accidente.

**Why this priority**: Aporta caracterización adicional pedida en la nota de clarificación funcional, pero depende de que el diagnóstico base funcione.

**Independent Test**: Evaluar solo el clasificador de rama sobre las 100 severidades con validación cruzada agrupada por severidad.

**Acceptance Scenarios**:

1. **Given** un par de simulaciones LOCA/LOCAC de la misma severidad, **When** se evalúa la rama, **Then** ambas van al mismo conjunto de evaluación y la rama se identifica por encima del azar de forma estadísticamente significativa.
2. **Given** una rotura con confianza límite, **When** no se alcanza el umbral, **Then** la rama se reporta como INCIERTO.

---

### User Story 4 - Tiempo de confirmación honesto (Priority: P3)

El equipo necesita saber cuánto tarda el sistema en confirmar un diagnóstico de forma sostenida y reportarlo sin maquillar: el dato de NPPAD llega cada 10 s, por lo que la meta de 3 s no es alcanzable en este canal.

**Why this priority**: Es una medida de calidad, no una función; su resultado sustenta la necesidad del canal rápido (feature 003).

**Independent Test**: Medir la latencia de confirmación causal sobre las muestras de prueba y reportarla por clase.

**Acceptance Scenarios**:

1. **Given** una secuencia de prueba, **When** se evalúa con datos revelados paso a paso, **Then** se registra el primer instante en que el diagnóstico correcto se sostiene el número de evaluaciones requerido.
2. **Given** la resolución de 10 s del dataset, **When** se informa la meta de 3 s, **Then** el reporte la declara inalcanzable en este canal y la deriva al canal rápido.

---

### Edge Cases

- NORM tiene una sola simulación de 302 filas: no alcanza para tres bloques de 150 pasos, así que NORM queda sin muestras de prueba.
- ATWS tiene una sola simulación que se autoestabiliza: las ventanas de esa clase están autocorrelacionadas.
- Antes de la rotura, un LOCA es indistinguible de un ATWS (reactor a potencia, sin cambios): en los primeros ~450–550 s el diagnóstico puede decir ATWS con alta confianza y corregirse al ocurrir la rotura.
- Las severidades de LOCA y LOCAC repartidas al azar por separado dejan severidades de prueba disjuntas entre clases y hunden la evaluación de rama a nivel de azar.
- Un modelo que acierta pero con confianza baja (< 0.80) termina marcando INCIERTO aunque tenga razón.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST seleccionar las corridas de NORM, LOCA (rama caliente), LOCAC (rama fría) y ATWS y reducir las 97 variables a 12 sensores de lazo primario y neutrónica.
- **FR-002**: El sistema MUST producir, por cada ventana, las 12 variables normalizadas y 7 variables de margen térmico en unidades físicas, alineadas fila a fila.
- **FR-003**: El sistema MUST dividir LOCA y LOCAC por corrida completa y, para el clasificador de rama, por severidad pareada (la severidad N de LOCA y la de LOCAC van al mismo conjunto).
- **FR-004**: El sistema MUST ajustar los escaladores solo con datos de entrenamiento y persistirlos.
- **FR-005**: El sistema MUST clasificar cada secuencia en NORM, familia LOCA o ATWS y reportar la confianza.
- **FR-006**: El sistema MUST caracterizar la rama (caliente/fría) solo cuando el diagnóstico es familia LOCA con confianza suficiente.
- **FR-007**: El sistema MUST reportar INCIERTO cuando la confianza sea menor a 0.80 y contarlo como "no resuelto" en la exactitud estándar.
- **FR-008**: El sistema MUST usar únicamente información causal (hasta el instante `t`) en cualquier característica derivada, incluido el pico de sobrepotencia previo al disparo.
- **FR-009**: El sistema MUST ponderar las clases por frecuencia inversa (con tope) para compensar el desbalance.
- **FR-010**: El sistema MUST seleccionar el modelo final priorizando F1 y, ante empate, la menor pérdida de validación (modelo más decidido).
- **FR-011**: El sistema MUST medir y reportar el tiempo de confirmación causal por clase y la latencia de inferencia.
- **FR-012**: El sistema MUST archivar cada iteración fallida con sus métricas para comparación.
- **FR-013**: El sistema MUST declarar en la metadata y en la documentación las limitaciones conocidas de los datos (NORM sin prueba, ATWS de una sola corrida, simulador único).

### Key Entities

- **Corrida NPPAD**: una simulación (serie temporal de 97 variables a 10 s) de una clase y una severidad.
- **Ventana**: 150 pasos × 12 variables normalizadas (1500 s), con etiqueta de clase.
- **Margen térmico**: 150 pasos × 7 variables físicas (DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR) asociadas a la misma ventana.
- **Escalador**: media y desviación de entrenamiento por variable.
- **Partición por severidad**: asignación de cada severidad 1–100 a train/val/test, igual para LOCA y LOCAC.
- **Diagnóstico**: clase (NORM, LOCA, LOCAC, ATWS, INCIERTO), confianza y etapa que lo decidió.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La clasificación NORM/familia LOCA/ATWS acierta el 100 % de las 33 muestras de prueba.
- **SC-002**: La rama caliente/fría se identifica con 99.0 % ± 2.0 % de acierto en validación cruzada de 5 particiones sobre las 100 severidades (frente a 48 % por azar en la iteración previa).
- **SC-003**: De las 33 muestras de prueba, 29 reciben diagnóstico concreto y las 29 son correctas (0 errores entre las no inciertas); la exactitud combinada estándar es 87.9 % y la tasa de INCIERTO es 12.1 %.
- **SC-004**: Ningún accidente de prueba (LOCA, LOCAC, ATWS) se diagnostica como operación normal (0 falsos negativos).
- **SC-005**: La inferencia completa tarda menos de 10 ms por muestra (p95 ≈ 2.5 ms).
- **SC-006**: 29 de 33 secuencias de prueba se confirman en la ventana observada; las medianas de confirmación son 300 s (LOCA), 350 s (LOCAC) y 50 s (ATWS). La meta de 3 s se declara no alcanzable con datos a 10 s.

## Assumptions

- Los datos de NPPAD son simulaciones de PCTRAN de una sola configuración de planta; no hay validación contra otro código termohidráulico ni datos de planta.
- El dato llega cada 10 s (150 pasos = 1500 s); el plan de trabajo original mencionaba 0.05 s por error y ya está identificado para corrección (feature 006).
- El accidente en NPPAD comienza hacia los 100 s de la ventana; los tiempos reportados descuentan ese tramo.
- Un solo archivo de NORM y de ATWS es todo lo que existe en el dataset original; sus métricas son orientativas.
- `WLR` (caudal de fuga) está entre las 12 entradas del canal lento aunque no es medible en planta; se espera una ablación sin esa variable (tarea abierta en `tasks.md`).
- El umbral de incertidumbre (0.80) y la regla de 3 evaluaciones seguidas provienen del plan de trabajo.
