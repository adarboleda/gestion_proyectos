# Feature Specification: Clasificador de Etapa 1 (familia del evento) para PWR 3L

**Feature Branch**: `005-clasificador-etapa1`

**Created**: 2026-11-03

**Status**: Draft

**Input**: User description: "Entrenar el clasificador de Etapa 1 (familia del evento) de IANuclear para la planta PWR 3L (tarea de Jira de Abner Arboleda): una Bi-LSTM que distingue operación normal (NORM), familia LOCA (LOCA rama caliente y LOCAC rama fría) y transitorio con disparo (ATWS y TRIP_OK). Debe entrenarse con prefijos cortos de la secuencia para que decida con pocos segundos de datos después del inicio del evento, y con pesos de clase para compensar el desbalance. Usa las corridas usables y el reparto sin fuga de la funcionalidad 004 (entrenamiento, validación y prueba) y el escalado ajustado solo con entrenamiento de la 003. Debe reportar con honestidad qué tan rápido y qué tan bien distingue las tres familias en las corridas de prueba, incluidas las falsas alarmas en operación normal. La salida es consultiva: el modelo recomienda, no actúa sobre la planta."

## Clarifications

### Session 2026-11-03

- Q: ¿Qué datos ve el modelo en cada instante para decidir (el «prefijo corto»)? → A: En cada segundo τ, los últimos 30 s hasta τ (al empezar la corrida, lo disponible desde t = 0); se entrena con el tramo previo al evento y los primeros 60 s del evento.
- Q: En las corridas de evento, ¿cómo se etiquetan los instantes anteriores al inicio del evento? → A: Como operación normal.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entrenar el clasificador de las tres familias (Priority: P1)

Un analista entrena, con una sola ejecución, un clasificador que a partir de las variables medibles de la planta reconoce si la planta está en operación normal, en un evento de la familia LOCA o en un transitorio con disparo, usando solo las corridas de entrenamiento y validación del reparto sin fuga, y obtiene el modelo y su configuración guardados para usarlos después.

**Why this priority**: Es el entregable de la tarea. Sin el modelo entrenado no hay detección temprana; las demás historias dependen de él.

**Independent Test**: Ejecutar el entrenamiento sobre un conjunto pequeño de corridas conocidas y comprobar que se guardan el modelo, los parámetros de escala, las clases, la configuración y el historial, que ninguna corrida de prueba participó y que dos ejecuciones con la misma semilla producen el mismo resultado.

**Acceptance Scenarios**:

1. **Given** las corridas usables y su reparto en entrenamiento, validación y prueba, **When** se entrena el clasificador, **Then** solo las corridas de entrenamiento ajustan el modelo y los parámetros de escala, y solo las de validación deciden cuándo parar.
2. **Given** que la operación normal aporta muchas más muestras que las otras familias, **When** se entrena, **Then** cada familia pesa en el aprendizaje en proporción inversa a su frecuencia, y los pesos usados quedan registrados.
3. **Given** los mismos datos y la misma semilla, **When** se repite el entrenamiento, **Then** se obtienen el mismo modelo y las mismas métricas.
4. **Given** el entrenamiento terminado, **When** se revisa la salida, **Then** están guardados el modelo, los parámetros de escala, las clases, la configuración, la semilla y el historial de entrenamiento.

---

### User Story 2 - Evaluar qué tan rápido y qué tan bien decide (Priority: P1)

El analista obtiene, sobre las corridas de prueba que el modelo nunca vio, cuán bien distingue las tres familias según los segundos transcurridos desde el inicio del evento, cuánto tarda en confirmar la familia correcta en cada corrida y cuántas falsas alarmas da en operación normal.

**Why this priority**: La tarea pide decidir con pocos segundos de datos. Sin medir la calidad en función del tiempo y las falsas alarmas, no se puede saber si el clasificador sirve para detección temprana; la constitución exige reportar también los resultados negativos.

**Independent Test**: Evaluar un modelo sobre corridas de prueba conocidas y comprobar que el reporte contiene, para cada corrida de evento, su tiempo de confirmación o «no detectada», las métricas por familia en cada horizonte de segundos y el conteo de falsas alarmas.

**Acceptance Scenarios**:

1. **Given** el modelo entrenado, **When** se evalúa en las corridas de prueba, **Then** el reporte muestra la matriz de confusión y la precisión, la exhaustividad y el F1 de cada familia, en total y en los horizontes de 1, 2, 3, 5, 10, 20 y 30 segundos desde el inicio del evento.
2. **Given** una corrida de prueba de un evento, **When** se evalúa, **Then** el reporte indica el primer instante en que el modelo confirma la familia correcta, medido en segundos desde el inicio del evento, o «no detectada» si nunca la confirma.
3. **Given** las corridas de operación normal de prueba y el tramo anterior al evento de las demás, **When** se evalúa, **Then** el reporte cuenta los instantes y las corridas en que el modelo confirma una familia distinta de operación normal (falsas alarmas).
4. **Given** las corridas LOCA de prueba, **When** se evalúa, **Then** el tiempo de confirmación se informa también agrupado por tamaño de rotura.

---

### User Story 3 - Obtener una recomendación para datos nuevos (Priority: P2)

El analista entrega al modelo guardado los datos de una corrida hasta un instante dado y recibe la probabilidad de cada familia y una recomendación (la familia más probable, o «incierto» si ninguna alcanza la confianza mínima), presentada como recomendación consultiva.

**Why this priority**: Permite usar el modelo fuera del entrenamiento (en la etapa 2, en el modo sombra o en la consola del operador), pero la tarea se cumple con el entrenamiento y la evaluación.

**Independent Test**: Cargar el modelo guardado, pasarle una secuencia y comprobar que devuelve tres probabilidades que suman 1, la familia recomendada o «incierto» según el umbral, y el aviso de que es una recomendación.

**Acceptance Scenarios**:

1. **Given** el modelo guardado y los datos de una corrida hasta un instante, **When** se pide una clasificación, **Then** se obtienen las probabilidades de las tres familias, que suman 1.
2. **Given** que ninguna familia alcanza la confianza mínima, **When** se pide una clasificación, **Then** la recomendación es «incierto».
3. **Given** cualquier clasificación, **When** se presenta, **Then** está identificada como recomendación consultiva y no como una orden.

---

### Edge Cases

- El evento empieza casi al iniciar la corrida (por ejemplo, en t = 1 s): hay muy pocos datos previos de operación normal en esa corrida.
- Una corrida de evento sin instante de inicio conocido: la preparación se detiene con un error que nombra la corrida, porque sin ese instante no se puede etiquetar ni medir el tiempo de detección.
- Las roturas muy pequeñas (2 a 10 cm²) cambian las variables lentamente: pueden no detectarse en los primeros 30 s; se reportan, no se ocultan.
- Las corridas de operación normal incluyen maniobras (reducción de potencia, rechazo de carga) que pueden parecerse al inicio de un transitorio.
- El conjunto de prueba tiene pocas corridas (13 en el reparto de 004): las métricas tienen mucha incertidumbre y el reporte lo advierte.
- Una familia sin corridas en validación o en prueba: el reporte lo indica con un cero y no calcula métricas inventadas.
- Se vuelve a entrenar sobre una salida anterior: se reemplaza por completo sin mezclar resultados de ejecuciones distintas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST clasificar en tres familias: operación normal (NORM), familia LOCA (LOCA rama caliente y LOCAC rama fría) y transitorio con disparo (ATWS y TRIP_OK). Las corridas cortas, descartadas y OOD MUST NOT usarse.
- **FR-002**: El sistema MUST usar el reparto sin fuga de la funcionalidad 004: todas las muestras de una corrida MUST pertenecer al conjunto de esa corrida, y la verificación de fuga MUST ejecutarse antes de entrenar.
- **FR-003**: El sistema MUST usar como entrada las 26 variables medibles en sala de control, escaladas con parámetros ajustados solo con las corridas de entrenamiento (funcionalidad 003); MUST NOT usar el caudal de fuga ni los márgenes térmicos como entrada.
- **FR-004**: El sistema MUST formar una muestra por cada segundo τ de cada corrida, a partir de τ = 5 s, con los datos de los últimos 30 s hasta τ (o desde t = 0 si τ es menor que 30 s): un prefijo corto que el modelo podría ver en tiempo real. El entrenamiento MUST usar todas las muestras de las corridas NORM, todas las del tramo previo al evento y las de los primeros 60 s de cada evento; la validación y la evaluación MUST usar todas las muestras de sus corridas.
- **FR-005**: El sistema MUST etiquetar cada muestra de una corrida de evento según el instante de inicio del evento: operación normal si τ es anterior al inicio y la familia del evento desde el inicio en adelante; el inicio se redondea hacia arriba al segundo entero. Los segundos desde el inicio del evento (τ − inicio) se guardan con cada muestra para medir los horizontes de FR-009.
- **FR-006**: El sistema MUST ponderar cada familia en el entrenamiento en proporción inversa a su frecuencia en las muestras de entrenamiento y MUST registrar los pesos usados.
- **FR-007**: El sistema MUST producir el mismo modelo y las mismas métricas con los mismos datos, la misma configuración y la misma semilla.
- **FR-008**: El sistema MUST elegir el modelo final (cuándo parar de entrenar) usando solo las corridas de validación; las corridas de prueba MUST usarse solo en la evaluación final.
- **FR-009**: El sistema MUST reportar, sobre las corridas de prueba, la matriz de confusión y la precisión, la exhaustividad y el F1 de cada familia, más el F1 macro, en total y para los horizontes de 1, 2, 3, 5, 10, 20 y 30 segundos desde el inicio del evento.
- **FR-010**: El sistema MUST reportar para cada corrida de evento de prueba su tiempo de confirmación: el primer instante desde el inicio del evento en que la familia correcta tiene confianza de al menos 0,80 durante 2 segundos seguidos, o «no detectada». Para LOCA MUST agruparlo también por tamaño de rotura.
- **FR-011**: El sistema MUST contar las falsas alarmas en las corridas de prueba: instantes y corridas en que se confirma (misma regla de FR-010) una familia distinta de NORM durante operación normal (corridas NORM y tramo previo al evento).
- **FR-012**: El sistema MUST guardar el modelo, los parámetros de escala, las clases, la configuración, la semilla, los pesos de clase, el historial de entrenamiento y el reporte de evaluación, y MUST poder regenerarlos con una sola ejecución documentada.
- **FR-013**: El sistema MUST ofrecer la clasificación de una secuencia nueva hasta un instante dado, devolviendo las probabilidades de las tres familias y la familia recomendada, o «incierto» si ninguna alcanza 0,80; toda salida MUST identificarse como recomendación consultiva.
- **FR-014**: El sistema MUST detenerse con un error que nombre la corrida cuando una corrida de evento usable no tenga instante de inicio conocido.
- **FR-015**: El sistema MUST NOT modificar los datos de origen ni usar datos de NPPAD.

### Key Entities

- **Familia**: NORM, LOCA (LOCA y LOCAC) o transitorio con disparo (ATWS y TRIP_OK; etiqueta TRANS); es la etiqueta que aprende el modelo.
- **Corrida**: una simulación PWR 3L usable, con su clase, su conjunto (del reparto de 004), su instante de inicio del evento y, si es LOCA, su área de rotura.
- **Muestra**: los datos que ve el modelo en un instante de una corrida, con la familia que le corresponde en ese instante y los segundos transcurridos desde el inicio del evento.
- **Modelo entrenado**: el clasificador y todo lo necesario para reutilizarlo: parámetros de escala, clases, configuración, semilla y pesos de clase.
- **Reporte de evaluación**: métricas por familia y por horizonte, tiempos de confirmación por corrida, falsas alarmas y advertencias.
- **Recomendación**: probabilidades de las tres familias y familia recomendada o «incierto».

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En las corridas de prueba, la familia LOCA con rotura de 50 cm² o más se confirma en 10 segundos o menos desde el inicio del evento en el 100 % de los casos.
- **SC-002**: En las corridas de operación normal de prueba hay 0 falsas alarmas confirmadas.
- **SC-003**: Sobre las corridas de prueba, el F1 macro de las tres familias en los primeros 30 segundos desde el inicio del evento (más las muestras de operación normal) es de al menos 0,80.
- **SC-004**: El 100 % de las corridas de evento de prueba aparece en el reporte con su tiempo de confirmación o «no detectada».
- **SC-005**: Dos entrenamientos con los mismos datos y la misma semilla, en la misma máquina y con la misma versión del entorno, producen métricas idénticas en el 100 % de los valores.
- **SC-006**: Entrenar y evaluar con todas las corridas usables termina en menos de 15 minutos en una computadora portátil sin aceleración gráfica.
- **SC-007**: 0 muestras de una corrida aparecen en un conjunto distinto del de su corrida.

## Assumptions

- Se usa solo PWR 3L: tiene un dato por segundo, cinco clases y suficientes corridas por familia. NPPAD no sirve para esta tarea (un dato cada 10 s y una sola simulación de operación normal y de ATWS), y la constitución prohíbe mezclar plantas.
- El reparto es el de la funcionalidad 004 (63 corridas de entrenamiento, 15 de validación y 13 de prueba con los datos reales), sin cambios.
- El instante de inicio del evento se toma del validador de corridas del proyecto (`t_inicio_real`). Para las corridas TRIP_OK manuales que no tienen validación (R59–R62) se usa el instante planificado del nombre de su carpeta. Las corridas NORM no lo necesitan.
- La regla de confirmación (confianza de al menos 0,80 durante 2 segundos seguidos) y las metas de SC-001 y SC-002 vienen del plan de detección rápida del proyecto de referencia; si no se alcanzan, se reporta el resultado tal como salga.
- Este clasificador es la Etapa 1; distinguir la rama caliente de la fría y el ATWS del disparo correcto (Etapa 2) queda fuera.
- Integrar el modelo en la consola del operador o en el modo sombra queda fuera; aquí solo se entrena, se evalúa y se ofrece la clasificación de una secuencia.
