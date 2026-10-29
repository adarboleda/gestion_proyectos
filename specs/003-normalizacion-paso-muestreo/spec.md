# Feature Specification: Normalización solo con entrenamiento y verificación automática del paso de muestreo

**Feature Branch**: `003-normalizacion-paso-muestreo`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Normalización y verificación automática del paso de muestreo. Normalizar las variables de entrada usando solo el conjunto de entrenamiento. Calcular el paso de muestreo a partir de la columna TIME y detener el proceso si no es constante, en lugar de asumirlo." Alcance acordado con el usuario: aplicarlo a las dos preparaciones de datos del repositorio, NPPAD (funcionalidad 001) y PWR 3L (funcionalidad 002), sin tocar el resto de 002 (grupos, reparto, reporte), que está a cargo de otras personas.

## Clarifications

### Session 2026-10-28

> Preguntas de `/speckit-clarify` respondidas por el usuario.

- Q: Si todos los archivos tienen un paso constante y común pero distinto del de diseño (p. ej. 5 s en NPPAD en lugar de 10 s), ¿se detiene o se usa el medido? → A: No se compara con ningún valor esperado: se usa el paso medido, la duración de la muestra se calcula con él (con 5 s serían 750 s) y ambos se publican en metadatos y reporte. Comparar con un valor fijo volvería a suponer el paso.
- Q: ¿Qué se hace con la regla «el tiempo empieza en 0»? → A: Se mantiene en PWR 3L (regla de 002, FR-014 de esa spec) y no se añade a NPPAD.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El paso de muestreo se mide, no se supone (Priority: P1)

Un analista prepara los datos de una planta (NPPAD o PWR 3L). Hoy la preparación de NPPAD **supone** que hay un dato cada 10 s sin mirar el tiempo, y la de PWR 3L **supone** 1 s. Con esta funcionalidad, la preparación calcula el paso de muestreo a partir de la columna de tiempo de cada archivo, comprueba que sea constante en todo el archivo y que sea el mismo en todos los archivos del dataset, y se detiene con un error claro si no lo es.

**Why this priority**: Una ventana de «150 pasos» o de «300 pasos» solo representa 1500 s o 300 s si el paso es el que se cree. Un archivo con un hueco en el tiempo, un tiempo repetido o un muestreo distinto produciría muestras que mezclan escalas de tiempo sin que nadie lo note, y el clasificador aprendería de datos incoherentes (principio III: honestidad y reproducibilidad).

**Independent Test**: Preparar un dataset sintético con paso constante y comprobar que el paso informado es el medido; luego alterar el tiempo de un archivo (hueco, repetición, retroceso, paso distinto al del resto) y comprobar que la preparación se detiene nombrando el archivo, la fila y la causa, sin escribir ningún conjunto.

**Acceptance Scenarios**:

1. **Given** un dataset cuyos archivos avanzan todos con el mismo paso, **When** se prepara, **Then** la preparación termina y publica el paso medido (en segundos) y la duración de cada muestra (pasos × paso).
2. **Given** un archivo cuyo tiempo cambia de paso en alguna fila (también después de la parte que entra en la muestra), **When** se prepara, **Then** se detiene con un error que nombra el archivo, la fila donde cambia el paso y los dos valores de paso.
3. **Given** un archivo con un tiempo repetido o que retrocede, **When** se prepara, **Then** se detiene con un error que nombra el archivo y la fila.
4. **Given** dos archivos con pasos constantes pero distintos entre sí, **When** se prepara, **Then** se detiene nombrando el archivo discordante, su paso y el paso del resto del dataset.
5. **Given** un archivo sin la columna de tiempo o con un valor de tiempo no numérico, faltante o no finito, **When** se prepara, **Then** se detiene con el error de dato defectuoso habitual que nombra la variable de tiempo.

---

### User Story 2 - Las variables de entrada se normalizan solo con entrenamiento (Priority: P1)

El analista obtiene las variables de entrada normalizadas (media 0 y desviación 1 por variable) con parámetros calculados **solo** con las muestras de entrenamiento; esos mismos parámetros se aplican, sin recalcular, a validación y prueba, y se guardan para usarlos después con datos nuevos. Vale para NPPAD (12 variables de planta) y para PWR 3L (26 variables medibles en sala de control).

**Why this priority**: Es el principio II de la constitución (cero fuga de datos): si la media o la desviación se calculan con validación o prueba, las métricas posteriores quedan infladas.

**Independent Test**: Normalizar conjuntos sintéticos y comprobar que (a) los parámetros coinciden con los calculados a mano sobre las filas de entrenamiento, (b) cambiar validación o prueba no altera ningún parámetro, (c) entrenamiento queda con media ≈ 0 y desviación ≈ 1 por variable, y (d) una variable sin variación en entrenamiento no produce valores no válidos y queda informada.

**Acceptance Scenarios**:

1. **Given** los conjuntos de entrenamiento, validación y prueba, **When** se normalizan las entradas, **Then** los parámetros se calculan solo con las filas de entrenamiento y se aplican tal cual a los tres conjuntos.
2. **Given** dos ejecuciones que difieren solo en validación o prueba, **When** se normalizan, **Then** los parámetros son idénticos.
3. **Given** una variable de entrada constante en entrenamiento, **When** se normaliza, **Then** no aparece ningún valor no válido y la variable se informa como «sin varianza».
4. **Given** los márgenes térmicos, **When** se normalizan las entradas, **Then** los márgenes no forman parte de la normalización y quedan en sus unidades originales.
5. **Given** un conjunto de entrenamiento vacío o con una forma distinta de la esperada, **When** se intenta normalizar, **Then** el proceso se detiene con un error claro en lugar de producir parámetros inválidos.

---

### User Story 3 - El paso medido queda registrado (Priority: P2)

El analista ve en el reporte y en los metadatos de la preparación el paso de muestreo medido y la duración resultante de cada muestra, en lugar de una constante escrita a mano.

**Why this priority**: Permite comprobar, sin abrir los datos, que las ventanas representan el tiempo esperado; y quien consuma los artefactos lee el valor real.

**Independent Test**: Preparar el dataset sintético de NPPAD y comprobar que los metadatos y el reporte muestran el paso medido y la duración de la muestra.

**Acceptance Scenarios**:

1. **Given** una preparación de NPPAD terminada, **When** se leen los metadatos, **Then** el campo del paso de muestreo contiene el valor medido del tiempo y hay un campo con la duración de la muestra en segundos.
2. **Given** una preparación terminada, **When** se lee el reporte impreso, **Then** la sección de configuración indica el paso medido y que fue medido a partir del tiempo.
3. **Given** la lectura de las corridas PWR 3L, **When** termina, **Then** cada corrida leída lleva su paso medido y el dataset tiene un paso común disponible para el reporte que construya la funcionalidad 002.

---

### Edge Cases

- Un archivo con una sola fila de datos: no se puede calcular el paso; se detiene nombrando el archivo.
- Diferencias de tiempo con ruido de redondeo del archivo de texto (p. ej. 9.9999999 y 10.0000001): se aceptan como el mismo paso dentro de una tolerancia relativa muy pequeña (una millonésima del paso); una diferencia mayor detiene la preparación.
- Un cambio de paso **después** de la parte que entra en la muestra (después de la fila 150 en NPPAD o de la 300 en PWR 3L): también detiene, porque se valida el archivo completo (lección F5 de 001).
- PWR 3L: el tiempo debe además empezar en 0 (regla ya existente de 002, que se conserva); en NPPAD no se exige un valor inicial.
- PWR 3L: una corrida corta (menos de 300 filas) también se mide y su paso cuenta para el paso común del dataset, aunque no aporte muestra.
- Corridas descartadas u OOD de PWR 3L: no se leen, así que no se miden ni cuentan para el paso común.
- Una variable de entrada sin varianza en entrenamiento: queda con escala 1 (sin dividir por cero) y se informa.
- Re-ejecución con los mismos datos: mismo paso medido y mismos parámetros de normalización.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST calcular el paso de muestreo de cada archivo leído como la diferencia entre valores consecutivos de la columna de tiempo, usando **todas** las filas del archivo, y MUST NOT usar un paso fijo escrito en la configuración ni compararlo con un valor de diseño: el paso común medido es el que se usa y se publica.
- **FR-002**: El sistema MUST detenerse con un error que nombre el archivo, la variable de tiempo, la fila donde ocurre y la causa cuando el tiempo no avanza (diferencia cero o negativa) o cuando el paso cambia dentro del archivo más allá de la tolerancia (una millonésima relativa del paso); el mensaje de paso no constante MUST mostrar los dos valores de paso.
- **FR-003**: El sistema MUST detenerse cuando un archivo tenga menos de dos filas de datos, porque no se puede calcular su paso.
- **FR-004**: El sistema MUST comprobar que todos los archivos leídos de un mismo dataset tienen el mismo paso (con la misma tolerancia) y, si no, MUST detenerse nombrando el archivo discordante, su paso, el paso del resto y el archivo donde se midió ese paso.
- **FR-005**: Ante cualquiera de los errores de FR-002 a FR-004, la preparación MUST NOT escribir ningún conjunto ni artefacto (igual que con cualquier archivo defectuoso).
- **FR-006**: En PWR 3L se MUST conservar la comprobación de que el tiempo empieza en 0; en NPPAD no se añade ninguna regla sobre el valor inicial.
- **FR-007**: El sistema MUST publicar en los metadatos de NPPAD el paso medido (`paso_segundos`) y la duración de la muestra en segundos (`duracion_muestra_segundos` = pasos por muestra × paso), y MUST indicarlos en el reporte impreso.
- **FR-008**: En PWR 3L, la lectura MUST dejar en cada corrida leída su paso medido y MUST ofrecer el paso común del dataset para que lo usen el reporte y los metadatos de la funcionalidad 002.
- **FR-009**: El sistema MUST calcular los parámetros de normalización (media y desviación por variable de entrada) solo con las filas de las muestras de entrenamiento, MUST aplicarlos sin recalcular a entrenamiento, validación y prueba, y MUST permitir persistirlos.
- **FR-010**: Una variable de entrada sin varianza en entrenamiento MUST NOT producir valores no válidos (se usa escala 1) y MUST informarse por su nombre.
- **FR-011**: La normalización MUST detenerse con un error claro si el conjunto de entrenamiento está vacío o si un conjunto no tiene la forma esperada (muestras × pasos × variables de entrada de esa planta).
- **FR-012**: Los márgenes térmicos MUST NOT intervenir en la normalización.
- **FR-013**: NPPAD y PWR 3L MUST seguir siendo preparaciones separadas: cada una mide su propio paso y normaliza con su propio entrenamiento; nunca se combinan datos de las dos plantas (principio IV).
- **FR-014**: Con los mismos datos y configuración, el paso medido y los parámetros de normalización MUST ser idénticos entre ejecuciones.

### Key Entities

- **Paso de muestreo**: tiempo (s) entre dos filas consecutivas de un archivo; se mide de la columna de tiempo. Atributos: valor, archivo donde se midió.
- **Paso común del dataset**: el paso que comparten todos los archivos leídos de una planta; es el que se publica.
- **Parámetros de normalización**: media y desviación por variable de entrada, calculadas solo con entrenamiento; incluye la lista de variables sin varianza y el número de filas usadas.
- **Muestra**: ventana de pasos consecutivos de una simulación; su duración en segundos es pasos × paso común.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los archivos con tiempo alterado (hueco, repetición, retroceso, paso distinto al del resto, una sola fila) detiene la preparación con un mensaje que nombra el archivo, y no se escribe ningún artefacto.
- **SC-002**: Con los datos reales, el paso publicado es el medido: 10 s en NPPAD (202 simulaciones) y 1 s en las corridas PWR 3L de entrenamiento (100 archivos), sin ninguna constante de paso en la configuración.
- **SC-003**: Los parámetros de normalización coinciden (tolerancia relativa 1e-12) con los calculados solo sobre entrenamiento, y cambiar validación o prueba deja el 100 % de los parámetros sin cambios.
- **SC-004**: Tras normalizar, cada variable de entrada de entrenamiento queda con |media| < 1e-4 y |desviación − 1| < 1e-4 (salvo las sin varianza, que se informan).
- **SC-005**: Ninguna prueba existente de 001 o 002 deja de pasar por esta funcionalidad, salvo las que verifican el conjunto exacto de claves de `metadata.json` de 001 (que suma `duracion_muestra_segundos` por FR-007) o el texto del mensaje de tiempo de 002, que se actualizan.
- **SC-006**: Dos ejecuciones con los mismos datos producen el mismo paso y parámetros idénticos byte a byte.

## Assumptions

- Los datos reales están en `IA-Nuclear` (NPPAD en `NuclearPowerPlantAccidentData/Operation_csv_data`, PWR 3L en `PWR 3L`); se midió al escribir esta spec: NPPAD tiene paso 10 s constante desde 0 en las 202 simulaciones de las cuatro clases; PWR 3L tiene paso 1 s constante desde 0 en los 100 archivos de las cinco clases de entrenamiento.
- La tolerancia de una millonésima relativa del paso cubre el redondeo al exportar el tiempo como texto; los datos reales no la necesitan (los pasos son exactos).
- La normalización de NPPAD ya se ajustaba solo con entrenamiento (001); aquí se verifica con pruebas adicionales y se añaden los controles de forma y de entrenamiento vacío. La de PWR 3L no existía: se crea como componente, listo para que lo use el comando de 002 cuando se terminen los grupos y el reparto (tareas de otras personas).
- El número de pasos por muestra (150 en NPPAD, 300 en PWR 3L) no cambia; lo que cambia es que su duración en segundos se calcula con el paso medido.
- Quedan fuera: los grupos, el reparto, el reporte y el comando de 002; la normalización relativa al estado inicial (ingeniería de características del clasificador); y cualquier cambio en el número de pasos.
