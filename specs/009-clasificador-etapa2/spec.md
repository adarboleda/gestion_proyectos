# Feature Specification: Clasificador de Etapa 2 (rama caliente o fría) para PWR 3L

**Feature Branch**: `009-clasificador-etapa2`

**Created**: 2026-11-04

**Status**: Draft

**Input**: User description: "Entrenar el clasificador de Etapa 2 (rama caliente o fría): Bi-LSTM que separa LOCA de LOCAC cuando la Etapa 1 detecta la familia LOCA, con los canales de desviación pico de PWR y PWNT. Si la confianza es menor al 80 %, el sistema se abstiene (UNCERTAIN). Tomar como referencia el proyecto IA-Nuclear (prueba_rama_caliente_fria_pwr3l.py). Limitarse a esta parte: la Etapa 1, la regla de ATWS, la consola y el modo sombra son de otros integrantes."

## Clarifications

### Session 2026-11-04

- Q: ¿Qué entradas recibe la Bi-LSTM de Etapa 2? → A: [NEEDS CLARIFICATION: solo los canales de desviación pico de PWR y PWNT, o las 26 variables de sala de control más esos dos canales]
- Q: ¿Sobre qué muestras se evalúa la Etapa 2? → A: [NEEDS CLARIFICATION: solo sobre los instantes de evento de las corridas LOCA/LOCAC de prueba (Etapa 1 ideal), o encadenada con la salida real de la Etapa 1]

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entrenar el clasificador de rama caliente o fría (Priority: P1)

Un analista entrena, con una sola ejecución, un clasificador que, una vez que se sabe que la planta está en un evento de la familia LOCA, decide si la rotura está en la rama caliente (LOCA) o en la rama fría (LOCAC), usando los canales de desviación pico de la potencia térmica (PWR) y del flujo neutrónico (PWNT), solo con las corridas LOCA y LOCAC de entrenamiento y validación del reparto sin fuga, y obtiene el modelo y su configuración guardados.

**Why this priority**: Es el entregable de la tarea; las demás historias dependen de él.

**Independent Test**: Entrenar sobre corridas sintéticas LOCA/LOCAC conocidas y comprobar que se guardan el modelo, el escalador, las clases, los canales, la configuración y el historial; que ninguna corrida de prueba participó, y que dos ejecuciones con la misma semilla producen el mismo resultado.

**Acceptance Scenarios**:

1. **Given** las corridas usables y el reparto de 004, **When** se entrena, **Then** solo intervienen corridas LOCA y LOCAC; solo las de entrenamiento ajustan el modelo y el escalador, y solo las de validación deciden cuándo parar.
2. **Given** una corrida LOCA o LOCAC, **When** se calculan los canales de desviación pico, **Then** en cada segundo valen el máximo, en los últimos 15 s, de la media móvil de 3 s de PWR y de PWNT menos su valor inicial, usando solo datos hasta ese segundo.
3. **Given** clases con distinto número de muestras, **When** se entrena, **Then** cada clase pesa en proporción inversa a su frecuencia y los pesos quedan registrados.
4. **Given** los mismos datos y la misma semilla, **When** se repite el entrenamiento, **Then** se obtienen el mismo modelo y las mismas métricas.

---

### User Story 2 - Evaluar la separación y la abstención (Priority: P1)

El analista obtiene, sobre las corridas LOCA y LOCAC de prueba, qué tan bien separa el modelo las dos ramas según los segundos desde el inicio del evento, cuántas veces se abstiene (UNCERTAIN) y cuántas se equivoca con confianza, por corrida y por tamaño de rotura.

**Why this priority**: Una recomendación de rama equivocada lleva al operador a un procedimiento de emergencia equivocado; la abstención por debajo del 80 % es la salvaguarda, y la constitución exige informar también los resultados negativos.

**Independent Test**: Evaluar un modelo sobre corridas de prueba conocidas y comprobar que el reporte contiene la matriz de confusión con la columna UNCERTAIN, las métricas por horizonte, la cobertura y el resultado de cada corrida.

**Acceptance Scenarios**:

1. **Given** el modelo entrenado, **When** se evalúa en prueba, **Then** el reporte muestra precisión, exhaustividad y F1 de LOCA y LOCAC, en total y a 1, 2, 3, 5, 10, 20 y 30 s del inicio del evento.
2. **Given** las predicciones con confianza menor a 0,80, **When** se evalúa, **Then** se cuentan como UNCERTAIN y el reporte separa la cobertura (fracción de instantes con decisión), la exactitud sobre las decisiones tomadas y los errores con confianza.
3. **Given** una corrida de prueba, **When** se evalúa, **Then** el reporte indica el primer instante en que se confirma la rama correcta (≥ 0,80 dos segundos seguidos), si alguna vez se confirmó la rama equivocada, o «sin decisión».
4. **Given** las corridas de prueba, **When** se evalúa, **Then** los resultados se agrupan también por tamaño de rotura.

---

### User Story 3 - Obtener la recomendación de rama tras la Etapa 1 (Priority: P2)

El analista entrega al modelo guardado los datos de una corrida hasta un instante y la familia que dio la Etapa 1, y recibe las probabilidades de LOCA y LOCAC y la rama recomendada o UNCERTAIN, como recomendación consultiva. Si la Etapa 1 no indicó la familia LOCA, la Etapa 2 no se aplica.

**Why this priority**: Es la forma de usar el modelo en cascada con la Etapa 1, pero la tarea se cumple con el entrenamiento y la evaluación.

**Independent Test**: Cargar el modelo guardado y comprobar las probabilidades (suman 1), UNCERTAIN bajo 0,80, «no aplica» si la familia no es LOCA, y el aviso consultivo.

**Acceptance Scenarios**:

1. **Given** la familia LOCA de la Etapa 1 y una serie, **When** se clasifica, **Then** se obtienen dos probabilidades que suman 1 y la rama recomendada si la mayor es al menos 0,80.
2. **Given** que ninguna rama alcanza 0,80, **When** se clasifica, **Then** la recomendación es UNCERTAIN.
3. **Given** que la Etapa 1 indicó NORM, TRANS o INCIERTO, **When** se pide la Etapa 2, **Then** responde «no aplica» sin ejecutar el modelo.
4. **Given** cualquier salida, **When** se presenta, **Then** está identificada como recomendación consultiva.

---

### Edge Cases

- Roturas grandes: tras el disparo del reactor PWR y PWNT caen a ~5 %; la desviación pico conserva el máximo de los últimos 15 s, así que la señal del pico se pierde 15 s después del disparo. Se reporta por horizonte, no se oculta.
- Roturas muy pequeñas (2 a 20 cm²): el pico de potencia es casi nulo en ambas ramas; se espera abstención, no una decisión forzada.
- El evento empieza casi al iniciar la corrida (t = 1 s): la ventana de 15 s se recorta a lo disponible desde t = 0.
- Corrida LOCA o LOCAC sin instante de inicio conocido: se detiene con un error que nombra la corrida.
- Falta la columna PWR o PWNT, o tiene valores no numéricos: se detiene con un error que nombra el archivo y la variable.
- No hay corridas de una de las dos ramas en entrenamiento, validación o prueba: se detiene (entrenamiento) o se informa con cero (evaluación) sin inventar métricas.
- Prueba con pocas corridas (5 LOCA/LOCAC en el reparto de 004): el reporte advierte la incertidumbre.
- Se vuelve a entrenar sobre una salida anterior: se reemplazan solo los artefactos de esta etapa.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST clasificar en dos clases: LOCA (rotura en rama caliente) y LOCAC (rotura en rama fría), usando solo corridas usables de esas clases; las demás clases, las cortas, las descartadas y las OOD MUST NOT usarse.
- **FR-002**: El sistema MUST usar el reparto sin fuga de la funcionalidad 004 sin cambios y ejecutar su verificación de fuga antes de entrenar; todas las muestras de una corrida MUST pertenecer a su conjunto.
- **FR-003**: El sistema MUST calcular, para PWR y PWNT, el canal de desviación pico causal: en cada segundo τ, el máximo de la media móvil de 3 s en [τ − 14, τ] menos el valor inicial de la variable (t = 0), usando solo datos hasta τ.
- **FR-004**: El sistema MUST usar como entrada de la Bi-LSTM los canales definidos en la aclaración de entradas, escalados con parámetros ajustados solo con las corridas de entrenamiento (003); MUST NOT usar el caudal de fuga (WLR) ni los márgenes térmicos.
- **FR-005**: El sistema MUST formar una muestra por segundo τ desde el inicio del evento (redondeado hacia arriba) hasta el final de la corrida, con la ventana de los últimos 30 s hasta τ (rellenada con la primera fila al comenzar), etiquetada con la clase de la corrida y con k = τ − inicio. El entrenamiento MUST usar los primeros 60 s de cada evento; validación y evaluación, todas las muestras de evento.
- **FR-006**: El sistema MUST ponderar cada clase en proporción inversa a su frecuencia en entrenamiento y registrar los pesos.
- **FR-007**: El sistema MUST elegir el modelo final solo con las corridas de validación (parada temprana); la prueba MUST usarse solo en la evaluación final.
- **FR-008**: El sistema MUST producir el mismo modelo y las mismas métricas con los mismos datos, configuración y semilla.
- **FR-009**: El sistema MUST abstenerse (UNCERTAIN) cuando la mayor probabilidad sea menor que 0,80.
- **FR-010**: El sistema MUST reportar sobre prueba: matriz de confusión con la columna UNCERTAIN; precisión, exhaustividad y F1 de cada rama sobre todas las muestras (UNCERTAIN cuenta como no acierto); cobertura, exactitud sobre las decisiones y errores con confianza; en total y a 1, 2, 3, 5, 10, 20 y 30 s.
- **FR-011**: El sistema MUST reportar para cada corrida de prueba el tiempo de confirmación de la rama correcta (≥ 0,80 dos segundos seguidos), si se confirmó la rama equivocada, o «sin decisión», y agruparlo por tamaño de rotura.
- **FR-012**: El sistema MUST guardar el modelo, el escalador, las clases, los canales, la configuración, la semilla, los pesos, el historial y el reporte, y regenerarlos con una sola ejecución documentada, sin tocar los artefactos de la Etapa 1.
- **FR-013**: El sistema MUST ofrecer la clasificación de una serie nueva junto con la familia de la Etapa 1: si la familia no es LOCA, «no aplica»; si es LOCA, las probabilidades de las dos ramas y la recomendada o UNCERTAIN; toda salida MUST identificarse como consultiva.
- **FR-014**: El sistema MUST detenerse con un error que nombre la corrida, el archivo o la variable si falta el inicio del evento o PWR/PWNT no son válidos.
- **FR-015**: El sistema MUST NOT modificar los datos de origen, ni usar NPPAD, ni modificar el código de la Etapa 1, de la regla de ATWS ni de la preparación de datos.

### Key Entities

- **Rama**: LOCA (caliente) o LOCAC (fría); etiqueta que aprende el modelo.
- **Canal de desviación pico**: serie derivada de PWR o PWNT según FR-003.
- **Muestra**: ventana de 30 s hasta τ, con su rama y los segundos desde el inicio del evento.
- **Modelo de Etapa 2**: Bi-LSTM y todo lo necesario para reutilizarla (canales, escalador, clases, umbral, semilla, pesos).
- **Reporte**: métricas por horizonte, abstención, resultado por corrida y por área, advertencias.
- **Recomendación**: probabilidades de las dos ramas y rama recomendada, UNCERTAIN o «no aplica».

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En prueba, el 100 % de los instantes en los que el modelo decide (confianza ≥ 0,80) en los primeros 30 s del evento elige la rama correcta (0 errores con confianza).
- **SC-002**: En prueba, las corridas de rotura de 50 cm² o más se confirman en la rama correcta en 10 s o menos desde el inicio del evento.
- **SC-003**: El 100 % de las corridas LOCA/LOCAC de prueba aparece en el reporte con su resultado.
- **SC-004**: Dos entrenamientos con los mismos datos y semilla, en la misma máquina y entorno, producen métricas idénticas.
- **SC-005**: Entrenar y evaluar termina en menos de 15 minutos en una portátil sin GPU.
- **SC-006**: 0 muestras de una corrida aparecen en un conjunto distinto del de su corrida.

## Assumptions

- Solo PWR 3L (un dato por segundo); la constitución prohíbe mezclar con NPPAD.
- El reparto es el de 004: con los datos reales, 24 corridas LOCA/LOCAC en entrenamiento, 6 en validación y 5 en prueba.
- El inicio del evento se toma con la misma función de la Etapa 1 (`inicios_evento`), que se reutiliza sin modificarla.
- La ventana de 15 s y la media móvil de 3 s de la desviación pico vienen de `prueba_rama_caliente_fria_pwr3l.py` de IA-Nuclear; el valor inicial (t = 0) se toma como nominal.
- PWR no está entre las 26 entradas de 002; aquí se lee del mismo archivo solo para formar su canal de desviación pico.
- El umbral de 0,80 y la regla de confirmación de 2 s son los de la Etapa 1; si no se alcanzan las metas, se informa tal como salga.
- Fuera de alcance: modificar la Etapa 1, separar ATWS de TRIP_OK, la consola y el modo sombra.
