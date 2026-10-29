# Feature Specification: Preparación de datos NPPAD sin fuga de información

**Feature Branch**: `001-preparacion-datos`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Un analista necesita preparar los datos de simulación de accidentes del dataset NPPAD (Universidad Tsinghua, simulador PCTRAN, carpeta Operation_csv_data) para entrenar y evaluar después un clasificador de accidentes de reactor PWR. Las clases son operación normal, LOCA rama caliente, LOCA rama fría (LOCAC) y ATWS. Debe obtener conjuntos de entrenamiento, validación y prueba sin fuga de información: una simulación nunca puede estar en dos conjuntos. Debe trabajar con 12 variables de planta escaladas usando solo datos de entrenamiento, y conservar aparte, sin escalar, 7 variables de margen térmico. Cada muestra es una secuencia de 150 pasos de 10 s. Operación normal y ATWS tienen una sola simulación en el dataset: el sistema debe manejarlo y advertirlo, no ocultarlo. El analista debe recibir un reporte con el número de muestras por clase y por conjunto y las limitaciones conocidas."

## Clarifications

### Session 2026-10-20

- Q: ¿Cómo se tratan las clases con una sola simulación (operación normal y ATWS)? → A: Se asigna la simulación completa a entrenamiento; esas clases quedan sin muestras de validación ni de prueba y el reporte lo advierte.
- Q: ¿Cómo se extraen las muestras de 150 pasos dentro de cada simulación? → A: Una sola muestra por simulación, tomada de los primeros 150 pasos (desde el inicio).
- Q: Ante un archivo de simulación defectuoso (variable ausente, valores no numéricos o faltantes, menos de 150 pasos), ¿se detiene la preparación o se excluye la simulación? → A: Se detiene con un error que nombra el archivo y la causa; no se escribe ningún conjunto.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conjuntos de entrenamiento, validación y prueba sin fuga (Priority: P1)

Un analista toma las simulaciones de las cuatro clases (operación normal, LOCA de rama caliente, LOCA de rama fría y ATWS) y obtiene conjuntos de entrenamiento, validación y prueba en los que ninguna simulación aparece en más de un conjunto, con las 12 variables de planta escaladas usando únicamente datos de entrenamiento. Cada muestra es una secuencia de 150 pasos de 10 s (1500 s), tomada del inicio de su simulación; hay una muestra por simulación.

**Why this priority**: Es el núcleo de la funcionalidad. Si las simulaciones se mezclan entre conjuntos o el escalado usa datos de validación o prueba, todas las métricas posteriores se inflan y el diagnóstico parecería mejor de lo que es.

**Independent Test**: Ejecutar la preparación y comprobar automáticamente que (a) la intersección entre los identificadores de simulación de dos conjuntos cualesquiera es vacía, y (b) los parámetros de escala coinciden con los calculados solo sobre el conjunto de entrenamiento.

**Acceptance Scenarios**:

1. **Given** las simulaciones de LOCA y LOCAC del dataset, **When** se preparan los conjuntos, **Then** cada simulación completa cae en un solo conjunto y su muestra va con ella.
2. **Given** una simulación de LOCA y la simulación de LOCAC de igual severidad, **When** se asignan a los conjuntos, **Then** ambas van al mismo conjunto.
3. **Given** los conjuntos ya formados, **When** se escalan las 12 variables de planta, **Then** los parámetros de escala se calculan solo con el conjunto de entrenamiento y se guardan para aplicarlos sin recalcular a validación, prueba o datos nuevos.
4. **Given** la misma configuración y los mismos datos de origen, **When** el analista repite la preparación, **Then** obtiene exactamente la misma asignación de simulaciones a conjuntos y los mismos valores.

---

### User Story 2 - Márgenes térmicos conservados aparte y sin escalar (Priority: P2)

Para cada muestra, el analista dispone de las 7 variables de margen térmico (relación de salida de ebullición nucleada DNBR, temperatura pico de vaina, márgenes de subenfriamiento, temperatura de saturación y fracciones de daño) en sus unidades físicas originales, alineadas paso a paso con las 12 variables de planta de esa misma muestra.

**Why this priority**: Estas variables sirven de referencia para evaluar después el margen térmico, no como entrada del clasificador. Deben quedar intactas y correctamente emparejadas, pero la preparación de las muestras puede probarse sin ellas.

**Independent Test**: Para una muestra elegida, comparar sus 7 variables de margen con las del archivo de origen en las mismas filas y comprobar que son idénticas y que no pasaron por ningún escalado.

**Acceptance Scenarios**:

1. **Given** una muestra de 150 pasos, **When** se consultan sus márgenes térmicos, **Then** hay 7 valores por paso, en las mismas posiciones temporales que las variables de planta, sin escalar.
2. **Given** los conjuntos escalados, **When** se revisan las 7 variables de margen, **Then** ninguna forma parte de las variables escaladas ni de los parámetros de escala.

---

### User Story 3 - Reporte de conteos y limitaciones (Priority: P2)

El analista recibe un reporte que indica cuántas muestras hay por clase y por conjunto, qué simulaciones originaron cada conjunto y cuáles son las limitaciones conocidas de los datos, entre ellas que operación normal y ATWS tienen una sola simulación en el dataset.

**Why this priority**: Sin el reporte no se puede juzgar qué tan confiables serán las métricas posteriores; la honestidad sobre los límites de los datos es un requisito del proyecto.

**Independent Test**: Generar el reporte y verificar que la suma de muestras por conjunto coincide con el total, que cada clase aparece en la tabla (incluso con cero muestras en un conjunto) y que las clases de una sola simulación llevan una advertencia visible.

**Acceptance Scenarios**:

1. **Given** los conjuntos formados, **When** se genera el reporte, **Then** muestra una tabla de muestras por clase y por conjunto cuyos totales coinciden con el número de muestras producidas.
2. **Given** las clases de operación normal y ATWS con una sola simulación, **When** se genera el reporte, **Then** cada una lleva una advertencia explícita de que se asignó completa a entrenamiento y no tiene muestras de validación ni de prueba.
3. **Given** una clase sin muestras en algún conjunto, **When** se genera el reporte, **Then** esa celda aparece con cero y una nota, no se omite.

---

### Edge Cases

- Operación normal y ATWS tienen una sola simulación cada una: van completas a entrenamiento (FR-007), quedan sin muestras de validación y prueba, y el reporte lo advierte.
- Una simulación con menos de 150 pasos no puede producir su muestra: la preparación se detiene con un error que nombra el archivo.
- Un archivo de origen con alguna de las 19 variables requeridas ausente, con valores no numéricos o faltantes: la preparación se detiene con un error que nombra el archivo y la causa, y nunca rellena valores en silencio.
- Una variable con desviación estándar cero en entrenamiento: no puede escalarse por división; se informa en vez de producir valores no válidos.
- Las simulaciones de LOCA y LOCAC no están en el mismo número ni tienen las mismas severidades: las que no tengan pareja se asignan sin romper la regla de no compartir conjunto.
- Como cada simulación aporta una sola muestra, las clases quedan con tantas muestras como simulaciones: operación normal y ATWS tendrán una cada una, frente a unas 100 de LOCA y de LOCAC; el reporte hace visible ese desbalance.
- Se vuelve a ejecutar la preparación sobre una salida previa: debe producir el mismo resultado y no mezclar restos de ejecuciones anteriores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST leer las simulaciones de operación normal, LOCA (rama caliente), LOCAC (rama fría) y ATWS del dataset NPPAD, y MUST NOT modificar los archivos de origen.
- **FR-002**: El sistema MUST producir exactamente una muestra por simulación, formada por sus primeros 150 pasos consecutivos de 10 s, con una etiqueta de clase y el identificador de la simulación de origen.
- **FR-003**: El sistema MUST asignar cada simulación completa a exactamente uno de los conjuntos de entrenamiento, validación o prueba, de modo que ninguna simulación comparta muestras entre dos conjuntos.
- **FR-004**: El sistema MUST asignar al mismo conjunto la simulación de LOCA y la de LOCAC de igual severidad.
- **FR-005**: El sistema MUST usar las 12 variables de planta como entrada de cada muestra: presión, temperaturas, caudales de lazo, niveles, flujo neutrónico, potencia, inyección de emergencia y caudal de fuga.
- **FR-006**: El sistema MUST calcular los parámetros de escala de las 12 variables solo con el conjunto de entrenamiento, aplicarlos a los tres conjuntos y persistirlos para su reutilización.
- **FR-007**: Para las clases con una sola simulación (operación normal y ATWS), el sistema MUST asignar la simulación completa al conjunto de entrenamiento, MUST NOT partirla entre conjuntos, y MUST declarar en el reporte que esas clases no tienen muestras de validación ni de prueba.
- **FR-008**: El sistema MUST conservar para cada muestra las 7 variables de margen térmico (DNBR, temperatura pico de vaina, dos márgenes de subenfriamiento, temperatura de saturación y dos fracciones de daño) en sus unidades originales, sin escalar y alineadas paso a paso con las 12 variables de planta.
- **FR-009**: El sistema MUST emitir un reporte con el número de muestras por clase y por conjunto, la lista de simulaciones de cada conjunto y las limitaciones conocidas.
- **FR-010**: El reporte MUST advertir de forma visible cada clase con una sola simulación y toda clase sin muestras en un conjunto.
- **FR-011**: El sistema MUST producir el mismo resultado al repetir la preparación con los mismos datos de origen y la misma configuración.
- **FR-012**: El sistema MUST detener la preparación con un error que nombre el archivo y la causa, sin escribir ningún conjunto, cuando falten variables requeridas, haya valores no numéricos o faltantes, o la simulación tenga menos de 150 pasos; MUST NOT excluir simulaciones ni rellenar valores en silencio.
- **FR-013**: El sistema MUST regenerar todos los resultados con una sola ejecución documentada; los artefactos generados MUST NOT editarse a mano.

### Key Entities

- **Simulación**: una corrida completa del simulador, con una clase (operación normal, LOCA, LOCAC o ATWS), una severidad cuando aplica (LOCA y LOCAC) y una serie temporal con una fila cada 10 s.
- **Muestra**: secuencia de los primeros 150 pasos (1500 s) de una simulación, una por simulación, con las 12 variables de planta escaladas, los márgenes térmicos asociados, la etiqueta de clase y el identificador de su simulación de origen.
- **Variables de planta**: las 12 entradas del clasificador (P, TAVG, THA, TCA, WRCA, WRCB, LVPZ, LVCR, PWNT, PWR, WECS, WLR).
- **Márgenes térmicos**: 7 variables de referencia en unidades físicas (DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR), no escaladas y no usadas como entrada.
- **Conjunto**: entrenamiento, validación o prueba; contiene simulaciones completas, sin intersección con los otros.
- **Parámetros de escala**: valores calculados con entrenamiento para cada una de las 12 variables y guardados para aplicar el mismo escalado después.
- **Reporte de preparación**: conteos de muestras por clase y conjunto, simulaciones por conjunto, advertencias y limitaciones conocidas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las simulaciones aparece en exactamente un conjunto, y la verificación automática de intersección entre conjuntos da cero coincidencias.
- **SC-002**: Los parámetros de escala coinciden exactamente con los calculados solo sobre entrenamiento, y cambiar los datos de validación o prueba no altera ni un valor de esos parámetros.
- **SC-003**: Las 7 variables de margen térmico de una muestra coinciden en el 100 % de los valores con las del archivo de origen, sin ningún escalado.
- **SC-004**: En el reporte, la suma de muestras por clase y por conjunto es igual al total de muestras producidas, y las 4 clases aparecen en los 3 conjuntos, incluso con cero muestras.
- **SC-005**: El 100 % de las clases con una sola simulación y de las celdas con cero muestras lleva una advertencia visible en el reporte.
- **SC-006**: Dos ejecuciones con los mismos datos y configuración producen conjuntos y reporte idénticos en el 100 % de los casos.
- **SC-007**: Los archivos del dataset original quedan sin cambios tras la preparación, comprobado comparando su contenido antes y después.
- **SC-008**: El analista obtiene los conjuntos y el reporte con una sola ejecución documentada, sin pasos manuales intermedios.

## Assumptions

- El dataset NPPAD está disponible localmente, con las clases en carpetas separadas dentro de `Operation_csv_data` (operación normal, LOCA, LOCAC y ATWS); cada archivo es una simulación con una fila cada 10 s.
- El dataset contiene una simulación de operación normal (unas 300 filas), una de ATWS, y 100 de LOCA y 100 de LOCAC con severidades de 1 a 100; las demás carpetas del dataset (otros accidentes) quedan fuera del alcance.
- Se propone un reparto de simulaciones de 70 % / 15 % / 15 % para entrenamiento, validación y prueba, con una semilla fija para que sea reproducible.
- Los primeros 150 pasos de cada simulación bastan para el diagnóstico posterior; el resto de las filas de cada archivo no se usa en esta funcionalidad.
- Las 12 variables de planta y las 7 de margen térmico son las definidas por el proyecto; los valores originales se consideran correctos y no se corrigen.
- Los tres conjuntos se usan solo para entrenar y evaluar un clasificador posterior; construir ese clasificador queda fuera de esta funcionalidad.
- Operación normal y ATWS no tendrán métricas sobre datos no vistos, porque provienen de una sola simulación cada una; cualquier conclusión sobre esas clases se considera no verificada.
